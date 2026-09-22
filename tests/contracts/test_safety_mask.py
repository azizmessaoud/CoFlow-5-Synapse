from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from coflow5.control import (
    ActionProposal,
    DeterministicSafetyMask,
    ProposalSource,
    SafetyReason,
    SignalSnapshot,
    controlled_cross_plan,
)
from coflow5.control.a1_controller import A1FlowController
from coflow5.sumo_adapter import signal_executor as executor_module
from coflow5.sumo_adapter.signal_executor import (
    ImmutableSafetyLog,
    SignalExecutorRegistry,
)

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "harness/work/03-safety-mask/artifacts"


class FakeTrafficLight:
    def __init__(self) -> None:
        self.state = "GrGr"
        self.writes: list[tuple[str, str]] = []

    def setRedYellowGreenState(self, signal_id: str, state: str) -> None:
        self.state = state
        self.writes.append((signal_id, state))

    def getRedYellowGreenState(self, signal_id: str) -> str:
        assert signal_id == "J0"
        return self.state


class FakeConnection:
    def __init__(self) -> None:
        self.trafficlight = FakeTrafficLight()


def _executor():
    connection = FakeConnection()
    log = ImmutableSafetyLog()
    registry = SignalExecutorRegistry()
    executor = registry.acquire(
        signal_id="J0", connection=connection,
        safety_mask=DeterministicSafetyMask(controlled_cross_plan()),
        initial_phase_id="NS_GREEN", initial_phase_entered_at=0.0,
        run_id="run-test", scenario_hash="sha256:" + "1" * 64, log=log,
    )
    return connection, log, registry, executor


def test_mask_enforces_legal_transition_minimum_green_yellow_and_all_red() -> None:
    mask = DeterministicSafetyMask(controlled_cross_plan())
    direct = mask.evaluate(
        ActionProposal("p1", "J0", "EW_GREEN"), SignalSnapshot("NS_GREEN", 0.0), 5.0
    )
    assert (direct.accepted, direct.reason) == (False, SafetyReason.YELLOW_REQUIRED)
    early_yellow = mask.evaluate(
        ActionProposal("p2", "J0", "NS_YELLOW"), SignalSnapshot("NS_GREEN", 0.0), 4.999
    )
    assert early_yellow.reason is SafetyReason.MINIMUM_GREEN
    assert mask.evaluate(
        ActionProposal("p3", "J0", "NS_YELLOW"), SignalSnapshot("NS_GREEN", 0.0), 5.0
    ).accepted
    assert mask.evaluate(
        ActionProposal("p4", "J0", "ALL_RED_TO_EW"), SignalSnapshot("NS_YELLOW", 5.0), 6.999
    ).reason is SafetyReason.YELLOW_MINIMUM
    assert mask.evaluate(
        ActionProposal("p5", "J0", "EW_GREEN"), SignalSnapshot("ALL_RED_TO_EW", 7.0), 7.999
    ).reason is SafetyReason.ALL_RED_MINIMUM
    assert mask.evaluate(
        ActionProposal("p6", "J0", "UNKNOWN"), SignalSnapshot("NS_GREEN", 0.0), 8.0
    ).reason is SafetyReason.UNKNOWN_PHASE


def test_conflicts_and_remaining_pedestrian_clearance_are_rejected() -> None:
    mask = DeterministicSafetyMask(controlled_cross_plan())
    conflict = mask.evaluate(
        ActionProposal("p1", "J0", "CONFLICTING_TEST"), SignalSnapshot("NS_GREEN", 0), 10
    )
    assert conflict.reason is SafetyReason.CONFLICTING_GREENS
    pedestrian = mask.evaluate(
        ActionProposal("p2", "J0", "EW_GREEN"),
        SignalSnapshot("ALL_RED_TO_EW", 7, {"north_south_crossing": 0.001}), 8,
    )
    assert pedestrian.reason is SafetyReason.PEDESTRIAN_CLEARANCE
    complete = mask.evaluate(
        ActionProposal("p3", "J0", "EW_GREEN"),
        SignalSnapshot("ALL_RED_TO_EW", 7, {"north_south_crossing": 0.0}), 8,
    )
    assert complete.accepted


def test_connection_scoped_registry_issues_exactly_one_a1_writer_per_signal() -> None:
    connection, log, registry, _ = _executor()
    assert registry.writer_count_by_signal == {"J0": 1}
    for competing_registry in (registry, SignalExecutorRegistry()):
        with pytest.raises(RuntimeError, match="sole writer"):
            competing_registry.acquire(
                signal_id="J0", connection=connection,
                safety_mask=DeterministicSafetyMask(controlled_cross_plan()),
                initial_phase_id="NS_GREEN", initial_phase_entered_at=0,
                run_id="other", scenario_hash="sha256:" + "2" * 64, log=log,
            )
    with pytest.raises(PermissionError, match="only A1"):
        SignalExecutorRegistry().acquire(
            signal_id="J1", connection=connection,
            safety_mask=DeterministicSafetyMask(controlled_cross_plan()),
            initial_phase_id="NS_GREEN", initial_phase_entered_at=0,
            run_id="other", scenario_hash="sha256:" + "2" * 64, log=log, owner="A2",
        )


