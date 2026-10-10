from datetime import datetime, timezone

from coflow5.a4 import A4SituationAgent, ForecastPayload, SituationClassification
from coflow5.a5 import A5SustainabilityAgent, SustainabilityAdvicePayload
from coflow5.control import (
    A1RequestArbitrator,
    ArbitrationContext,
    DeterministicSafetyMask,
    controlled_cross_plan,
)
from coflow5.messaging import InProcessMessageBoard, PriorityClass
from coflow5.messaging.a1_forecasts import read_a1_forecasts


NOW = datetime(2026, 9, 22, tzinfo=timezone.utc)
RUN_ID = "j0-advisory-loop-19"
SCENARIO_HASH = "sha256:" + "9" * 64


def _context(simulation_time: float) -> ArbitrationContext:
    return ArbitrationContext(
        run_id=RUN_ID,
        scenario_hash=SCENARIO_HASH,
        signal_id="J0",
        simulation_time=simulation_time,
        current_phase_id="NS_GREEN",
        phase_entered_at=0,
        flow_requested_phase_id="NS_GREEN",
        downstream_feasible_by_movement={"east": True, "north": True},
    )


def test_a4_a5_advice_is_bounded_and_a1_records_dispositions() -> None:
    board = InProcessMessageBoard()
    A4SituationAgent(board).publish_forecast(
        run_id=RUN_ID,
        scenario_hash=SCENARIO_HASH,
        message_id="incident-001",
        correlation_id="incident-001",
        created_at=NOW,
        simulation_time=20,
        payload=ForecastPayload(
            scenario_case="injected_incident",
            signal_id="J0",
            target="east_queue",
            source_time=19,
            horizon_seconds=30,
            predicted_value=0.3,
            confidence=0.9,
            model_name="persistence",
            model_version="persistence-v1",
            expires_at=30,
            classification=SituationClassification.LIKELY_INCIDENT,
            residual=4,
            evidence_basis="seeded J0 incident fixture",
        ),
    )
    A5SustainabilityAgent(board).publish_advice(
        run_id=RUN_ID,
        scenario_hash=SCENARIO_HASH,
        message_id="eco-001",
        correlation_id="incident-001",
        created_at=NOW,
        simulation_time=20,
        payload=SustainabilityAdvicePayload(
            scenario_case="injected_incident",
            signal_id="J0",
            sensitive_link_id="school-link",
            requested_movement="east",
            requested_phase_id="EW_GREEN",
            co2_proxy_mg_s=1200,
            nox_proxy_mg_s=18,
            stop_count=7,
            queue_length=5,
            expected_benefit_seconds=6,
            other_traffic_externality_seconds=2,
            downstream_available=True,
            proxy_source="SUMO/HBEFA emission proxy",
            advice_expires_at=30,
        ),
    )
    result = A1RequestArbitrator(
        transport=board,
        safety_mask=DeterministicSafetyMask(controlled_cross_plan()),
    ).arbitrate(_context(20))

    forecast_read = read_a1_forecasts(
        board,
        run_id=RUN_ID,
        scenario_hash=SCENARIO_HASH,
        signal_id="J0",
        valid_at=20,
    )
    assert forecast_read.forecasts and forecast_read.forecasts[0].message_id == "incident-001"
    assert {decision.referenced_message_id for decision in result.decisions} == {"eco-001"}
    assert len({decision.event_id for decision in result.decisions}) == 1
    assert all(decision.run_id == RUN_ID for decision in result.decisions)
    assert all(decision.scenario_hash == SCENARIO_HASH for decision in result.decisions)
    assert any(decision.priority_class == PriorityClass.SUSTAINABILITY for decision in result.decisions)


def test_expired_advice_is_rejected_without_changing_local_control() -> None:
    board = InProcessMessageBoard()
    A4SituationAgent(board).publish_forecast(
        run_id=RUN_ID,
        scenario_hash=SCENARIO_HASH,
        message_id="stale-incident",
        correlation_id="stale-incident",
        created_at=NOW,
        simulation_time=20,
        payload=ForecastPayload(
            scenario_case="stale_incident",
            signal_id="J0",
            target="east_queue",
            source_time=19,
            horizon_seconds=30,
            predicted_value=0.3,
            confidence=0.9,
            model_name="persistence",
            model_version="persistence-v1",
            expires_at=20,
            classification=SituationClassification.LIKELY_INCIDENT,
            residual=4,
            evidence_basis="seeded J0 incident fixture",
        ),
    )
    result = A1RequestArbitrator(
        transport=board,
        safety_mask=DeterministicSafetyMask(controlled_cross_plan()),
    ).arbitrate(_context(21))

    assert result.selected_action == "NS_GREEN"
    assert result.decisions == ()
