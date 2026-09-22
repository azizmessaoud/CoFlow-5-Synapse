from __future__ import annotations

import json
from dataclasses import FrozenInstanceError
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from coflow5.control.recovery import (
    REQUIRED_RECOVERY_LADDER,
    RecoveryExhaustedError,
    RecoveryMode,
    RecoverySupervisor,
)
from coflow5.evaluation.failure_artifacts import generate_failure_injection_artifacts

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "harness/work/08-failure-injection/artifacts"


@pytest.fixture(scope="module", autouse=True)
def generated_row08_artifacts() -> None:
    generate_failure_injection_artifacts(ROOT)


def test_required_recovery_ladder_is_exact_immutable_and_visible() -> None:
    supervisor = RecoverySupervisor(run_id="recovery-test", scenario_hash="sha256:" + "a" * 64)
    first = supervisor.report_failure(
        trigger="max-pressure-deadline", simulation_time=10.0,
        health_evidence={"deadline": "missed"},
    )
    second = supervisor.report_failure(
        trigger="actuated-invalid-output", simulation_time=11.0,
        health_evidence={"output": "invalid"},
    )
    assert REQUIRED_RECOVERY_LADDER == (
        RecoveryMode.COOPERATIVE_MAX_PRESSURE,
        RecoveryMode.ACTUATED,
        RecoveryMode.FIXED_TIME,
    )
    assert [(item.previous_mode, item.next_mode) for item in supervisor.transitions] == [
        (RecoveryMode.COOPERATIVE_MAX_PRESSURE, RecoveryMode.ACTUATED),
        (RecoveryMode.ACTUATED, RecoveryMode.FIXED_TIME),
    ]
    assert len({first.event_id, second.event_id}) == 2
    assert all(item.trigger and item.health_evidence for item in supervisor.transitions)
    with pytest.raises(FrozenInstanceError):
        first.trigger = "changed"  # type: ignore[misc]
    with pytest.raises(RecoveryExhaustedError, match="no hidden fallback"):
        supervisor.report_failure(
            trigger="fixed-time-failed", simulation_time=12.0,
            health_evidence={"heartbeat": "missed"},
        )


def test_optional_dqn_can_only_enter_required_ladder_at_max_pressure() -> None:
    supervisor = RecoverySupervisor(
        run_id="optional-test", scenario_hash="sha256:" + "b" * 64,
        optional_dqn_enabled=True,
    )
    transition = supervisor.report_failure(
        trigger="optional-dqn-invalid-output", simulation_time=1.0,
        health_evidence={"model": "unavailable"},
    )
    assert (transition.previous_mode, transition.next_mode) == (
        RecoveryMode.OPTIONAL_DQN, RecoveryMode.COOPERATIVE_MAX_PRESSURE,
    )
    assert REQUIRED_RECOVERY_LADDER[0] is supervisor.mode


def test_recovery_artifact_contains_only_required_path_and_unique_joined_events() -> None:
    audit = json.loads((ARTIFACTS / "recovery-audit.json").read_text(encoding="utf-8"))
    rows = pq.read_table(ARTIFACTS / "faults.parquet").to_pylist()
    transitions = [row for row in rows if row["event_kind"] == "transition"]
    assert audit["valid"] is True
    assert audit["required_recovery_ladder"] == [
        "COOPERATIVE_MAX_PRESSURE", "ACTUATED", "FIXED_TIME"
    ]
    assert audit["observed_required_transitions"] == [
        ["COOPERATIVE_MAX_PRESSURE", "ACTUATED"],
        ["ACTUATED", "FIXED_TIME"],
    ]
    assert audit["unexpected_transitions"] == []
    assert audit["optional_dqn_dependency"] is False
    assert audit["hidden_exception_swallowing"] is False
    assert len({row["event_id"] for row in rows}) == len(rows)
    assert all(row["trigger"] and row["health_evidence_json"] for row in transitions)
    assert all(
        row["run_id"] == audit["run_id"]
        and row["scenario_hash"] == audit["scenario_hash"]
        for row in rows
    )
