from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from coflow5.evidence.professor_page import (
    EvidencePageError,
    forbid_protected_destination,
    generate_evidence_page_artifacts,
)

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = {
    "evidence-page.txt", "evidence-page.json", "input-audit.json", "page-manifest.json"
}


@pytest.fixture(scope="module")
def artifacts(tmp_path_factory: pytest.TempPathFactory) -> Path:
    destination = tmp_path_factory.mktemp("row10c") / "artifacts"
    generate_evidence_page_artifacts(ROOT, destination)
    return destination


def test_page_artifacts_are_exact_hash_bound_and_identity_separated(artifacts: Path) -> None:
    assert {path.name for path in artifacts.iterdir()} == REQUIRED
    page = json.loads((artifacts / "evidence-page.json").read_text(encoding="utf-8"))
    audit = json.loads((artifacts / "input-audit.json").read_text(encoding="utf-8"))
    manifest = json.loads((artifacts / "page-manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "completed" and manifest["immutable"] is True
    assert manifest["generator"] == "deterministic-template"
    refs = {row["path"]: row for row in manifest["artifact_references"]}
    assert set(refs) == REQUIRED - {"page-manifest.json"}
    for name, reference in refs.items():
        path = artifacts / name
        assert reference["sha256"] == "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        assert reference["bytes"] == path.stat().st_size
    assert audit["locked_input_count"] == 12
    assert audit["locked_input_hash_mismatches"] == 0
    assert audit["source_gates_green"] == 3
    assert audit["manifest_artifact_hash_mismatches"] == 0
    assert audit["identity_errors"] == 0
    sections = page["sections"]
    identities = {
        (sections[name]["run_id"], sections[name]["scenario_hash"])
        for name in ("traffic", "advice_fixture", "recovery_fixture")
    }
    assert len(identities) == 3
    assert page["page_id"] == manifest["page_id"]


def test_generation_and_cli_are_byte_deterministic(artifacts: Path, tmp_path: Path) -> None:
    second = tmp_path / "second"
    generate_evidence_page_artifacts(ROOT, second)
    for name in REQUIRED:
        assert (artifacts / name).read_bytes() == (second / name).read_bytes()
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/show_evidence_page.py")],
        cwd=ROOT, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == (artifacts / "evidence-page.txt").read_text(encoding="utf-8")
    assert result.stderr == ""


def test_page_claims_preserve_mixed_result_missing_values_and_limits(artifacts: Path) -> None:
    text = (artifacts / "evidence-page.txt").read_text(encoding="utf-8")
    page = json.loads((artifacts / "evidence-page.json").read_text(encoding="utf-8"))
    comparison = page["sections"]["traffic"]["comparison"]
    assert [row["completed_trips"] for row in comparison] == [71, 84, 70]
    assert page["sections"]["traffic"]["same_run_request_detail"] == {
        "accepted_requests": "not in this run",
        "rejected_requests": "not in this run",
        "reason_codes": "not in this run",
    }
    assert page["winner_claim"] is None
    assert page["one_seed_only"] is True
    assert page["significance_test_performed"] is False
    assert "Max-Pressure reproduces the bounded Row 05 advisory fixture" in text
    assert "No winner announced." in text


def test_all_frozen_pack_destinations_are_rejected_without_writes(tmp_path: Path) -> None:
    names = (
        "02-evidence-bundle", "03-safety-mask", "04-baselines", "05-max-pressure",
        "06-message-board", "07-a2-a3", "08-failure-injection", "09-eval-harness",
        "10-a4-a5", "10b-max-pressure-trip-kpis",
    )
    for name in names:
        target = (ROOT / "harness/work" / name).resolve()
        with pytest.raises(EvidencePageError, match="frozen evidence pack"):
            forbid_protected_destination(ROOT, target)
        with pytest.raises(EvidencePageError, match="frozen evidence pack"):
            forbid_protected_destination(ROOT, target / "nested-row10c")
    allowed = tmp_path / "artifacts"
    forbid_protected_destination(ROOT, allowed.resolve())
    assert not allowed.exists()



def test_page_sources_have_no_control_llm_or_network_runtime() -> None:
    import ast

    paths = (
        ROOT / "src/coflow5/evidence/professor_page.py",
        ROOT / "scripts/generate_evidence_page.py",
        ROOT / "scripts/show_evidence_page.py",
    )
    forbidden_imports = {
        "traci", "libsumo", "transformers", "langgraph", "openai",
        "anthropic", "requests", "httpx",
    }
    for path in paths:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        assert not (imported & forbidden_imports), path
        lowered = source.lower()
        assert "signal_executor" not in lowered and "max_pressure_runner" not in lowered
