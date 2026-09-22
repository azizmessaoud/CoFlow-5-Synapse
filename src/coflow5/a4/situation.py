from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from coflow5.messaging import (
    MessageEnvelope,
    MessageTransport,
    PriorityClass,
    PublishResult,
    Topic,
)


class TimeSeriesPoint(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    simulation_time: float = Field(ge=0)
    value: float

    @model_validator(mode="after")
    def finite_values(self) -> "TimeSeriesPoint":
        if not math.isfinite(self.simulation_time) or not math.isfinite(self.value):
            raise ValueError("time-series values must be finite")
        return self


@dataclass(frozen=True)
class ChronologicalSplit:
    train: tuple[TimeSeriesPoint, ...]
    validation: tuple[TimeSeriesPoint, ...]
    test: tuple[TimeSeriesPoint, ...]


@dataclass(frozen=True)
class ForecastScore:
    model_name: str
    model_version: str
    status: str
    validation_mae: float | None
    fit_end_time: float
    evaluation_start_time: float
    evaluation_end_time: float


@dataclass(frozen=True)
class ForecastModelSelection:
    selected_model: str
    selected_model_version: str
    lightgbm_accepted: bool
    scores: tuple[ForecastScore, ...]


class SituationClassification(str, Enum):
    NORMAL = "normal"
    DETECTED_ANOMALY = "detected_anomaly"
    LIKELY_INCIDENT = "likely_incident"
    CONGESTION = "congestion"
    STALE_DATA = "stale_data"
    INSUFFICIENT_DATA = "insufficient_data"


class SituationEvidence(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source_time: float = Field(ge=0)
    current_time: float = Field(ge=0)
    sample_count: int = Field(ge=0)
    residual: float
    ewma: float
    cusum: float
    speed_ratio: float = Field(ge=0)
    occupancy: float = Field(ge=0, le=1)
    stale_after_seconds: float = Field(default=5, gt=0)
    minimum_samples: int = Field(default=5, ge=1)
    residual_threshold: float = Field(default=2, gt=0)
    ewma_threshold: float = Field(default=2, gt=0)
    cusum_threshold: float = Field(default=5, gt=0)

    @model_validator(mode="after")
    def finite_values_and_time_order(self) -> "SituationEvidence":
        numeric = (
            self.source_time, self.current_time, self.residual, self.ewma, self.cusum,
            self.speed_ratio, self.occupancy, self.stale_after_seconds,
            self.residual_threshold, self.ewma_threshold, self.cusum_threshold,
        )
        if not all(math.isfinite(value) for value in numeric):
            raise ValueError("situation evidence must be finite")
        if self.current_time < self.source_time:
            raise ValueError("current_time cannot precede source_time")
        return self


class ForecastPayload(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    scenario_case: str = Field(min_length=1)
    signal_id: str = Field(min_length=1)
    target: str = Field(min_length=1)
    source_time: float = Field(ge=0)
    horizon_seconds: float = Field(gt=0)
    predicted_value: float
    confidence: float = Field(ge=0, le=1)
    model_name: str = Field(min_length=1)
    model_version: str = Field(min_length=1)
    expires_at: float = Field(ge=0)
    classification: SituationClassification
    residual: float
    evidence_basis: str = Field(min_length=1)

    @model_validator(mode="after")
    def finite_values_and_expiry(self) -> "ForecastPayload":
        numeric = (
            self.source_time, self.horizon_seconds, self.predicted_value,
            self.confidence, self.expires_at, self.residual,
        )
        if not all(math.isfinite(value) for value in numeric):
            raise ValueError("forecast evidence must be finite")
        if self.expires_at < self.source_time:
            raise ValueError("forecast expiry cannot precede source time")
        return self


def chronological_split(
    points: tuple[TimeSeriesPoint, ...], *, train_fraction: float = 0.6,
    validation_fraction: float = 0.2,
) -> ChronologicalSplit:
    if not math.isfinite(train_fraction) or not math.isfinite(validation_fraction):
        raise ValueError("split fractions must be finite")
    if not 0 < train_fraction < 1 or not 0 < validation_fraction < 1:
        raise ValueError("split fractions must be between zero and one")
    if train_fraction + validation_fraction >= 1:
        raise ValueError("test split must be non-empty")
    if len(points) < 10:
        raise ValueError("at least ten time-series points are required")
    ordered = tuple(sorted(points, key=lambda point: point.simulation_time))
    times = [point.simulation_time for point in ordered]
    if len(set(times)) != len(times):
        raise ValueError("time-series timestamps must be unique")
    train_end = int(len(ordered) * train_fraction)
    validation_end = train_end + int(len(ordered) * validation_fraction)
    if train_end < 2 or validation_end <= train_end or validation_end >= len(ordered):
        raise ValueError("split fractions create an empty or unfit partition")
    return ChronologicalSplit(
        train=ordered[:train_end],
        validation=ordered[train_end:validation_end],
        test=ordered[validation_end:],
    )


def _mae(actual: tuple[float, ...], predicted: tuple[float, ...]) -> float:
    return sum(abs(a - p) for a, p in zip(actual, predicted, strict=True)) / len(actual)


def _fit_autoregression(train: tuple[TimeSeriesPoint, ...]) -> tuple[float, float]:
    x = [point.value for point in train[:-1]]
    y = [point.value for point in train[1:]]
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    denominator = sum((value - x_mean) ** 2 for value in x)
    slope = 0.0 if denominator == 0 else sum(
        (x_value - x_mean) * (y_value - y_mean)
        for x_value, y_value in zip(x, y, strict=True)
    ) / denominator
    return y_mean - slope * x_mean, slope


def evaluate_forecast_ladder(
    split: ChronologicalSplit, *, lightgbm_validation_mae: float | None = None,
) -> ForecastModelSelection:
    previous = (split.train[-1], *split.validation[:-1])
    actual = tuple(point.value for point in split.validation)
    persistence_predictions = tuple(point.value for point in previous)
    persistence_mae = _mae(actual, persistence_predictions)
    intercept, slope = _fit_autoregression(split.train)
    simple_predictions = tuple(intercept + slope * point.value for point in previous)
    simple_mae = _mae(actual, simple_predictions)
    fit_end = split.train[-1].simulation_time
    evaluation_start = split.validation[0].simulation_time
    evaluation_end = split.validation[-1].simulation_time
    scores = [
        ForecastScore("persistence", "persistence-v1", "evaluated", persistence_mae, fit_end, evaluation_start, evaluation_end),
        ForecastScore("simple_autoregression", "simple-ar-v1", "evaluated", simple_mae, fit_end, evaluation_start, evaluation_end),
    ]
    selected = min(
        scores,
        key=lambda score: (
            score.validation_mae if score.validation_mae is not None else math.inf,
            score.model_name,
        ),
    )
    lightgbm_accepted = False
    if lightgbm_validation_mae is None:
        scores.append(ForecastScore(
            "lightgbm", "not-installed", "not_available_not_accepted", None,
            fit_end, evaluation_start, evaluation_end,
        ))
    else:
        if not math.isfinite(lightgbm_validation_mae) or lightgbm_validation_mae < 0:
            raise ValueError("LightGBM validation MAE must be finite and non-negative")
        candidate = ForecastScore(
            "lightgbm", "external-candidate", "evaluated_candidate",
            lightgbm_validation_mae, fit_end, evaluation_start, evaluation_end,
        )
        scores.append(candidate)
        if lightgbm_validation_mae < float(selected.validation_mae):
            selected = candidate
            lightgbm_accepted = True
    return ForecastModelSelection(
        selected_model=selected.model_name,
        selected_model_version=selected.model_version,
        lightgbm_accepted=lightgbm_accepted,
        scores=tuple(scores),
    )


class A4SituationAgent:
    """A4 publishes bounded forecasts and alerts; it has no actuation capability."""

    source_agent = "A4_SITUATION"

    def __init__(self, transport: MessageTransport) -> None:
        self._transport = transport

    @staticmethod
    def classify(evidence: SituationEvidence) -> SituationClassification:
        if evidence.sample_count < evidence.minimum_samples:
            return SituationClassification.INSUFFICIENT_DATA
        if evidence.current_time - evidence.source_time > evidence.stale_after_seconds:
            return SituationClassification.STALE_DATA
        anomaly = (
            abs(evidence.residual) >= evidence.residual_threshold
            or abs(evidence.ewma) >= evidence.ewma_threshold
            or abs(evidence.cusum) >= evidence.cusum_threshold
        )
        if not anomaly:
            return SituationClassification.NORMAL
        if evidence.speed_ratio <= 0.4 and evidence.occupancy < 0.8:
            return SituationClassification.LIKELY_INCIDENT
        if evidence.occupancy >= 0.8:
            return SituationClassification.CONGESTION
        return SituationClassification.DETECTED_ANOMALY

    def publish_forecast(
        self, *, run_id: str, scenario_hash: str, message_id: str,
        correlation_id: str, created_at: datetime, simulation_time: float,
        payload: ForecastPayload,
    ) -> PublishResult:
        if payload.source_time > simulation_time:
            raise ValueError("forecast source time cannot be in the future")
        if payload.expires_at < simulation_time:
            raise ValueError("forecast expires before publication")
        envelope = MessageEnvelope(
            run_id=run_id, scenario_hash=scenario_hash, message_id=message_id,
            correlation_id=correlation_id, source_agent=self.source_agent,
            destination_or_topic=Topic.FORECAST.value, created_at=created_at,
            simulation_time=simulation_time, expires_at=payload.expires_at,
            priority_class=PriorityClass.GENERAL_FLOW, confidence=payload.confidence,
            schema_version=1, payload_type="situation_forecast",
            payload=payload.model_dump(mode="json"),
            provenance="a4-chronological-forecast-ladder-v1",
        )
        return self._transport.publish(envelope, valid_at=simulation_time)

    def publish_alert(
        self, *, run_id: str, scenario_hash: str, message_id: str,
        correlation_id: str, created_at: datetime, simulation_time: float,
        payload: ForecastPayload,
    ) -> PublishResult:
        if payload.classification is SituationClassification.NORMAL:
            raise ValueError("normal evidence is a forecast, not an alert")
        if payload.source_time > simulation_time or payload.expires_at < simulation_time:
            raise ValueError("alert time bounds are invalid")
        envelope = MessageEnvelope(
            run_id=run_id, scenario_hash=scenario_hash, message_id=message_id,
            correlation_id=correlation_id, source_agent=self.source_agent,
            destination_or_topic=Topic.ALERTS.value, created_at=created_at,
            simulation_time=simulation_time, expires_at=payload.expires_at,
            priority_class=PriorityClass.GENERAL_FLOW, confidence=payload.confidence,
            schema_version=1, payload_type="situation_alert",
            payload=payload.model_dump(mode="json"),
            provenance="a4-ewma-cusum-classification-v1",
        )
        return self._transport.publish(envelope, valid_at=simulation_time)
