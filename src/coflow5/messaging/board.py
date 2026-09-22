from __future__ import annotations

import hashlib
import json
import math
from collections import OrderedDict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Mapping, Protocol, runtime_checkable

from pydantic import ValidationError

from coflow5.messaging.envelope import (
    PRIORITY_RANK,
    SUPPORTED_TOPICS,
    MessageDisposition,
    MessageEnvelope,
    identity_from_raw,
)


@dataclass(frozen=True)
class DispositionRecord:
    sequence: int
    disposition: MessageDisposition
    recorded_at: datetime
    reason: str
    run_id: str | None
    scenario_hash: str | None
    message_id: str | None
    topic: str | None
    simulation_time: float | None


@dataclass(frozen=True)
class PublishResult:
    disposition: MessageDisposition
    accepted: bool
    message: MessageEnvelope | None
    record: DispositionRecord


@dataclass(frozen=True)
class ReadResult:
    disposition: MessageDisposition
    messages: tuple[MessageEnvelope, ...]
    record: DispositionRecord

    @property
    def available(self) -> bool:
        return self.disposition is not MessageDisposition.UNAVAILABLE


@runtime_checkable
class MessageTransport(Protocol):
    """Transport boundary used by agents; no concrete broker leaks through it."""

    def publish(
        self,
        message: MessageEnvelope | Mapping[str, Any],
        *,
        valid_at: float | None = None,
    ) -> PublishResult: ...

    def read(
        self,
        topic: str,
        *,
        valid_at: float,
        run_id: str | None = None,
        scenario_hash: str | None = None,
    ) -> ReadResult: ...


Transport = MessageTransport


