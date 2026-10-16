from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from coflow5.control.recovery import (
    REQUIRED_RECOVERY_LADDER,
    RecoveryExhaustedError,
    RecoveryMode,
    RecoverySupervisor,
)


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
