from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Mapping

from coflow5.control.safety import (
    ActionProposal,
    DeterministicSafetyMask,
    ProposalSource,
    SafetyReason,
    SignalSnapshot,
)
from coflow5.messaging.board import MessageTransport
from coflow5.messaging.envelope import (
    PRIORITY_RANK,
    MessageEnvelope,
    PriorityClass,
    Topic,
)


@dataclass(frozen=True)
class ArbitrationContext:
    run_id: str
    scenario_hash: str
    signal_id: str
    simulation_time: float
    current_phase_id: str
    phase_entered_at: float
    flow_requested_phase_id: str
    downstream_feasible_by_movement: Mapping[str, bool] = field(default_factory=dict)
    pedestrian_remaining_clearance: Mapping[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not all((self.run_id, self.scenario_hash, self.signal_id, self.current_phase_id)):
            raise ValueError("arbitration identity and current phase are required")
        if not all(math.isfinite(value) for value in (self.simulation_time, self.phase_entered_at)):
            raise ValueError("arbitration times must be finite")
        if self.simulation_time < self.phase_entered_at:
            raise ValueError("simulation time cannot precede phase entry")
        clearances = dict(self.pedestrian_remaining_clearance)
        if any(not math.isfinite(value) or value < 0 for value in clearances.values()):
            raise ValueError("pedestrian clearances must be finite and non-negative")
        object.__setattr__(
            self, "downstream_feasible_by_movement",
            MappingProxyType(dict(self.downstream_feasible_by_movement)),
        )
        object.__setattr__(self, "pedestrian_remaining_clearance", MappingProxyType(clearances))


@dataclass(frozen=True)
class RequestDecision:
    run_id: str
    scenario_hash: str
    event_id: str
    referenced_message_id: str
    reply_message_id: str
    simulation_time: float
    recorded_at: str
    source_agent: str
    priority_class: str
    accepted: bool
    selected_action: str
    reason_code: str
    safety_reason_code: str
    constraints: tuple[str, ...]
    provenance: str = "a1-deterministic-request-arbitration-v1"


@dataclass(frozen=True)
class ArbitrationRound:
    selected_action: str
    decisions: tuple[RequestDecision, ...]
    replies: tuple[MessageEnvelope, ...]


@dataclass(frozen=True)
class _Candidate:
    message: MessageEnvelope
    requested_phase_id: str
    requested_movement: str
    expected_benefit: float
    externality: float
    urgency: float
    eta: float
    safety_reason: SafetyReason

    @property
    def priority_rank(self) -> int:
        return PRIORITY_RANK[self.message.priority_class.value]

    @property
    def net_benefit(self) -> float:
        return self.expected_benefit - self.externality


class A1RequestArbitrator:
    """Pure request arbitration; accepted actions still require normal A1 submission."""

    def __init__(self, *, transport: MessageTransport, safety_mask: DeterministicSafetyMask) -> None:
        self._transport = transport
        self._safety_mask = safety_mask

    def arbitrate(self, context: ArbitrationContext) -> ArbitrationRound:
        read = self._transport.read(
            Topic.REQUESTS.value,
            valid_at=context.simulation_time,
            run_id=context.run_id,
            scenario_hash=context.scenario_hash,
        )
        requests = tuple(
            message for message in read.messages
            if message.destination_or_topic == Topic.REQUESTS.value
            and message.payload.get("signal_id") == context.signal_id
        )
        active_clearance = dict(context.pedestrian_remaining_clearance)
        for message in requests:
            if message.payload_type != "active_crossing_state":
                continue
            if message.payload.get("active_crossing") is not True:
                continue
            crossing = message.payload.get("crossing_id")
            remaining = message.payload.get("remaining_clearance_seconds")
            if isinstance(crossing, str) and self._finite_number(remaining) and float(remaining) > 0:
                active_clearance[crossing] = max(active_clearance.get(crossing, 0.0), float(remaining))

        snapshot = SignalSnapshot(
            phase_id=context.current_phase_id,
            phase_entered_at=context.phase_entered_at,
            pedestrian_remaining_clearance=active_clearance,
        )
        feasible: list[_Candidate] = []
        pre_rejections: dict[str, tuple[str, str]] = {}
        for message in requests:
            parsed = self._candidate(message, context, snapshot)
            if isinstance(parsed, tuple):
                pre_rejections[message.message_id] = parsed
            else:
                feasible.append(parsed)

        ranked = sorted(feasible, key=self._rank_key)
        winner = ranked[0] if ranked else None
        selected_action = winner.requested_phase_id if winner else context.flow_requested_phase_id
        decisions: list[RequestDecision] = []
        replies: list[MessageEnvelope] = []
        for message in requests:
            candidate = next((item for item in feasible if item.message.message_id == message.message_id), None)
            if message.message_id in pre_rejections:
                reason_code, safety_reason = pre_rejections[message.message_id]
                accepted = False
            elif winner is not None and candidate is not None and message.message_id == winner.message.message_id:
                accepted = True
                reason_code = self._accepted_reason(message.priority_class)
                safety_reason = candidate.safety_reason.value
            else:
                accepted = False
                safety_reason = candidate.safety_reason.value if candidate else "NOT_EVALUATED"
                reason_code = (
                    "REJECTED_SAME_TIER_TIEBREAK"
                    if winner is not None
                    and candidate is not None
                    and candidate.priority_rank == winner.priority_rank
                    else "REJECTED_HIGHER_PRIORITY_REQUEST"
                )
            event_id = self._event_id(context, message.message_id)
            reply_message_id = f"reply-{event_id}"
            decision = RequestDecision(
                run_id=context.run_id,
                scenario_hash=context.scenario_hash,
                event_id=event_id,
                referenced_message_id=message.message_id,
                reply_message_id=reply_message_id,
                simulation_time=context.simulation_time,
                recorded_at=datetime.now(timezone.utc).isoformat(),
                source_agent=message.source_agent,
                priority_class=message.priority_class.value,
                accepted=accepted,
                selected_action=selected_action,
                reason_code=reason_code,
                safety_reason_code=safety_reason,
                constraints=(
                    "priority=active_safety>emergency>pedestrian_deadline>late_transit>flow",
                    "same_tier=urgency_then_net_benefit_then_externality_then_eta_then_expiry_then_message_id",
                    "downstream-feasibility-required",
                    "accepted-action-still-requires-deterministic-safety-mask-and-A1-executor",
                    "single-writer=A1_FLOW",
                ),
            )
            reply = MessageEnvelope(
                run_id=context.run_id,
                scenario_hash=context.scenario_hash,
                message_id=reply_message_id,
                correlation_id=f"{message.correlation_id}:{message.message_id}",
                source_agent="A1_FLOW",
                destination_or_topic=Topic.REPLIES.value,
                created_at=datetime.now(timezone.utc),
                simulation_time=context.simulation_time,
                expires_at=max(context.simulation_time, message.expires_at),
                priority_class=message.priority_class,
                confidence=1.0,
                schema_version=1,
                payload_type="request_decision_reply",
                payload={
                    "referenced_message_id": message.message_id,
                    "event_id": event_id,
                    "accepted": accepted,
                    "selected_action": selected_action,
                    "reason_code": reason_code,
                    "safety_reason_code": safety_reason,
                },
                provenance=decision.provenance,
            )
            result = self._transport.publish(reply, valid_at=context.simulation_time)
            if not result.accepted or result.message is None:
                raise RuntimeError(f"A1 reply publication failed: {result.disposition.value}")
            decisions.append(decision)
            replies.append(result.message)
        decisions.sort(key=lambda item: item.referenced_message_id)
        replies.sort(key=lambda item: item.message_id)
        return ArbitrationRound(selected_action, tuple(decisions), tuple(replies))

    def _candidate(
        self,
        message: MessageEnvelope,
        context: ArbitrationContext,
        snapshot: SignalSnapshot,
    ) -> _Candidate | tuple[str, str]:
        payload = message.payload
        phase = payload.get("requested_phase_id")
        movement = payload.get("requested_movement")
        benefit = payload.get("expected_benefit_seconds", 0.0)
        externality = payload.get(
            "civilian_delay_externality_seconds",
            payload.get("other_traffic_externality_seconds", 0.0),
        )
        urgency = payload.get("urgency", 0.0)
        eta = payload.get("eta_seconds", math.inf)
        if (
            not isinstance(phase, str) or not phase
            or not isinstance(movement, str) or not movement
            or not self._finite_non_negative(benefit)
            or not self._finite_non_negative(externality)
            or not self._finite_non_negative(urgency)
            or not (eta == math.inf or self._finite_non_negative(eta))
        ):
            return "REJECTED_INVALID_REQUEST", "NOT_EVALUATED"
        if payload.get("downstream_available") is False:
            return "REJECTED_DOWNSTREAM_BLOCKED", "NOT_EVALUATED"
        if not context.downstream_feasible_by_movement.get(movement, True):
            return "REJECTED_DOWNSTREAM_BLOCKED", "NOT_EVALUATED"
        safety = self._safety_mask.evaluate(
            ActionProposal(
                proposal_id=f"arbitrate-{message.message_id}",
                signal_id=context.signal_id,
                requested_phase_id=phase,
                source=ProposalSource.A1_FLOW,
            ),
            snapshot,
            context.simulation_time,
        )
        if not safety.accepted:
            return safety.reason.value, safety.reason.value
        return _Candidate(
            message=message,
            requested_phase_id=phase,
            requested_movement=movement,
            expected_benefit=float(benefit),
            externality=float(externality),
            urgency=float(urgency),
            eta=float(eta),
            safety_reason=safety.reason,
        )

    @staticmethod
    def _rank_key(candidate: _Candidate) -> tuple[float | str, ...]:
        return (
            -candidate.priority_rank,
            -candidate.urgency,
            -candidate.net_benefit,
            -candidate.expected_benefit,
            candidate.externality,
            candidate.eta,
            candidate.message.expires_at,
            candidate.message.message_id,
        )

    @staticmethod
    def _accepted_reason(priority: PriorityClass) -> str:
        return {
            PriorityClass.ACTIVE_SAFETY: "ACCEPTED_ACTIVE_CROSSING_CLEARANCE",
            PriorityClass.EMERGENCY: "ACCEPTED_EMERGENCY_PRIORITY",
            PriorityClass.PEDESTRIAN_DEADLINE: "ACCEPTED_PEDESTRIAN_DEADLINE",
            PriorityClass.LATE_TRANSIT: "ACCEPTED_CONDITIONAL_LATE_TRANSIT",
        }.get(priority, "ACCEPTED_BOUNDED_ADVISORY")

    @staticmethod
    def _event_id(context: ArbitrationContext, message_id: str) -> str:
        raw = (
            f"{context.run_id}|{context.scenario_hash}|{context.signal_id}|"
            f"{context.simulation_time:.9f}|{message_id}"
        ).encode()
        return f"evt-{hashlib.sha256(raw).hexdigest()[:24]}"

    @staticmethod
    def _finite_number(value: object) -> bool:
        return (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and math.isfinite(float(value))
        )

    @classmethod
    def _finite_non_negative(cls, value: object) -> bool:
        return cls._finite_number(value) and float(value) >= 0
