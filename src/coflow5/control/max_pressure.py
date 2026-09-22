from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Mapping, Sequence

from coflow5.control.a1_controller import A1FlowController
from coflow5.control.safety import (
    ActionProposal,
    DeterministicSafetyMask,
    ProposalSource,
    SignalPlan,
    SignalSnapshot,
)


@dataclass(frozen=True)
class MovementPressure:
    """Local queue state for one controlled movement."""

    upstream_queue: float
    downstream_queue: float
    downstream_capacity: float

    def __post_init__(self) -> None:
        values = (self.upstream_queue, self.downstream_queue, self.downstream_capacity)
        if not all(math.isfinite(value) for value in values):
            raise ValueError("movement pressure values must be finite")
        if self.upstream_queue < 0 or self.downstream_queue < 0:
            raise ValueError("queue values cannot be negative")
        if self.downstream_capacity <= 0:
            raise ValueError("downstream capacity must be positive")

    @property
    def available_capacity_ratio(self) -> float:
        return max(0.0, min(1.0, 1.0 - self.downstream_queue / self.downstream_capacity))

    @property
    def capacity_weighted_pressure(self) -> float:
        local_pressure = self.upstream_queue - self.downstream_queue
        return local_pressure * self.available_capacity_ratio


@dataclass(frozen=True)
class AdvisoryRequest:
    """A bounded, non-actuating request that can only influence a legal A1 choice."""

    message_id: str
    run_id: str
    signal_id: str
    requested_phase_id: str
    source: str
    valid_from: float
    expires_at: float
    weight: float = 1.0

    def __post_init__(self) -> None:
        if not all((self.message_id, self.run_id, self.signal_id, self.requested_phase_id, self.source)):
            raise ValueError("advisory identity, source, signal, and requested phase are required")
        if not all(math.isfinite(value) for value in (self.valid_from, self.expires_at, self.weight)):
            raise ValueError("advisory bounds must be finite")
        if self.valid_from < 0 or self.expires_at < self.valid_from:
            raise ValueError("advisory validity window is invalid")
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError("advisory weight must be bounded to [0, 1]")


@dataclass(frozen=True)
class MaxPressureObservation:
    simulation_time: float
    current_phase_id: str
    phase_entered_at: float
    movements: Mapping[str, MovementPressure]
    advisories: tuple[AdvisoryRequest, ...] = ()
    pedestrian_remaining_clearance: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not math.isfinite(self.simulation_time) or not math.isfinite(self.phase_entered_at):
            raise ValueError("phase times must be finite")
        if self.phase_entered_at < 0 or self.simulation_time < self.phase_entered_at:
            raise ValueError("observation time cannot precede phase entry")
        movements = dict(self.movements)
        if not movements:
            raise ValueError("at least one local movement is required")
        clearances = dict(self.pedestrian_remaining_clearance)
        if any(not math.isfinite(value) or value < 0 for value in clearances.values()):
            raise ValueError("pedestrian clearances must be finite and non-negative")
        object.__setattr__(self, "movements", MappingProxyType(movements))
        object.__setattr__(self, "advisories", tuple(self.advisories))
        object.__setattr__(self, "pedestrian_remaining_clearance", MappingProxyType(clearances))


@dataclass(frozen=True)
class ActionScore:
    phase_id: str
    total: float
    pressure: float
    phase_timing: float
    advisory: float
    movement_ids: tuple[str, ...]
    downstream_available: bool


@dataclass(frozen=True)
class MaxPressureDecision:
    run_id: str
    scenario_hash: str
    event_id: str
    proposal_id: str
    signal_id: str
    simulation_time: float
    recorded_at: str
    current_phase_id: str
    accepted_action: str
    accepted_score: float
    rejected_alternatives: tuple[str, ...]
    action_scores: tuple[ActionScore, ...]
    constraints: tuple[str, ...]
    reason_code: str
    considered_message_ids: tuple[str, ...]
    safety_reason_code: str
    provenance: str = "cooperative-max-pressure-v1"


CONTROLLED_CROSS_ACTION_MOVEMENTS: Mapping[str, tuple[str, ...]] = MappingProxyType({
    "NS_GREEN": ("north", "south"),
    "NS_YELLOW": ("east", "west"),
    "ALL_RED_TO_EW": ("east", "west"),
    "EW_GREEN": ("east", "west"),
    "EW_YELLOW": ("north", "south"),
    "ALL_RED_TO_NS": ("north", "south"),
})


