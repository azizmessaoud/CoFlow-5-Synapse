from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from collections import defaultdict

from pydantic import BaseModel, ConfigDict, Field, model_validator

from coflow5.messaging import (
    MessageEnvelope,
    MessageTransport,
    PriorityClass,
    PublishResult,
    Topic,
)

PROXY_LABEL = "SUMO/HBEFA emission proxy — not measured air quality"


class EmissionProxyObservation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    link_id: str = Field(min_length=1)
    simulation_time: float = Field(ge=0)
    co2_proxy_mg_s: float = Field(ge=0)
    nox_proxy_mg_s: float = Field(ge=0)
    stop_count: float = Field(ge=0)
    sensitive: bool
    receptor_type: str = Field(min_length=1)

    @model_validator(mode="after")
    def finite_values(self) -> "EmissionProxyObservation":
        values = (
            self.simulation_time, self.co2_proxy_mg_s,
            self.nox_proxy_mg_s, self.stop_count,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("emission proxy observations must be finite")
        return self


@dataclass(frozen=True)
class LinkDisplacement:
    link_id: str
    receptor_type: str
    sensitive: bool
    baseline_co2_mg_s: float
    observed_co2_mg_s: float
    co2_delta_mg_s: float
    baseline_nox_mg_s: float
    observed_nox_mg_s: float
    nox_delta_mg_s: float
    stop_delta: float
    classification: str
    proxy_label: str = PROXY_LABEL


class SustainabilityAdvicePayload(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_case: str = Field(min_length=1)
    signal_id: str = Field(min_length=1)
    sensitive_link_id: str = Field(min_length=1)
    requested_movement: str = Field(min_length=1)
    requested_phase_id: str = Field(min_length=1)
    co2_proxy_mg_s: float = Field(ge=0)
    nox_proxy_mg_s: float = Field(ge=0)
    stop_count: float = Field(ge=0)
    queue_length: float = Field(ge=0)
    expected_benefit_seconds: float = Field(ge=0)
    other_traffic_externality_seconds: float = Field(ge=0)
    downstream_available: bool
    proxy_source: str = Field(min_length=1)
    measured_air_quality: bool = False
    advice_expires_at: float = Field(ge=0)

    @model_validator(mode="after")
    def finite_values_and_proxy_boundary(self) -> "SustainabilityAdvicePayload":
        values = (
            self.co2_proxy_mg_s, self.nox_proxy_mg_s, self.stop_count,
            self.queue_length, self.expected_benefit_seconds,
            self.other_traffic_externality_seconds, self.advice_expires_at,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("sustainability advice must be finite")
        if "emission proxy" not in self.proxy_source.lower():
            raise ValueError("sustainability advice must be labelled an emission proxy")
        if self.measured_air_quality:
            raise ValueError("SUMO/HBEFA evidence is not measured air quality")
        return self


def _averages(
    observations: tuple[EmissionProxyObservation, ...],
) -> dict[str, tuple[float, float, float, bool, str]]:
    grouped: dict[str, list[EmissionProxyObservation]] = defaultdict(list)
    for observation in observations:
        grouped[observation.link_id].append(observation)
    values: dict[str, tuple[float, float, float, bool, str]] = {}
    for link_id, rows in grouped.items():
        receptor_types = {row.receptor_type for row in rows}
        sensitive = {row.sensitive for row in rows}
        if len(receptor_types) != 1 or len(sensitive) != 1:
            raise ValueError(f"inconsistent link metadata: {link_id}")
        count = len(rows)
        values[link_id] = (
            sum(row.co2_proxy_mg_s for row in rows) / count,
            sum(row.nox_proxy_mg_s for row in rows) / count,
            sum(row.stop_count for row in rows) / count,
            rows[0].sensitive,
            rows[0].receptor_type,
        )
    return values


def compute_link_displacement(
    baseline: tuple[EmissionProxyObservation, ...],
    observed: tuple[EmissionProxyObservation, ...], *, selected_links: set[str],
) -> tuple[LinkDisplacement, ...]:
    if not selected_links:
        raise ValueError("at least one sensitive link must be selected")
    baseline_values = _averages(baseline)
    observed_values = _averages(observed)
    missing = selected_links - baseline_values.keys() | selected_links - observed_values.keys()
    if missing:
        raise ValueError(f"selected links missing paired evidence: {sorted(missing)}")
    results: list[LinkDisplacement] = []
    for link_id in sorted(selected_links):
        base_co2, base_nox, base_stops, base_sensitive, base_type = baseline_values[link_id]
        obs_co2, obs_nox, obs_stops, obs_sensitive, obs_type = observed_values[link_id]
        if (base_sensitive, base_type) != (obs_sensitive, obs_type):
            raise ValueError(f"paired link metadata changed: {link_id}")
        if not base_sensitive:
            raise ValueError(f"selected link is not marked sensitive: {link_id}")
        co2_delta = obs_co2 - base_co2
        classification = "improved" if co2_delta < 0 else "worsened" if co2_delta > 0 else "unchanged"
        results.append(LinkDisplacement(
            link_id=link_id, receptor_type=base_type, sensitive=True,
            baseline_co2_mg_s=base_co2, observed_co2_mg_s=obs_co2,
            co2_delta_mg_s=co2_delta, baseline_nox_mg_s=base_nox,
            observed_nox_mg_s=obs_nox, nox_delta_mg_s=obs_nox - base_nox,
            stop_delta=obs_stops - base_stops, classification=classification,
        ))
    return tuple(results)


class A5SustainabilityAgent:
    """A5 publishes bounded emission-proxy advice and never actuates signals."""

    source_agent = "A5_SUSTAINABILITY"

    def __init__(self, transport: MessageTransport) -> None:
        self._transport = transport

    def publish_advice(
        self, *, run_id: str, scenario_hash: str, message_id: str,
        correlation_id: str, created_at: datetime, simulation_time: float,
        payload: SustainabilityAdvicePayload,
    ) -> PublishResult:
        if payload.advice_expires_at < simulation_time:
            raise ValueError("sustainability advice expires before publication")
        envelope = MessageEnvelope(
            run_id=run_id, scenario_hash=scenario_hash, message_id=message_id,
            correlation_id=correlation_id, source_agent=self.source_agent,
            destination_or_topic=Topic.ECO.value, created_at=created_at,
            simulation_time=simulation_time, expires_at=payload.advice_expires_at,
            priority_class=PriorityClass.SUSTAINABILITY, confidence=1.0,
            schema_version=1, payload_type="sustainability_advice",
            payload=payload.model_dump(mode="json"),
            provenance="a5-link-emission-proxy-advice-v1",
        )
        return self._transport.publish(envelope, valid_at=simulation_time)
