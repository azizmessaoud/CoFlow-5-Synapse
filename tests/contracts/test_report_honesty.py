from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from coflow5.evaluation import generate_evaluation_artifacts

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "harness/work/09-eval-harness/artifacts"


@pytest.fixture(scope="module", autouse=True)
def generated_row09_artifacts() -> None:
    generate_evaluation_artifacts(ROOT)


def test_every_claim_has_canonical_identity_and_join_audit_is_clean() -> None:
    report = json.loads((ARTIFACTS / "evaluation-report.json").read_text(encoding="utf-8"))
    manifests = {}
    for path in (ROOT / "harness/work").glob("0[4-8]-*/artifacts/*run_manifest.json"):
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifests[manifest["run_id"]] = manifest
    for claim in report["claims"]:
        assert claim["classification"] in {"requirement", "directional", "exploratory"}
        assert claim["evidence_refs"]
        for ref in claim["evidence_refs"]:
            assert ref["run_id"] in manifests
            assert ref["scenario_hash"] == manifests[ref["run_id"]]["scenario_hash"]
    audit = json.loads((ARTIFACTS / "join-audit.json").read_text(encoding="utf-8"))
    assert audit["pass"] and sum(
        audit[key] for key in (
            "orphan_run_references", "orphan_scenario_references",
            "orphan_event_references", "orphan_message_references",
        )
    ) == 0


def test_proxy_and_emergency_claim_boundaries_are_explicit() -> None:
    report = json.loads((ARTIFACTS / "evaluation-report.json").read_text(encoding="utf-8"))
    boundaries = report["claim_boundaries"]
    assert "emission proxies only" in boundaries["emissions"]
    assert "ambient sensor" in boundaries["emissions"]
    assert "simulated travel-time effects only" in boundaries["emergency"]
    assert "casualty" in boundaries["emergency"]
    sustainability = [
        row for row in pq.read_table(ARTIFACTS / "run_kpis.parquet").to_pylist()
        if row["metric_category"] == "sustainability-proxy"
    ]
    assert sustainability and sustainability[0]["metric_value"] is None
    assert "emission-proxy" in sustainability[0]["unit"]


def test_headline_is_paired_and_claim_scan_passes() -> None:
    report = json.loads((ARTIFACTS / "evaluation-report.json").read_text(encoding="utf-8"))
    headline = json.dumps(report["headline"]).lower()
    assert "paired/matched" in headline
    assert "best episode" not in headline
    assert report["null_results"] and report["negative_or_mixed_results"]
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_eval_claim_flags.py")],
        cwd=ROOT, capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
