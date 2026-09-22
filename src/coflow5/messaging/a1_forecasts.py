from __future__ import annotations

import math
from dataclasses import dataclass

from coflow5.messaging.board import MessageTransport
from coflow5.messaging.envelope import MessageDisposition, Topic


@dataclass(frozen=True)
class ForecastAdvisory:
    message_id: str
    run_id: str
    scenario_hash: str
    signal_id: str
    target: str
    source_time: float
    horizon_seconds: float
    predicted_value: float
    confidence: float
    model_version: str
    classification: str
    expires_at: float


@dataclass(frozen=True)
class A1ForecastRead:
    disposition: MessageDisposition
    forecasts: tuple[ForecastAdvisory, ...]
    transport_error: str | None = None

    @property
    def local_only(self) -> bool:
        return not self.forecasts


def read_a1_forecasts(
    transport: MessageTransport, *, run_id: str, scenario_hash: str,
    signal_id: str, valid_at: float,
) -> A1ForecastRead:
    """Read valid A4 forecasts; any failure or bad row means local-only control."""
    try:
        result = transport.read(
            Topic.FORECAST.value, valid_at=valid_at,
            run_id=run_id, scenario_hash=scenario_hash,
        )
    except Exception as exc:
        detail = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
        return A1ForecastRead(MessageDisposition.UNAVAILABLE, (), detail)
    if result.disposition in {
        MessageDisposition.EMPTY, MessageDisposition.UNAVAILABLE,
        MessageDisposition.MALFORMED, MessageDisposition.UNSUPPORTED,
    }:
        return A1ForecastRead(result.disposition, ())
    forecasts: list[ForecastAdvisory] = []
    for envelope in result.messages:
        payload = envelope.payload
        numeric = (
            payload.get("source_time"), payload.get("horizon_seconds"),
            payload.get("predicted_value"), payload.get("confidence"),
        )
        if (
            envelope.payload_type != "situation_forecast"
            or payload.get("signal_id") != signal_id
            or any(not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(float(value)) for value in numeric)
            or float(payload["source_time"]) > valid_at
            or not isinstance(payload.get("target"), str)
            or not isinstance(payload.get("model_version"), str)
            or not isinstance(payload.get("classification"), str)
        ):
            continue
        forecasts.append(ForecastAdvisory(
            message_id=envelope.message_id, run_id=envelope.run_id,
            scenario_hash=envelope.scenario_hash, signal_id=signal_id,
            target=str(payload["target"]), source_time=float(payload["source_time"]),
            horizon_seconds=float(payload["horizon_seconds"]),
            predicted_value=float(payload["predicted_value"]),
            confidence=float(payload["confidence"]),
            model_version=str(payload["model_version"]),
            classification=str(payload["classification"]), expires_at=envelope.expires_at,
        ))
    forecasts.sort(key=lambda item: (item.target, item.message_id))
    return A1ForecastRead(result.disposition, tuple(forecasts))
