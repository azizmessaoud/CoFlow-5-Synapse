from datetime import datetime, timezone

import pytest

from coflow5.a2 import A2EmergencyAgent, EmergencyPriorityPayload, RoadPosition
from coflow5.a5 import (
    A5SustainabilityAgent,
    EmissionProxyObservation,
    SustainabilityAdvicePayload,
    compute_link_displacement,
)
from coflow5.control import A1RequestArbitrator, ArbitrationContext, DeterministicSafetyMask, controlled_cross_plan
from coflow5.messaging import InProcessMessageBoard, PriorityClass, Topic

RUN_ID = "row10-a5-test"
SCENARIO_HASH = "sha256:" + "5" * 64
NOW = datetime(2026, 9, 22, tzinfo=timezone.utc)


def _payload(*, downstream: bool = True) -> SustainabilityAdvicePayload:
    return SustainabilityAdvicePayload(
        scenario_case="maria_school_link", signal_id="J0", sensitive_link_id="school-link",
        requested_movement="east", requested_phase_id="EW_GREEN",
        co2_proxy_mg_s=1200, nox_proxy_mg_s=18, stop_count=7, queue_length=5,
        expected_benefit_seconds=6, other_traffic_externality_seconds=2,
        downstream_available=downstream, proxy_source="SUMO/HBEFA emission proxy",
        advice_expires_at=25,
    )


def _context() -> ArbitrationContext:
    return ArbitrationContext(
        run_id=RUN_ID, scenario_hash=SCENARIO_HASH, signal_id="J0", simulation_time=20,
        current_phase_id="NS_GREEN", phase_entered_at=0, flow_requested_phase_id="NS_GREEN",
        downstream_feasible_by_movement={"east": True, "north": True},
    )


def test_a5_publishes_finite_expiring_proxy_labelled_advice() -> None:
    board = InProcessMessageBoard()
    result = A5SustainabilityAgent(board).publish_advice(
        run_id=RUN_ID, scenario_hash=SCENARIO_HASH, message_id="eco-001",
        correlation_id="maria-001", created_at=NOW, simulation_time=20, payload=_payload(),
    )
    assert result.accepted and result.message is not None
    message = result.message
    assert message.destination_or_topic == Topic.ECO.value
    assert message.priority_class is PriorityClass.SUSTAINABILITY
    assert message.payload["proxy_source"] == "SUMO/HBEFA emission proxy"
    assert message.payload["measured_air_quality"] is False
    assert message.expires_at == 25

    for bad in (float("nan"), float("inf"), float("-inf")):
        values = _payload().model_dump()
        values["co2_proxy_mg_s"] = bad
        with pytest.raises(ValueError):
            SustainabilityAdvicePayload(**values)
    assert board.storage_size == 1


def test_link_level_displacement_keeps_improvements_and_deterioration_visible() -> None:
    baseline = (
        EmissionProxyObservation(link_id="school-link", simulation_time=10, co2_proxy_mg_s=1000, nox_proxy_mg_s=10, stop_count=5, sensitive=True, receptor_type="school"),
        EmissionProxyObservation(link_id="residential-link", simulation_time=10, co2_proxy_mg_s=800, nox_proxy_mg_s=8, stop_count=4, sensitive=True, receptor_type="residential"),
    )
    observed = (
        EmissionProxyObservation(link_id="school-link", simulation_time=10, co2_proxy_mg_s=900, nox_proxy_mg_s=9, stop_count=4, sensitive=True, receptor_type="school"),
        EmissionProxyObservation(link_id="residential-link", simulation_time=10, co2_proxy_mg_s=920, nox_proxy_mg_s=9, stop_count=6, sensitive=True, receptor_type="residential"),
    )
    rows = compute_link_displacement(baseline, observed, selected_links={"school-link", "residential-link"})
    assert {row.link_id for row in rows} == {"school-link", "residential-link"}
    by_link = {row.link_id: row for row in rows}
    assert by_link["school-link"].co2_delta_mg_s < 0 and by_link["school-link"].classification == "improved"
    assert by_link["residential-link"].co2_delta_mg_s > 0 and by_link["residential-link"].classification == "worsened"
    assert all(row.proxy_label == "SUMO/HBEFA emission proxy — not measured air quality" for row in rows)


def test_a1_rejects_eco_advice_for_spillback_and_higher_priority() -> None:
    blocked_board = InProcessMessageBoard()
    A5SustainabilityAgent(blocked_board).publish_advice(
        run_id=RUN_ID, scenario_hash=SCENARIO_HASH, message_id="eco-blocked",
        correlation_id="eco-blocked", created_at=NOW, simulation_time=20,
        payload=_payload(downstream=False),
    )
    blocked = A1RequestArbitrator(
        transport=blocked_board, safety_mask=DeterministicSafetyMask(controlled_cross_plan())
    ).arbitrate(_context())
    assert len(blocked.decisions) == 1
    assert blocked.decisions[0].reason_code == "REJECTED_DOWNSTREAM_BLOCKED"
    assert blocked.selected_action == "NS_GREEN"

    board = InProcessMessageBoard()
    A5SustainabilityAgent(board).publish_advice(
        run_id=RUN_ID, scenario_hash=SCENARIO_HASH, message_id="eco-lower",
        correlation_id="priority-conflict", created_at=NOW, simulation_time=20,
        payload=_payload().model_copy(update={
            "requested_movement": "north", "requested_phase_id": "NS_GREEN",
        }),
    )
    A2EmergencyAgent(board).publish_priority_request(
        run_id=RUN_ID, scenario_hash=SCENARIO_HASH, message_id="emergency-higher",
        correlation_id="priority-conflict", created_at=NOW, simulation_time=20,
        payload=EmergencyPriorityPayload(
            scenario_case="eco_emergency_conflict", vehicle_id="ambulance", signal_id="J0",
            position=RoadPosition(edge_id="N", lane_id="N_0", distance_m=20),
            route=("N", "S"), next_controlled_junctions=("J0",), eta_seconds=3,
            urgency=1, expected_benefit_seconds=15, civilian_delay_externality_seconds=4,
            requested_movement="north", requested_phase_id="NS_GREEN",
            downstream_available=True, request_expires_at=25,
        ),
    )
    result = A1RequestArbitrator(
        transport=board, safety_mask=DeterministicSafetyMask(controlled_cross_plan())
    ).arbitrate(_context())
    by_id = {d.referenced_message_id: d for d in result.decisions}
    assert by_id["emergency-higher"].accepted
    assert not by_id["eco-lower"].accepted
    assert by_id["eco-lower"].reason_code == "REJECTED_HIGHER_PRIORITY_REQUEST"
    assert len({d.event_id for d in result.decisions}) == 2
