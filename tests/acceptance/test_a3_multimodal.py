from datetime import datetime, timezone

import pytest

from coflow5.a2 import A2EmergencyAgent, EmergencyPriorityPayload, RoadPosition
from coflow5.a3 import A3MultimodalAgent, CrossingStatePayload
from coflow5.control import (
    A1RequestArbitrator,
    ArbitrationContext,
    DeterministicSafetyMask,
    controlled_cross_plan,
)
from coflow5.messaging import InProcessMessageBoard, PriorityClass

RUN_ID = "row07-a3-test"
SCENARIO_HASH = "sha256:" + "3" * 64
NOW = datetime(2026, 9, 22, tzinfo=timezone.utc)


def test_active_crossing_outranks_emergency_and_preserves_remaining_clearance() -> None:
    board = InProcessMessageBoard()
    a3 = A3MultimodalAgent(board)
    crossing = a3.publish_crossing_state(
        run_id=RUN_ID, scenario_hash=SCENARIO_HASH, message_id="crossing-active",
        correlation_id="conflict", created_at=NOW, simulation_time=10, expires_at=15,
        payload=CrossingStatePayload(
            scenario_case="crossing_emergency_conflict", crossing_id="north_south_crossing",
            signal_id="J0", active_crossing=True, remaining_clearance_seconds=8,
            requested_movement="pedestrian_east_west", requested_phase_id="NS_GREEN",
            expected_benefit_seconds=8, civilian_delay_externality_seconds=2,
        ),
    )
    assert crossing.accepted and crossing.message is not None
    assert crossing.message.priority_class is PriorityClass.ACTIVE_SAFETY
    assert crossing.message.payload["active_crossing"] is True
    assert crossing.message.payload["remaining_clearance_seconds"] == 8
    A2EmergencyAgent(board).publish_priority_request(
        run_id=RUN_ID, scenario_hash=SCENARIO_HASH, message_id="emergency-conflicting",
        correlation_id="conflict", created_at=NOW, simulation_time=10,
        payload=EmergencyPriorityPayload(
            scenario_case="crossing_emergency_conflict", vehicle_id="ambulance",
            signal_id="J0", position=RoadPosition(edge_id="E", lane_id="E_0", distance_m=50),
            route=("E", "W"), next_controlled_junctions=("J0",), eta_seconds=5,
            urgency=1, expected_benefit_seconds=20, civilian_delay_externality_seconds=4,
            requested_movement="east", requested_phase_id="EW_GREEN",
            downstream_available=True, request_expires_at=15,
        ),
    )
    result = A1RequestArbitrator(
        transport=board, safety_mask=DeterministicSafetyMask(controlled_cross_plan())
    ).arbitrate(ArbitrationContext(
        run_id=RUN_ID, scenario_hash=SCENARIO_HASH, signal_id="J0", simulation_time=10,
        current_phase_id="NS_GREEN", phase_entered_at=0, flow_requested_phase_id="NS_GREEN",
        downstream_feasible_by_movement={"east": True, "pedestrian_east_west": True},
    ))
    by_id = {item.referenced_message_id: item for item in result.decisions}
    assert by_id["crossing-active"].accepted
    assert by_id["crossing-active"].reason_code == "ACCEPTED_ACTIVE_CROSSING_CLEARANCE"
    assert not by_id["emergency-conflicting"].accepted
    assert by_id["emergency-conflicting"].reason_code == "REJECTED_PEDESTRIAN_CLEARANCE"
    assert result.selected_action == "NS_GREEN"


