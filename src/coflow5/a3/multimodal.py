from __future__ import annotations

import math
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from coflow5.messaging import (
    MessageEnvelope,
    MessageTransport,
    PriorityClass,
    PublishResult,
    Topic,
)


class CrossingStatePayload(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_case: str = Field(min_length=1)
    crossing_id: str = Field(min_length=1)
    signal_id: str = Field(min_length=1)
    active_crossing: bool
    remaining_clearance_seconds: float = Field(ge=0)
    requested_movement: str = Field(min_length=1)
    requested_phase_id: str = Field(min_length=1)
    expected_benefit_seconds: float = Field(default=0, ge=0)
    civilian_delay_externality_seconds: float = Field(default=0, ge=0)

    @model_validator(mode="after")
    def values_are_finite(self) -> "CrossingStatePayload":
        values = (
            self.remaining_clearance_seconds,
            self.expected_benefit_seconds,
            self.civilian_delay_externality_seconds,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("crossing evidence must be finite")
        return self


    @model_validator(mode="after")
    def active_crossing_has_clearance(self) -> "CrossingStatePayload":
        if self.active_crossing and self.remaining_clearance_seconds <= 0:
            raise ValueError("an active crossing requires positive remaining clearance")
        return self


class PedestrianDeadlinePayload(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_case: str = Field(min_length=1)
    crossing_id: str = Field(min_length=1)
    signal_id: str = Field(min_length=1)
    wait_age_seconds: float = Field(ge=0)
    deadline_seconds: float = Field(gt=0)
    seconds_to_deadline: float

    @model_validator(mode="after")
    def values_are_finite(self) -> "PedestrianDeadlinePayload":
        values = (
            self.wait_age_seconds,
            self.deadline_seconds,
            self.seconds_to_deadline,
            self.expected_benefit_seconds,
            self.civilian_delay_externality_seconds,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("pedestrian deadline evidence must be finite")
        return self

    requested_movement: str = Field(min_length=1)
    requested_phase_id: str = Field(min_length=1)
    expected_benefit_seconds: float = Field(ge=0)
    civilian_delay_externality_seconds: float = Field(ge=0)


class TransitPriorityPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_case: str = Field(min_length=1)
    vehicle_id: str = Field(min_length=1)
    signal_id: str = Field(min_length=1)
    schedule_deviation_seconds: float
    observed_headway_seconds: float = Field(gt=0)
    target_headway_seconds: float = Field(gt=0)
    headway_gap_seconds: float
    evidence_basis: tuple[str, ...]
    requested_movement: str = Field(min_length=1)
    requested_phase_id: str = Field(min_length=1)
    expected_benefit_seconds: float = Field(ge=0)
    other_traffic_externality_seconds: float = Field(ge=0)

    @model_validator(mode="after")
    def values_are_finite(self) -> "TransitPriorityPayload":
        values = (
            self.schedule_deviation_seconds,
            self.observed_headway_seconds,
            self.target_headway_seconds,
            self.headway_gap_seconds,
            self.expected_benefit_seconds,
            self.other_traffic_externality_seconds,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("transit evidence must be finite")
        return self


class A3MultimodalAgent:
    """A3 publishes bounded pedestrian/transit evidence and never actuates signals."""

    source_agent = "A3_MULTIMODAL"

    def __init__(
        self,
        transport: MessageTransport,
        *,
        minimum_deadline_seconds: float = 20.0,
        maximum_deadline_seconds: float = 180.0,
        escalation_window_seconds: float = 15.0,
        minimum_transit_lateness_seconds: float = 30.0,
        minimum_headway_gap_seconds: float = 60.0,
    ) -> None:
        bounds = (
            minimum_deadline_seconds,
            maximum_deadline_seconds,
            escalation_window_seconds,
            minimum_transit_lateness_seconds,
            minimum_headway_gap_seconds,
        )
        if not all(math.isfinite(value) and value >= 0 for value in bounds):
            raise ValueError("A3 bounds must be finite and non-negative")
        if minimum_deadline_seconds <= 0 or maximum_deadline_seconds < minimum_deadline_seconds:
            raise ValueError("pedestrian deadline bounds are invalid")
        self._transport = transport
        self.minimum_deadline_seconds = minimum_deadline_seconds
        self.maximum_deadline_seconds = maximum_deadline_seconds
        self.escalation_window_seconds = escalation_window_seconds
        self.minimum_transit_lateness_seconds = minimum_transit_lateness_seconds
        self.minimum_headway_gap_seconds = minimum_headway_gap_seconds

    def publish_crossing_state(
        self,
        *,
        run_id: str,
        scenario_hash: str,
        message_id: str,
        correlation_id: str,
        created_at: datetime,
        simulation_time: float,
        expires_at: float,
        payload: CrossingStatePayload,
    ) -> PublishResult:
        if expires_at < simulation_time:
            raise ValueError("crossing-state expiry cannot precede publication")
        priority = (
            PriorityClass.ACTIVE_SAFETY
            if payload.active_crossing
            else PriorityClass.GENERAL_FLOW
        )
        return self._publish(
            run_id=run_id,
            scenario_hash=scenario_hash,
            message_id=message_id,
            correlation_id=correlation_id,
            created_at=created_at,
            simulation_time=simulation_time,
            expires_at=expires_at,
            priority=priority,
            payload_type="active_crossing_state",
            payload=payload.model_dump(mode="json"),
            provenance="a3-crossing-clearance-rule-v1",
        )

    def publish_pedestrian_deadline(
        self,
        *,
        run_id: str,
        scenario_hash: str,
        message_id: str,
        correlation_id: str,
        created_at: datetime,
        simulation_time: float,
        expires_at: float,
        scenario_case: str,
        crossing_id: str,
        signal_id: str,
        wait_age_seconds: float,
        deadline_seconds: float,
        requested_movement: str,
        requested_phase_id: str,
        expected_benefit_seconds: float,
        civilian_delay_externality_seconds: float,
    ) -> PublishResult | None:
        if not self.minimum_deadline_seconds <= deadline_seconds <= self.maximum_deadline_seconds:
            raise ValueError("pedestrian deadline is outside configured bounds")
        seconds_to_deadline = deadline_seconds - wait_age_seconds
        if seconds_to_deadline > self.escalation_window_seconds:
            return None
        payload = PedestrianDeadlinePayload(
            scenario_case=scenario_case,
            crossing_id=crossing_id,
            signal_id=signal_id,
            wait_age_seconds=wait_age_seconds,
            deadline_seconds=deadline_seconds,
            seconds_to_deadline=seconds_to_deadline,
            requested_movement=requested_movement,
            requested_phase_id=requested_phase_id,
            expected_benefit_seconds=expected_benefit_seconds,
            civilian_delay_externality_seconds=civilian_delay_externality_seconds,
        )
        return self._publish(
            run_id=run_id,
            scenario_hash=scenario_hash,
            message_id=message_id,
            correlation_id=correlation_id,
            created_at=created_at,
            simulation_time=simulation_time,
            expires_at=expires_at,
            priority=PriorityClass.PEDESTRIAN_DEADLINE,
            payload_type="pedestrian_deadline_request",
            payload=payload.model_dump(mode="json"),
            provenance="a3-bounded-pedestrian-deadline-rule-v1",
        )

    def publish_transit_priority(
        self,
        *,
        run_id: str,
        scenario_hash: str,
        message_id: str,
        correlation_id: str,
        created_at: datetime,
        simulation_time: float,
        expires_at: float,
        scenario_case: str,
        vehicle_id: str,
        signal_id: str,
        schedule_deviation_seconds: float,
        observed_headway_seconds: float,
        target_headway_seconds: float,
        requested_movement: str,
        requested_phase_id: str,
        expected_benefit_seconds: float,
        other_traffic_externality_seconds: float,
    ) -> PublishResult | None:
        headway_gap = observed_headway_seconds - target_headway_seconds
        evidence: list[str] = []
        if schedule_deviation_seconds >= self.minimum_transit_lateness_seconds:
            evidence.append("late")
        if headway_gap >= self.minimum_headway_gap_seconds:
            evidence.append("headway_gap")
        if not evidence:
            return None
        payload = TransitPriorityPayload(
            scenario_case=scenario_case,
            vehicle_id=vehicle_id,
            signal_id=signal_id,
            schedule_deviation_seconds=schedule_deviation_seconds,
            observed_headway_seconds=observed_headway_seconds,
            target_headway_seconds=target_headway_seconds,
            headway_gap_seconds=headway_gap,
            evidence_basis=tuple(evidence),
            requested_movement=requested_movement,
            requested_phase_id=requested_phase_id,
            expected_benefit_seconds=expected_benefit_seconds,
            other_traffic_externality_seconds=other_traffic_externality_seconds,
        )
        return self._publish(
            run_id=run_id,
            scenario_hash=scenario_hash,
            message_id=message_id,
            correlation_id=correlation_id,
            created_at=created_at,
            simulation_time=simulation_time,
            expires_at=expires_at,
            priority=PriorityClass.LATE_TRANSIT,
            payload_type="conditional_transit_priority_request",
            payload=payload.model_dump(mode="json"),
            provenance="a3-evidence-based-transit-rule-v1",
        )

    def _publish(
        self,
        *,
        run_id: str,
        scenario_hash: str,
        message_id: str,
        correlation_id: str,
        created_at: datetime,
        simulation_time: float,
        expires_at: float,
        priority: PriorityClass,
        payload_type: str,
        payload: dict[str, object],
        provenance: str,
    ) -> PublishResult:
        envelope = MessageEnvelope(
            run_id=run_id,
            scenario_hash=scenario_hash,
            message_id=message_id,
            correlation_id=correlation_id,
            source_agent=self.source_agent,
            destination_or_topic=Topic.REQUESTS.value,
            created_at=created_at,
            simulation_time=simulation_time,
            expires_at=expires_at,
            priority_class=priority,
            confidence=1.0,
            schema_version=1,
            payload_type=payload_type,
            payload=payload,
            provenance=provenance,
        )
        return self._transport.publish(envelope, valid_at=simulation_time)
