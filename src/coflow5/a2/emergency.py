from __future__ import annotations

import math
from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from coflow5.messaging import (
    MessageEnvelope,
    MessageTransport,
    PriorityClass,
    PublishResult,
    Topic,
)


class RoadPosition(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    edge_id: str = Field(min_length=1)
    lane_id: str = Field(min_length=1)
    distance_m: float = Field(ge=0)


class EmergencyPriorityPayload(BaseModel):
    """Transparent evidence for one bounded emergency corridor request."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_case: str = Field(min_length=1)
    vehicle_id: str = Field(min_length=1)
    signal_id: str = Field(min_length=1)
    position: RoadPosition
    route: tuple[str, ...] = ()
    next_controlled_junctions: tuple[str, ...] = ()
    eta_seconds: float = Field(ge=0)
    urgency: float = Field(ge=0, le=1)
    expected_benefit_seconds: float = Field(ge=0)
    civilian_delay_externality_seconds: float = Field(ge=0)
    requested_movement: str = Field(min_length=1)
    requested_phase_id: str = Field(min_length=1)
    downstream_available: bool
    request_expires_at: float = Field(ge=0)

    @model_validator(mode="after")
    def route_or_controlled_junction_is_required(self) -> Self:
        if not self.route and not self.next_controlled_junctions:
            raise ValueError("route or next controlled junctions are required")
        numeric = (
            self.position.distance_m,
            self.eta_seconds,
            self.urgency,
            self.expected_benefit_seconds,
            self.civilian_delay_externality_seconds,
            self.request_expires_at,
        )
        if not all(math.isfinite(value) for value in numeric):
            raise ValueError("emergency request values must be finite")
        return self


class A2EmergencyAgent:
    """A2 can publish typed requests; it owns no observation or signal capability."""

    source_agent = "A2_EMERGENCY"

    def __init__(self, transport: MessageTransport) -> None:
        self._transport = transport

    def publish_priority_request(
        self,
        *,
        run_id: str,
        scenario_hash: str,
        message_id: str,
        correlation_id: str,
        created_at: datetime,
        simulation_time: float,
        payload: EmergencyPriorityPayload,
        confidence: float = 1.0,
    ) -> PublishResult:
        if payload.request_expires_at < simulation_time:
            raise ValueError("emergency request expiry cannot precede publication")
        envelope = MessageEnvelope(
            run_id=run_id,
            scenario_hash=scenario_hash,
            message_id=message_id,
            correlation_id=correlation_id,
            source_agent=self.source_agent,
            destination_or_topic=Topic.REQUESTS.value,
            created_at=created_at,
            simulation_time=simulation_time,
            expires_at=payload.request_expires_at,
            priority_class=PriorityClass.EMERGENCY,
            confidence=confidence,
            schema_version=1,
            payload_type="emergency_priority_request",
            payload=payload.model_dump(mode="json"),
            provenance="a2-emergency-transparent-rule-v1",
        )
        return self._transport.publish(envelope, valid_at=simulation_time)
