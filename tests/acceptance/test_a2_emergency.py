from dataclasses import FrozenInstanceError
from datetime import datetime, timezone

import pytest

from coflow5.a2 import A2EmergencyAgent, EmergencyPriorityPayload, RoadPosition
from coflow5.control import (
    A1RequestArbitrator,
    ArbitrationContext,
    DeterministicSafetyMask,
    controlled_cross_plan,
)
from coflow5.messaging import InProcessMessageBoard, MessageEnvelope, Topic

RUN_ID = "row07-a2-test"
SCENARIO_HASH = "sha256:" + "7" * 64
NOW = datetime(2026, 9, 22, tzinfo=timezone.utc)


def _payload(*, externality: float = 4.0, downstream: bool = True) -> EmergencyPriorityPayload:
    return EmergencyPriorityPayload(
        scenario_case="two_emergencies", vehicle_id="ambulance-1", signal_id="J0",
        position=RoadPosition(edge_id="N_in", lane_id="N_in_0", distance_m=75),
        route=("N_in", "S_out"), next_controlled_junctions=("J0",), eta_seconds=8,
        urgency=0.9, expected_benefit_seconds=15,
        civilian_delay_externality_seconds=externality, requested_movement="north",
        requested_phase_id="NS_GREEN", downstream_available=downstream,
        request_expires_at=25,
    )


def _publish(agent: A2EmergencyAgent, message_id: str, payload: EmergencyPriorityPayload):
    return agent.publish_priority_request(
        run_id=RUN_ID, scenario_hash=SCENARIO_HASH, message_id=message_id,
        correlation_id=message_id, created_at=NOW, simulation_time=20, payload=payload,
    )


def _arbitrator(board: InProcessMessageBoard) -> A1RequestArbitrator:
    return A1RequestArbitrator(
        transport=board, safety_mask=DeterministicSafetyMask(controlled_cross_plan())
    )


def _context() -> ArbitrationContext:
    return ArbitrationContext(
        run_id=RUN_ID, scenario_hash=SCENARIO_HASH, signal_id="J0",
        simulation_time=20, current_phase_id="NS_GREEN", phase_entered_at=0,
        flow_requested_phase_id="NS_GREEN", downstream_feasible_by_movement={"north": True},
    )


def test_a2_publishes_complete_expiring_transport_request() -> None:
    board = InProcessMessageBoard()
    result = _publish(A2EmergencyAgent(board), "emergency-complete", _payload())
    assert result.accepted and isinstance(result.message, MessageEnvelope)
    message = result.message
    assert message.destination_or_topic == Topic.REQUESTS.value
    assert message.source_agent == "A2_EMERGENCY"
    assert message.expires_at == message.payload["request_expires_at"] == 25
    assert {
        "position", "route", "next_controlled_junctions", "eta_seconds", "urgency",
        "expected_benefit_seconds", "civilian_delay_externality_seconds",
        "requested_movement", "request_expires_at",
    } <= message.payload.keys()
    with pytest.raises(Exception):
        EmergencyPriorityPayload(
            scenario_case="invalid", vehicle_id="e", signal_id="J0",
            position=RoadPosition(edge_id="N", lane_id="N_0", distance_m=1),
            eta_seconds=1, urgency=1, expected_benefit_seconds=1,
            civilian_delay_externality_seconds=1, requested_movement="north",
            requested_phase_id="NS_GREEN", downstream_available=True,
            request_expires_at=2,
        )


def test_a1_rejects_emergency_when_downstream_is_blocked() -> None:
    board = InProcessMessageBoard()
    _publish(A2EmergencyAgent(board), "emergency-blocked", _payload(downstream=False))
    result = _arbitrator(board).arbitrate(_context())
    assert len(result.decisions) == 1
    decision = result.decisions[0]
    assert not decision.accepted
    assert decision.reason_code == "REJECTED_DOWNSTREAM_BLOCKED"
    assert decision.selected_action == "NS_GREEN"


def test_two_emergencies_use_deterministic_externality_tiebreak_and_one_reply_each() -> None:
    board = InProcessMessageBoard()
    agent = A2EmergencyAgent(board)
    _publish(agent, "emergency-beta", _payload(externality=6))
    _publish(agent, "emergency-alpha", _payload(externality=4))
    result = _arbitrator(board).arbitrate(_context())
    by_id = {item.referenced_message_id: item for item in result.decisions}
    assert by_id["emergency-alpha"].accepted
    assert by_id["emergency-alpha"].reason_code == "ACCEPTED_EMERGENCY_PRIORITY"
    assert not by_id["emergency-beta"].accepted
    assert by_id["emergency-beta"].reason_code == "REJECTED_SAME_TIER_TIEBREAK"
    assert len(result.replies) == len(result.decisions) == 2
    assert len({item.event_id for item in result.decisions}) == 2
    assert {reply.payload["referenced_message_id"] for reply in result.replies} == set(by_id)
    with pytest.raises(FrozenInstanceError):
        by_id["emergency-alpha"].accepted = False  # type: ignore[misc]
