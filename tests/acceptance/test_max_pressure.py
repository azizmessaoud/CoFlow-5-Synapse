from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from coflow5.control import DeterministicSafetyMask, controlled_cross_plan
from coflow5.control.a1_controller import A1FlowController
from coflow5.control.max_pressure import (
    AdvisoryRequest,
    CooperativeMaxPressureController,
    MaxPressureObservation,
    MovementPressure,
)
from coflow5.sumo_adapter.signal_executor import ImmutableSafetyLog, SignalExecutorRegistry

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "harness/work/05-max-pressure/artifacts"
RUN_ID = "run-max-pressure-test"
SCENARIO_HASH = "sha256:" + "5" * 64


class FakeTrafficLight:
    def __init__(self) -> None:
        self.state = "GrGr"
        self.writes: list[tuple[str, str]] = []

    def setRedYellowGreenState(self, signal_id: str, state: str) -> None:
        self.state = state
        self.writes.append((signal_id, state))

    def getRedYellowGreenState(self, signal_id: str) -> str:
        return self.state


class FakeConnection:
    def __init__(self) -> None:
        self.trafficlight = FakeTrafficLight()


def _controller():
    connection = FakeConnection()
    log = ImmutableSafetyLog()
    mask = DeterministicSafetyMask(controlled_cross_plan())
    executor = SignalExecutorRegistry().acquire(
        signal_id="J0",
        connection=connection,
        safety_mask=mask,
        initial_phase_id="NS_GREEN",
        initial_phase_entered_at=0.0,
        run_id=RUN_ID,
        scenario_hash=SCENARIO_HASH,
        log=log,
    )
    controller = CooperativeMaxPressureController(
        a1=A1FlowController(executor),
        safety_mask=mask,
        run_id=RUN_ID,
        scenario_hash=SCENARIO_HASH,
        signal_id="J0",
    )
    return controller, connection, log


def _movements(ns: float = 1.0, ew: float = 5.0, ew_capacity: float = 20.0):
    return {
        "north": MovementPressure(ns, 0.0, 20.0),
        "south": MovementPressure(ns, 0.0, 20.0),
        "east": MovementPressure(ew, 0.0, ew_capacity),
        "west": MovementPressure(ew, 0.0, ew_capacity),
    }


def _observation(
    *,
    movements=None,
    advisories=(),
    simulation_time: float = 6.0,
) -> MaxPressureObservation:
    return MaxPressureObservation(
        simulation_time=simulation_time,
        current_phase_id="NS_GREEN",
        phase_entered_at=0.0,
        movements=movements or _movements(),
        advisories=advisories,
    )


@pytest.fixture(scope="session", autouse=True)
def generated_max_pressure_evidence() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/generate_max_pressure_artifacts.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "run_id=" in result.stdout
    assert "missing green" not in result.stderr.lower()


def test_scores_only_legal_actions_from_pressure_timing_and_downstream_capacity() -> None:
    controller, connection, log = _controller()
    decision = controller.decide(
        proposal_id="local-only",
        observation=_observation(movements=_movements(ns=1.0, ew=8.0)),
    )
    assert decision.accepted_action == "NS_YELLOW"
    assert {score.phase_id for score in decision.action_scores} == {"NS_GREEN", "NS_YELLOW"}
    assert all(score.phase_id != "EW_GREEN" for score in decision.action_scores)
    assert all(score.phase_timing != 0 for score in decision.action_scores)
    assert decision.action_scores[0].pressure > decision.action_scores[1].pressure
    assert decision.considered_message_ids == ()
    assert decision.reason_code == "MAX_PRESSURE_LOCAL_ONLY"
    assert decision.constraints and decision.rejected_alternatives == ("NS_GREEN",)
    assert len(log.events) == len(log.commands) == 1
    assert connection.trafficlight.writes == [("J0", "yryr")]

    blocked = MovementPressure(10.0, 10.0, 10.0)
    assert blocked.available_capacity_ratio == 0.0
    assert blocked.capacity_weighted_pressure == 0.0


def test_fully_blocked_transition_is_hard_masked_before_advisory_scoring() -> None:
    controller, connection, _ = _controller()
    blocked_movements = {
        "north": MovementPressure(1.0, 0.0, 20.0),
        "south": MovementPressure(1.0, 0.0, 20.0),
        "east": MovementPressure(10.0, 10.0, 10.0),
        "west": MovementPressure(10.0, 10.0, 10.0),
    }
    request = AdvisoryRequest(
        "blocked-request", RUN_ID, "J0", "NS_YELLOW", "A2", 5.0, 8.0, 1.0
    )
    decision = controller.decide(
        proposal_id="blocked-downstream",
        observation=_observation(movements=blocked_movements, advisories=(request,)),
    )
    blocked_score = next(
        score for score in decision.action_scores if score.phase_id == "NS_YELLOW"
    )
    assert decision.accepted_action == "NS_GREEN"
    assert decision.considered_message_ids == ()
    assert blocked_score.downstream_available is False
    assert blocked_score.advisory == 0.0
    assert "downstream_blocked_actions=NS_YELLOW" in decision.constraints
    assert connection.trafficlight.writes == [("J0", "GrGr")]


