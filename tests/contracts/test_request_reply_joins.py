import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from coflow5.evidence.cooperation_artifacts import (
    DECISION_SCHEMA,
    KPI_SCHEMA,
    MESSAGE_SCHEMA,
    SCENARIO_FILES,
    TRIP_SCHEMA,
    generate_cooperation_artifacts,
)

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = {
    "run_manifest.json", "messages.parquet", "decision_events.parquet",
    "trips.parquet", "cooperation-kpis.parquet",
}


@pytest.fixture(scope="module")
def row07_artifacts(tmp_path_factory: pytest.TempPathFactory) -> Path:
    destination = tmp_path_factory.mktemp("row07-native") / "artifacts"
    generate_cooperation_artifacts(ROOT, destination)
    return destination


def _rows(artifacts: Path, name: str) -> list[dict]:
    return pq.read_table(artifacts / name).to_pylist()


def _scenario_hash() -> str:
    digest = hashlib.sha256()
    for relative in SCENARIO_FILES:
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update((ROOT / relative).read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def test_exact_artifacts_are_hash_bound_to_one_native_run_and_exact_schemas(
    row07_artifacts: Path,
) -> None:
    assert {path.name for path in row07_artifacts.iterdir()} == REQUIRED
    manifest = json.loads(
        (row07_artifacts / "run_manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["status"] == "completed" and manifest["immutable"] is True
    assert manifest["backend"] == "traci"
    assert manifest["controller"] == "cooperative-max-pressure"
    assert manifest["scenario_hash"] == _scenario_hash()
    assert manifest["scenario_files"] == list(SCENARIO_FILES)
    assert manifest["versions"]["python"].startswith("3.11.")
    assert manifest["versions"]["sumo"] == manifest["versions"]["traci"] == "1.27.1"
    assert "cooperation-control.sumocfg" in " ".join(manifest["sumo_command"])
    assert "--tripinfo-output" in manifest["sumo_command"]
    assert manifest["timings"]["simulation_steps"] > 0
    assert manifest["source_revision"] is None
    assert "src/coflow5/sumo_adapter/cooperation_runner.py" in manifest["source_hashes"]

    assert {item["path"] for item in manifest["artifact_references"]} == REQUIRED - {
        "run_manifest.json"
    }
    for reference in manifest["artifact_references"]:
        path = row07_artifacts / reference["path"]
        assert "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"]
        assert pq.read_table(path).num_rows == reference["rows"]
    schemas = {
        "messages.parquet": MESSAGE_SCHEMA,
        "decision_events.parquet": DECISION_SCHEMA,
        "trips.parquet": TRIP_SCHEMA,
        "cooperation-kpis.parquet": KPI_SCHEMA,
    }
    for name, schema in schemas.items():
        table = pq.read_table(row07_artifacts / name)
        assert table.schema == schema
        assert set(table.column("run_id").to_pylist()) == {manifest["run_id"]}
        assert set(table.column("scenario_hash").to_pylist()) == {manifest["scenario_hash"]}


def test_every_request_has_one_reply_and_one_immutable_decision_join(
    row07_artifacts: Path,
) -> None:
    messages = _rows(row07_artifacts, "messages.parquet")
    decisions = _rows(row07_artifacts, "decision_events.parquet")
    requests = {row["message_id"]: row for row in messages if row["record_kind"] == "request"}
    replies = [row for row in messages if row["record_kind"] == "reply"]
    assert "early-bus-forbidden" not in requests
    assert len(decisions) == len(requests) == len(replies) == 7
    assert len({row["event_id"] for row in decisions}) == len(decisions)
    assert {row["referenced_message_id"] for row in decisions} == set(requests)
    assert {row["referenced_message_id"] for row in replies} == set(requests)
    decision_by_event = {row["event_id"]: row for row in decisions}
    for reply in replies:
        decision = decision_by_event[reply["event_id"]]
        assert reply["referenced_message_id"] == decision["referenced_message_id"]
        assert reply["reason_code"] == decision["reason_code"]
        assert reply["accepted"] == decision["accepted"]
        assert reply["run_id"] == decision["run_id"]
        assert reply["scenario_hash"] == decision["scenario_hash"]
    assert all(row["reason_code"] and row["safety_reason_code"] for row in decisions)

    by_request = {row["referenced_message_id"]: row for row in decisions}
    assert by_request["crossing-active-001"]["accepted"] is True
    assert by_request["emergency-conflict-001"]["reason_code"] == "REJECTED_PEDESTRIAN_CLEARANCE"
    assert by_request["emergency-alpha"]["accepted"] is True
    assert by_request["emergency-beta"]["reason_code"] == "REJECTED_SAME_TIER_TIEBREAK"
    assert by_request["emergency-blocked-001"]["reason_code"] == "REJECTED_DOWNSTREAM_BLOCKED"


def test_native_trips_and_kpis_separate_benefits_externalities_and_modal_outcomes(
    row07_artifacts: Path,
) -> None:
    trips = _rows(row07_artifacts, "trips.parquet")
    assert len(trips) == 46
    assert {row["actor_type"] for row in trips} == {"civilian", "emergency", "transit"}
    assert {"crossing_emergency_conflict", "two_emergencies", "late_bus", "early_bus"} <= {
        row["scenario_case"] for row in trips
    }
    assert all("paired-native-traci-tripinfo" in row["evidence_basis"] for row in trips)
    assert all(not row["unfinished"] for row in trips)
    assert all(row["baseline_duration_s"] is not None for row in trips)
    assert all(row["observed_duration_s"] is not None for row in trips)

    rows = _rows(row07_artifacts, "cooperation-kpis.parquet")
    metrics = {row["metric_name"]: row for row in rows}
    required = {
        "emergency_travel_effect_s", "civilian_delay_externality_s",
        "pedestrian_mean_wait_s", "pedestrian_p95_wait_s", "pedestrian_max_wait_s",
        "pedestrian_remaining_clearance_s", "pedestrian_clearance_truncations",
        "transit_lateness_s", "transit_headway_regularity_s",
        "transit_other_traffic_externality_s", "specialist_signal_writes",
        "post_passage_recovery_completed",
    }
    assert required <= metrics.keys()
    assert metrics["pedestrian_clearance_truncations"]["metric_value"] == 0
    assert metrics["specialist_signal_writes"]["metric_value"] == 0
    assert metrics["post_passage_recovery_completed"]["metric_value"] == 1
    assert metrics["emergency_travel_effect_s"]["metric_category"] == "emergency"
    assert metrics["civilian_delay_externality_s"]["metric_category"] == "externality"
    assert metrics["transit_other_traffic_externality_s"]["metric_category"] == "externality"
    assert "native traci" in metrics["emergency_travel_effect_s"]["evidence_basis"].lower()
    assert "native traci" in metrics["civilian_delay_externality_s"]["evidence_basis"].lower()
    assert "not a roadside measurement" in metrics["pedestrian_mean_wait_s"]["evidence_basis"]
    assert "not a causal traffic-effect estimate" in metrics[
        "transit_other_traffic_externality_s"
    ]["evidence_basis"]
    assert all("no lives-saved claim" in row["claim_boundary"].lower() for row in rows)
    assert all("no measured-air-quality claim" in row["claim_boundary"].lower() for row in rows)
