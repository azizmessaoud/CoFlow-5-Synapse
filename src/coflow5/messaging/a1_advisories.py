from __future__ import annotations

import math
from dataclasses import dataclass

from coflow5.control.max_pressure import AdvisoryRequest
from coflow5.messaging.board import MessageTransport
from coflow5.messaging.envelope import MessageDisposition, Topic


@dataclass(frozen=True)
class A1AdvisoryRead:
    disposition: MessageDisposition
    advisories: tuple[AdvisoryRequest, ...]
    transport_error: str | None = None


def read_a1_advisories(
    transport: MessageTransport,
    *,
    run_id: str,
    scenario_hash: str,
    signal_id: str,
    valid_at: float,
) -> A1AdvisoryRead:
    """Translate valid request payloads; any board failure means local-only control."""
    try:
        result = transport.read(
            Topic.REQUESTS.value,
            valid_at=valid_at,
            run_id=run_id,
            scenario_hash=scenario_hash,
        )
    except Exception as exc:
        detail = f"{type(exc).__name__}: {exc}" if str(exc) else type(exc).__name__
        return A1AdvisoryRead(MessageDisposition.UNAVAILABLE, (), detail)
    if result.disposition in {
        MessageDisposition.EMPTY,
        MessageDisposition.UNAVAILABLE,
        MessageDisposition.MALFORMED,
        MessageDisposition.UNSUPPORTED,
    }:
        return A1AdvisoryRead(result.disposition, ())

    advisories: list[AdvisoryRequest] = []
    for envelope in result.messages:
        if envelope.payload_type != "priority_request":
            continue
        requested_phase = envelope.payload.get("requested_phase_id")
        requested_signal = envelope.payload.get("signal_id")
        weight = envelope.payload.get("weight", envelope.confidence)
        if (
            not isinstance(requested_phase, str)
            or requested_signal != signal_id
            or not isinstance(weight, (int, float))
            or isinstance(weight, bool)
            or not math.isfinite(float(weight))
            or not 0 <= float(weight) <= 1
        ):
            continue
        advisories.append(AdvisoryRequest(
            message_id=envelope.message_id,
            run_id=envelope.run_id,
            signal_id=signal_id,
            requested_phase_id=requested_phase,
            source=envelope.source_agent,
            valid_from=envelope.simulation_time,
            expires_at=envelope.expires_at,
            weight=float(weight),
        ))
    return A1AdvisoryRead(result.disposition, tuple(advisories))