def test_pedestrian_deadline_escalation_is_near_deadline_and_bounded() -> None:
    board = InProcessMessageBoard()
    a3 = A3MultimodalAgent(board, minimum_deadline_seconds=20, maximum_deadline_seconds=120,
                           escalation_window_seconds=15)
    common = dict(
        run_id=RUN_ID, scenario_hash=SCENARIO_HASH, correlation_id="ped", created_at=NOW,
        simulation_time=20, expires_at=25, scenario_case="pedestrian_deadline",
        crossing_id="east_west_crossing", signal_id="J0",
        requested_movement="pedestrian_east_west", requested_phase_id="EW_GREEN",
        expected_benefit_seconds=10, civilian_delay_externality_seconds=3,
    )
    assert a3.publish_pedestrian_deadline(
        message_id="ped-too-early", wait_age_seconds=20, deadline_seconds=60, **common
    ) is None
    result = a3.publish_pedestrian_deadline(
        message_id="ped-near", wait_age_seconds=50, deadline_seconds=60, **common
    )
    assert result is not None and result.accepted and result.message is not None
    assert result.message.priority_class is PriorityClass.PEDESTRIAN_DEADLINE
    assert result.message.payload["seconds_to_deadline"] == 10
    with pytest.raises(ValueError, match="outside configured bounds"):
        a3.publish_pedestrian_deadline(
            message_id="ped-unbounded", wait_age_seconds=50, deadline_seconds=500, **common
        )


def test_transit_priority_requires_lateness_or_headway_gap_evidence() -> None:
    board = InProcessMessageBoard()
    a3 = A3MultimodalAgent(board, minimum_transit_lateness_seconds=30,
                           minimum_headway_gap_seconds=60)
    common = dict(
        run_id=RUN_ID, scenario_hash=SCENARIO_HASH, created_at=NOW,
        simulation_time=30, expires_at=35, signal_id="J0", target_headway_seconds=300,
        requested_movement="east", requested_phase_id="EW_GREEN",
        expected_benefit_seconds=25, other_traffic_externality_seconds=3,
    )
    early = a3.publish_transit_priority(
        message_id="early-bus", correlation_id="early", scenario_case="early_bus",
        vehicle_id="bus-early", schedule_deviation_seconds=-10,
        observed_headway_seconds=300, **common,
    )
    assert early is None
    late = a3.publish_transit_priority(
        message_id="late-bus", correlation_id="late", scenario_case="late_bus",
        vehicle_id="bus-late", schedule_deviation_seconds=90,
        observed_headway_seconds=320, **common,
    )
    assert late is not None and late.message is not None
    assert late.message.priority_class is PriorityClass.LATE_TRANSIT
    assert late.message.payload["evidence_basis"] == ("late",)
    gap = a3.publish_transit_priority(
        message_id="gap-bus", correlation_id="gap", scenario_case="headway_gap",
        vehicle_id="bus-gap", schedule_deviation_seconds=0,
        observed_headway_seconds=370, **common,
    )
    assert gap is not None and gap.message is not None
    assert gap.message.payload["evidence_basis"] == ("headway_gap",)



@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_a3_rejects_non_finite_crossing_and_deadline_evidence(bad: float) -> None:
    with pytest.raises(ValueError):
        CrossingStatePayload(
            scenario_case="nonfinite", crossing_id="crossing", signal_id="J0",
            active_crossing=True, remaining_clearance_seconds=bad,
            requested_movement="pedestrian", requested_phase_id="NS_GREEN",
            expected_benefit_seconds=1, civilian_delay_externality_seconds=1,
        )
    board = InProcessMessageBoard()
    a3 = A3MultimodalAgent(board)
    with pytest.raises(ValueError):
        a3.publish_pedestrian_deadline(
            run_id=RUN_ID, scenario_hash=SCENARIO_HASH,
            message_id=f"bad-{bad}", correlation_id="bad", created_at=NOW,
            simulation_time=20, expires_at=25, scenario_case="pedestrian_deadline",
            crossing_id="crossing", signal_id="J0", wait_age_seconds=bad,
            deadline_seconds=60, requested_movement="pedestrian",
            requested_phase_id="EW_GREEN", expected_benefit_seconds=1,
            civilian_delay_externality_seconds=1,
        )
    assert board.storage_size == 0
