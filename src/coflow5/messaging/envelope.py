from __future__ import annotations

import math
from datetime import datetime
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    JsonValue,
    field_serializer,
    field_validator,
    model_validator,
)


class Topic(str, Enum):
    STATE = "state"
    FORECAST = "forecast"
    ALERTS = "alerts"
    ECO = "eco"
    REQUESTS = "requests"
    REPLIES = "replies"
    HEALTH = "health"


SUPPORTED_TOPICS = frozenset(topic.value for topic in Topic)


class PriorityClass(str, Enum):
    ACTIVE_SAFETY = "active_safety"
    EMERGENCY = "emergency"
    PEDESTRIAN_DEADLINE = "pedestrian_deadline"
    LATE_TRANSIT = "late_transit"
    GENERAL_FLOW = "general_flow"
    SUSTAINABILITY = "sustainability"


PRIORITY_RANK = {
    PriorityClass.ACTIVE_SAFETY.value: 6,
    PriorityClass.EMERGENCY.value: 5,
    PriorityClass.PEDESTRIAN_DEADLINE.value: 4,
    PriorityClass.LATE_TRANSIT.value: 3,
    PriorityClass.GENERAL_FLOW.value: 2,
    PriorityClass.SUSTAINABILITY.value: 1,
}


class MessageDisposition(str, Enum):
    ACCEPTED = "accepted"
    DUPLICATE = "duplicate"
    EXPIRED = "expired"
    MALFORMED = "malformed"
    UNSUPPORTED = "unsupported"
    CONTRADICTORY = "contradictory"
    OUT_OF_ORDER = "out_of_order"
    UNAVAILABLE = "unavailable"
    EMPTY = "empty"
    EVICTED = "evicted"


Disposition = MessageDisposition


def _freeze_json(value: JsonValue) -> JsonValue:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze_json(item) for key, item in value.items()})  # type: ignore[return-value]
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)  # type: ignore[return-value]
    return value


def thaw_json(value: Any) -> JsonValue:
    """Return a recursively mutable JSON representation of a frozen payload."""
    if isinstance(value, Mapping):
        return {str(key): thaw_json(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [thaw_json(item) for item in value]
    return value


class MessageEnvelope(BaseModel):
    """Canonical, immutable transport-neutral advisory envelope."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: str = Field(min_length=1)
    scenario_hash: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    message_id: str = Field(min_length=1)
    correlation_id: str = Field(min_length=1)
    source_agent: str = Field(min_length=1)
    destination_or_topic: str = Field(min_length=1)
    created_at: datetime
    simulation_time: float = Field(ge=0)
    expires_at: float = Field(ge=0)
    priority_class: PriorityClass
    confidence: float = Field(ge=0, le=1)
    schema_version: int = Field(ge=1)
    payload_type: str = Field(min_length=1)
    payload: dict[str, JsonValue]
    provenance: str = Field(min_length=1)

    @field_validator("payload", mode="after")
    @classmethod
    def payload_must_be_deeply_immutable(
        cls, value: dict[str, JsonValue]
    ) -> Mapping[str, JsonValue]:
        return _freeze_json(value)  # type: ignore[return-value]

    @field_serializer("payload")
    def serialize_payload(self, value: Mapping[str, JsonValue]) -> JsonValue:
        return thaw_json(value)

    @field_validator(
        "run_id", "message_id", "correlation_id", "source_agent",
        "destination_or_topic", "payload_type", "provenance",
    )
    @classmethod
    def no_blank_identifiers(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message string fields cannot be blank")
        return value

    @field_validator("created_at")
    @classmethod
    def timestamp_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        return value

    @model_validator(mode="after")
    def finite_times(self) -> "MessageEnvelope":
        if not math.isfinite(self.simulation_time) or not math.isfinite(self.expires_at):
            raise ValueError("simulation and expiry times must be finite")
        if not math.isfinite(self.confidence):
            raise ValueError("confidence must be finite")
        return self

    @property
    def topic(self) -> str:
        return self.destination_or_topic

    @property
    def ttl_seconds(self) -> float:
        return self.expires_at - self.simulation_time

    def is_valid_at(self, simulation_time: float) -> bool:
        return (
            math.isfinite(simulation_time)
            and self.simulation_time <= simulation_time <= self.expires_at
        )


def identity_from_raw(value: Any) -> tuple[str | None, str | None, str | None]:
    if isinstance(value, MessageEnvelope):
        return value.run_id, value.scenario_hash, value.message_id
    if isinstance(value, dict):
        return tuple(
            item if isinstance(item, str) and item else None
            for item in (value.get("run_id"), value.get("scenario_hash"), value.get("message_id"))
        )  # type: ignore[return-value]
    return None, None, None
