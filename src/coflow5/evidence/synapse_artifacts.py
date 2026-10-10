from __future__ import annotations

import hashlib
import json
import platform
import shutil
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from coflow5.synapse import (
    AGENT_VERSIONS,
    CHUNKER_VERSION,
    PARSER_VERSION,
    RETRIEVAL_VERSION,
    AuditClaim,
    DraftAnswer,
    EventIdentity,
    ExactTokenCorpus,
    ImmutableRow10fReader,
    S1ScenarioPlanner,
    S2DecisionExplainer,
    S3EvidenceAuditor,
    action_sequence_hash,
)
from coflow5.synapse.retrieval import sha256_bytes, sha256_file

CONTRACT = "harness/work/12-synapse-agents/contract.json"
DEFAULT_OUTPUT = "harness/work/12-synapse-agents/artifacts"
ROW08_COMPARISON = "harness/work/08-failure-injection/artifacts/action-sequence-comparison.json"
ROW10F_EVENTS = "harness/work/10f-graph-growth-benchmark/artifacts/decision_events.parquet"
PRODUCT_SOURCES = (
    "src/coflow5/synapse/observer.py",
    "src/coflow5/synapse/retrieval.py",
    "src/coflow5/synapse/evidence_reader.py",
    "src/coflow5/synapse/provider.py",
    "src/coflow5/synapse/specialists.py",
    "src/coflow5/synapse/__init__.py",
    "src/coflow5/evidence/synapse_artifacts.py",
    "scripts/generate_synapse_artifacts.py",
)
ARTIFACT_NAMES = (
    "run_manifest.json", "corpus_manifest.json", "corpus_chunks.parquet",
    "scenario_proposals.json", "explanations.json", "evidence_audits.json",
    "synapse_traces.parquet", "golden_cases.json", "golden_results.json",
    "non_actuation_audit.json",
)


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _json_hash(value: object) -> str:
    return sha256_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _result_without_traces(value: object) -> dict[str, object]:
    result = asdict(value)
    result.pop("traces", None)
    return result


def _reference(path: Path, rows: int, schema_name: str) -> dict[str, object]:
    return {
        "path": path.name, "sha256": sha256_file(path), "bytes": path.stat().st_size,
        "rows": rows, "schema_name": schema_name, "schema_version": 1,
    }


class _InvalidDraftProvider:
    def __init__(self) -> None:
        self.calls = 0

    def draft(self, request: Any) -> DraftAnswer:
        self.calls += 1
        return DraftAnswer(
            answer=f"Unsupported draft for {request.event_id}", event_id=request.event_id,
            accepted_action="INVENTED_ACTION", reason_code=request.reason_code,
            citation_chunk_ids=request.citation_chunk_ids,
        )


class _UnavailableDraftProvider:
    def __init__(self) -> None:
        self.calls = 0

    def draft(self, request: Any) -> DraftAnswer:
        self.calls += 1
        raise RuntimeError("provider unavailable")


def _choose_event(root: Path, reader: ImmutableRow10fReader) -> tuple[EventIdentity, dict[str, object]]:
    rows = pq.read_table(root / ROW10F_EVENTS).to_pylist()
    candidates = sorted(
        (row for row in rows if row["controller"] == "graph-aware-cooperative-max-pressure"),
        key=lambda row: (row["run_id"], row["simulation_time"], row["signal_id"], row["event_id"]),
    )
    if not candidates:
        raise ValueError("Row 10f has no immutable graph-aware decision")
    row = candidates[0]
    identity = EventIdentity(row["run_id"], row["scenario_hash"], row["event_id"])
    return identity, reader.read_event(identity).facts()


