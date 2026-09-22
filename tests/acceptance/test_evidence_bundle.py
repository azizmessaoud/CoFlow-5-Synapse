from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from coflow5.evidence import validate_bundle
from coflow5.evidence.schemas import PARQUET_SCHEMAS, RunManifest
from coflow5.smoke import scenario_hash

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "harness" / "work" / "02-evidence-bundle" / "artifacts"


@pytest.fixture(scope="session", autouse=True)
def generated_native_bundle() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "generate_evidence_bundle.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "status=completed" in result.stdout


def _manifest() -> dict:
    return json.loads((ARTIFACTS / "run_manifest.json").read_text(encoding="utf-8"))


def test_complete_native_bundle_has_canonical_immutable_manifest() -> None:
    raw = _manifest()
    manifest = RunManifest.model_validate(raw)
    assert manifest.status == "completed"
    assert manifest.immutable is True
    assert manifest.backend == "traci"
    assert manifest.scenario_hash == scenario_hash(ROOT)
    assert manifest.configuration_hash.startswith("sha256:")
    assert manifest.versions.python.startswith("3.11.")
    assert manifest.versions.sumo == "1.27.1"
    assert manifest.versions.traci == "1.27.1"
    assert manifest.versions.duckdb == "1.3.2"
    assert manifest.versions.pyarrow == "21.0.0"
    assert manifest.versions.pydantic == "2.11.7"
    assert manifest.seeds == {"sumo": 20260922}
    assert {ref.path for ref in manifest.artifact_references} == set(PARQUET_SCHEMAS)


def test_state_trips_and_kpis_are_derived_from_the_native_traci_run() -> None:
    state = pq.read_table(ARTIFACTS / "state.parquet").to_pylist()
    trips = pq.read_table(ARTIFACTS / "trips.parquet").to_pylist()
    kpis = pq.read_table(ARTIFACTS / "run_kpis.parquet").to_pylist()
    manifest = _manifest()

    assert state
    assert trips
    assert len(kpis) == 1
    assert sum(row["departed_vehicles"] for row in state) == len(trips) == 20
    assert sum(row["arrived_vehicles"] for row in state) == 20
    assert all(not row["unfinished"] for row in trips)
    assert kpis[0]["completed_trips"] == len(trips)
    assert kpis[0]["unfinished_trips"] == 0
    assert kpis[0]["simulation_steps"] == len(state) == manifest["timings"]["simulation_steps"]
    assert kpis[0]["mean_duration_s"] == pytest.approx(
        sum(row["duration"] for row in trips) / len(trips)
    )
    assert kpis[0]["total_time_loss_s"] == pytest.approx(
        sum(row["time_loss_s"] for row in trips)
    )
    assert max(row["active_vehicles"] for row in state) == kpis[0]["max_active_vehicles"]


def test_message_disposition_and_lifecycle_events_keep_immutable_joins() -> None:
    messages = pq.read_table(ARTIFACTS / "messages.parquet").to_pylist()
    events = pq.read_table(ARTIFACTS / "decision_events.parquet").to_pylist()
    manifest = _manifest()
    publications = [row for row in messages if row["record_kind"] == "message"]
    dispositions = [row for row in messages if row["record_kind"] == "disposition"]

    assert len(publications) == len(dispositions) == 1
    assert publications[0]["message_id"] == dispositions[0]["message_id"]
    assert dispositions[0]["disposition"] == "recorded"
    assert [row["event_kind"] for row in events] == ["transition", "transition"]
    assert len({row["event_id"] for row in events}) == len(events)
    assert all(row["considered_message_ids"] == [publications[0]["message_id"]] for row in events)
    for row in messages + events:
        assert row["run_id"] == manifest["run_id"]
        assert row["scenario_hash"] == manifest["scenario_hash"]


def test_required_artifacts_parse_and_join_audit_is_zero_error() -> None:
    expected = {
        "run_manifest.json",
        "state.parquet",
        "messages.parquet",
        "decision_events.parquet",
        "trips.parquet",
        "run_kpis.parquet",
        "join-audit.json",
    }
    assert expected == {path.name for path in ARTIFACTS.iterdir()}
    audit = validate_bundle(ARTIFACTS)
    on_disk = json.loads((ARTIFACTS / "join-audit.json").read_text(encoding="utf-8"))
    assert audit["valid"] is True
    assert audit["errors"] == []
    assert audit["artifact_checks"] == {"missing": 0, "corrupt": 0}
    assert audit["schema_checks"] == {"errors": 0, "checked": 5}
    assert audit["join_checks"] == {
        "missing": 0,
        "duplicate": 0,
        "cross_scenario": 0,
        "orphan": 0,
    }
    assert on_disk["run_id"] == audit["run_id"]
    assert on_disk["valid"] is True
