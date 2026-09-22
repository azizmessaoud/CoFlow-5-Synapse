from __future__ import annotations

import math
import uuid
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping

from coflow5.messaging import InProcessMessageBoard, MessageDisposition, MessageEnvelope


class FailureClass(str, Enum):
    MESSAGE_ABSENCE = "message_absence"
    MESSAGE_LOSS_DROP = "message_loss_drop"
    MESSAGE_DELAY = "message_delay"
    MESSAGE_DUPLICATION = "message_duplication"
    MESSAGE_EXPIRY = "message_expiry"
    MALFORMED_PAYLOAD = "malformed_payload"
    MESSAGE_CONTRADICTION = "message_contradiction"
    ADVISER_SILENCE = "adviser_silence"


class InjectionDisposition(str, Enum):
    ABSENT = "absent"
    DROPPED = "dropped"
    DELAYED = "delayed"
    DUPLICATE = "duplicate"
    EXPIRED = "expired"
    MALFORMED = "malformed"
    CONTRADICTORY = "contradictory"
    SILENT = "silent"


@dataclass(frozen=True)
class FaultInjection:
    failure_class: FailureClass
    simulation_time: float
    message_id: str | None = None
    delay_seconds: float = 0.0

    def __post_init__(self) -> None:
        if not math.isfinite(self.simulation_time) or self.simulation_time < 0:
            raise ValueError("fault simulation_time must be finite and non-negative")
        if not math.isfinite(self.delay_seconds) or self.delay_seconds < 0:
            raise ValueError("delay_seconds must be finite and non-negative")
        if self.failure_class is FailureClass.MESSAGE_DELAY and self.delay_seconds <= 0:
            raise ValueError("message delay requires a positive delay_seconds")
        if self.failure_class not in {
            FailureClass.MESSAGE_ABSENCE,
            FailureClass.ADVISER_SILENCE,
        } and not self.message_id:
            raise ValueError("message fault requires message_id evidence")


@dataclass(frozen=True)
class FaultEvidence:
    run_id: str
    scenario_hash: str
    event_id: str
    failure_class: FailureClass
    simulation_time: float
    message_id: str | None
    disposition: InjectionDisposition
    detail: str


@dataclass(frozen=True)
class FaultInjectionResult:
    evidence: FaultEvidence
    delivered: tuple[MessageEnvelope, ...]
    transport_dispositions: tuple[MessageDisposition, ...]
    metadata: Mapping[str, Any]


