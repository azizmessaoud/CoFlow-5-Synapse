from __future__ import annotations

from dataclasses import dataclass

from coflow5.control.a1_controller import A1FlowController
from coflow5.control.max_pressure import (
    CooperativeMaxPressureController,
    MaxPressureObservation,
    MovementPressure,
)
from coflow5.control.safety import DeterministicSafetyMask, controlled_cross_plan
from coflow5.control.situation_aware import (
    A1SituationAwareMaxPressureController,
    SituationAwareMaxPressureResult,
)
from coflow5.messaging.board import MessageTransport
from coflow5.sumo_adapter.signal_executor import ImmutableSafetyLog, SignalExecutorRegistry


class _ProbeTrafficLight:
    def __init__(self) -> None:
        self.state = "GrGr"
        self.writes: list[tuple[str, str]] = []

    def setRedYellowGreenState(self, signal_id: str, state: str) -> None:
        self.state = state
        self.writes.append((signal_id, state))

    def getRedYellowGreenState(self, signal_id: str) -> str:
        return self.state


class _ProbeConnection:
    def __init__(self) -> None:
        self.trafficlight = _ProbeTrafficLight()


@dataclass(frozen=True)
class ForecastFallbackProbe:
    result: SituationAwareMaxPressureResult
    a1_signal_write_count: int
    a4_signal_write_count: int
    safety_event_count: int
    command_count: int


def run_forecast_fallback_probe(
    *, transport: MessageTransport, run_id: str, scenario_hash: str,
    signal_id: str = "J0", simulation_time: float = 20.0,
) -> ForecastFallbackProbe:
    """Execute one legal in-memory A1 decision for Row 10 fallback evidence."""
    connection = _ProbeConnection()
    log = ImmutableSafetyLog()
    mask = DeterministicSafetyMask(controlled_cross_plan())
    executor = SignalExecutorRegistry().acquire(
        signal_id=signal_id,
        connection=connection,
        safety_mask=mask,
        initial_phase_id="NS_GREEN",
        initial_phase_entered_at=0.0,
        run_id=run_id,
        scenario_hash=scenario_hash,
        log=log,
    )
    local = CooperativeMaxPressureController(
        a1=A1FlowController(executor),
        safety_mask=mask,
        run_id=run_id,
        scenario_hash=scenario_hash,
        signal_id=signal_id,
    )
    result = A1SituationAwareMaxPressureController(
        controller=local,
        transport=transport,
        run_id=run_id,
        scenario_hash=scenario_hash,
        signal_id=signal_id,
    ).decide(
        proposal_id=f"a4-fallback-{simulation_time:g}",
        observation=MaxPressureObservation(
            simulation_time=simulation_time,
            current_phase_id="NS_GREEN",
            phase_entered_at=0.0,
            movements={
                "north": MovementPressure(1, 0, 20),
                "south": MovementPressure(1, 0, 20),
                "east": MovementPressure(5, 0, 20),
                "west": MovementPressure(5, 0, 20),
            },
        ),
    )
    return ForecastFallbackProbe(
        result=result,
        a1_signal_write_count=len(connection.trafficlight.writes),
        a4_signal_write_count=0,
        safety_event_count=len(log.events),
        command_count=len(log.commands),
    )