def test_duplicate_advisory_identity_contributes_once_and_conflicts_are_ignored() -> None:
    request = AdvisoryRequest(
        "same-message", RUN_ID, "J0", "NS_YELLOW", "A2", 5.0, 8.0, 0.2
    )
    controller, _, _ = _controller()
    decision = controller.decide(
        proposal_id="duplicate-message",
        observation=_observation(advisories=(request, request)),
    )
    requested = next(
        score for score in decision.action_scores if score.phase_id == "NS_YELLOW"
    )
    assert decision.considered_message_ids == ("same-message",)
    assert requested.advisory == pytest.approx(0.6)

    conflicting = AdvisoryRequest(
        "same-message", RUN_ID, "J0", "NS_YELLOW", "A2", 5.0, 8.0, 0.4
    )
    controller2, _, _ = _controller()
    conflicted = controller2.decide(
        proposal_id="conflicting-message",
        observation=_observation(advisories=(request, conflicting)),
    )
    conflicted_score = next(
        score for score in conflicted.action_scores if score.phase_id == "NS_YELLOW"
    )
    assert conflicted.considered_message_ids == ()
    assert conflicted_score.advisory == 0.0


def test_valid_same_run_advisory_is_bounded_and_empty_board_remains_live() -> None:
    controller, _, _ = _controller()
    messages = (
        AdvisoryRequest("valid", RUN_ID, "J0", "NS_YELLOW", "A2", 5.0, 8.0, 1.0),
        AdvisoryRequest("wrong-run", "other-run", "J0", "NS_YELLOW", "A2", 5.0, 8.0, 1.0),
        AdvisoryRequest("expired", RUN_ID, "J0", "NS_YELLOW", "A3", 0.0, 5.5, 1.0),
        AdvisoryRequest("illegal", RUN_ID, "J0", "EW_GREEN", "A3", 5.0, 8.0, 1.0),
    )
    decision = controller.decide(
        proposal_id="with-message",
        observation=_observation(movements=_movements(ns=3.0, ew=2.0), advisories=messages),
    )
    assert decision.considered_message_ids == ("valid",)
    assert decision.reason_code == "MAX_PRESSURE_WITH_ADVISORY"
    requested = next(score for score in decision.action_scores if score.phase_id == "NS_YELLOW")
    assert requested.advisory == pytest.approx(3.0)

    controller2, _, _ = _controller()
    no_messages = controller2.decide(
        proposal_id="empty-board",
        observation=_observation(simulation_time=1.0, advisories=()),
    )
    assert no_messages.accepted_action == "NS_GREEN"
    assert no_messages.considered_message_ids == ()
    assert no_messages.safety_reason_code == "ACCEPTED"


def test_proposal_retry_returns_original_decision_and_rejects_conflicting_reuse() -> None:
    controller, connection, log = _controller()
    original_observation = _observation(movements=_movements(ns=5.0, ew=1.0))
    first = controller.decide(
        proposal_id="stable-proposal", observation=original_observation
    )
    retry = controller.decide(
        proposal_id="stable-proposal", observation=original_observation
    )
    assert retry is first
    assert retry.accepted_action == log.events[0].requested_phase_id
    assert retry.accepted_action == log.commands[0].phase_id
    assert len(connection.trafficlight.writes) == len(log.events) == len(log.commands) == 1

    with pytest.raises(ValueError, match="reused with different observation"):
        controller.decide(
            proposal_id="stable-proposal",
            observation=_observation(movements=_movements(ns=1.0, ew=8.0)),
        )
    assert len(connection.trafficlight.writes) == len(log.events) == len(log.commands) == 1
    assert log.events[0].event_id == first.event_id


def test_native_artifacts_are_source_bound_and_join_observations_to_commands() -> None:
    manifest = json.loads((ARTIFACTS / "run_manifest.json").read_text(encoding="utf-8"))
    audit = json.loads((ARTIFACTS / "controller-audit.json").read_text(encoding="utf-8"))
    decisions = pq.read_table(ARTIFACTS / "decision_events.parquet").to_pylist()
    observations = pq.read_table(ARTIFACTS / "observations.parquet").to_pylist()
    commands = pq.read_table(ARTIFACTS / "executed_commands.parquet").to_pylist()
    assert manifest["controller"] == "cooperative-max-pressure"
    assert manifest["backend"] == "traci" and manifest["status"] == "completed"
    assert manifest["versions"]["python"].startswith("3.11.")
    assert manifest["versions"]["sumo"] == "1.27.1"
    assert manifest["sumo_command"][0].lower().endswith("sumo.exe")
    assert audit["valid"] is True and audit["actual_traci_execution"] is True
    assert audit["runs_without_advisory_messages"] is True
    assert audit["runs_with_advisory_messages"] is True
    assert audit["reinforcement_learning_required"] is False
    assert audit["first_recovery_target_for_optional_dqn"] == "cooperative-max-pressure"
    assert audit["one_writer_per_signal"] is True
    assert audit["event_sets_match"] is True
    assert audit["action_join_errors"] == audit["observation_join_errors"] == 0
    assert len(decisions) == len(observations) == len(commands) > 0
    assert {row["event_id"] for row in decisions} == {row["event_id"] for row in observations}
    assert {row["event_id"] for row in decisions} == {row["event_id"] for row in commands}
    accepted = {row["event_id"]: row["accepted_action"] for row in decisions}
    assert all(accepted[row["event_id"]] == row["phase_id"] for row in commands)
    assert all(json.loads(row["movement_inputs_json"]) for row in observations)
    assert manifest["source_hashes"] == audit["source_hashes"]
    for relative, expected in manifest["source_hashes"].items():
        actual = "sha256:" + hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert expected == actual
