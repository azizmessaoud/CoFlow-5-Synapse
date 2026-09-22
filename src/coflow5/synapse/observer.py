from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Protocol, Sequence


@dataclass(frozen=True)
class ImmutableDecisionView:
    run_id: str
    scenario_hash: str
    event_id: str
    simulation_time: float
    selected_action: str
    reason_code: str


@dataclass(frozen=True)
class ObservationReceipt:
    event_id: str
    observer_available: bool
    explanation_status: str
    failure_type: str | None = None
    failure_detail: str | None = None


class ExplanationObserver(Protocol):
    def observe(self, decision: ImmutableDecisionView) -> str: ...


class ExplanationObserverBoundary:
    """Dispatches an immutable post-decision copy; it has no control callback."""

    def __init__(self, observer: ExplanationObserver | None) -> None:
        self._observer = observer

    def observe_after_decision(self, decision: ImmutableDecisionView) -> ObservationReceipt:
        if self._observer is None:
            return ObservationReceipt(
                event_id=decision.event_id,
                observer_available=False,
                explanation_status="unavailable",
                failure_type="ObserverUnavailable",
                failure_detail="Synapse observer is killed or not configured",
            )
        try:
            status = self._observer.observe(decision)
        except Exception as exc:
            return ObservationReceipt(
                event_id=decision.event_id,
                observer_available=False,
                explanation_status="failed-visible",
                failure_type=type(exc).__name__,
                failure_detail=str(exc) or type(exc).__name__,
            )
        return ObservationReceipt(
            event_id=decision.event_id,
            observer_available=True,
            explanation_status=status,
        )


def action_sequence_hash(actions: Sequence[str]) -> str:
    canonical = json.dumps(list(actions), separators=(",", ":"), ensure_ascii=True).encode()
    return "sha256:" + hashlib.sha256(canonical).hexdigest()
