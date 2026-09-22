from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from types import MappingProxyType
from typing import Mapping


class PhaseKind(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    ALL_RED = "all_red"


class ProposalSource(str, Enum):
    A1_FLOW = "a1-flow"
    HUMAN_OVERRIDE = "human-override"


class SafetyReason(str, Enum):
    ACCEPTED = "ACCEPTED"
    UNKNOWN_PHASE = "REJECTED_UNKNOWN_PHASE"
    ILLEGAL_TRANSITION = "REJECTED_ILLEGAL_TRANSITION"
    MINIMUM_GREEN = "REJECTED_MINIMUM_GREEN"
    YELLOW_REQUIRED = "REJECTED_YELLOW_REQUIRED"
    YELLOW_MINIMUM = "REJECTED_YELLOW_MINIMUM"
    ALL_RED_REQUIRED = "REJECTED_ALL_RED_REQUIRED"
    ALL_RED_MINIMUM = "REJECTED_ALL_RED_MINIMUM"
    CONFLICTING_GREENS = "REJECTED_CONFLICTING_GREENS"
    PEDESTRIAN_CLEARANCE = "REJECTED_PEDESTRIAN_CLEARANCE"
    NON_FINITE_INPUT = "REJECTED_NON_FINITE_INPUT"
    INVALID_TIMING = "REJECTED_INVALID_TIMING"
    INVALID_CLEARANCE = "REJECTED_INVALID_CLEARANCE"


@dataclass(frozen=True)
class PhaseSpec:
    phase_id: str
    signal_state: str
    kind: PhaseKind
    green_movements: frozenset[str] = frozenset()


@dataclass(frozen=True)
class SignalPlan:
    phases: Mapping[str, PhaseSpec]
    legal_transitions: Mapping[str, frozenset[str]]
    conflicting_movements: frozenset[frozenset[str]]
    pedestrian_conflicts: Mapping[str, frozenset[str]]
    minimum_green_seconds: float
    yellow_seconds: float
    all_red_seconds: float

    def __post_init__(self) -> None:
        phases = dict(self.phases)
        transitions = {key: frozenset(value) for key, value in self.legal_transitions.items()}
        pedestrian = {key: frozenset(value) for key, value in self.pedestrian_conflicts.items()}
        timings = (self.minimum_green_seconds, self.yellow_seconds, self.all_red_seconds)
        if not phases:
            raise ValueError("signal plan requires at least one phase")
        if any(key != phase.phase_id for key, phase in phases.items()):
            raise ValueError("phase mapping keys must equal phase_id")
        if set(transitions) != set(phases):
            raise ValueError("every phase requires a transition entry")
        if any(not targets <= set(phases) for targets in transitions.values()):
            raise ValueError("transition graph references an unknown phase")
        if any(not isfinite(value) or value < 0 for value in timings):
            raise ValueError("timing bounds must be finite and non-negative")
        object.__setattr__(self, "phases", MappingProxyType(phases))
        object.__setattr__(self, "legal_transitions", MappingProxyType(transitions))
        object.__setattr__(self, "pedestrian_conflicts", MappingProxyType(pedestrian))


@dataclass(frozen=True)
class SignalSnapshot:
    phase_id: str
    phase_entered_at: float
    pedestrian_remaining_clearance: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "pedestrian_remaining_clearance",
            MappingProxyType(dict(self.pedestrian_remaining_clearance)),
        )


@dataclass(frozen=True)
class ActionProposal:
    proposal_id: str
    signal_id: str
    requested_phase_id: str
    source: ProposalSource = ProposalSource.A1_FLOW

    def __post_init__(self) -> None:
        if not self.proposal_id or not self.signal_id or not self.requested_phase_id:
            raise ValueError("proposal_id, signal_id, and requested_phase_id are required")


@dataclass(frozen=True)
class SafetyDecision:
    accepted: bool
    reason: SafetyReason
    requested_phase: PhaseSpec | None


