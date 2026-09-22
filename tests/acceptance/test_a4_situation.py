from datetime import datetime, timezone

import pytest

from coflow5.a4 import (
    A4SituationAgent,
    ForecastPayload,
    SituationClassification,
    SituationEvidence,
    TimeSeriesPoint,
    chronological_split,
    evaluate_forecast_ladder,
)
from coflow5.control import (
    A1SituationAwareMaxPressureController,
    DeterministicSafetyMask,
    controlled_cross_plan,
)
from coflow5.control.a1_controller import A1FlowController
from coflow5.control.max_pressure import (
    CooperativeMaxPressureController,
    MaxPressureObservation,
    MovementPressure,
)
from coflow5.messaging import InProcessMessageBoard, MessageDisposition, Topic, read_a1_forecasts
from coflow5.sumo_adapter.signal_executor import ImmutableSafetyLog, SignalExecutorRegistry

RUN_ID = "row10-a4-test"
SCENARIO_HASH = "sha256:" + "4" * 64
NOW = datetime(2026, 9, 22, tzinfo=timezone.utc)


def test_chronological_split_and_model_ladder_never_fit_future_rows() -> None:
    points = tuple(TimeSeriesPoint(simulation_time=float(i), value=2.0 * i + 3.0) for i in range(30))
    split = chronological_split(tuple(reversed(points)), train_fraction=0.6, validation_fraction=0.2)
    assert len(split.train) == 18 and len(split.validation) == 6 and len(split.test) == 6
    assert max(p.simulation_time for p in split.train) < min(p.simulation_time for p in split.validation)
    assert max(p.simulation_time for p in split.validation) < min(p.simulation_time for p in split.test)

    result = evaluate_forecast_ladder(split)
    by_name = {score.model_name: score for score in result.scores}
    assert {"persistence", "simple_autoregression", "lightgbm"} == set(by_name)
    assert by_name["persistence"].status == "evaluated"
    assert by_name["simple_autoregression"].status == "evaluated"
    assert by_name["simple_autoregression"].fit_end_time == split.train[-1].simulation_time
    assert by_name["simple_autoregression"].evaluation_start_time == split.validation[0].simulation_time
    assert by_name["lightgbm"].status == "not_available_not_accepted"
    assert result.selected_model in {"persistence", "simple_autoregression"}
    assert result.lightgbm_accepted is False


def test_a4_publishes_finite_expiring_forecast_with_required_provenance() -> None:
    board = InProcessMessageBoard()
    agent = A4SituationAgent(board)
    payload = ForecastPayload(
        scenario_case="omar_forecast", signal_id="J0", target="north_arrivals",
        source_time=10.0, horizon_seconds=30.0, predicted_value=12.5,
        confidence=0.8, model_name="simple_autoregression", model_version="a4-simple-ar-v1",
        expires_at=16.0, classification=SituationClassification.NORMAL,
        residual=0.2, evidence_basis="chronological validation winner",
    )
    result = agent.publish_forecast(
        run_id=RUN_ID, scenario_hash=SCENARIO_HASH, message_id="forecast-001",
        correlation_id="omar-001", created_at=NOW, simulation_time=10.0, payload=payload,
    )
    assert result.accepted and result.message is not None
    message = result.message
    assert message.destination_or_topic == Topic.FORECAST.value
    assert message.expires_at == 16.0
    assert message.payload["horizon_seconds"] == 30.0
    assert message.payload["source_time"] == 10.0
    assert message.payload["model_version"] == "a4-simple-ar-v1"
    assert message.payload["classification"] == "normal"

    for bad in (float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError):
            ForecastPayload(
                scenario_case="bad", signal_id="J0", target="arrivals", source_time=1,
                horizon_seconds=30, predicted_value=bad, confidence=0.5,
                model_name="persistence", model_version="v1", expires_at=2,
                classification=SituationClassification.NORMAL, residual=0,
                evidence_basis="invalid fixture",
            )
    assert board.storage_size == 1


