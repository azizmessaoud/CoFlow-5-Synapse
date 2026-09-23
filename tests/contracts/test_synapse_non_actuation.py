from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from coflow5.synapse import (
    ExplanationObserverBoundary,
    ImmutableDecisionView,
    action_sequence_hash,
)

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src/coflow5"
ARTIFACTS = ROOT / "harness/work/08-failure-injection/artifacts"
FORBIDDEN_FAMILIES = {"synapse", "retrieval", "provider", "specialists", "a2", "a3", "a4", "a5"}


def test_frozen_row08_non_actuation_input_matches_sealed_hash() -> None:
    contract = json.loads((ROOT / "harness/work/12-synapse-agents/contract.json").read_text(encoding="utf-8"))
    relative = "harness/work/08-failure-injection/artifacts/action-sequence-comparison.json"
    actual = "sha256:" + hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
    assert actual == contract["locked_inputs"][relative]


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    values: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.update(alias.name.lower() for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            values.add(node.module.lower())
    return values


def test_synapse_retrieval_provider_and_specialists_have_no_actuation_imports() -> None:
    violations: list[str] = []
    for path in SRC.rglob("*.py"):
        relative = path.relative_to(SRC)
        family = relative.parts[0] if len(relative.parts) > 1 else relative.stem
        if family not in FORBIDDEN_FAMILIES:
            continue
        imported = _imports(path)
        forbidden = {
            name for name in imported
            if name == "traci" or name.startswith("traci.")
            or name == "libsumo" or name.startswith("libsumo.")
            or "signal_executor" in name
        }
        if forbidden:
            violations.append(f"{relative}: {sorted(forbidden)}")
    assert not violations, "non-actuating boundary violation: " + "; ".join(violations)


def test_killed_observer_returns_visible_failure_without_action_callback() -> None:
    view = ImmutableDecisionView(
        run_id="run", scenario_hash="sha256:" + "c" * 64, event_id="event",
        simulation_time=1.0, selected_action="NS_GREEN",
        reason_code="MAX_PRESSURE_LOCAL_ONLY",
    )
    receipt = ExplanationObserverBoundary(None).observe_after_decision(view)
    assert receipt.observer_available is False
    assert receipt.explanation_status == "unavailable"
    assert receipt.failure_type == "ObserverUnavailable"
    assert action_sequence_hash([view.selected_action]) == action_sequence_hash(["NS_GREEN"])
    assert not hasattr(ExplanationObserverBoundary, "propose_phase")
    assert not hasattr(ExplanationObserverBoundary, "execute")


def test_synapse_provider_and_retrieval_outages_have_identical_action_hashes() -> None:
    comparison = json.loads(
        (ARTIFACTS / "action-sequence-comparison.json").read_text(encoding="utf-8")
    )
    audit = json.loads((ARTIFACTS / "recovery-audit.json").read_text(encoding="utf-8"))
    required = {
        "synapse_available", "synapse_killed", "retrieval_unavailable",
        "hosted_provider_unavailable",
    }
    assert set(comparison["variants"]) == required
    hashes = {
        value["action_sequence_hash"] for value in comparison["variants"].values()
    }
    sequences = {
        tuple(value["action_sequence"]) for value in comparison["variants"].values()
    }
    assert comparison["hashes_equal"] is True and len(hashes) == 1
    assert len(sequences) == 1
    assert comparison["observer_failures_visible"] is True
    assert audit["action_sequence_hashes_equal"] is True
    assert comparison["run_id"] == audit["run_id"]
    assert comparison["scenario_hash"] == audit["scenario_hash"]


def test_row12_paths_have_no_process_adapter_network_or_model_dependencies() -> None:
    forbidden_roots = {
        "traci", "libsumo", "subprocess", "socket", "requests", "urllib", "httpx",
        "openai", "anthropic", "transformers", "sentence_transformers", "torch",
        "langgraph", "pgvector",
    }
    violations: list[str] = []
    for path in (SRC / "synapse").rglob("*.py"):
        imported = _imports(path)
        forbidden = {
            name for name in imported
            if name.split(".")[0] in forbidden_roots or "sumo_adapter" in name
        }
        if forbidden:
            violations.append(f"{path.relative_to(SRC)}: {sorted(forbidden)}")
    assert not violations, "Row 12 dependency boundary violation: " + "; ".join(violations)


def test_row12_non_actuation_audit_retains_outage_hash_invariance(tmp_path: Path) -> None:
    from coflow5.evidence.synapse_artifacts import generate_synapse_artifacts

    artifacts = tmp_path / "artifacts"
    generate_synapse_artifacts(ROOT, artifacts)
    audit = json.loads((artifacts / "non_actuation_audit.json").read_text(encoding="utf-8"))
    row12_hashes = {
        value["action_sequence_hash"]
        for value in audit["row12_replay"]["variants"].values()
    }
    assert audit["row08_source"]["hashes_equal"] is True
    assert audit["row12_replay"]["hashes_equal"] is True
    assert len(row12_hashes) == 1
    assert audit["synapse_actuation_capability"] is None
    assert audit["frozen_evidence_mutated"] is False
