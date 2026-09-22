from __future__ import annotations

from datetime import datetime, timezone

from hypothesis import given, strategies as st

from coflow5.messaging import InProcessMessageBoard, MessageDisposition, MessageEnvelope

RUN_ID = "run-board-properties"
SCENARIO_HASH = "sha256:" + "a" * 64


def _message(
    message_id: str,
    *,
    simulation_time: float = 10.0,
    expires_at: float = 20.0,
    correlation_id: str = "window-1",
    topic: str = "requests",
    payload: dict | None = None,
) -> MessageEnvelope:
    return MessageEnvelope(
        run_id=RUN_ID,
        scenario_hash=SCENARIO_HASH,
        message_id=message_id,
        correlation_id=correlation_id,
        source_agent="A2_EMERGENCY",
        destination_or_topic=topic,
        created_at=datetime.now(timezone.utc),
        simulation_time=simulation_time,
        expires_at=expires_at,
        priority_class="emergency",
        confidence=0.8,
        schema_version=1,
        payload_type="priority_request",
        payload=payload or {"signal_id": "J0", "requested_phase_id": "NS_GREEN"},
        provenance="property-test",
    )


@given(st.integers(min_value=2, max_value=20))
def test_duplicate_message_ids_are_idempotent_and_use_one_storage_slot(repeats: int) -> None:
    board = InProcessMessageBoard(capacity=4)
    message = _message("same-id")
    assert board.publish(message).disposition is MessageDisposition.ACCEPTED
    results = [board.publish(message).disposition for _ in range(repeats)]
    assert set(results) == {MessageDisposition.DUPLICATE}
    assert board.storage_size == 1
    assert len(board.read("requests", valid_at=10.0).messages) == 1


@given(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
def test_valid_at_reads_include_expiry_boundary_then_expire(now: float) -> None:
    board = InProcessMessageBoard()
    message = _message("ttl", simulation_time=now, expires_at=now + 5.0)
    assert board.publish(message, valid_at=now).accepted
    assert board.read("requests", valid_at=now + 5.0).messages == (message,)
    expired = board.read("requests", valid_at=now + 5.001)
    assert expired.disposition is MessageDisposition.EMPTY
    assert expired.messages == ()
    assert MessageDisposition.EXPIRED in {entry.disposition for entry in board.audit_log}


def test_every_required_rejection_has_an_explicit_disposition() -> None:
    board = InProcessMessageBoard()
    accepted = _message("accepted")
    assert board.publish(accepted).disposition is MessageDisposition.ACCEPTED
    assert board.publish(accepted).disposition is MessageDisposition.DUPLICATE

    expired = _message("expired", simulation_time=0.0, expires_at=1.0, correlation_id="expired")
    assert board.publish(expired, valid_at=2.0).disposition is MessageDisposition.EXPIRED

    malformed = accepted.model_dump(mode="python") | {"message_id": "malformed", "confidence": 2.0}
    assert board.publish(malformed).disposition is MessageDisposition.MALFORMED

    unsupported = _message("unsupported", correlation_id="unsupported", topic="unknown")
    assert board.publish(unsupported).disposition is MessageDisposition.UNSUPPORTED

    contradictory = _message(
        "contradictory", payload={"signal_id": "J0", "requested_phase_id": "NS_YELLOW"}
    )
    assert board.publish(contradictory).disposition is MessageDisposition.CONTRADICTORY

    out_of_order = _message("old", simulation_time=9.0, correlation_id="older")
    assert board.publish(out_of_order).disposition is MessageDisposition.OUT_OF_ORDER

    board.set_available(False)
    assert board.read("requests", valid_at=10.0).disposition is MessageDisposition.UNAVAILABLE
    board.set_available(True)
    assert board.read("health", valid_at=10.0).disposition is MessageDisposition.EMPTY


def test_storage_is_bounded_and_reads_are_priority_then_time_deterministic() -> None:
    board = InProcessMessageBoard(capacity=2)
    for index in range(3):
        assert board.publish(
            _message(
                f"bounded-{index}",
                simulation_time=10.0 + index,
                expires_at=30.0,
                correlation_id=f"window-{index}",
            )
        ).accepted
    assert board.storage_size == board.capacity == 2
    result = board.read("requests", valid_at=20.0)
    assert [message.message_id for message in result.messages] == ["bounded-2", "bounded-1"]
    assert MessageDisposition.EVICTED in {entry.disposition for entry in board.audit_log}



def test_duplicate_id_remains_rejected_after_storage_and_metadata_pressure() -> None:
    board = InProcessMessageBoard(capacity=1)
    original = _message("dup-old", correlation_id="original")
    assert board.publish(original).disposition is MessageDisposition.ACCEPTED

    for index in range(1000):
        result = board.publish(
            _message(
                f"pressure-{index}",
                correlation_id=f"pressure-window-{index}",
                simulation_time=10.0 + index,
                expires_at=2000.0,
            )
        )
        assert result.disposition in {
            MessageDisposition.ACCEPTED,
            MessageDisposition.DUPLICATE,
        }

    assert board.storage_size == 1
    sizes = board.metadata_sizes
    assert all(size <= board.metadata_capacity for size in sizes.values())
    assert board.publish(original).disposition is MessageDisposition.DUPLICATE
    conflicting_reuse = _message(
        "dup-old",
        correlation_id="conflicting-reuse",
        payload={"signal_id": "J0", "requested_phase_id": "EW_GREEN"},
    )
    assert board.publish(conflicting_reuse).disposition is MessageDisposition.DUPLICATE


def test_publication_from_future_relative_to_valid_at_is_out_of_order() -> None:
    board = InProcessMessageBoard()
    future = _message("future", simulation_time=20.0, expires_at=30.0)
    result = board.publish(future, valid_at=10.0)
    assert result.disposition is MessageDisposition.OUT_OF_ORDER
    assert result.accepted is False
    assert "future" in result.record.reason
    assert board.storage_size == 0
