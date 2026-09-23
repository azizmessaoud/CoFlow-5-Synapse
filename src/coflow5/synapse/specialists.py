from __future__ import annotations

import re
import time
from dataclasses import asdict, dataclass
from typing import Literal, Mapping, Sequence

from coflow5.synapse.evidence_reader import EventIdentity, EvidenceReadError, ImmutableGraphDecision, ImmutableRow10fReader
from coflow5.synapse.provider import DraftAnswer, DraftRequest, OptionalDraftProvider
from coflow5.synapse.retrieval import ExactTokenCorpus, RetrievalHit, RetrievalUnavailable, exact_tokens

AGENT_VERSIONS = {"S1": "scenario-planner-v1", "S2": "decision-explainer-v1", "S3": "evidence-auditor-v1"}
TEMPLATE_VERSION = "deterministic-template-v1"
VERIFY_VERSION = "exact-fact-verifier-v1"


@dataclass(frozen=True)
class TraceRow:
    schema_version: int
    run_id: str
    scenario_hash: str
    event_id: str | None
    request_id: str
    chunk_id: str | None
    agent_id: str
    agent_version: str
    stage: str
    outcome: str
    attempt: int
    latency_ms: float
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float
    generation_version: str
    verification_version: str


def _token_count(value: str) -> int:
    return len(re.findall(r"[A-Za-z0-9_-]+", value))


def _trace(*, identity: EventIdentity, request_id: str, agent_id: str, stage: str,
           outcome: str, started: float, attempt: int = 1, chunk_id: str | None = None,
           input_text: str = "", output_text: str = "") -> TraceRow:
    return TraceRow(
        schema_version=1, run_id=identity.run_id, scenario_hash=identity.scenario_hash,
        event_id=identity.event_id or None, request_id=request_id, chunk_id=chunk_id,
        agent_id=agent_id, agent_version=AGENT_VERSIONS[agent_id], stage=stage,
        outcome=outcome, attempt=attempt,
        latency_ms=round((time.perf_counter() - started) * 1000.0, 6),
        input_tokens=_token_count(input_text), output_tokens=_token_count(output_text),
        estimated_cost_usd=0.0, generation_version=TEMPLATE_VERSION,
        verification_version=VERIFY_VERSION,
    )


@dataclass(frozen=True)
class ScenarioProposal:
    schema_version: int
    request_id: str
    source_run_id: str
    scenario_hash: str
    title: str
    demand_scale: float
    horizon_seconds: int
    status: Literal["awaiting-human-approval"]
    artifact_kind: Literal["proposal-only"]
    automatic_approval: Literal[False]
    executed: Literal[False]
    agent_id: Literal["S1"]
    agent_version: str


@dataclass(frozen=True)
class PlannerResult:
    proposal: ScenarioProposal
    traces: tuple[TraceRow, ...]


class S1ScenarioPlanner:
    def plan(self, *, request_id: str, source_run_id: str, scenario_hash: str,
             title: str, demand_scale: float, horizon_seconds: int) -> PlannerResult:
        started = time.perf_counter()
        if not request_id or not source_run_id or not scenario_hash.startswith("sha256:"):
            raise ValueError("proposal requires request, source run, and scenario identities")
        if not title.strip() or not 0.5 <= demand_scale <= 2.0:
            raise ValueError("proposal title or demand scale is outside bounds")
        if not 30 <= horizon_seconds <= 3600:
            raise ValueError("proposal horizon is outside 30..3600 seconds")
        proposal = ScenarioProposal(
            schema_version=1, request_id=request_id, source_run_id=source_run_id,
            scenario_hash=scenario_hash, title=title.strip(), demand_scale=float(demand_scale),
            horizon_seconds=horizon_seconds, status="awaiting-human-approval",
            artifact_kind="proposal-only", automatic_approval=False, executed=False,
            agent_id="S1", agent_version=AGENT_VERSIONS["S1"],
        )
        identity = EventIdentity(source_run_id, scenario_hash, "")
        trace = _trace(identity=identity, request_id=request_id, agent_id="S1", stage="terminal",
                       outcome="awaiting-human-approval", started=started, output_text=title)
        return PlannerResult(proposal=proposal, traces=(trace,))