class DeterministicSafetyMask:
    """Pure, deterministic validation shared by A1 and human overrides."""

    def __init__(self, plan: SignalPlan) -> None:
        self.plan = plan

    def evaluate(
        self, proposal: ActionProposal, snapshot: SignalSnapshot, simulation_time: float
    ) -> SafetyDecision:
        current = self.plan.phases.get(snapshot.phase_id)
        target = self.plan.phases.get(proposal.requested_phase_id)
        if current is None:
            raise ValueError(f"snapshot references unknown phase: {snapshot.phase_id}")
        if not isfinite(simulation_time) or not isfinite(snapshot.phase_entered_at):
            return SafetyDecision(False, SafetyReason.NON_FINITE_INPUT, target)
        clearance_values = tuple(snapshot.pedestrian_remaining_clearance.values())
        if any(not isfinite(value) for value in clearance_values):
            return SafetyDecision(False, SafetyReason.NON_FINITE_INPUT, target)
        if any(value < 0 for value in clearance_values):
            return SafetyDecision(False, SafetyReason.INVALID_CLEARANCE, target)
        if simulation_time < snapshot.phase_entered_at:
            return SafetyDecision(False, SafetyReason.INVALID_TIMING, target)
        if target is None:
            return SafetyDecision(False, SafetyReason.UNKNOWN_PHASE, None)

        if self._has_conflicting_greens(target):
            return SafetyDecision(False, SafetyReason.CONFLICTING_GREENS, target)
        if self._truncates_pedestrian_clearance(target, snapshot):
            return SafetyDecision(False, SafetyReason.PEDESTRIAN_CLEARANCE, target)

        if current.kind is PhaseKind.GREEN and target.phase_id != current.phase_id:
            if target.kind in {PhaseKind.GREEN, PhaseKind.ALL_RED}:
                return SafetyDecision(False, SafetyReason.YELLOW_REQUIRED, target)
            if simulation_time < snapshot.phase_entered_at + self.plan.minimum_green_seconds:
                return SafetyDecision(False, SafetyReason.MINIMUM_GREEN, target)
        elif current.kind is PhaseKind.YELLOW and target.phase_id != current.phase_id:
            if target.kind is not PhaseKind.ALL_RED:
                return SafetyDecision(False, SafetyReason.ALL_RED_REQUIRED, target)
            if simulation_time < snapshot.phase_entered_at + self.plan.yellow_seconds:
                return SafetyDecision(False, SafetyReason.YELLOW_MINIMUM, target)
        elif current.kind is PhaseKind.ALL_RED and target.phase_id != current.phase_id:
            if target.kind is not PhaseKind.GREEN:
                return SafetyDecision(False, SafetyReason.ILLEGAL_TRANSITION, target)
            if simulation_time < snapshot.phase_entered_at + self.plan.all_red_seconds:
                return SafetyDecision(False, SafetyReason.ALL_RED_MINIMUM, target)

        if target.phase_id not in self.plan.legal_transitions[current.phase_id]:
            return SafetyDecision(False, SafetyReason.ILLEGAL_TRANSITION, target)
        return SafetyDecision(True, SafetyReason.ACCEPTED, target)

    def _has_conflicting_greens(self, target: PhaseSpec) -> bool:
        return any(pair <= target.green_movements for pair in self.plan.conflicting_movements)

    def _truncates_pedestrian_clearance(
        self, target: PhaseSpec, snapshot: SignalSnapshot
    ) -> bool:
        conflicting_crossings = self.plan.pedestrian_conflicts.get(target.phase_id, frozenset())
        return any(
            snapshot.pedestrian_remaining_clearance.get(crossing, 0.0) > 0
            for crossing in conflicting_crossings
        )


def controlled_cross_plan() -> SignalPlan:
    """Small four-link plan used by row 03 and its native TraCI evidence run."""
    # J0 link order is N, E, S, W; opposing approaches occupy alternating indexes.
    phases = {
        "NS_GREEN": PhaseSpec("NS_GREEN", "GrGr", PhaseKind.GREEN, frozenset({"north", "south"})),
        "NS_YELLOW": PhaseSpec("NS_YELLOW", "yryr", PhaseKind.YELLOW),
        "ALL_RED_TO_EW": PhaseSpec("ALL_RED_TO_EW", "rrrr", PhaseKind.ALL_RED),
        "EW_GREEN": PhaseSpec("EW_GREEN", "rGrG", PhaseKind.GREEN, frozenset({"east", "west"})),
        "EW_YELLOW": PhaseSpec("EW_YELLOW", "ryry", PhaseKind.YELLOW),
        "ALL_RED_TO_NS": PhaseSpec("ALL_RED_TO_NS", "rrrr", PhaseKind.ALL_RED),
        "CONFLICTING_TEST": PhaseSpec(
            "CONFLICTING_TEST", "GGrr", PhaseKind.GREEN, frozenset({"north", "east"})
        ),
    }
    return SignalPlan(
        phases=phases,
        legal_transitions={
            "NS_GREEN": frozenset({"NS_GREEN", "NS_YELLOW", "CONFLICTING_TEST"}),
            "NS_YELLOW": frozenset({"NS_YELLOW", "ALL_RED_TO_EW"}),
            "ALL_RED_TO_EW": frozenset({"ALL_RED_TO_EW", "EW_GREEN"}),
            "EW_GREEN": frozenset({"EW_GREEN", "EW_YELLOW", "CONFLICTING_TEST"}),
            "EW_YELLOW": frozenset({"EW_YELLOW", "ALL_RED_TO_NS"}),
            "ALL_RED_TO_NS": frozenset({"ALL_RED_TO_NS", "NS_GREEN"}),
            "CONFLICTING_TEST": frozenset({"CONFLICTING_TEST"}),
        },
        conflicting_movements=frozenset(
            {
                frozenset({"north", "east"}), frozenset({"north", "west"}),
                frozenset({"south", "east"}), frozenset({"south", "west"}),
            }
        ),
        pedestrian_conflicts={
            "NS_GREEN": frozenset({"east_west_crossing"}),
            "EW_GREEN": frozenset({"north_south_crossing"}),
        },
        minimum_green_seconds=5.0,
        yellow_seconds=2.0,
        all_red_seconds=1.0,
    )
