from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from coflow5.control import DeterministicSafetyMask, controlled_cross_plan
from coflow5.control.a1_controller import A1FlowController
from coflow5.control.max_pressure import (
    CooperativeMaxPressureController,
    MaxPressureObservation,
    MovementPressure,
)
from coflow5.evidence.message_board_artifacts import generate_message_board_artifacts
from coflow5.messaging import InProcessMessageBoard, MessageDisposition, read_a1_advisories
from coflow5.sumo_adapter.signal_executor import ImmutableSafetyLog, SignalExecutorRegistry

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "harness/work/06-message-board/artifacts"
RUN_ID = "run-empty-board-control"
SCENARIO_HASH = "sha256:" + "b" * 64


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
    capability = SignalExecutorRegistry().acquire(
        signal_id="J0",
        connection=connection,
        safety_mask=mask,
        initial_phase_id="NS_GREEN",
        initial_phase_entered_at=0.0,
        run_id=RUN_ID,
        scenario_hash=SCENARIO_HASH,
        log=log,
    )
    return CooperativeMaxPressureController(
        a1=A1FlowController(capability),
        safety_mask=mask,
        run_id=RUN_ID,
        scenario_hash=SCENARIO_HASH,
        signal_id="J0",
    ), log


def _observation(advisories=()):
    return MaxPressureObservation(
        simulation_time=1.0,
        current_phase_id="NS_GREEN",
        phase_entered_at=0.0,
        movements={
            movement: MovementPressure(2.0, 0.0, 20.0)
            for movement in ("north", "south", "east", "west")
        },
        advisories=advisories,
    )


@pytest.mark.parametrize("unavailable", [False, True])
def test_a1_continues_legal_local_max_pressure_on_empty_or_unavailable_board(
    unavailable: bool,
) -> None:
    board = InProcessMessageBoard()
    board.inject_unavailable(unavailable)
    board_read = read_a1_advisories(
        board,
        run_id=RUN_ID,
        scenario_hash=SCENARIO_HASH,
        signal_id="J0",
        valid_at=1.0,
    )
    expected = MessageDisposition.UNAVAILABLE if unavailable else MessageDisposition.EMPTY
    assert board_read.disposition is expected
    assert board_read.advisories == ()

    controller, log = _controller()
    decision = controller.decide(
        proposal_id=f"board-{expected.value}",
        observation=_observation(board_read.advisories),
    )
    assert decision.reason_code == "MAX_PRESSURE_LOCAL_ONLY"
    assert decision.considered_message_ids == ()
    assert decision.accepted_action == "NS_GREEN"
    assert decision.safety_reason_code == "ACCEPTED"
    assert len(log.events) == len(log.commands) == 1


@pytest.fixture(scope="session")
def generated_message_board_artifacts(tmp_path_factory: pytest.TempPathFactory) -> Path:
    artifacts = tmp_path_factory.mktemp("row06-message-board") / "artifacts"
    manifest = generate_message_board_artifacts(ROOT, artifacts)
    assert manifest["run_id"]
    return artifacts


def test_artifacts_have_complete_message_decision_and_scenario_joins(
    generated_message_board_artifacts: Path,
) -> None:
    artifacts = generated_message_board_artifacts
    manifest = json.loads((artifacts / "run_manifest.json").read_text(encoding="utf-8"))
    audit = json.loads((artifacts / "message-audit.json").read_text(encoding="utf-8"))
    messages = pq.read_table(artifacts / "messages.parquet").to_pylist()
    decisions = pq.read_table(artifacts / "decision_events.parquet").to_pylist()

    assert audit["valid"] is True
    assert audit["unresolved_considered_message_ids"] == []
    assert audit["unresolved_disposition_message_ids"] == []
    assert audit["identity_errors"] == 0
    assert audit["empty_board_legal_decision_count"] > 0
    assert audit["unavailable_board_continues_local_max_pressure"] is True
    assert set(audit["required_dispositions"]) <= set(audit["disposition_counts"])

    publication_ids = {
        row["message_id"] for row in messages if row["record_kind"] == "message"
    }
    assert publication_ids
    assert all(
        row["run_id"] == manifest["run_id"]
        and row["scenario_hash"] == manifest["scenario_hash"]
        for row in messages + decisions
    )
    assert all(
        message_id in publication_ids
        for decision in decisions
        for message_id in decision["considered_message_ids"]
    )
