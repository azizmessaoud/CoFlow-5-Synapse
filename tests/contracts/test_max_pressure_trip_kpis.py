from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from coflow5.evidence.max_pressure_trip_artifacts import (
    RUN_KPI_SCHEMA,
    TRIP_SCHEMA,
    _forbid_protected_destination,
    generate_max_pressure_trip_artifacts,
)
from coflow5.sumo_adapter.max_pressure_trip_runner import linear_percentile

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = {
    "run_manifest.json",
    "trips.parquet",
    "run_kpis.parquet",
    "matched-comparison.json",
    "input-audit.json",
}
EXPECTED_SCENARIO_HASH = "sha256:152b75ac1da3e313b75a952d39e7ff1089d47f258d867b8932dd8a997130fdce"


@pytest.fixture(scope="module")
def artifacts(tmp_path_factory: pytest.TempPathFactory) -> Path:
    destination = tmp_path_factory.mktemp("row10b") / "artifacts"
    generate_max_pressure_trip_artifacts(ROOT, destination)
    return destination


def test_native_artifacts_are_exact_hash_bound_and_inputs_remain_locked(artifacts: Path) -> None:
    assert {path.name for path in artifacts.iterdir()} == REQUIRED
    manifest = json.loads((artifacts / "run_manifest.json").read_text(encoding="utf-8"))
    audit = json.loads((artifacts / "input-audit.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "completed" and manifest["immutable"] is True
    assert manifest["backend"] == "traci"
    assert manifest["controller"] == "cooperative-max-pressure"
    assert manifest["scenario_hash"] == EXPECTED_SCENARIO_HASH
    assert manifest["seeds"] == {"sumo": 37, "evaluation": 37}
    refs = {row["path"]: row for row in manifest["artifact_references"]}
    assert set(refs) == REQUIRED - {"run_manifest.json"}
    for name, schema in {"trips.parquet": TRIP_SCHEMA, "run_kpis.parquet": RUN_KPI_SCHEMA}.items():
        table = pq.read_table(artifacts / name)
        assert table.schema == schema
        assert refs[name]["rows"] == table.num_rows
        assert refs[name]["sha256"] == "sha256:" + hashlib.sha256((artifacts / name).read_bytes()).hexdigest()
    for relative, expected in manifest["source_hashes"].items():
        assert "sha256:" + hashlib.sha256((ROOT / relative).read_bytes()).hexdigest() == expected
    assert audit["all_locked_input_hashes_match"] is True
    assert audit["locked_inputs_unchanged_during_generation"] is True
    assert audit["row05_frozen_source_drift_count"] == 1
    assert audit["row05_frozen_source_drift"][0]["path"] == "src/coflow5/sumo_adapter/max_pressure_runner.py"
    assert audit["row05_frozen_source_drift"][0]["approved_default_empty_launch_hook"] is True


def test_trip_rows_recompute_every_kpi_and_retain_all_84_planned_ids(artifacts: Path) -> None:
    trips = pq.read_table(artifacts / "trips.parquet").to_pylist()
    kpis = pq.read_table(artifacts / "run_kpis.parquet").to_pylist()
    assert len(kpis) == 1 and len(trips) == 84
    kpi = kpis[0]
    assert len({row["trip_id"] for row in trips}) == 84
    assert {row["run_id"] for row in trips} == {kpi["run_id"]}
    assert {row["scenario_hash"] for row in trips} == {EXPECTED_SCENARIO_HASH}
    assert {row["seed"] for row in trips} == {37}
    assert {row["controller"] for row in trips} == {"cooperative-max-pressure"}
    completed = [row for row in trips if row["trip_status"] == "completed"]
    unfinished = [row for row in trips if row["trip_status"] != "completed"]
    durations = [row["duration_s"] for row in completed]
    waits = [row["waiting_time_s"] for row in completed]
    losses = [row["time_loss_s"] for row in completed]
    assert kpi["planned_trips"] == 84
    assert kpi["completed_trips"] == len(completed)
    assert kpi["unfinished_trips"] == len(unfinished)
    assert kpi["completed_trips"] + kpi["unfinished_trips"] == 84
    assert kpi["completion_rate"] == pytest.approx(len(completed) / 84)
    assert kpi["mean_duration_s"] == pytest.approx(sum(durations) / len(durations))
    assert kpi["p95_duration_s"] == pytest.approx(linear_percentile(durations, 0.95))
    assert kpi["max_duration_s"] == max(durations)
    assert kpi["mean_waiting_time_s"] == pytest.approx(sum(waits) / len(waits))
    assert kpi["p95_waiting_time_s"] == pytest.approx(linear_percentile(waits, 0.95))
    assert kpi["max_waiting_time_s"] == max(waits)
    assert kpi["total_time_loss_s"] == pytest.approx(sum(losses))
    assert kpi["standstill_vehicle_seconds"] == sum(row["standstill_seconds"] for row in trips)
    assert kpi["vehicles_with_standstill"] == sum(row["standstill_seconds"] > 0 for row in trips)
    assert kpi["teleport_events"] == 0


def test_three_controller_comparison_is_matched_and_makes_no_winner_claim(artifacts: Path) -> None:
    comparison = json.loads((artifacts / "matched-comparison.json").read_text(encoding="utf-8"))
    manifest = json.loads((artifacts / "run_manifest.json").read_text(encoding="utf-8"))
    audit = manifest["runtime_audit"]
    assert comparison["parity_pass"] is True
    assert comparison["scenario_hash"] == EXPECTED_SCENARIO_HASH
    assert comparison["seed"] == 37
    assert comparison["configured_horizon_seconds"] == 120.0
    assert [row["controller"] for row in comparison["controller_rows"]] == [
        "fixed-time", "actuated", "cooperative-max-pressure"
    ]
    assert all(row["planned_trips"] == 84 for row in comparison["controller_rows"])
    assert comparison["one_seed_only"] is True
    assert comparison["significance_test_performed"] is False
    assert comparison["winner_claim"] is None
    assert "insufficient" in comparison["claim_boundary"].lower()
    assert audit["actual_traci_execution"] is True
    assert audit["writer_count_by_signal"] == {"J0": 1}
    assert audit["decision_count"] == audit["safety_event_count"] == audit["accepted_command_count"]
    assert audit["event_sets_match"] is True
    assert audit["rejected_or_conflicting_executed_commands"] == 0
    assert audit["reinforcement_learning_required"] is False
    assert audit["advisory_message_count"] == 1


def test_all_protected_row_destinations_are_rejected_without_file_changes() -> None:
    protected = [
        ROOT / "harness/work" / name
        for name in (
            "02-evidence-bundle", "03-safety-mask", "04-baselines", "05-max-pressure",
            "06-message-board", "07-a2-a3", "08-failure-injection", "09-eval-harness",
        )
    ]
    before = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for directory in protected
        for path in directory.rglob("*")
        if path.is_file()
    }
    for directory in protected:
        for destination in (directory, directory / "nested-row10b-output"):
            with pytest.raises(ValueError, match="protected Rows 02-09"):
                _forbid_protected_destination(ROOT, destination.resolve())
    after = {
        str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
        for directory in protected
        for path in directory.rglob("*")
        if path.is_file()
    }
    assert after == before