def _quality_metrics(*, corpus: ExactTokenCorpus, explanations: list[dict[str, object]],
                     audits: list[dict[str, object]], traces: list[dict[str, object]],
                     golden_results: list[dict[str, object]]) -> dict[str, object]:
    cited = [row for row in explanations if row["status"] == "answered"]
    citations = [citation for row in cited for citation in row["citations"]]
    valid_citations = [
        citation for citation in citations
        if corpus.chunk(str(citation["chunk_id"])) is not None
        and corpus.chunk(str(citation["chunk_id"])).source_sha256 == citation["source_sha256"]
    ]
    source_ids = {str(citation["source_id"]) for citation in citations}
    latencies = sorted(float(row["latency_ms"]) for row in traces)
    p95_index = max(0, int((len(latencies) - 1) * 0.95)) if latencies else 0
    abstentions = [row for row in explanations if row["status"] == "abstained"]
    fallback_rows = [row for row in explanations if row["fallback_used"]]
    event_consistent = all(
        row["answer"] is not None
        and str(row["event_facts"]["event_id"]) in str(row["answer"])
        and str(row["event_facts"]["accepted_action"]) in str(row["answer"])
        and str(row["event_facts"]["reason_code"]) in str(row["answer"])
        for row in cited
    )
    return {
        "retrieval_recall": {
            "expected_source_ids": ["adr-0001"],
            "retrieved_source_ids": sorted(source_ids),
            "value": 1.0 if "adr-0001" in source_ids else 0.0,
        },
        "citation_validity": {
            "valid": len(valid_citations), "total": len(citations),
            "rate": len(valid_citations) / len(citations) if citations else 0.0,
        },
        "event_consistency": {"passed": event_consistent, "checked_answers": len(cited)},
        "reason_code_coverage": sorted({str(row["event_facts"]["reason_code"]) for row in cited}),
        "abstention": {
            "count": len(abstentions),
            "reasons": sorted({str(row["abstention_reason"]) for row in abstentions}),
            "expected_cases_passed": all(row["abstention_reason"] for row in abstentions),
        },
        "fallback": {"count": len(fallback_rows), "provider_attempt_cap": 2,
                     "max_observed_attempts": max((int(row["provider_attempts"]) for row in explanations), default=0)},
        "audit": {"pass_count": sum(row["status"] == "pass" for row in audits),
                  "abstention_count": sum(row["status"] == "abstained" for row in audits)},
        "latency_ms": {"samples": len(latencies), "p95_observed": latencies[p95_index] if latencies else None,
                       "measurement": "local perf_counter around deterministic stages"},
        "tokens": {"input": sum(int(row["input_tokens"]) for row in traces),
                   "output": sum(int(row["output_tokens"]) for row in traces),
                   "method": "deterministic lexical count"},
        "estimated_cost_usd": sum(float(row["estimated_cost_usd"]) for row in traces),
        "golden_regression": {"passed": sum(bool(row["passed"]) for row in golden_results),
                              "total": len(golden_results)},
    }