class DeterministicFailureInjector:
    """Applies a declared communication fault without gaining control authority."""

    def __init__(self, board: InProcessMessageBoard, *, run_id: str, scenario_hash: str) -> None:
        if not run_id or not scenario_hash:
            raise ValueError("run_id and scenario_hash are required")
        self._board = board
        self._run_id = run_id
        self._scenario_hash = scenario_hash
        self._sequence = 0

    def inject(
        self,
        injection: FaultInjection,
        *,
        message: MessageEnvelope | Mapping[str, Any] | None = None,
        conflicting_message: MessageEnvelope | None = None,
    ) -> FaultInjectionResult:
        self._sequence += 1
        failure = injection.failure_class
        delivered: tuple[MessageEnvelope, ...] = ()
        dispositions: tuple[MessageDisposition, ...] = ()
        metadata: dict[str, Any] = {}

        if failure is FailureClass.MESSAGE_ABSENCE:
            disposition = InjectionDisposition.ABSENT
            detail = "no advisory was published"
        elif failure is FailureClass.ADVISER_SILENCE:
            disposition = InjectionDisposition.SILENT
            detail = "expected adviser produced no advisory before the decision deadline"
        else:
            if message is None:
                raise ValueError(f"{failure.value} requires a message or raw payload")
            if failure is FailureClass.MESSAGE_CONTRADICTION:
                if conflicting_message is None:
                    raise TypeError("contradiction requires a conflicting MessageEnvelope")
                self._validate_identity(injection, conflicting_message)
                if isinstance(message, MessageEnvelope):
                    if (message.run_id, message.scenario_hash) != (
                        self._run_id,
                        self._scenario_hash,
                    ):
                        raise ValueError("baseline contradiction message identity must match the run")
            else:
                self._validate_identity(injection, message)
            if failure is FailureClass.MESSAGE_LOSS_DROP:
                disposition = InjectionDisposition.DROPPED
                detail = "message deterministically dropped before transport publication"
            elif failure is FailureClass.MESSAGE_DELAY:
                disposition = InjectionDisposition.DELAYED
                detail = "message held beyond this decision epoch"
                metadata["release_at"] = injection.simulation_time + injection.delay_seconds
            elif failure is FailureClass.MESSAGE_DUPLICATION:
                if not isinstance(message, MessageEnvelope):
                    raise TypeError("duplication requires a validated MessageEnvelope")
                first = self._board.publish(message, valid_at=injection.simulation_time)
                second = self._board.publish(message, valid_at=injection.simulation_time)
                if not first.accepted or second.disposition is not MessageDisposition.DUPLICATE:
                    raise RuntimeError("message board did not enforce idempotent duplication")
                delivered = (message,)
                dispositions = (first.disposition, second.disposition)
                disposition = InjectionDisposition.DUPLICATE
                detail = second.record.reason
            elif failure is FailureClass.MESSAGE_EXPIRY:
                result = self._board.publish(message, valid_at=injection.simulation_time)
                if result.disposition is not MessageDisposition.EXPIRED:
                    raise RuntimeError("expiry injection did not produce EXPIRED disposition")
                dispositions = (result.disposition,)
                disposition = InjectionDisposition.EXPIRED
                detail = result.record.reason
            elif failure is FailureClass.MALFORMED_PAYLOAD:
                result = self._board.publish(message, valid_at=injection.simulation_time)
                if result.disposition is not MessageDisposition.MALFORMED:
                    raise RuntimeError("malformed injection did not produce MALFORMED disposition")
                dispositions = (result.disposition,)
                disposition = InjectionDisposition.MALFORMED
                detail = result.record.reason
            elif failure is FailureClass.MESSAGE_CONTRADICTION:
                if not isinstance(message, MessageEnvelope) or conflicting_message is None:
                    raise TypeError("contradiction requires two validated MessageEnvelope values")
                first = self._board.publish(message, valid_at=injection.simulation_time)
                second = self._board.publish(conflicting_message, valid_at=injection.simulation_time)
                if not first.accepted or second.disposition is not MessageDisposition.CONTRADICTORY:
                    raise RuntimeError("contradiction injection did not produce CONTRADICTORY disposition")
                delivered = (message,)
                dispositions = (first.disposition, second.disposition)
                disposition = InjectionDisposition.CONTRADICTORY
                detail = second.record.reason
            else:  # pragma: no cover - exhaustive Enum guard
                raise ValueError(f"unsupported failure class: {failure}")

        event_name = (
            f"{self._sequence}|{failure.value}|{injection.simulation_time:.9f}|"
            f"{injection.message_id or 'not-applicable'}"
        )
        event_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"coflow5:{self._run_id}:{event_name}"))
        evidence = FaultEvidence(
            run_id=self._run_id,
            scenario_hash=self._scenario_hash,
            event_id=event_id,
            failure_class=failure,
            simulation_time=injection.simulation_time,
            message_id=injection.message_id,
            disposition=disposition,
            detail=detail,
        )
        return FaultInjectionResult(
            evidence=evidence,
            delivered=delivered,
            transport_dispositions=dispositions,
            metadata=MappingProxyType(metadata),
        )

    def _validate_identity(
        self,
        injection: FaultInjection,
        message: MessageEnvelope | Mapping[str, Any],
    ) -> None:
        if isinstance(message, MessageEnvelope):
            run_id = message.run_id
            scenario_hash = message.scenario_hash
            message_id = message.message_id
        else:
            run_id = message.get("run_id")
            scenario_hash = message.get("scenario_hash")
            message_id = message.get("message_id")
        if (run_id, scenario_hash, message_id) != (
            self._run_id,
            self._scenario_hash,
            injection.message_id,
        ):
            raise ValueError("fault and message identities must match")