def test_registry_exposes_no_constructible_writer_or_factory_authority() -> None:
    connection, _, _, registered = _executor()
    assert not hasattr(executor_module, "SignalExecutor")
    assert not any("AUTHORITY" in name or "TOKEN" in name for name in vars(executor_module))
    assert not hasattr(registered, "connection")
    assert not hasattr(registered, "trafficlight")
    assert connection.trafficlight.writes == []




def test_runtime_capability_type_cannot_be_cloned_into_a_second_writer() -> None:
    connection, _, registry, capability = _executor()
    with pytest.raises(TypeError):
        type(capability)()
    with pytest.raises(PermissionError, match="only be created by its registry"):
        type(capability)(object())
    assert registry.writer_count_by_signal == {"J0": 1}
    assert connection.trafficlight.writes == []

def test_duplicate_proposal_is_idempotent_before_physical_write() -> None:
    connection, log, _, registered = _executor()
    proposal = ActionProposal("duplicate", "J0", "NS_YELLOW")
    first = registered.submit(proposal, simulation_time=5.0)
    second = registered.submit(proposal, simulation_time=99.0)
    assert second == first
    assert connection.trafficlight.writes == [("J0", "yryr")]
    assert len(log.events) == 1
    assert len(log.commands) == 1


def test_rejected_proposal_has_one_event_and_never_executes() -> None:
    connection, log, _, executor = _executor()
    event = executor.submit(ActionProposal("illegal", "J0", "EW_GREEN"), simulation_time=5)
    assert not event.accepted
    assert len(log.events) == 1
    assert log.events[0].event_id == event.event_id
    assert log.commands == ()
    assert connection.trafficlight.writes == []


def test_human_override_traverses_the_same_mask_and_event_path() -> None:
    connection, log, _, executor = _executor()
    controller = A1FlowController(executor)
    rejected = controller.human_override(
        proposal_id="human-early", signal_id="J0", phase_id="NS_YELLOW", simulation_time=4.9
    )
    accepted = controller.human_override(
        proposal_id="human-safe", signal_id="J0", phase_id="NS_YELLOW", simulation_time=5.0
    )
    assert rejected.reason_code == SafetyReason.MINIMUM_GREEN.value
    assert accepted.accepted is True
    assert [event.source for event in log.events] == [
        ProposalSource.HUMAN_OVERRIDE.value, ProposalSource.HUMAN_OVERRIDE.value
    ]
    assert len(log.events) == 2 and len(log.commands) == 1
    assert connection.trafficlight.writes == [("J0", "yryr")]


def test_non_finite_inputs_are_reason_coded_and_never_execute() -> None:
    for index, (simulation_time, clearance) in enumerate(
        ((float("nan"), 0.0), (float("inf"), 0.0), (5.0, float("nan")), (5.0, float("inf")))
    ):
        connection, log, _, executor = _executor()
        event = executor.submit(
            ActionProposal(f"non-finite-{index}", "J0", "NS_YELLOW"),
            simulation_time=simulation_time,
            pedestrian_remaining_clearance={"north_south_crossing": clearance},
        )
        assert event.accepted is False
        assert event.reason_code == SafetyReason.NON_FINITE_INPUT.value
        assert connection.trafficlight.writes == []
        assert len(log.events) == 1 and log.commands == ()


def test_native_traci_artifacts_join_every_proposal_command_and_rejection() -> None:
    manifest = json.loads((ARTIFACTS / "run_manifest.json").read_text(encoding="utf-8"))
    audit = json.loads((ARTIFACTS / "safety-audit.json").read_text(encoding="utf-8"))
    events = pq.read_table(ARTIFACTS / "decision_events.parquet").to_pylist()
    commands = pq.read_table(ARTIFACTS / "executed_commands.parquet").to_pylist()
    assert manifest["backend"] == "traci" and manifest["status"] == "completed"
    assert manifest["versions"]["python"] == "3.11.9"
    assert manifest["versions"]["sumo"] == "1.27.1"
    assert audit["actual_traci_execution"] is True
    assert audit["one_writer_per_signal"] is True
    assert audit["controlled_link_mapping_validated"] is True
    assert audit["illegal_executed_actions"] == 0
    assert audit["physically_conflicting_executed_actions"] == 0
    assert audit["physical_conflict_details"] == []
    for command in commands:
        state = command["signal_state"]
        assert len(state) == len(audit["controlled_links"])
        assert not any(
            state[first] in {"G", "g"} and state[second] in {"G", "g"}
            for first, second in audit["conflicting_link_pairs"]
        )
    assert audit["human_override_events"] >= 2
    assert len(events) == audit["proposal_count"] == audit["event_count"]
    assert len({row["event_id"] for row in events}) == len(events)
    accepted = {row["event_id"] for row in events if row["accepted"]}
    rejected = {row["event_id"] for row in events if not row["accepted"]}
    executed = {row["event_id"] for row in commands}
    assert accepted == executed
    assert rejected.isdisjoint(executed)
    for row in events + commands:
        assert (row["run_id"], row["scenario_hash"]) == (
            manifest["run_id"], manifest["scenario_hash"]
        )
