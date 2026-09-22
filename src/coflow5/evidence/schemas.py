from __future__ import annotations

from datetime import datetime
from typing import Literal

import pyarrow as pa
from pydantic import BaseModel, ConfigDict, Field, field_validator

HASH_PATTERN = r"^sha256:[0-9a-f]{64}$"


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class ArtifactReference(FrozenModel):
    path: str
    sha256: str = Field(pattern=HASH_PATTERN)
    bytes: int = Field(ge=0)
    rows: int = Field(ge=0)
    schema_name: str
    schema_version: int = Field(ge=1)

    @field_validator("path")
    @classmethod
    def local_artifact_name(cls, value: str) -> str:
        if not value or "/" in value or "\\" in value or value in {".", ".."}:
            raise ValueError("artifact path must be one local file name")
        return value


class VersionRecord(FrozenModel):
    python: str
    sumo: str
    traci: str
    coflow5: str
    duckdb: str
    pyarrow: str
    pydantic: str


class RunTimings(FrozenModel):
    started_at: datetime
    finished_at: datetime
    wall_seconds: float = Field(ge=0)
    simulation_begin: float = Field(ge=0)
    simulation_end: float = Field(ge=0)
    simulation_steps: int = Field(ge=0)


class RunManifest(FrozenModel):
    schema_version: Literal[1]
    run_id: str = Field(min_length=1)
    scenario_hash: str = Field(pattern=HASH_PATTERN)
    configuration_hash: str = Field(pattern=HASH_PATTERN)
    scenario_files: tuple[str, ...]
    versions: VersionRecord
    seeds: dict[str, int]
    status: Literal["completed", "failed", "invalid"]
    failure_reason: str | None = None
    timings: RunTimings
    backend: Literal["traci"]
    controller: str
    source_revision: str | None
    source_hashes: dict[str, str] = Field(default_factory=dict)
    native_command: tuple[str, ...]
    sumo_command: tuple[str, ...] | None = None
    artifact_references: tuple[ArtifactReference, ...]
    finalized_at: datetime
    immutable: Literal[True]


class EvidenceRow(FrozenModel):
    schema_version: Literal[1]
    run_id: str = Field(min_length=1)
    scenario_hash: str = Field(pattern=HASH_PATTERN)


class StateRecord(EvidenceRow):
    simulation_time: float = Field(ge=0)
    min_expected_vehicles: int = Field(ge=0)
    loaded_vehicles: int = Field(ge=0)
    departed_vehicles: int = Field(ge=0)
    arrived_vehicles: int = Field(ge=0)
    active_vehicles: int = Field(ge=0)
    halting_vehicles: int = Field(ge=0)
    mean_speed_mps: float = Field(ge=0)
    total_waiting_seconds: float = Field(ge=0)
    starting_teleports: int = Field(ge=0)
    ending_teleports: int = Field(ge=0)


class MessageRecord(EvidenceRow):
    message_id: str = Field(min_length=1)
    record_kind: Literal["message", "disposition"]
    simulation_time: float = Field(ge=0)
    created_at: datetime
    source: str
    topic: str
    payload_type: str
    payload_json: str
    disposition: str | None = None


class EventRecord(EvidenceRow):
    event_id: str = Field(min_length=1)
    event_kind: Literal["decision", "fault", "transition"]
    simulation_time: float = Field(ge=0)
    recorded_at: datetime
    reason_code: str
    considered_message_ids: tuple[str, ...] = ()
    selected_action: str | None = None
    fault_code: str | None = None
    previous_mode: str | None = None
    next_mode: str | None = None
    provenance: str


class DecisionEvent(EventRecord):
    event_kind: Literal["decision"]
    selected_action: str


class FaultEvent(EventRecord):
    event_kind: Literal["fault"]
    fault_code: str


class TransitionEvent(EventRecord):
    event_kind: Literal["transition"]
    previous_mode: str
    next_mode: str


class TripRecord(EvidenceRow):
    trip_id: str = Field(min_length=1)
    depart: float = Field(ge=0)
    arrival: float
    duration: float = Field(ge=0)
    route_length_m: float = Field(ge=0)
    waiting_time_s: float = Field(ge=0)
    time_loss_s: float = Field(ge=0)
    depart_delay_s: float = Field(ge=0)
    unfinished: bool


class RunKpiRecord(EvidenceRow):
    completed_trips: int = Field(ge=0)
    unfinished_trips: int = Field(ge=0)
    mean_duration_s: float = Field(ge=0)
    p95_duration_s: float = Field(ge=0)
    max_duration_s: float = Field(ge=0)
    mean_waiting_time_s: float = Field(ge=0)
    total_time_loss_s: float = Field(ge=0)
    simulation_steps: int = Field(ge=0)
    max_active_vehicles: int = Field(ge=0)
    teleport_events: int = Field(ge=0)


STATE_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()), ("scenario_hash", pa.string()),
    ("simulation_time", pa.float64()), ("min_expected_vehicles", pa.int64()),
    ("loaded_vehicles", pa.int64()), ("departed_vehicles", pa.int64()),
    ("arrived_vehicles", pa.int64()), ("active_vehicles", pa.int64()),
    ("halting_vehicles", pa.int64()), ("mean_speed_mps", pa.float64()),
    ("total_waiting_seconds", pa.float64()), ("starting_teleports", pa.int64()),
    ("ending_teleports", pa.int64()),
])

MESSAGE_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()), ("scenario_hash", pa.string()),
    ("message_id", pa.string()), ("record_kind", pa.string()),
    ("simulation_time", pa.float64()), ("created_at", pa.string()), ("source", pa.string()),
    ("topic", pa.string()), ("payload_type", pa.string()), ("payload_json", pa.string()),
    ("disposition", pa.string()),
])

EVENT_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()), ("scenario_hash", pa.string()),
    ("event_id", pa.string()), ("event_kind", pa.string()),
    ("simulation_time", pa.float64()), ("recorded_at", pa.string()),
    ("reason_code", pa.string()), ("considered_message_ids", pa.list_(pa.string())),
    ("selected_action", pa.string()), ("fault_code", pa.string()),
    ("previous_mode", pa.string()), ("next_mode", pa.string()), ("provenance", pa.string()),
])

TRIP_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()), ("scenario_hash", pa.string()),
    ("trip_id", pa.string()), ("depart", pa.float64()), ("arrival", pa.float64()),
    ("duration", pa.float64()), ("route_length_m", pa.float64()),
    ("waiting_time_s", pa.float64()), ("time_loss_s", pa.float64()),
    ("depart_delay_s", pa.float64()), ("unfinished", pa.bool_()),
])

KPI_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()), ("scenario_hash", pa.string()),
    ("completed_trips", pa.int64()), ("unfinished_trips", pa.int64()),
    ("mean_duration_s", pa.float64()), ("p95_duration_s", pa.float64()),
    ("max_duration_s", pa.float64()), ("mean_waiting_time_s", pa.float64()),
    ("total_time_loss_s", pa.float64()), ("simulation_steps", pa.int64()),
    ("max_active_vehicles", pa.int64()), ("teleport_events", pa.int64()),
])

PARQUET_SCHEMAS = {
    "state.parquet": ("state", STATE_SCHEMA, StateRecord),
    "messages.parquet": ("message", MESSAGE_SCHEMA, MessageRecord),
    "decision_events.parquet": ("event", EVENT_SCHEMA, EventRecord),
    "trips.parquet": ("trip", TRIP_SCHEMA, TripRecord),
    "run_kpis.parquet": ("run_kpi", KPI_SCHEMA, RunKpiRecord),
}