class CooperativeMaxPressureController:
    """Required A1 controller; deterministic, local, and independent of learned models."""

    label = "cooperative-max-pressure"
    first_recovery_target = "cooperative-max-pressure"

    def __init__(
        self,
        *,
        a1: A1FlowController,
        safety_mask: DeterministicSafetyMask,
        run_id: str,
        scenario_hash: str,
        signal_id: str,
        action_movements: Mapping[str, Sequence[str]] = CONTROLLED_CROSS_ACTION_MOVEMENTS,
        maximum_advisory_bonus: float = 3.0,
        phase_timing_weight: float = 0.25,
    ) -> None:
        if not run_id or not scenario_hash or not signal_id:
            raise ValueError("run, scenario, and signal identity are required")
        if not math.isfinite(maximum_advisory_bonus) or maximum_advisory_bonus < 0:
            raise ValueError("maximum advisory bonus must be finite and non-negative")
        if not math.isfinite(phase_timing_weight) or phase_timing_weight < 0:
            raise ValueError("phase timing weight must be finite and non-negative")
        normalized = {phase: tuple(sorted(set(movements))) for phase, movements in action_movements.items()}
        if any(not movements for movements in normalized.values()):
            raise ValueError("each operational action requires local movements")
        self.__a1 = a1
        self.__mask = safety_mask
        self.__plan: SignalPlan = safety_mask.plan
        self.__run_id = run_id
        self.__scenario_hash = scenario_hash
        self.__signal_id = signal_id
        self.__action_movements = MappingProxyType(normalized)
        self.__maximum_advisory_bonus = maximum_advisory_bonus
        self.__phase_timing_weight = phase_timing_weight
        self.__decisions_by_proposal: dict[str, tuple[tuple[object, ...], MaxPressureDecision]] = {}

    @staticmethod
    def _observation_fingerprint(observation: MaxPressureObservation) -> tuple[object, ...]:
        movements = tuple(sorted(
            (
                movement_id,
                value.upstream_queue,
                value.downstream_queue,
                value.downstream_capacity,
            )
            for movement_id, value in observation.movements.items()
        ))
        advisories = tuple(sorted(
            (
                item.message_id,
                item.run_id,
                item.signal_id,
                item.requested_phase_id,
                item.source,
                item.valid_from,
                item.expires_at,
                item.weight,
            )
            for item in observation.advisories
        ))
        return (
            observation.simulation_time,
            observation.current_phase_id,
            observation.phase_entered_at,
            movements,
            advisories,
            tuple(sorted(observation.pedestrian_remaining_clearance.items())),
        )

    def decide(self, *, proposal_id: str, observation: MaxPressureObservation) -> MaxPressureDecision:
        if not proposal_id:
            raise ValueError("proposal_id is required")
        fingerprint = self._observation_fingerprint(observation)
        previous = self.__decisions_by_proposal.get(proposal_id)
        if previous is not None:
            previous_fingerprint, previous_decision = previous
            if previous_fingerprint != fingerprint:
                raise ValueError(f"proposal_id reused with different observation: {proposal_id}")
            return previous_decision
        if observation.current_phase_id not in self.__plan.phases:
            raise ValueError(f"unknown current phase: {observation.current_phase_id}")
        snapshot = SignalSnapshot(
            phase_id=observation.current_phase_id,
            phase_entered_at=observation.phase_entered_at,
            pedestrian_remaining_clearance=observation.pedestrian_remaining_clearance,
        )
        candidate_ids: list[str] = []
        for phase_id in sorted(self.__plan.legal_transitions[observation.current_phase_id]):
            if phase_id not in self.__action_movements:
                continue
            safety = self.__mask.evaluate(
                ActionProposal(proposal_id, self.__signal_id, phase_id, ProposalSource.A1_FLOW),
                snapshot,
                observation.simulation_time,
            )
            if safety.accepted:
                candidate_ids.append(phase_id)
        if not candidate_ids:
            raise RuntimeError("deterministic safety mask exposed no legal Max-Pressure action")

        downstream_available: dict[str, bool] = {}
        for phase_id in candidate_ids:
            try:
                downstream_available[phase_id] = any(
                    observation.movements[movement_id].available_capacity_ratio > 0.0
                    for movement_id in self.__action_movements[phase_id]
                )
            except KeyError as exc:
                raise ValueError(f"missing local movement pressure: {exc.args[0]}") from exc
        # Holding the current phase remains a legal liveness fallback, but a fully
        # blocked transition can never be selected or promoted by an advisory.
        selectable_ids = {
            phase_id for phase_id in candidate_ids
            if downstream_available[phase_id] or phase_id == observation.current_phase_id
        }
        if not selectable_ids:
            raise RuntimeError("no live Max-Pressure action after downstream capacity mask")

        grouped_advisories: dict[str, list[AdvisoryRequest]] = {}
        for advisory in observation.advisories:
            if (
                advisory.run_id == self.__run_id
                and advisory.signal_id == self.__signal_id
                and advisory.valid_from <= observation.simulation_time <= advisory.expires_at
                and advisory.requested_phase_id in selectable_ids
            ):
                grouped_advisories.setdefault(advisory.message_id, []).append(advisory)
        # One message identity contributes at most once. Conflicting reuse of an
        # identity is not a valid advisory and contributes nothing.
        valid_advisories = tuple(
            copies[0]
            for message_id in sorted(grouped_advisories)
            if (copies := grouped_advisories[message_id])
            and all(item == copies[0] for item in copies)
        )
        considered_message_ids = tuple(item.message_id for item in valid_advisories)
        elapsed = observation.simulation_time - observation.phase_entered_at
        timing_scale = max(self.__plan.minimum_green_seconds, 1.0)
        bounded_elapsed = min(elapsed / timing_scale, 2.0)
        scores: list[ActionScore] = []
        for phase_id in candidate_ids:
            movement_ids = self.__action_movements[phase_id]
            pressure = sum(
                observation.movements[movement_id].capacity_weighted_pressure
                for movement_id in movement_ids
            )
            timing_direction = -1.0 if phase_id == observation.current_phase_id else 1.0
            timing = timing_direction * bounded_elapsed * self.__phase_timing_weight
            requested_weight = sum(
                item.weight for item in valid_advisories if item.requested_phase_id == phase_id
            )
            advisory = min(self.__maximum_advisory_bonus, requested_weight * self.__maximum_advisory_bonus)
            scores.append(ActionScore(
                phase_id=phase_id,
                total=pressure + timing + advisory,
                pressure=pressure,
                phase_timing=timing,
                advisory=advisory,
                movement_ids=movement_ids,
                downstream_available=downstream_available[phase_id],
            ))
        ranked_selectable = sorted(
            (score for score in scores if score.phase_id in selectable_ids),
            key=lambda score: (-score.total, score.phase_id),
        )
        accepted = ranked_selectable[0]
        rejected = sorted(
            (score for score in scores if score.phase_id != accepted.phase_id),
            key=lambda score: (
                score.phase_id not in selectable_ids,
                -score.total,
                score.phase_id,
            ),
        )
        ranked = (accepted, *rejected)
        safety_event = self.__a1.propose(
            proposal_id=proposal_id,
            signal_id=self.__signal_id,
            phase_id=accepted.phase_id,
            simulation_time=observation.simulation_time,
            pedestrian_remaining_clearance=observation.pedestrian_remaining_clearance,
        )
        if not safety_event.accepted:
            raise RuntimeError(
                f"scored legal action was rejected by SignalExecutor: {safety_event.reason_code}"
            )
        reason_code = (
            "MAX_PRESSURE_WITH_ADVISORY"
            if considered_message_ids
            else "MAX_PRESSURE_LOCAL_ONLY"
        )
        blocked_ids = sorted(
            phase_id for phase_id in candidate_ids
            if phase_id not in selectable_ids
        )
        constraints = (
            "deterministic-safety-mask",
            "legal-transition-only",
            f"phase_elapsed_seconds={elapsed:.3f}",
            f"maximum_advisory_bonus={self.__maximum_advisory_bonus:.3f}",
            "downstream_capacity_clamped_0_to_1",
            "downstream_blocked_actions=" + (",".join(blocked_ids) if blocked_ids else "none"),
            "duplicate_message_id_contributes_at_most_once",
            "single-writer=A1_FLOW",
        )
        decision = MaxPressureDecision(
            run_id=self.__run_id,
            scenario_hash=self.__scenario_hash,
            event_id=safety_event.event_id,
            proposal_id=proposal_id,
            signal_id=self.__signal_id,
            simulation_time=observation.simulation_time,
            recorded_at=datetime.now(timezone.utc).isoformat(),
            current_phase_id=observation.current_phase_id,
            accepted_action=accepted.phase_id,
            accepted_score=accepted.total,
            rejected_alternatives=tuple(score.phase_id for score in rejected),
            action_scores=tuple(ranked),
            constraints=constraints,
            reason_code=reason_code,
            considered_message_ids=considered_message_ids,
            safety_reason_code=safety_event.reason_code,
        )
        self.__decisions_by_proposal[proposal_id] = (fingerprint, decision)
        return decision