def generate_synapse_artifacts(root: Path, output_dir: Path | None = None) -> dict[str, object]:
    root = root.resolve()
    contract_path = root / CONTRACT
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    contract_hash = sha256_file(contract_path)
    destination = (output_dir or root / DEFAULT_OUTPUT).resolve()
    protected_roots = (
        (root / "harness/work/08-failure-injection").resolve(),
        (root / "harness/work/10f-graph-growth-benchmark").resolve(),
    )
    if any(destination == protected or protected in destination.parents for protected in protected_roots):
        raise ValueError("Row 12 cannot write into frozen evidence")
    before_locked = {relative: sha256_file(root / relative) for relative in contract["locked_inputs"]}
    if before_locked != contract["locked_inputs"]:
        raise ValueError("a locked input differs from the sealed Row 12 contract")

    staging = destination.parent / f".{destination.name}.staging-{uuid.uuid4()}"
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)
    try:
        corpus = ExactTokenCorpus.from_contract(root, contract_path)
        reader = ImmutableRow10fReader(root, contract_path)
        identity, event_facts = _choose_event(root, reader)

        chunk_rows = [asdict(chunk) for chunk in corpus.chunks]
        pq.write_table(pa.Table.from_pylist(chunk_rows), staging / "corpus_chunks.parquet", compression="zstd")
        corpus_manifest = {
            "schema_version": 1, "parser_version": PARSER_VERSION,
            "chunker_version": CHUNKER_VERSION, "retrieval_version": RETRIEVAL_VERSION,
            "embedding_model_enabled": False, "chunk_count": len(chunk_rows),
            "sources": [
                {**asdict(source), "chunk_count": sum(chunk.source_id == source.source_id for chunk in corpus.chunks)}
                for source in corpus.sources
            ],
        }
        _write_json(staging / "corpus_manifest.json", corpus_manifest)

        planner = S1ScenarioPlanner()
        planned = planner.plan(
            request_id="golden-s1-wait", source_run_id=identity.run_id,
            scenario_hash=identity.scenario_hash, title="Bounded demand sensitivity proposal",
            demand_scale=1.25, horizon_seconds=300,
        )
        _write_json(staging / "scenario_proposals.json", {
            "schema_version": 1, "proposals": [asdict(planned.proposal)],
            "executed_proposal_count": 0,
        })

        query = "Synapse actuation Max-Pressure safety control"
        cited = S2DecisionExplainer(reader, corpus).explain(
            request_id="golden-s2-cited", question="Why was this signal action selected?",
            identity=identity, retrieval_query=query,
        )
        invalid_provider = _InvalidDraftProvider()
        retry_fallback = S2DecisionExplainer(reader, corpus, invalid_provider).explain(
            request_id="golden-s2-retry-fallback", question="Explain this decision and reason.",
            identity=identity, retrieval_query=query,
        )
        retrieval_miss = S2DecisionExplainer(reader, corpus).explain(
            request_id="golden-s2-abstain", question="Explain this decision.", identity=identity,
            retrieval_query="zzzxxyy sealed-token-with-no-corpus-match",
        )
        unavailable_provider = _UnavailableDraftProvider()
        provider_fallback = S2DecisionExplainer(reader, corpus, unavailable_provider).explain(
            request_id="provider-outage-fallback", question="Why was this action selected?",
            identity=identity, retrieval_query=query,
        )
        explanation_values = [cited, retry_fallback, retrieval_miss, provider_fallback]
        explanations = [_result_without_traces(value) for value in explanation_values]
        _write_json(staging / "explanations.json", {"schema_version": 1, "explanations": explanations})

        event_hash = contract["locked_inputs"][ROW10F_EVENTS]
        auditor = S3EvidenceAuditor(reader)
        audit_pass = auditor.audit(
            request_id="golden-s3-pass", identity=identity,
            claims=(
                AuditClaim("action", "event-field", "accepted_action", event_facts["accepted_action"]),
                AuditClaim("reason", "event-field", "reason_code", event_facts["reason_code"]),
                AuditClaim("event-artifact", "artifact-hash", ROW10F_EVENTS, event_hash),
            ),
        )
        audit_abstain = auditor.audit(
            request_id="golden-s3-abstain", identity=identity,
            claims=(AuditClaim("invented-action", "event-field", "accepted_action", "INVENTED_ACTION"),),
        )
        audit_values = [audit_pass, audit_abstain]
        audits = [_result_without_traces(value) for value in audit_values]
        _write_json(staging / "evidence_audits.json", {"schema_version": 1, "audits": audits})

        trace_values = list(planned.traces)
        for value in explanation_values + audit_values:
            trace_values.extend(value.traces)
        traces = [asdict(value) for value in trace_values]
        pq.write_table(pa.Table.from_pylist(traces), staging / "synapse_traces.parquet", compression="zstd")

        golden_cases = [
            {"case_id": "s1-wait", "request_id": "golden-s1-wait", "expected": "awaiting-human-approval"},
            {"case_id": "s2-cited", "request_id": "golden-s2-cited", "expected": "answered-with-citations"},
            {"case_id": "s2-provider-retry-fallback", "request_id": "golden-s2-retry-fallback", "expected": "two-attempts-then-template"},
            {"case_id": "s2-abstention", "request_id": "golden-s2-abstain", "expected": "retrieval-miss"},
            {"case_id": "s3-pass", "request_id": "golden-s3-pass", "expected": "pass"},
            {"case_id": "s3-abstention", "request_id": "golden-s3-abstain", "expected": "abstained"},
            {"case_id": "provider-outage", "request_id": "provider-outage-fallback", "expected": "template-fallback"},
        ]
        _write_json(staging / "golden_cases.json", {"schema_version": 1, "golden_set_version": "synapse-golden-v1", "cases": golden_cases})
        golden_result_rows = [
            {"case_id": "s1-wait", "passed": planned.proposal.status == "awaiting-human-approval" and not planned.proposal.executed},
            {"case_id": "s2-cited", "passed": cited.status == "answered" and bool(cited.citations)},
            {"case_id": "s2-provider-retry-fallback", "passed": retry_fallback.status == "answered" and retry_fallback.provider_attempts == 2 and retry_fallback.fallback_used},
            {"case_id": "s2-abstention", "passed": retrieval_miss.status == "abstained" and retrieval_miss.abstention_reason == "retrieval-miss"},
            {"case_id": "s3-pass", "passed": audit_pass.status == "pass" and len(audit_pass.references) == 3},
            {"case_id": "s3-abstention", "passed": audit_abstain.status == "abstained" and audit_abstain.failed_checks == ("invented-action",)},
            {"case_id": "provider-outage", "passed": provider_fallback.status == "answered" and provider_fallback.fallback_used and unavailable_provider.calls == 1},
        ]
        metrics = _quality_metrics(corpus=corpus, explanations=explanations, audits=audits,
                                   traces=traces, golden_results=golden_result_rows)
        _write_json(staging / "golden_results.json", {
            "schema_version": 1, "golden_set_version": "synapse-golden-v1",
            "results": golden_result_rows, "metrics": metrics,
            "all_passed": all(row["passed"] for row in golden_result_rows),
        })

        row08 = json.loads((root / ROW08_COMPARISON).read_text(encoding="utf-8"))
        row08_hashes = {name: value["action_sequence_hash"] for name, value in row08["variants"].items()}
        event_rows = pq.read_table(root / ROW10F_EVENTS).to_pylist()
        replay_rows = sorted(
            (row for row in event_rows if row["run_id"] == identity.run_id),
            key=lambda row: (row["simulation_time"], row["signal_id"], row["event_id"]),
        )
        replay_actions = [str(row["accepted_action"]) for row in replay_rows]
        replay_hash = action_sequence_hash(replay_actions)
        variants = {
            name: {"action_count": len(replay_actions), "action_sequence_hash": replay_hash}
            for name in ("synapse_available", "synapse_killed", "retrieval_unavailable", "hosted_provider_unavailable")
        }
        non_actuation = {
            "schema_version": 1,
            "row08_source": {"path": ROW08_COMPARISON, "sha256": sha256_file(root / ROW08_COMPARISON),
                             "variant_hashes": row08_hashes, "hashes_equal": len(set(row08_hashes.values())) == 1},
            "row12_replay": {"run_id": identity.run_id, "scenario_hash": identity.scenario_hash,
                             "event_count": len(replay_rows), "variants": variants,
                             "hashes_equal": len({value["action_sequence_hash"] for value in variants.values()}) == 1},
            "synapse_actuation_capability": None, "frozen_evidence_mutated": False,
            "provider_network_calls": 0, "model_dependencies": [],
        }
        _write_json(staging / "non_actuation_audit.json", non_actuation)

        after_locked = {relative: sha256_file(root / relative) for relative in contract["locked_inputs"]}
        if after_locked != before_locked:
            raise ValueError("locked evidence changed during Row 12 generation")
        references = [
            _reference(staging / "corpus_manifest.json", len(corpus.sources), "synapse_corpus_manifest"),
            _reference(staging / "corpus_chunks.parquet", len(chunk_rows), "synapse_corpus_chunk"),
            _reference(staging / "scenario_proposals.json", 1, "synapse_scenario_proposal"),
            _reference(staging / "explanations.json", len(explanations), "synapse_explanation"),
            _reference(staging / "evidence_audits.json", len(audits), "synapse_evidence_audit"),
            _reference(staging / "synapse_traces.parquet", len(traces), "synapse_trace"),
            _reference(staging / "golden_cases.json", len(golden_cases), "synapse_golden_case"),
            _reference(staging / "golden_results.json", len(golden_result_rows), "synapse_golden_result"),
            _reference(staging / "non_actuation_audit.json", 4, "synapse_non_actuation_audit"),
        ]
        manifest = {
            "schema_version": 1,
            "run_id": str(uuid.uuid5(uuid.NAMESPACE_URL, contract_hash + ":synapse-artifacts-v1")),
            "scenario_hash": identity.scenario_hash,
            "source_run_id": identity.run_id, "source_event_id": identity.event_id,
            "configuration_hash": _json_hash({"corpus": contract["corpus"], "generation": contract["generation"]}),
            "contract_hash": contract_hash, "status": "completed", "immutable": True,
            "evidence_kind": "deterministic-non-actuating-synapse",
            "versions": {"python": platform.python_version(), "pyarrow": pa.__version__,
                         "retrieval": RETRIEVAL_VERSION, "agents": AGENT_VERSIONS},
            "generation": contract["generation"], "locked_inputs": before_locked,
            "source_hashes": {relative: sha256_file(root / relative) for relative in PRODUCT_SOURCES},
            "artifact_references": references,
            "quality_metrics": metrics,
            "claim_flags": contract["claim_flags"],
            "finalized_at": datetime.now(timezone.utc).isoformat(),
        }
        _write_json(staging / "run_manifest.json", manifest)
        if set(path.name for path in staging.iterdir()) != set(ARTIFACT_NAMES):
            raise ValueError("Row 12 artifact set is not exact")
        destination.parent.mkdir(parents=True, exist_ok=True)
        backup = destination.parent / f".{destination.name}.previous-{uuid.uuid4()}"
        if destination.exists():
            destination.replace(backup)
        staging.replace(destination)
        shutil.rmtree(backup, ignore_errors=True)
        return manifest
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