class InProcessMessageBoard:
    """Bounded deterministic board with idempotent publication and TTL reads."""

    def __init__(
        self,
        capacity: int = 256,
        *,
        audit_capacity: int | None = None,
        metadata_capacity: int | None = None,
        idempotency_bits: int | None = None,
        supported_schema_versions: frozenset[int] = frozenset({1}),
    ) -> None:
        if capacity < 1:
            raise ValueError("capacity must be at least one")
        if audit_capacity is not None and audit_capacity < 1:
            raise ValueError("audit_capacity must be at least one")
        if metadata_capacity is not None and metadata_capacity < 1:
            raise ValueError("metadata_capacity must be at least one")
        if idempotency_bits is not None and idempotency_bits < 64:
            raise ValueError("idempotency_bits must be at least 64")
        if not supported_schema_versions:
            raise ValueError("at least one schema version must be supported")
        self._capacity = capacity
        self._metadata_capacity = metadata_capacity or max(capacity * 4, 32)
        self._idempotency_bits = idempotency_bits or max(65_536, capacity * 128)
        self._idempotency_ledger = bytearray((self._idempotency_bits + 7) // 8)
        self._messages: OrderedDict[str, MessageEnvelope] = OrderedDict()
        self._seen: OrderedDict[str, str] = OrderedDict()
        self._latest_stream_time: OrderedDict[tuple[str, str, str, str, str], float] = OrderedDict()
        self._correlations: OrderedDict[
            tuple[str, str, str, str, str, float, str], str
        ] = OrderedDict()
        self._audit: deque[DispositionRecord] = deque(
            maxlen=audit_capacity or max(64, capacity * 8)
        )
        self._supported_schema_versions = supported_schema_versions
        self._available = True
        self._sequence = 0
        self._lock = RLock()

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def storage_size(self) -> int:
        with self._lock:
            return len(self._messages)

    @property
    def metadata_capacity(self) -> int:
        return self._metadata_capacity

    @property
    def metadata_sizes(self) -> dict[str, int]:
        with self._lock:
            return {
                "exact_id_fingerprints": len(self._seen),
                "latest_stream_times": len(self._latest_stream_time),
                "correlations": len(self._correlations),
            }

    @property
    def available(self) -> bool:
        with self._lock:
            return self._available

    @property
    def audit_log(self) -> tuple[DispositionRecord, ...]:
        with self._lock:
            return tuple(self._audit)

    def set_available(self, available: bool) -> None:
        with self._lock:
            self._available = bool(available)

    def inject_unavailable(self, unavailable: bool = True) -> None:
        self.set_available(not unavailable)

    def publish(
        self,
        message: MessageEnvelope | Mapping[str, Any],
        *,
        valid_at: float | None = None,
    ) -> PublishResult:
        with self._lock:
            envelope = self._validate(message)
            if envelope is None:
                run_id, scenario_hash, message_id = identity_from_raw(message)
                record = self._record(
                    MessageDisposition.MALFORMED,
                    "envelope validation failed",
                    run_id=run_id,
                    scenario_hash=scenario_hash,
                    message_id=message_id,
                )
                return PublishResult(MessageDisposition.MALFORMED, False, None, record)

            if not self._available:
                return self._publish_rejection(
                    envelope, MessageDisposition.UNAVAILABLE, "transport is unavailable"
                )

            fingerprint = self._fingerprint(envelope)
            if self._id_was_seen(envelope.message_id):
                remembered = self._seen.get(envelope.message_id)
                detail = (
                    "message_id already processed idempotently"
                    if remembered is None or remembered == fingerprint
                    else "message_id already processed; conflicting duplicate ignored"
                )
                return self._publish_rejection(envelope, MessageDisposition.DUPLICATE, detail)

            self._remember_id(envelope.message_id, fingerprint)
            if envelope.destination_or_topic not in SUPPORTED_TOPICS:
                return self._publish_rejection(
                    envelope, MessageDisposition.UNSUPPORTED, "topic is not supported"
                )
            if envelope.schema_version not in self._supported_schema_versions:
                return self._publish_rejection(
                    envelope, MessageDisposition.UNSUPPORTED, "schema version is not supported"
                )

            now = envelope.simulation_time if valid_at is None else valid_at
            if not math.isfinite(now) or now < 0:
                return self._publish_rejection(
                    envelope, MessageDisposition.MALFORMED, "valid_at must be finite and non-negative"
                )
            if envelope.simulation_time > now:
                return self._publish_rejection(
                    envelope,
                    MessageDisposition.OUT_OF_ORDER,
                    f"message simulation_time {envelope.simulation_time} is in the future "
                    f"relative to valid_at {now}",
                )
            if envelope.expires_at < now:
                return self._publish_rejection(
                    envelope, MessageDisposition.EXPIRED, "message expired before publication"
                )

            stream_key = (
                envelope.run_id,
                envelope.scenario_hash,
                envelope.source_agent,
                envelope.destination_or_topic,
                envelope.payload_type,
            )
            latest = self._latest_stream_time.get(stream_key)
            if latest is not None and envelope.simulation_time < latest:
                return self._publish_rejection(
                    envelope,
                    MessageDisposition.OUT_OF_ORDER,
                    f"simulation_time {envelope.simulation_time} precedes stream time {latest}",
                )

            correlation_key = (
                envelope.run_id,
                envelope.scenario_hash,
                envelope.source_agent,
                envelope.destination_or_topic,
                envelope.correlation_id,
                envelope.simulation_time,
                envelope.payload_type,
            )
            prior_payload = self._correlations.get(correlation_key)
            payload_fingerprint = self._payload_fingerprint(envelope)
            if prior_payload is not None and prior_payload != payload_fingerprint:
                return self._publish_rejection(
                    envelope,
                    MessageDisposition.CONTRADICTORY,
                    "same source/correlation/time carries a different payload",
                )

            self._messages[envelope.message_id] = envelope
            self._remember_metadata(
                self._latest_stream_time, stream_key, envelope.simulation_time
            )
            self._remember_metadata(
                self._correlations, correlation_key, payload_fingerprint
            )
            if len(self._messages) > self._capacity:
                _, evicted = self._messages.popitem(last=False)
                self._record_for(
                    evicted, MessageDisposition.EVICTED, "bounded storage evicted oldest message"
                )
            record = self._record_for(
                envelope, MessageDisposition.ACCEPTED, "message accepted for valid-at-time reads"
            )
            return PublishResult(MessageDisposition.ACCEPTED, True, envelope, record)

    def read(
        self,
        topic: str,
        *,
        valid_at: float,
        run_id: str | None = None,
        scenario_hash: str | None = None,
    ) -> ReadResult:
        with self._lock:
            if not math.isfinite(valid_at) or valid_at < 0:
                record = self._record(
                    MessageDisposition.MALFORMED,
                    "valid_at must be finite and non-negative",
                    run_id=run_id,
                    scenario_hash=scenario_hash,
                    topic=topic,
                    simulation_time=valid_at,
                )
                return ReadResult(MessageDisposition.MALFORMED, (), record)
            if not self._available:
                record = self._record(
                    MessageDisposition.UNAVAILABLE,
                    "transport is unavailable; caller must degrade locally",
                    run_id=run_id,
                    scenario_hash=scenario_hash,
                    topic=topic,
                    simulation_time=valid_at,
                )
                return ReadResult(MessageDisposition.UNAVAILABLE, (), record)
            if topic not in SUPPORTED_TOPICS:
                record = self._record(
                    MessageDisposition.UNSUPPORTED,
                    "topic is not supported",
                    run_id=run_id,
                    scenario_hash=scenario_hash,
                    topic=topic,
                    simulation_time=valid_at,
                )
                return ReadResult(MessageDisposition.UNSUPPORTED, (), record)

            selected: list[MessageEnvelope] = []
            expired_ids: list[str] = []
            for message_id, envelope in self._messages.items():
                if envelope.expires_at < valid_at:
                    expired_ids.append(message_id)
                    self._record_for(
                        envelope,
                        MessageDisposition.EXPIRED,
                        f"message is not valid at simulation time {valid_at}",
                    )
                    continue
                if envelope.simulation_time > valid_at:
                    continue
                if envelope.destination_or_topic != topic:
                    continue
                if run_id is not None and envelope.run_id != run_id:
                    continue
                if scenario_hash is not None and envelope.scenario_hash != scenario_hash:
                    continue
                selected.append(envelope)
            for message_id in expired_ids:
                self._messages.pop(message_id, None)

            selected.sort(
                key=lambda item: (
                    -PRIORITY_RANK[item.priority_class.value],
                    -item.simulation_time,
                    item.message_id,
                )
            )
            disposition = MessageDisposition.ACCEPTED if selected else MessageDisposition.EMPTY
            reason = "valid messages returned" if selected else "no valid messages for read"
            record = self._record(
                disposition,
                reason,
                run_id=run_id,
                scenario_hash=scenario_hash,
                topic=topic,
                simulation_time=valid_at,
            )
            return ReadResult(disposition, tuple(selected), record)

    def _validate(self, value: MessageEnvelope | Mapping[str, Any]) -> MessageEnvelope | None:
        try:
            if isinstance(value, MessageEnvelope):
                return MessageEnvelope.model_validate(value.model_dump(mode="python"))
            return MessageEnvelope.model_validate(value)
        except (ValidationError, TypeError, ValueError):
            return None

    def _publish_rejection(
        self,
        envelope: MessageEnvelope,
        disposition: MessageDisposition,
        reason: str,
    ) -> PublishResult:
        record = self._record_for(envelope, disposition, reason)
        return PublishResult(disposition, False, envelope, record)

    def _id_positions(self, message_id: str) -> tuple[int, int, int, int]:
        digest = hashlib.sha256(message_id.encode("utf-8")).digest()
        return tuple(
            int.from_bytes(digest[offset:offset + 8], "big") % self._idempotency_bits
            for offset in range(0, 32, 8)
        )  # type: ignore[return-value]

    def _id_was_seen(self, message_id: str) -> bool:
        if message_id in self._seen:
            return True
        return all(
            self._idempotency_ledger[position // 8] & (1 << (position % 8))
            for position in self._id_positions(message_id)
        )

    def _remember_id(self, message_id: str, fingerprint: str) -> None:
        for position in self._id_positions(message_id):
            self._idempotency_ledger[position // 8] |= 1 << (position % 8)
        self._remember_metadata(self._seen, message_id, fingerprint)

    def _remember_metadata(
        self,
        mapping: OrderedDict[Any, Any],
        key: Any,
        value: Any,
    ) -> None:
        mapping[key] = value
        mapping.move_to_end(key)
        while len(mapping) > self._metadata_capacity:
            mapping.popitem(last=False)

    @staticmethod
    def _fingerprint(envelope: MessageEnvelope) -> str:
        return json.dumps(envelope.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))

    @staticmethod
    def _payload_fingerprint(envelope: MessageEnvelope) -> str:
        payload = envelope.model_dump(mode="json")["payload"]
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    def _record_for(
        self,
        envelope: MessageEnvelope,
        disposition: MessageDisposition,
        reason: str,
    ) -> DispositionRecord:
        return self._record(
            disposition,
            reason,
            run_id=envelope.run_id,
            scenario_hash=envelope.scenario_hash,
            message_id=envelope.message_id,
            topic=envelope.destination_or_topic,
            simulation_time=envelope.simulation_time,
        )

    def _record(
        self,
        disposition: MessageDisposition,
        reason: str,
        *,
        run_id: str | None = None,
        scenario_hash: str | None = None,
        message_id: str | None = None,
        topic: str | None = None,
        simulation_time: float | None = None,
    ) -> DispositionRecord:
        self._sequence += 1
        record = DispositionRecord(
            sequence=self._sequence,
            disposition=disposition,
            recorded_at=datetime.now(timezone.utc),
            reason=reason,
            run_id=run_id,
            scenario_hash=scenario_hash,
            message_id=message_id,
            topic=topic,
            simulation_time=simulation_time,
        )
        self._audit.append(record)
        return record