@dataclass(frozen=True)
class ExplanationResult:
    schema_version: int
    request_id: str
    classification: str
    status: Literal["answered", "abstained"]
    answer: str | None
    abstention_reason: str | None
    event_facts: Mapping[str, object]
    citations: tuple[Mapping[str, object], ...]
    provider_attempts: int
    fallback_used: bool
    generation_mode: str
    traces: tuple[TraceRow, ...]


class S2DecisionExplainer:
    def __init__(self, reader: ImmutableRow10fReader, corpus: ExactTokenCorpus,
                 provider: OptionalDraftProvider | None = None) -> None:
        self._reader = reader
        self._corpus = corpus
        self._provider = provider

    @staticmethod
    def classify(question: str) -> str:
        tokens = set(exact_tokens(question))
        return "decision-explanation" if tokens & {"why", "action", "decision", "signal", "reason", "explain"} else "unsupported"

    @staticmethod
    def _template(event: ImmutableGraphDecision, hits: Sequence[RetrievalHit]) -> DraftAnswer:
        citation_ids = tuple(hit.chunk.chunk_id for hit in hits)
        answer = (
            f"Immutable event {event.event_id} selected {event.accepted_action} at {event.signal_id} "
            f"with reason {event.reason_code}. Synapse reports this completed decision and does not alter it. "
            f"Policy support: [{citation_ids[0]}]."
        )
        return DraftAnswer(answer, event.event_id, event.accepted_action, event.reason_code, citation_ids)

    @staticmethod
    def _valid_draft(draft: DraftAnswer, event: ImmutableGraphDecision, hits: Sequence[RetrievalHit]) -> bool:
        valid_ids = {hit.chunk.chunk_id for hit in hits}
        return (
            draft.event_id == event.event_id
            and draft.accepted_action == event.accepted_action
            and draft.reason_code == event.reason_code
            and bool(draft.citation_chunk_ids)
            and set(draft.citation_chunk_ids).issubset(valid_ids)
            and event.event_id in draft.answer
            and event.accepted_action in draft.answer
            and event.reason_code in draft.answer
        )

    def _abstain(self, *, request_id: str, classification: str, identity: EventIdentity,
                 reason: str, facts: Mapping[str, object], traces: list[TraceRow], started: float) -> ExplanationResult:
        traces.append(_trace(identity=identity, request_id=request_id, agent_id="S2", stage="terminal",
                             outcome="abstained", started=started, output_text=reason))
        return ExplanationResult(1, request_id, classification, "abstained", None, reason,
                                 dict(facts), (), 0, False, "none", tuple(traces))

    def explain(self, *, request_id: str, question: str, identity: EventIdentity,
                retrieval_query: str | None = None) -> ExplanationResult:
        traces: list[TraceRow] = []
        classification = self.classify(question)
        if classification == "unsupported":
            return self._abstain(request_id=request_id, classification=classification, identity=identity,
                                 reason="unsupported-question", facts={}, traces=traces, started=time.perf_counter())
        started = time.perf_counter()
        try:
            event = self._reader.read_event(identity)
        except EvidenceReadError as exc:
            traces.append(_trace(identity=identity, request_id=request_id, agent_id="S2", stage="event-fetch",
                                 outcome="failed", started=started, input_text=question, output_text=str(exc)))
            return self._abstain(request_id=request_id, classification=classification, identity=identity,
                                 reason="invalid-event-identity", facts={"requested_event_id": identity.event_id},
                                 traces=traces, started=started)
        traces.append(_trace(identity=identity, request_id=request_id, agent_id="S2", stage="event-fetch",
                             outcome="verified", started=started, input_text=question, output_text=event.event_id))
        facts = event.facts()
        retrieval_started = time.perf_counter()
        try:
            hits = self._corpus.search(retrieval_query if retrieval_query is not None else question)
        except RetrievalUnavailable:
            traces.append(_trace(identity=identity, request_id=request_id, agent_id="S2", stage="retrieval",
                                 outcome="unavailable", started=retrieval_started, input_text=question))
            return self._abstain(request_id=request_id, classification=classification, identity=identity,
                                 reason="retrieval-unavailable", facts=facts, traces=traces, started=started)
        for hit in hits:
            traces.append(_trace(identity=identity, request_id=request_id, agent_id="S2", stage="retrieval",
                                 outcome="hit", started=retrieval_started, chunk_id=hit.chunk.chunk_id,
                                 input_text=question, output_text=hit.chunk.content))
        if not hits:
            traces.append(_trace(identity=identity, request_id=request_id, agent_id="S2", stage="retrieval",
                                 outcome="miss", started=retrieval_started, input_text=question))
            return self._abstain(request_id=request_id, classification=classification, identity=identity,
                                 reason="retrieval-miss", facts=facts, traces=traces, started=started)

        attempts = 0
        fallback = False
        draft: DraftAnswer | None = None
        if self._provider is not None:
            provider_request = DraftRequest(request_id, question, event.event_id, event.accepted_action,
                                            event.reason_code, tuple(hit.chunk.chunk_id for hit in hits))
            for attempt in (1, 2):
                attempts = attempt
                generation_started = time.perf_counter()
                try:
                    candidate = self._provider.draft(provider_request)
                except Exception as exc:
                    traces.append(_trace(identity=identity, request_id=request_id, agent_id="S2", stage="generation",
                                         outcome="provider-unavailable", started=generation_started, attempt=attempt,
                                         input_text=question, output_text=type(exc).__name__))
                    break
                traces.append(_trace(identity=identity, request_id=request_id, agent_id="S2", stage="generation",
                                     outcome="provider-structured-draft", started=generation_started, attempt=attempt,
                                     input_text=question, output_text="typed-fields-received"))
                verify_started = time.perf_counter()
                if self._valid_draft(candidate, event, hits):
                    # Provider prose is untrusted and never released. The provider may only
                    # supply typed event/citation fields; verified fields select the closed
                    # deterministic template that renders immutable facts and citations.
                    draft = self._template(event, hits)
                    traces.append(_trace(identity=identity, request_id=request_id, agent_id="S2", stage="verification",
                                         outcome="passed", started=verify_started, attempt=attempt,
                                         output_text="typed-fields-verified-local-template"))
                    break
                traces.append(_trace(identity=identity, request_id=request_id, agent_id="S2", stage="verification",
                                     outcome="failed", started=verify_started, attempt=attempt,
                                     output_text="event-or-citation-mismatch"))
                if attempt == 1:
                    traces.append(_trace(identity=identity, request_id=request_id, agent_id="S2", stage="retry",
                                         outcome="one-retry", started=verify_started, attempt=2))
            if draft is None:
                fallback = True
                fallback_started = time.perf_counter()
                traces.append(_trace(identity=identity, request_id=request_id, agent_id="S2", stage="fallback",
                                     outcome="deterministic-template", started=fallback_started, attempt=attempts))

        if draft is None:
            generation_started = time.perf_counter()
            draft = self._template(event, hits)
            traces.append(_trace(identity=identity, request_id=request_id, agent_id="S2", stage="generation",
                                 outcome="deterministic-template", started=generation_started,
                                 input_text=question, output_text=draft.answer))
            verify_started = time.perf_counter()
            if not self._valid_draft(draft, event, hits):
                return self._abstain(request_id=request_id, classification=classification, identity=identity,
                                     reason="deterministic-verification-failed", facts=facts,
                                     traces=traces, started=started)
            traces.append(_trace(identity=identity, request_id=request_id, agent_id="S2", stage="verification",
                                 outcome="passed", started=verify_started, output_text=draft.answer))

        citations = tuple(hit.citation() for hit in hits if hit.chunk.chunk_id in draft.citation_chunk_ids)
        traces.append(_trace(identity=identity, request_id=request_id, agent_id="S2", stage="terminal",
                             outcome="answered", started=started, output_text=draft.answer))
        mode = "provider-verified" if self._provider is not None and not fallback else TEMPLATE_VERSION
        return ExplanationResult(1, request_id, classification, "answered", draft.answer, None, facts,
                                 citations, attempts, fallback, mode, tuple(traces))


