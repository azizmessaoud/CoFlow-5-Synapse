from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from math import isfinite
from threading import RLock
from typing import Any, Iterator, Mapping
from uuid import NAMESPACE_URL, uuid5
from weakref import WeakKeyDictionary

from coflow5.control import ActionProposal, DeterministicSafetyMask, SignalSnapshot

A1_SIGNAL_OWNER = "A1_FLOW"


@dataclass(frozen=True)
class SafetyEvent:
    run_id: str
    scenario_hash: str
    event_id: str
    proposal_id: str
    signal_id: str
    simulation_time: float
    recorded_at: str
    source: str
    requested_phase_id: str
    accepted: bool
    reason_code: str
    provenance: str


@dataclass(frozen=True)
class ExecutedSignalCommand:
    run_id: str
    scenario_hash: str
    event_id: str
    proposal_id: str
    signal_id: str
    simulation_time: float
    executed_at: str
    source: str
    phase_id: str
    signal_state: str


class ImmutableSafetyLog:
    """Append-only events with one serialized submission per proposal identity."""

    def __init__(self) -> None:
        self._events: list[SafetyEvent] = []
        self._commands: list[ExecutedSignalCommand] = []
        self._events_by_proposal: dict[str, SafetyEvent] = {}
        self._lock = RLock()

    @property
    def events(self) -> tuple[SafetyEvent, ...]:
        with self._lock:
            return tuple(self._events)

    @property
    def commands(self) -> tuple[ExecutedSignalCommand, ...]:
        with self._lock:
            return tuple(self._commands)

    @contextmanager
    def submission(self, proposal_id: str) -> Iterator[SafetyEvent | None]:
        """Hold the log lock across duplicate check, actuation, and append."""
        with self._lock:
            yield self._events_by_proposal.get(proposal_id)

    def append(self, event: SafetyEvent, command: ExecutedSignalCommand | None) -> None:
        # Called while submission() holds the re-entrant lock.
        with self._lock:
            if event.proposal_id in self._events_by_proposal:
                raise ValueError(f"proposal already has an immutable event: {event.proposal_id}")
            if command is not None and command.event_id != event.event_id:
                raise ValueError("command and event identity differ")
            if event.accepted != (command is not None):
                raise ValueError("accepted event must have exactly one command")
            self._events_by_proposal[event.proposal_id] = event
            self._events.append(event)
            if command is not None:
                self._commands.append(command)


