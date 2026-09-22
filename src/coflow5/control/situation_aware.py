from __future__ import annotations

from dataclasses import dataclass

from coflow5.control.max_pressure import (
    CooperativeMaxPressureController,
    MaxPressureDecision,
    MaxPressureObservation,
)
from coflow5.messaging.a1_forecasts import A1ForecastRead, read_a1_forecasts
from coflow5.messaging.board import MessageTransport


@dataclass(frozen=True)
class SituationAwareMaxPressureResult:
    """One A1 decision plus the read-only A4 input used for provenance."""

    decision: MaxPressureDecision
    forecast_read: A1ForecastRead

    @property
    def local_only(self) -> bool:
        return self.forecast_read.local_only


class A1SituationAwareMaxPressureController:
    """Read A4 forecasts without giving A4 any signal-write capability.

    Forecasts are evidence inputs only in Row 10. If none are usable, A1 still
    executes the unchanged deterministic local cooperative Max-Pressure path.
    """

    def __init__(
        self,
        *,
        controller: CooperativeMaxPressureController,
        transport: MessageTransport,
        run_id: str,
        scenario_hash: str,
        signal_id: str,
    ) -> None:
        if not run_id or not scenario_hash or not signal_id:
            raise ValueError("run, scenario, and signal identity are required")
        self.__controller = controller
        self.__transport = transport
        self.__run_id = run_id
        self.__scenario_hash = scenario_hash
        self.__signal_id = signal_id

    def decide(
        self, *, proposal_id: str, observation: MaxPressureObservation,
    ) -> SituationAwareMaxPressureResult:
        forecast_read = read_a1_forecasts(
            self.__transport,
            run_id=self.__run_id,
            scenario_hash=self.__scenario_hash,
            signal_id=self.__signal_id,
            valid_at=observation.simulation_time,
        )
        decision = self.__controller.decide(
            proposal_id=proposal_id,
            observation=observation,
        )
        return SituationAwareMaxPressureResult(
            decision=decision,
            forecast_read=forecast_read,
        )
