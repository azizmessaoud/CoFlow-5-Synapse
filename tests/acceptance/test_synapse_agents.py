from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq

from coflow5.synapse import (
    AuditClaim, DraftAnswer, EventIdentity, ExactTokenCorpus, ImmutableRow10fReader,
    S1ScenarioPlanner, S2DecisionExplainer, S3EvidenceAuditor,
)

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "harness/work/12-synapse-agents/contract.json"
EVENTS = ROOT / "harness/work/10f-graph-growth-benchmark/artifacts/decision_events.parquet"
QUERY = "Synapse actuation Max-Pressure safety control"


def identity() -> EventIdentity:
    row = next(row for row in pq.read_table(EVENTS).to_pylist() if row["controller"] == "graph-aware-cooperative-max-pressure")
    return EventIdentity(row["run_id"], row["scenario_hash"], row["event_id"])


class InvalidProvider:
    def __init__(self) -> None:
        self.calls = 0

    def draft(self, request):
        self.calls += 1
        return DraftAnswer("invented", request.event_id, "INVENTED", request.reason_code, request.citation_chunk_ids)


class FailedProvider:
    def __init__(self) -> None:
        self.calls = 0

    def draft(self, request):
        self.calls += 1
        raise RuntimeError("outage")


class UnsupportedClaimProvider:
    def __init__(self, claim: str) -> None:
        self.claim = claim
        self.calls = 0

    def draft(self, request):
        self.calls += 1
        return DraftAnswer(
            f"Event {request.event_id} selected {request.accepted_action} for "
            f"{request.reason_code}. {self.claim}",
            request.event_id,
            request.accepted_action,
            request.reason_code,
            request.citation_chunk_ids,
        )


def components():
    return ImmutableRow10fReader(ROOT, CONTRACT), ExactTokenCorpus.from_contract(ROOT, CONTRACT)


def test_s1_writes_only_a_bounded_waiting_proposal() -> None:
    item = identity()
    result = S1ScenarioPlanner().plan(
        request_id="request-s1", source_run_id=item.run_id, scenario_hash=item.scenario_hash,
        title="Demand sensitivity", demand_scale=1.25, horizon_seconds=300,
    )
    assert result.proposal.status == "awaiting-human-approval"
    assert result.proposal.artifact_kind == "proposal-only"
    assert result.proposal.automatic_approval is False and result.proposal.executed is False
    assert not hasattr(S1ScenarioPlanner, "approve") and not hasattr(S1ScenarioPlanner, "launch")


def test_s2_cites_one_hash_valid_event_and_verifies_every_fact() -> None:
    reader, corpus = components()
    result = S2DecisionExplainer(reader, corpus).explain(
        request_id="request-s2", question="Why was this signal action selected?",
        identity=identity(), retrieval_query=QUERY,
    )
    assert result.status == "answered" and result.citations
    assert result.event_facts["event_id"] in result.answer
    assert result.event_facts["accepted_action"] in result.answer
    assert result.event_facts["reason_code"] in result.answer
    assert {row.stage for row in result.traces} >= {"event-fetch", "retrieval", "generation", "verification", "terminal"}


def test_s2_retries_invalid_draft_once_and_provider_outage_falls_back() -> None:
    reader, corpus = components()
    bad = InvalidProvider()
    retried = S2DecisionExplainer(reader, corpus, bad).explain(
        request_id="retry", question="Explain this decision.", identity=identity(), retrieval_query=QUERY,
    )
    assert bad.calls == 2 and retried.provider_attempts == 2
    assert retried.status == "answered" and retried.fallback_used
    assert sum(row.stage == "retry" for row in retried.traces) == 1
    failed = FailedProvider()
    fallback = S2DecisionExplainer(reader, corpus, failed).explain(
        request_id="outage", question="Why this action?", identity=identity(), retrieval_query=QUERY,
    )
    assert failed.calls == 1 and fallback.status == "answered" and fallback.fallback_used
    assert fallback.generation_mode == "deterministic-template-v1"


def test_s2_miss_or_invalid_event_abstains_without_policy_invention() -> None:
    reader, corpus = components()
    miss = S2DecisionExplainer(reader, corpus).explain(
        request_id="miss", question="Explain this decision.", identity=identity(),
        retrieval_query="zzzxxyy token-with-no-corpus-match",
    )
    assert miss.status == "abstained" and miss.abstention_reason == "retrieval-miss"
    assert miss.answer is None and miss.citations == () and miss.event_facts["event_id"]
    item = identity()
    invalid = S2DecisionExplainer(reader, corpus).explain(
        request_id="invalid", question="Explain this decision.",
        identity=EventIdentity(item.run_id, item.scenario_hash, "not-an-event"), retrieval_query=QUERY,
    )
    assert invalid.status == "abstained" and invalid.abstention_reason == "invalid-event-identity"
    assert invalid.answer is None and invalid.citations == ()


def test_s2_never_releases_unsupported_provider_prose() -> None:
    forbidden_claims = (
        "This saved lives.",
        "This is measured air quality.",
        "This proves deployment and live control.",
        "This controller is the winner with superior model performance.",
        "Policy requires automatic signal execution.",
    )
    reader, corpus = components()
    expected = S2DecisionExplainer(reader, corpus).explain(
        request_id="local-template", question="Explain this decision.",
        identity=identity(), retrieval_query=QUERY,
    )
    for index, claim in enumerate(forbidden_claims):
        provider = UnsupportedClaimProvider(claim)
        result = S2DecisionExplainer(reader, corpus, provider).explain(
            request_id=f"unsupported-{index}", question="Explain this decision.",
            identity=identity(), retrieval_query=QUERY,
        )
        assert provider.calls == 1 and result.provider_attempts == 1
        assert result.status == "answered" and result.generation_mode == "provider-verified"
        assert result.answer == expected.answer
        assert claim not in result.answer


def test_s3_passes_only_all_supported_claims_and_otherwise_abstains() -> None:
    reader, _ = components()
    item = identity()
    event = reader.read_event(item)
    locked = json.loads(CONTRACT.read_text(encoding="utf-8"))["locked_inputs"]
    path = "harness/work/10f-graph-growth-benchmark/artifacts/decision_events.parquet"
    passed = S3EvidenceAuditor(reader).audit(
        request_id="audit-pass", identity=item,
        claims=(AuditClaim("action", "event-field", "accepted_action", event.accepted_action),
                AuditClaim("artifact", "artifact-hash", path, locked[path])),
    )
    assert passed.status == "pass" and len(passed.references) == 2 and not passed.failed_checks
    failed = S3EvidenceAuditor(reader).audit(
        request_id="audit-fail", identity=item,
        claims=(AuditClaim("wrong", "event-field", "reason_code", "INVENTED_REASON"),),
    )
    assert failed.status == "abstained" and failed.failed_checks == ("wrong",)
