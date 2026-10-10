from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from coflow5.evidence.synapse_artifacts import ARTIFACT_NAMES, generate_synapse_artifacts

ROOT = Path(__file__).resolve().parents[2]


def file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture(scope="module")
def artifacts(tmp_path_factory: pytest.TempPathFactory) -> Path:
    destination = tmp_path_factory.mktemp("row12-synapse") / "artifacts"
    generate_synapse_artifacts(ROOT, destination)
    return destination


def load(artifacts: Path, name: str):
    return json.loads((artifacts / name).read_text(encoding="utf-8"))


def test_exact_ten_artifacts_are_manifest_and_source_hash_bound(artifacts: Path) -> None:
    assert {path.name for path in artifacts.iterdir()} == set(ARTIFACT_NAMES)
    manifest = load(artifacts, "run_manifest.json")
    assert manifest["status"] == "completed" and manifest["immutable"] is True
    assert manifest["contract_hash"] == file_hash(ROOT / "harness/work/12-synapse-agents/contract.json")
    for reference in manifest["artifact_references"]:
        assert file_hash(artifacts / reference["path"]) == reference["sha256"]
    for path, expected in manifest["locked_inputs"].items():
        assert file_hash(ROOT / path) == expected
    for path, expected in manifest["source_hashes"].items():
        assert file_hash(ROOT / path) == expected


def test_every_explanation_audit_and_trace_has_zero_orphan_references(artifacts: Path) -> None:
    manifest = load(artifacts, "run_manifest.json")
    chunks = {row["chunk_id"] for row in pq.read_table(artifacts / "corpus_chunks.parquet").to_pylist()}
    explanations = load(artifacts, "explanations.json")["explanations"]
    audits = load(artifacts, "evidence_audits.json")["audits"]
    cases = {row["request_id"] for row in load(artifacts, "golden_cases.json")["cases"]}
    traces = pq.read_table(artifacts / "synapse_traces.parquet").to_pylist()
    assert all(row["request_id"] in cases for row in explanations + audits + traces)
    assert all(citation["chunk_id"] in chunks for row in explanations for citation in row["citations"])
    assert all(row["run_id"] == manifest["source_run_id"] for row in traces)
    assert all(row["scenario_hash"] == manifest["scenario_hash"] for row in traces)
    assert all(row["chunk_id"] is None or row["chunk_id"] in chunks for row in traces)
    assert {row["stage"] for row in traces} >= {"event-fetch", "retrieval", "generation", "verification", "retry", "fallback", "terminal"}
    assert all("secret" not in json.dumps(row).lower() for row in traces)


def test_golden_metrics_and_abstention_are_visible_without_invention(artifacts: Path) -> None:
    results = load(artifacts, "golden_results.json")
    metrics = results["metrics"]
    assert results["all_passed"] is True
    assert metrics["golden_regression"]["passed"] == metrics["golden_regression"]["total"] == 7
    assert metrics["retrieval_recall"]["value"] == 1.0
    assert metrics["citation_validity"]["rate"] == 1.0
    assert metrics["event_consistency"]["passed"] is True
    assert metrics["abstention"]["expected_cases_passed"] is True
    assert metrics["fallback"]["max_observed_attempts"] <= 2
    assert metrics["latency_ms"]["samples"] > 0
    assert metrics["tokens"]["input"] > 0 and metrics["estimated_cost_usd"] == 0.0
    assert load(artifacts, "scenario_proposals.json")["executed_proposal_count"] == 0


def test_row08_and_row12_action_hashes_are_invariant_across_outages(artifacts: Path) -> None:
    audit = load(artifacts, "non_actuation_audit.json")
    assert audit["row08_source"]["hashes_equal"] is True
    assert audit["row08_source"]["sha256"] == file_hash(ROOT / "harness/work/08-failure-injection/artifacts/action-sequence-comparison.json")
    assert audit["row12_replay"]["hashes_equal"] is True
    assert len({value["action_sequence_hash"] for value in audit["row12_replay"]["variants"].values()}) == 1
    assert audit["synapse_actuation_capability"] is None
    assert audit["frozen_evidence_mutated"] is False
    assert audit["provider_network_calls"] == 0 and audit["model_dependencies"] == []


def test_claim_flags_and_disabled_models_remain_explicit(artifacts: Path) -> None:
    manifest = load(artifacts, "run_manifest.json")
    corpus = load(artifacts, "corpus_manifest.json")
    text = json.dumps(manifest).lower()
    assert corpus["embedding_model_enabled"] is False
    assert manifest["generation"]["hosted_or_local_model"]["enabled"] is False
    assert manifest["generation"]["network_calls"] is False
    assert len(manifest["claim_flags"]) == 5
    assert "no lives saved" in text and "no measured air quality" in text and "no deployment" in text
