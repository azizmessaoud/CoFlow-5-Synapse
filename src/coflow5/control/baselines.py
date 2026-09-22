from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Protocol


@dataclass(frozen=True)
class BaselineObservation:
    simulation_time: float
    current_phase_id: str
    phase_elapsed_seconds: float
    halting_by_approach: Mapping[str, int]


class BaselineController(Protocol):
    label: str

    def propose_phase(self, observation: BaselineObservation) -> str | None: ...


_NEXT_CLEARANCE_PHASE = {
    "NS_YELLOW": "ALL_RED_TO_EW",
    "ALL_RED_TO_EW": "EW_GREEN",
    "EW_YELLOW": "ALL_RED_TO_NS",
    "ALL_RED_TO_NS": "NS_GREEN",
}

_CLEARANCE_SECONDS = {
    "NS_YELLOW": 2.0,
    "ALL_RED_TO_EW": 1.0,
    "EW_YELLOW": 2.0,
    "ALL_RED_TO_NS": 1.0,
}


@dataclass(frozen=True)
class FixedTimeController:
    """A deterministic two-stage fixed-time policy; A1 remains the signal owner."""

    green_seconds: float = 15.0
    label: str = "fixed-time"

    def __post_init__(self) -> None:
        if self.green_seconds < 5.0:
            raise ValueError("fixed green must satisfy the five-second safety minimum")

    def propose_phase(self, observation: BaselineObservation) -> str | None:
        phase = observation.current_phase_id
        elapsed = observation.phase_elapsed_seconds
        if phase == "NS_GREEN" and elapsed >= self.green_seconds:
            return "NS_YELLOW"
        if phase == "EW_GREEN" and elapsed >= self.green_seconds:
            return "EW_YELLOW"
        threshold = _CLEARANCE_SECONDS.get(phase)
        if threshold is not None and elapsed >= threshold:
            return _NEXT_CLEARANCE_PHASE[phase]
        return None


@dataclass(frozen=True)
class ActuatedController:
    """Queue-actuated policy with bounded greens and deterministic gap-out behavior."""

    minimum_green_seconds: float = 5.0
    maximum_green_seconds: float = 25.0
    switch_queue_advantage: int = 1
    label: str = "actuated"

    def __post_init__(self) -> None:
        if self.minimum_green_seconds < 5.0:
            raise ValueError("actuated minimum green must satisfy the safety plan")
        if self.maximum_green_seconds < self.minimum_green_seconds:
            raise ValueError("maximum green cannot precede minimum green")
        if self.switch_queue_advantage < 0:
            raise ValueError("queue advantage cannot be negative")

    def propose_phase(self, observation: BaselineObservation) -> str | None:
        phase = observation.current_phase_id
        elapsed = observation.phase_elapsed_seconds
        threshold = _CLEARANCE_SECONDS.get(phase)
        if threshold is not None:
            return _NEXT_CLEARANCE_PHASE[phase] if elapsed >= threshold else None
        if phase not in {"NS_GREEN", "EW_GREEN"}:
            raise ValueError(f"unsupported baseline phase: {phase}")
        if elapsed < self.minimum_green_seconds:
            return None

        ns_queue = int(observation.halting_by_approach.get("north", 0)) + int(
            observation.halting_by_approach.get("south", 0)
        )
        ew_queue = int(observation.halting_by_approach.get("east", 0)) + int(
            observation.halting_by_approach.get("west", 0)
        )
        current_queue, opposing_queue = (
            (ns_queue, ew_queue) if phase == "NS_GREEN" else (ew_queue, ns_queue)
        )
        gap_out = opposing_queue >= current_queue + self.switch_queue_advantage
        max_out = elapsed >= self.maximum_green_seconds
        if gap_out or max_out:
            return "NS_YELLOW" if phase == "NS_GREEN" else "EW_YELLOW"
        return None
