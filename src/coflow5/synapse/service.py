from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from time import perf_counter

MAX_QUESTION_LENGTH = 2000
FALLBACK_STATES = frozenset({"verified", "template", "abstain"})


@dataclass(frozen=True)
class Provenance:
    run_id: str | None
    scenario_hash: str | None
    event_id: str | None
    message_id: str | None
    bundle_digest: str | None
    corpus_hash: str | None
    query_hash: str

    def as_dict(self) -> dict[str, str | None]:
        return {
            "run_id": self.run_id,
            "scenario_hash": self.scenario_hash,
            "event_id": self.event_id,
            "message_id": self.message_id,
            "bundle_digest": self.bundle_digest,
            "corpus_hash": self.corpus_hash,
            "query_hash": self.query_hash,
        }


@dataclass(frozen=True)
class ExplanationResult:
    fallback: str
    answer: str
    provenance: Provenance
    citations: tuple[str, ...]
    cache_key: tuple[str | None, str, str]


@dataclass(frozen=True)
class EvidenceEvent:
    run_id: str
    scenario_hash: str
    event_id: str
    message_id: str | None
    bundle_digest: str
    facts: Mapping[str, object]


class SynapseService:
    """Read-only explanations over supplied evidence and an allow-listed corpus."""

    def __init__(
        self,
        *,
        events: Mapping[str, EvidenceEvent],
        policies: Mapping[str, str],
        corpus_hash: str,
        endpoint: str = "explanations",
    ) -> None:
        if not corpus_hash:
            raise ValueError("corpus_hash is required")
        self._events = dict(events)
        self._policies = dict(policies)
        self._corpus_hash = corpus_hash
        self._endpoint = endpoint
        self._cache: dict[tuple[str | None, str, str], ExplanationResult] = {}
        self._requests = 0
        self._fallback_counts = {state: 0 for state in FALLBACK_STATES}
        self._latencies_ms: list[float] = []
        self._cost_units = 0

    def explain(self, question: str, *, event_id: str, policy_id: str | None = None) -> ExplanationResult:
        query_hash = _query_hash(question, policy_id)
        if not question.strip() or len(question) > MAX_QUESTION_LENGTH:
            raise ValueError("question must be non-empty and within the length bound")
        started = perf_counter()
        self._requests += 1
        self._cost_units += len(question)
        event = self._events.get(event_id)
        if event is None:
            provenance = Provenance(
                None, None, event_id, None, None, self._corpus_hash, query_hash
            )
            result = ExplanationResult(
                "abstain",
                "I cannot verify this explanation because the event is missing.",
                provenance,
                (),
                (None, self._endpoint, query_hash),
            )
            self._record(result, started)
            return result
        cache_key = (event.bundle_digest, self._endpoint, query_hash)
        cached = self._cache.get(cache_key)
        if cached is not None:
            self._record(cached, started)
            return cached
        citation = policy_id if policy_id in self._policies else None
        fallback = "verified" if citation else "template"
        policy_marker = "" if citation else " [policy support missing]"
        answer = (
            f"At {event.facts.get('simulation_time', 'the recorded time')}, "
            f"the signal controller (A1) selected {event.facts.get('selected_action', 'an action')} "
            f"because {event.facts.get('reason_code', 'the recorded reason')}."
            f"{policy_marker}"
        )
        result = ExplanationResult(
            fallback,
            answer,
            Provenance(
                event.run_id,
                event.scenario_hash,
                event.event_id,
                event.message_id,
                event.bundle_digest,
                self._corpus_hash,
                query_hash,
            ),
            (citation,) if citation else (),
            cache_key,
        )
        self._cache[cache_key] = result
        self._record(result, started)
        return result

    def audit(
        self,
        claim: str,
        *,
        event_id: str,
        policy_id: str | None = None,
    ) -> ExplanationResult:
        result = self.explain(claim, event_id=event_id, policy_id=policy_id)
        if result.fallback == "abstain":
            return result
        supported = any(
            str(value).lower() in claim.lower()
            for value in self._events[event_id].facts.values()
            if isinstance(value, (str, int, float))
        )
        if not supported:
            abstention = ExplanationResult(
                "abstain",
                "I cannot verify that claim from the recorded evidence.",
                result.provenance,
                result.citations,
                result.cache_key,
            )
            self._record(abstention, perf_counter())
            return abstention
        return result

    def metrics(self) -> dict[str, float | int]:
        requests = self._requests
        return {
            "request_count": requests,
            "abstention_count": self._fallback_counts["abstain"],
            "template_count": self._fallback_counts["template"],
            "verified_count": self._fallback_counts["verified"],
            "abstention_rate": (
                self._fallback_counts["abstain"] / requests if requests else 0.0
            ),
            "fallback_rate": (
                (self._fallback_counts["template"] + self._fallback_counts["abstain"])
                / requests
                if requests
                else 0.0
            ),
            "average_latency_ms": (
                sum(self._latencies_ms) / len(self._latencies_ms)
                if self._latencies_ms
                else 0.0
            ),
            "cost_units": self._cost_units,
        }

    def event_summaries(self, event_ids: list[str]) -> list[dict[str, object]]:
        return [
            {
                "run_id": event.run_id,
                "scenario_hash": event.scenario_hash,
                "event_id": event.event_id,
                "message_id": event.message_id,
                "bundle_digest": event.bundle_digest,
            }
            for event_id in event_ids
            if (event := self._events.get(event_id)) is not None
        ]

    def _record(self, result: ExplanationResult, started: float) -> None:
        self._fallback_counts[result.fallback] += 1
        self._latencies_ms.append((perf_counter() - started) * 1000)


def _query_hash(question: str, policy_id: str | None) -> str:
    canonical = json.dumps(
        {"policy_id": policy_id, "question": question},
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    )
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()
