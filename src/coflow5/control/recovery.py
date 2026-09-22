from __future__ import annotations

import math
import uuid
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping


class RecoveryMode(str, Enum):
    OPTIONAL_DQN = "OPTIONAL_DQN"
    COOPERATIVE_MAX_PRESSURE = "COOPERATIVE_MAX_PRESSURE"
    ACTUATED = "ACTUATED"
    FIXED_TIME = "FIXED_TIME"


REQUIRED_RECOVERY_LADDER = (
    RecoveryMode.COOPERATIVE_MAX_PRESSURE,
    RecoveryMode.ACTUATED,
    RecoveryMode.FIXED_TIME,
)

_NEXT_MODE = {
    RecoveryMode.OPTIONAL_DQN: RecoveryMode.COOPERATIVE_MAX_PRESSURE,
    RecoveryMode.COOPERATIVE_MAX_PRESSURE: RecoveryMode.ACTUATED,
    RecoveryMode.ACTUATED: RecoveryMode.FIXED_TIME,
}


@dataclass(frozen=True)
class RecoveryTransition:
    run_id: str
    scenario_hash: str
    event_id: str
    previous_mode: RecoveryMode
    next_mode: RecoveryMode
    trigger: str
    simulation_time: float
    health_evidence: Mapping[str, str]


class RecoveryExhaustedError(RuntimeError):
    """Raised visibly when FIXED_TIME itself cannot remain operational."""


class RecoverySupervisor:
    """Owns only controller mode selection; A1 and its safety mask retain actuation authority."""

    def __init__(
        self,
        *,
        run_id: str,
        scenario_hash: str,
        optional_dqn_enabled: bool = False,
    ) -> None:
        if not run_id or not scenario_hash:
            raise ValueError("run_id and scenario_hash are required")
        self._run_id = run_id
        self._scenario_hash = scenario_hash
        self._mode = (
            RecoveryMode.OPTIONAL_DQN
            if optional_dqn_enabled
            else RecoveryMode.COOPERATIVE_MAX_PRESSURE
        )
        self._transitions: list[RecoveryTransition] = []

    @property
    def mode(self) -> RecoveryMode:
        return self._mode

    @property
    def transitions(self) -> tuple[RecoveryTransition, ...]:
        return tuple(self._transitions)

    def report_failure(
        self,
        *,
        trigger: str,
        simulation_time: float,
        health_evidence: Mapping[str, str],
    ) -> RecoveryTransition:
        if not trigger.strip():
            raise ValueError("recovery trigger is required")
        if not math.isfinite(simulation_time) or simulation_time < 0:
            raise ValueError("simulation_time must be finite and non-negative")
        evidence = {str(key): str(value) for key, value in health_evidence.items()}
        if not evidence or any(not key.strip() or not value.strip() for key, value in evidence.items()):
            raise ValueError("non-empty health evidence is required")
        next_mode = _NEXT_MODE.get(self._mode)
        if next_mode is None:
            raise RecoveryExhaustedError(
                f"no hidden fallback after {self._mode.value}; trigger={trigger}"
            )
        sequence = len(self._transitions) + 1
        event_name = (
            f"{sequence}|{self._mode.value}|{next_mode.value}|"
            f"{simulation_time:.9f}|{trigger}"
        )
        transition = RecoveryTransition(
            run_id=self._run_id,
            scenario_hash=self._scenario_hash,
            event_id=str(uuid.uuid5(
                uuid.NAMESPACE_URL, f"coflow5:{self._run_id}:recovery:{event_name}"
            )),
            previous_mode=self._mode,
            next_mode=next_mode,
            trigger=trigger,
            simulation_time=simulation_time,
            health_evidence=MappingProxyType(evidence),
        )
        self._transitions.append(transition)
        self._mode = next_mode
        return transition
