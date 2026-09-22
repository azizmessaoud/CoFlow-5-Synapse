from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import pyarrow.parquet as pq

from coflow5.evidence.baseline_artifacts import build_baseline_comparison

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "harness/work/04-baselines/artifacts"


def _load(name: str) -> dict:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


def test_every_kpi_resolves_to_one_manifest_and_scenario() -> None:
    manifests = {
        manifest["run_id"]: manifest
        for manifest in (_load("fixed-time-run_manifest.json"), _load("actuated-run_manifest.json"))
    }
    rows = pq.read_table(ARTIFACTS / "run_kpis.parquet").to_pylist()
    assert len(manifests) == len(rows) == 2
    for row in rows:
        manifest = manifests[row["run_id"]]
        assert row["scenario_hash"] == manifest["scenario_hash"]
        assert row["seed"] == manifest["seeds"]["evaluation"]
        assert row["controller"] == manifest["controller"]
        assert row["status"] == manifest["status"]


def test_each_scenario_seed_cell_contains_both_baseline_labels() -> None:
    comparison = _load("baseline-comparison.json")
    assert comparison["pairing_keys"] == ["scenario_hash", "seed"]
    assert comparison["controller_labels"] == ["fixed-time", "actuated"]
    assert comparison["common_evaluation_seeds"] == [37]
    assert comparison["pair_cells"]
    for cell in comparison["pair_cells"]:
        assert set(cell["controller_labels"]) == {"fixed-time", "actuated"}
        assert cell["missing_controller_labels"] == []
        assert cell["complete_pair"] is True
        assert cell["included_in_metric_comparison"] is True


def test_completion_unfinished_and_status_counts_reconcile() -> None:
    comparison = _load("baseline-comparison.json")
    rows = pq.read_table(ARTIFACTS / "run_kpis.parquet").to_pylist()
    for row in rows:
        assert row["completed_trips"] + row["unfinished_trips"] == row["planned_trips"]
        expected = row["completed_trips"] / row["planned_trips"]
        assert row["completion_rate"] == expected
    assert comparison["unfinished_trip_count"] == sum(row["unfinished_trips"] for row in rows)
    assert sum(comparison["status_counts"].values()) == len(rows)


def test_failed_and_invalid_runs_remain_visible_with_explicit_exclusion() -> None:
    base = {
        "scenario_hash": "sha256:" + "a" * 64,
        "seed": 9,
        "unfinished_trips": 4,
        "completion_rate": 0.5,
        "mean_duration_s": 1.0,
        "p95_duration_s": 1.0,
        "mean_waiting_time_s": 1.0,
        "p95_waiting_time_s": 1.0,
        "standstill_vehicle_seconds": 1,
        "teleport_events": 0,
    }
    comparison = build_baseline_comparison([
        base | {"run_id": "fixed-failed", "controller": "fixed-time", "status": "failed", "failure_reason": "injected"},
        base | {"run_id": "act-invalid", "controller": "actuated", "status": "invalid", "failure_reason": "corrupt"},
    ])
    assert comparison["failed_run_count"] == 1
    assert comparison["invalid_run_count"] == 1
    assert len(comparison["visible_runs"]) == 2
    assert comparison["unfinished_trip_count"] == 8
    assert comparison["pair_cells"][0]["included_in_metric_comparison"] is False
    assert comparison["pair_cells"][0]["exclusion_reason"] == "non-completed-status"



def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    rank = (len(ordered) - 1) * percentile
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    fraction = rank - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def test_persisted_trip_rows_recompute_completion_unfinished_and_tails() -> None:
    trips = pq.read_table(ARTIFACTS / "baseline_trips.parquet").to_pylist()
    kpis = {
        row["run_id"]: row
        for row in pq.read_table(ARTIFACTS / "run_kpis.parquet").to_pylist()
    }
    expected_flow_counts = {
        "north-demand": 30,
        "south-demand": 30,
        "east-demand": 12,
        "west-demand": 12,
    }
    assert len(trips) == 84 * len(kpis)
    for run_id, kpi in kpis.items():
        run_trips = [row for row in trips if row["run_id"] == run_id]
        assert len(run_trips) == kpi["planned_trips"] == 84
        assert {
            flow_id: sum(row["flow_id"] == flow_id for row in run_trips)
            for flow_id in expected_flow_counts
        } == expected_flow_counts
        completed = [row for row in run_trips if row["trip_status"] == "completed"]
        unfinished = [
            row for row in run_trips
            if row["trip_status"] in {"active-at-horizon", "not-departed"}
        ]
        assert len(completed) == kpi["completed_trips"]
        assert len(unfinished) == kpi["unfinished_trips"]
        durations = [row["duration_s"] for row in completed]
        waits = [row["waiting_time_s"] for row in completed]
        assert kpi["mean_duration_s"] == sum(durations) / len(durations)
        assert kpi["p95_duration_s"] == _percentile(durations, 0.95)
        assert kpi["max_duration_s"] == max(durations)
        assert kpi["mean_waiting_time_s"] == sum(waits) / len(waits)
        assert kpi["p95_waiting_time_s"] == _percentile(waits, 0.95)
        assert kpi["max_waiting_time_s"] == max(waits)
        assert kpi["total_time_loss_s"] == sum(row["time_loss_s"] for row in completed)
        assert kpi["standstill_vehicle_seconds"] == sum(
            row["standstill_seconds"] for row in run_trips
        )


def test_successful_native_runs_reconcile_one_writer_events_commands_and_hashes() -> None:
    events = pq.read_table(ARTIFACTS / "safety_events.parquet").to_pylist()
    commands = pq.read_table(ARTIFACTS / "executed_commands.parquet").to_pylist()
    audit = _load("baseline-audit.json")
    comparison = _load("baseline-comparison.json")
    expected_extra_paths = {
        "baseline_trips.parquet",
        "safety_events.parquet",
        "executed_commands.parquet",
        "baseline-audit.json",
    }
    comparison_refs = {ref["path"]: ref for ref in comparison["artifact_references"]}
    assert expected_extra_paths <= set(comparison_refs)
    for name, reference in comparison_refs.items():
        path = ARTIFACTS / name
        assert reference["sha256"] == _sha256(path)
        assert reference["bytes"] == path.stat().st_size

    for label in ("fixed-time", "actuated"):
        manifest = _load(f"{label}-run_manifest.json")
        run_id = manifest["run_id"]
        run_events = [row for row in events if row["run_id"] == run_id]
        run_commands = [row for row in commands if row["run_id"] == run_id]
        run_audit = next(row for row in audit["runs"] if row["run_id"] == run_id)
        accepted_ids = {row["event_id"] for row in run_events if row["accepted"]}
        command_ids = {row["event_id"] for row in run_commands}
        assert manifest["status"] == "completed"
        assert run_audit["one_writer_per_signal"] is True
        assert run_audit["writer_count_by_signal"] == {"J0": 1}
        assert run_audit["rejected_count"] == 0
        assert run_audit["illegal_executed_actions"] == 0
        assert run_audit["physically_conflicting_executed_actions"] == 0
        assert run_audit["accepted_without_command"] == 0
        assert run_audit["command_without_accepted_event"] == 0
        assert accepted_ids == command_ids
        manifest_refs = {ref["path"]: ref for ref in manifest["artifact_references"]}
        assert expected_extra_paths <= set(manifest_refs)
        for name, reference in manifest_refs.items():
            path = ARTIFACTS / name
            assert reference["sha256"] == _sha256(path)
            assert reference["bytes"] == path.stat().st_size
