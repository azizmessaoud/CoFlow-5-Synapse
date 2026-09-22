from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from coflow5.evaluation.failure_artifacts import generate_failure_injection_artifacts
from coflow5.failures import FailureClass

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "harness/work/08-failure-injection/artifacts"
REQUIRED = {
    "run_manifest.json", "faults.parquet", "messages.parquet",
    "decision_events.parquet", "recovery-audit.json",
    "action-sequence-comparison.json",
}


@pytest.fixture(scope="module", autouse=True)
def generated_row08_artifacts() -> None:
    generate_failure_injection_artifacts(ROOT)


def _rows(name: str) -> list[dict]:
    return pq.read_table(ARTIFACTS / name).to_pylist()


def test_exact_artifacts_are_hash_bound_and_joined() -> None:
    assert {path.name for path in ARTIFACTS.iterdir()} == REQUIRED
    manifest = json.loads((ARTIFACTS / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "completed" and manifest["immutable"] is True
    assert {item["path"] for item in manifest["artifact_references"]} == REQUIRED - {
        "run_manifest.json"
    }
    for reference in manifest["artifact_references"]:
        path = ARTIFACTS / reference["path"]
        assert "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest() == reference["sha256"]
    for name in ("faults.parquet", "messages.parquet", "decision_events.parquet"):
        rows = _rows(name)
        assert rows
        assert {row["run_id"] for row in rows} == {manifest["run_id"]}
        assert {row["scenario_hash"] for row in rows} == {manifest["scenario_hash"]}


def test_every_contracted_fault_leaves_legal_local_max_pressure() -> None:
    faults = [row for row in _rows("faults.parquet") if row["event_kind"] == "fault"]
    decisions = _rows("decision_events.parquet")
    expected = {item.value for item in FailureClass}
    assert {row["failure_class"] for row in faults} == expected
    assert {row["failure_class"] for row in decisions} == expected
    assert len(faults) == len(decisions) == len(expected)
    assert len({row["event_id"] for row in faults}) == len(faults)
    assert all(row["visible"] for row in faults)
    assert all(
        row["controller_mode"] == "COOPERATIVE_MAX_PRESSURE"
        and row["legal"] is True
        and row["local_only"] is True
        and row["considered_message_ids"] == []
        and row["reason_code"] == "MAX_PRESSURE_LOCAL_ONLY"
        and row["safety_reason_code"] == "ACCEPTED"
        for row in decisions
    )
    fault_ids = {row["event_id"] for row in faults}
    assert all(row["fault_event_id"] in fault_ids for row in decisions)


def test_applicable_message_faults_retain_message_id_and_disposition() -> None:
    messages = _rows("messages.parquet")
    faults = {
        row["event_id"]: row for row in _rows("faults.parquet")
        if row["event_kind"] == "fault"
    }
    assert len(messages) == len(FailureClass)
    not_applicable = {
        FailureClass.MESSAGE_ABSENCE.value,
        FailureClass.ADVISER_SILENCE.value,
    }
    for row in messages:
        fault = faults[row["fault_event_id"]]
        assert row["failure_class"] == fault["failure_class"]
        assert row["disposition"] == fault["disposition"]
        if row["failure_class"] in not_applicable:
            assert row["message_id"] is None
        else:
            assert row["message_id"] and row["message_id"] == fault["message_id"]



def test_transport_exception_is_visible_not_silently_swallowed() -> None:
    from coflow5.messaging import MessageDisposition, read_a1_advisories

    class FailingTransport:
        def read(self, *args, **kwargs):
            raise RuntimeError("injected adviser transport failure")

    result = read_a1_advisories(
        FailingTransport(),  # type: ignore[arg-type]
        run_id="visible-failure", scenario_hash="sha256:" + "d" * 64,
        signal_id="J0", valid_at=1.0,
    )
    assert result.disposition is MessageDisposition.UNAVAILABLE
    assert result.advisories == ()
    assert result.transport_error == "RuntimeError: injected adviser transport failure"