class SignalExecutorRegistry:
    """Issues the only safe A1 submission capability per TraCI connection/signal."""

    __claims_lock = RLock()
    __claimed_signals: WeakKeyDictionary[Any, set[str]] = WeakKeyDictionary()

    def __init__(self) -> None:
        self.__executors: dict[str, object] = {}

    @property
    def writer_count_by_signal(self) -> dict[str, int]:
        return {signal_id: 1 for signal_id in self.__executors}

    @classmethod
    def __claim(cls, connection: Any, signal_id: str) -> None:
        with cls.__claims_lock:
            try:
                claimed = cls.__claimed_signals.get(connection)
            except TypeError as exc:
                raise TypeError("TraCI connection must support weak references") from exc
            if claimed is None:
                claimed = set()
                cls.__claimed_signals[connection] = claimed
            if signal_id in claimed:
                raise RuntimeError(f"signal already has its sole writer on this connection: {signal_id}")
            claimed.add(signal_id)

    @classmethod
    def __release_failed_claim(cls, connection: Any, signal_id: str) -> None:
        with cls.__claims_lock:
            claimed = cls.__claimed_signals.get(connection)
            if claimed is not None:
                claimed.discard(signal_id)
                if not claimed:
                    del cls.__claimed_signals[connection]

    def acquire(
        self,
        *,
        signal_id: str,
        connection: Any,
        safety_mask: DeterministicSafetyMask,
        initial_phase_id: str,
        initial_phase_entered_at: float,
        run_id: str,
        scenario_hash: str,
        log: ImmutableSafetyLog,
        owner: str = A1_SIGNAL_OWNER,
    ) -> object:
        if owner != A1_SIGNAL_OWNER:
            raise PermissionError("only A1 Flow can own a signal executor")
        if not isfinite(initial_phase_entered_at):
            raise ValueError("initial phase entry time must be finite")
        self.__claim(connection, signal_id)
        try:
            # The concrete capability type, constructor authority, and TraCI
            # connection exist only in this factory closure. Other modules receive
            # submit(), never a raw writer class, token, or connection.
            construction_authority = object()

            class _SafeSubmissionCapability:
                __slots__ = ("_SafeSubmissionCapability__phase_id", "_SafeSubmissionCapability__phase_entered_at")

                def __new__(cls, authority: object):
                    if authority is not construction_authority:
                        raise PermissionError("signal capability can only be created by its registry")
                    return super().__new__(cls)

                def __init__(self, authority: object) -> None:
                    if authority is not construction_authority:
                        raise PermissionError("signal capability can only be created by its registry")
                    self.__phase_id = initial_phase_id
                    self.__phase_entered_at = initial_phase_entered_at

                @property
                def current_phase_id(self) -> str:
                    return self.__phase_id

                def submit(
                    self,
                    proposal: ActionProposal,
                    *,
                    simulation_time: float,
                    pedestrian_remaining_clearance: Mapping[str, float] | None = None,
                ) -> SafetyEvent:
                    if proposal.signal_id != signal_id:
                        raise ValueError("proposal targets a different signal")
                    with log.submission(proposal.proposal_id) as existing:
                        if existing is not None:
                            return existing
                        snapshot = SignalSnapshot(
                            phase_id=self.__phase_id,
                            phase_entered_at=self.__phase_entered_at,
                            pedestrian_remaining_clearance=pedestrian_remaining_clearance or {},
                        )
                        decision = safety_mask.evaluate(proposal, snapshot, simulation_time)
                        event_id = str(
                            uuid5(NAMESPACE_URL, f"{run_id}:{signal_id}:{proposal.proposal_id}")
                        )
                        timestamp = datetime.now(timezone.utc).isoformat()
                        event = SafetyEvent(
                            run_id=run_id,
                            scenario_hash=scenario_hash,
                            event_id=event_id,
                            proposal_id=proposal.proposal_id,
                            signal_id=signal_id,
                            simulation_time=simulation_time,
                            recorded_at=timestamp,
                            source=proposal.source.value,
                            requested_phase_id=proposal.requested_phase_id,
                            accepted=decision.accepted,
                            reason_code=decision.reason.value,
                            provenance="deterministic-safety-mask-v1",
                        )
                        command: ExecutedSignalCommand | None = None
                        if decision.accepted:
                            assert decision.requested_phase is not None
                            target_state = decision.requested_phase.signal_state
                            # The only traffic-light write in product code.
                            connection.trafficlight.setRedYellowGreenState(signal_id, target_state)
                            command = ExecutedSignalCommand(
                                run_id=run_id,
                                scenario_hash=scenario_hash,
                                event_id=event_id,
                                proposal_id=proposal.proposal_id,
                                signal_id=signal_id,
                                simulation_time=simulation_time,
                                executed_at=timestamp,
                                source=proposal.source.value,
                                phase_id=decision.requested_phase.phase_id,
                                signal_state=target_state,
                            )
                            # Record every physical write before an observation check
                            # can raise, so no executed action is absent from evidence.
                            log.append(event, command)
                            observed = connection.trafficlight.getRedYellowGreenState(signal_id)
                            if observed != target_state:
                                raise RuntimeError("SUMO did not apply the accepted signal state")
                            if decision.requested_phase.phase_id != self.__phase_id:
                                self.__phase_id = decision.requested_phase.phase_id
                                self.__phase_entered_at = simulation_time
                        else:
                            log.append(event, None)
                        return event

            executor = _SafeSubmissionCapability(construction_authority)
        except Exception:
            self.__release_failed_claim(connection, signal_id)
            raise
        self.__executors[signal_id] = executor
        return executor