@dataclass(frozen=True)
class AuditClaim:
    claim_id: str
    source_type: Literal["event-field", "artifact-hash"]
    field_or_path: str
    expected: object


@dataclass(frozen=True)
class AuditResult:
    schema_version: int
    request_id: str
    status: Literal["pass", "abstained"]
    checks: tuple[Mapping[str, object], ...]
    references: tuple[Mapping[str, object], ...]
    failed_checks: tuple[str, ...]
    traces: tuple[TraceRow, ...]


class S3EvidenceAuditor:
    def __init__(self, reader: ImmutableRow10fReader) -> None:
        self._reader = reader

    def audit(self, *, request_id: str, identity: EventIdentity,
              claims: Sequence[AuditClaim]) -> AuditResult:
        traces: list[TraceRow] = []
        started = time.perf_counter()
        try:
            event = self._reader.read_event(identity)
        except EvidenceReadError as exc:
            traces.append(_trace(identity=identity, request_id=request_id, agent_id="S3", stage="event-fetch",
                                 outcome="failed", started=started, output_text=str(exc)))
            traces.append(_trace(identity=identity, request_id=request_id, agent_id="S3", stage="terminal",
                                 outcome="abstained", started=started))
            return AuditResult(1, request_id, "abstained", (), (), ("event-identity",), tuple(traces))
        traces.append(_trace(identity=identity, request_id=request_id, agent_id="S3", stage="event-fetch",
                             outcome="verified", started=started, output_text=event.event_id))
        facts = event.facts()
        checks: list[Mapping[str, object]] = []
        references: list[Mapping[str, object]] = []
        failed: list[str] = []
        for claim in claims:
            check_started = time.perf_counter()
            if claim.source_type == "event-field":
                actual = facts.get(claim.field_or_path, object())
                passed = claim.field_or_path in facts and actual == claim.expected
                reference = {"event_id": event.event_id, "field": claim.field_or_path,
                             "evidence_sha256": event.evidence_sha256} if passed else None
            else:
                passed = isinstance(claim.expected, str) and self._reader.verify_bound_artifact(
                    claim.field_or_path, claim.expected
                )
                actual = claim.expected if passed else None
                reference = {"path": claim.field_or_path, "sha256": claim.expected} if passed else None
            checks.append({"claim_id": claim.claim_id, "source_type": claim.source_type,
                           "field_or_path": claim.field_or_path, "expected": claim.expected,
                           "actual": actual, "passed": passed})
            if passed and reference is not None:
                references.append(reference)
            else:
                failed.append(claim.claim_id)
            traces.append(_trace(identity=identity, request_id=request_id, agent_id="S3", stage="verification",
                                 outcome="passed" if passed else "failed", started=check_started,
                                 input_text=claim.claim_id, output_text=str(passed)))
        status: Literal["pass", "abstained"] = "pass" if claims and not failed else "abstained"
        traces.append(_trace(identity=identity, request_id=request_id, agent_id="S3", stage="terminal",
                             outcome=status, started=started))
        return AuditResult(1, request_id, status, tuple(checks), tuple(references), tuple(failed), tuple(traces))


def public_dict(value: object) -> dict[str, object]:
    return asdict(value)