@pytest.mark.parametrize(
    ("evidence", "expected"),
    [
        (SituationEvidence(source_time=10, current_time=20, sample_count=2, residual=0, ewma=0, cusum=0, speed_ratio=1, occupancy=0.2), SituationClassification.INSUFFICIENT_DATA),
        (SituationEvidence(source_time=1, current_time=20, sample_count=10, residual=0, ewma=0, cusum=0, speed_ratio=1, occupancy=0.2), SituationClassification.STALE_DATA),
        (SituationEvidence(source_time=18, current_time=20, sample_count=10, residual=4, ewma=3, cusum=7, speed_ratio=0.3, occupancy=0.4), SituationClassification.LIKELY_INCIDENT),
        (SituationEvidence(source_time=18, current_time=20, sample_count=10, residual=4, ewma=3, cusum=7, speed_ratio=0.6, occupancy=0.9), SituationClassification.CONGESTION),
        (SituationEvidence(source_time=18, current_time=20, sample_count=10, residual=4, ewma=3, cusum=7, speed_ratio=0.9, occupancy=0.4), SituationClassification.DETECTED_ANOMALY),
        (SituationEvidence(source_time=18, current_time=20, sample_count=10, residual=0.2, ewma=0.1, cusum=0.2, speed_ratio=0.9, occupancy=0.4), SituationClassification.NORMAL),
    ],
)
def test_a4_classification_and_silent_stale_unavailable_fallback(
    evidence: SituationEvidence, expected: SituationClassification,
) -> None:
    assert A4SituationAgent.classify(evidence) is expected

    empty = InProcessMessageBoard()
    silent = read_a1_forecasts(empty, run_id=RUN_ID, scenario_hash=SCENARIO_HASH, signal_id="J0", valid_at=20)
    assert silent.disposition is MessageDisposition.EMPTY and silent.forecasts == () and silent.local_only

    stale_board = InProcessMessageBoard()
    A4SituationAgent(stale_board).publish_forecast(
        run_id=RUN_ID, scenario_hash=SCENARIO_HASH, message_id="stale", correlation_id="stale",
        created_at=NOW, simulation_time=10,
        payload=ForecastPayload(
            scenario_case="stale", signal_id="J0", target="arrivals", source_time=10,
            horizon_seconds=5, predicted_value=2, confidence=0.5, model_name="persistence",
            model_version="persistence-v1", expires_at=11,
            classification=SituationClassification.NORMAL, residual=0,
            evidence_basis="stale test",
        ),
    )
    stale = read_a1_forecasts(stale_board, run_id=RUN_ID, scenario_hash=SCENARIO_HASH, signal_id="J0", valid_at=20)
    assert stale.forecasts == () and stale.local_only

    empty.inject_unavailable()
    unavailable = read_a1_forecasts(empty, run_id=RUN_ID, scenario_hash=SCENARIO_HASH, signal_id="J0", valid_at=20)
    assert unavailable.disposition is MessageDisposition.UNAVAILABLE
    assert unavailable.forecasts == () and unavailable.local_only


class _FakeTrafficLight:
    def __init__(self) -> None:
        self.state = "GrGr"
        self.writes: list[tuple[str, str]] = []

    def setRedYellowGreenState(self, signal_id: str, state: str) -> None:
        self.state = state
        self.writes.append((signal_id, state))

    def getRedYellowGreenState(self, signal_id: str) -> str:
        return self.state


class _FakeConnection:
    def __init__(self) -> None:
        self.trafficlight = _FakeTrafficLight()


class _MalformedForecastTransport:
    def read(self, *args: object, **kwargs: object) -> object:
        return type("MalformedRead", (), {
            "disposition": MessageDisposition.MALFORMED,
            "messages": (),
        })()


def _situation_aware_controller(transport: object):
    connection = _FakeConnection()
    log = ImmutableSafetyLog()
    mask = DeterministicSafetyMask(controlled_cross_plan())
    executor = SignalExecutorRegistry().acquire(
        signal_id="J0", connection=connection, safety_mask=mask,
        initial_phase_id="NS_GREEN", initial_phase_entered_at=0,
        run_id=RUN_ID, scenario_hash=SCENARIO_HASH, log=log,
    )
    local = CooperativeMaxPressureController(
        a1=A1FlowController(executor), safety_mask=mask,
        run_id=RUN_ID, scenario_hash=SCENARIO_HASH, signal_id="J0",
    )
    controller = A1SituationAwareMaxPressureController(
        controller=local, transport=transport, run_id=RUN_ID,
        scenario_hash=SCENARIO_HASH, signal_id="J0",
    )
    return controller, connection, log


@pytest.mark.parametrize(
    ("case", "expected_disposition"),
    [
        ("silent", MessageDisposition.EMPTY),
        ("stale", MessageDisposition.EMPTY),
        ("unavailable", MessageDisposition.UNAVAILABLE),
        ("malformed", MessageDisposition.MALFORMED),
    ],
)
def test_a1_executes_local_max_pressure_when_a4_forecast_is_unusable(
    case: str, expected_disposition: MessageDisposition,
) -> None:
    transport: object = InProcessMessageBoard()
    if case == "stale":
        A4SituationAgent(transport).publish_forecast(
            run_id=RUN_ID, scenario_hash=SCENARIO_HASH,
            message_id="integrated-stale", correlation_id="integrated-stale",
            created_at=NOW, simulation_time=10,
            payload=ForecastPayload(
                scenario_case="integrated_stale", signal_id="J0", target="arrivals",
                source_time=10, horizon_seconds=5, predicted_value=2,
                confidence=0.5, model_name="persistence",
                model_version="persistence-v1", expires_at=11,
                classification=SituationClassification.NORMAL, residual=0,
                evidence_basis="integrated stale fallback test",
            ),
        )
    elif case == "unavailable":
        transport.inject_unavailable()
    elif case == "malformed":
        transport = _MalformedForecastTransport()

    controller, connection, log = _situation_aware_controller(transport)
    result = controller.decide(
        proposal_id=f"a4-fallback-{case}",
        observation=MaxPressureObservation(
            simulation_time=20, current_phase_id="NS_GREEN", phase_entered_at=0,
            movements={
                "north": MovementPressure(1, 0, 20),
                "south": MovementPressure(1, 0, 20),
                "east": MovementPressure(5, 0, 20),
                "west": MovementPressure(5, 0, 20),
            },
        ),
    )

    assert result.forecast_read.disposition is expected_disposition
    assert result.forecast_read.forecasts == () and result.local_only
    assert result.decision.reason_code == "MAX_PRESSURE_LOCAL_ONLY"
    assert result.decision.considered_message_ids == ()
    assert result.decision.safety_reason_code == "ACCEPTED"
    assert len(log.events) == len(log.commands) == 1
    assert connection.trafficlight.writes == [("J0", "yryr")]
