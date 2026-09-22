from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from coflow5.messaging import (
    InProcessMessageBoard,
    MessageEnvelope,
    MessageTransport,
    PriorityClass,
    SUPPORTED_TOPICS,
)

RUN_ID = "run-envelope-contract"
SCENARIO_HASH = "sha256:" + "6" * 64


def _values() -> dict:
    return {
        "run_id": RUN_ID,
        "scenario_hash": SCENARIO_HASH,
        "message_id": "message-1",
        "correlation_id": "decision-window-1",
        "source_agent": "A2_EMERGENCY",
        "destination_or_topic": "requests",
        "created_at": datetime.now(timezone.utc),
        "simulation_time": 10.0,
        "expires_at": 15.0,
        "priority_class": "emergency",
        "confidence": 0.9,
        "schema_version": 1,
        "payload_type": "priority_request",
        "payload": {"signal_id": "J0", "requested_phase_id": "NS_GREEN"},
        "provenance": "test-fixture",
    }


def test_message_envelope_has_exact_canonical_fields_and_is_immutable() -> None:
    expected = {
        "run_id", "scenario_hash", "message_id", "correlation_id", "source_agent",
        "destination_or_topic", "created_at", "simulation_time", "expires_at",
        "priority_class", "confidence", "schema_version", "payload_type", "payload",
        "provenance",
    }
    assert set(MessageEnvelope.model_fields) == expected
    envelope = MessageEnvelope(**_values())
    assert envelope.ttl_seconds == 5.0
    assert envelope.is_valid_at(15.0)
    assert envelope.priority_class is PriorityClass.EMERGENCY
    with pytest.raises(ValidationError):
        envelope.message_id = "replacement"  # type: ignore[misc]


def test_payload_is_deeply_immutable_copied_and_board_safe() -> None:
    source = {
        "signal_id": "J0",
        "requested_phase_id": "NS_GREEN",
        "nested": {"lanes": ["N_in_0"]},
    }
    envelope = MessageEnvelope(**(_values() | {"payload": source}))
    source["requested_phase_id"] = "CALLER_MUTATION"
    source["nested"]["lanes"].append("E_in_0")  # type: ignore[index,union-attr]

    assert envelope.payload["requested_phase_id"] == "NS_GREEN"
    assert envelope.payload["nested"]["lanes"] == ("N_in_0",)  # type: ignore[index]
    from coflow5.messaging import thaw_json
    thawed = thaw_json(envelope.payload)
    assert thawed == {
        "signal_id": "J0",
        "requested_phase_id": "NS_GREEN",
        "nested": {"lanes": ["N_in_0"]},
    }
    thawed["nested"]["lanes"].append("LOCAL_SERIALIZATION_COPY")  # type: ignore[index,union-attr]
    assert envelope.payload["nested"]["lanes"] == ("N_in_0",)  # type: ignore[index]
    with pytest.raises(TypeError):
        envelope.payload["requested_phase_id"] = "ILLEGAL_MUTATION"  # type: ignore[index]
    with pytest.raises(TypeError):
        envelope.payload["nested"]["lanes"][0] = "ILLEGAL_MUTATION"  # type: ignore[index]

    board = InProcessMessageBoard()
    published = board.publish(envelope)
    assert published.accepted
    assert published.message is not None
    assert published.message is not envelope
    with pytest.raises(TypeError):
        published.message.payload["requested_phase_id"] = "ILLEGAL_MUTATION"  # type: ignore[index]
    stored = board.read("requests", valid_at=10.0).messages[0]
    assert stored.payload["requested_phase_id"] == "NS_GREEN"


def test_message_envelope_rejects_extra_blank_naive_or_unbounded_values() -> None:
    for patch in (
        {"extra": "not-canonical"},
        {"message_id": " "},
        {"created_at": datetime.now()},
        {"confidence": 1.01},
        {"simulation_time": float("inf")},
    ):
        values = _values() | patch
        with pytest.raises(ValidationError):
            MessageEnvelope(**values)


def test_transport_protocol_and_required_topics_are_stable() -> None:
    board = InProcessMessageBoard(capacity=4)
    assert isinstance(board, MessageTransport)
    assert SUPPORTED_TOPICS == {
        "state", "forecast", "alerts", "eco", "requests", "replies", "health"
    }
