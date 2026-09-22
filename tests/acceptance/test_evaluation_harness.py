from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from coflow5.evaluation import generate_evaluation_artifacts

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "harness/work/09-eval-harness/artifacts"
REQUIRED = {
    "experiment-cells.parquet", "run_kpis.parquet", "evaluation-report.json",
    "join-audit.json", "limitations.md",
}


@pytest.fixture(scope="module", autouse=True)
def generated_row09_artifacts() -> None:
    generate_evaluation_artifacts(ROOT)


def test_exact_atomic_artifact_set_and_zero_orphan_audit() -> None:
    assert {path.name for path in ARTIFACTS.iterdir()} == REQUIRED
    assert not list((ROOT / "harness/work").rglob(".artifacts.staging-*"))
    audit = json.loads((ARTIFACTS / "join-audit.json").read_text(encoding="utf-8"))
    assert audit["pass"] is True
    assert audit["canonical_manifest_count"] == 6
    assert audit["orphan_run_references"] == 0
    assert audit["orphan_scenario_references"] == 0
    assert audit["orphan_event_references"] == 0
    assert audit["orphan_message_references"] == 0
    assert all(not values for values in audit["orphans"].values())


def test_experiment_cells_span_all_contracted_dimensions() -> None:
    rows = pq.read_table(ARTIFACTS / "experiment-cells.parquet").to_pylist()
    assert rows
    assert {row["controller"] for row in rows} >= {
        "fixed-time", "actuated", "cooperative-max-pressure",
    }
    assert len({row["scenario"] for row in rows}) > 1
    assert len({row["demand_regime"] for row in rows}) > 1
    assert any(row["incident"] != "none" for row in rows)
    assert any(row["communication_fault"] != "none" for row in rows)
    assert {row["adviser_agent_enabled"] for row in rows} >= {True, False}
    assert any(row["controller_fault"] != "none" for row in rows)
    assert any(row["recovery_mode"] != "none" for row in rows)
    assert any(row["synapse_fault"] != "none" for row in rows)
    assert all(row["seed"] is not None for row in rows)
    assert all(
        row["reason_code"]
        for row in rows
        if row["cell_status"] in {"failed", "invalid"}
    )


def test_kpis_cover_required_families_and_retain_outcomes() -> None:
    rows = pq.read_table(ARTIFACTS / "run_kpis.parquet").to_pylist()
    assert {row["metric_category"] for row in rows} >= {
        "safety", "efficiency", "emergency", "pedestrian", "transit",
        "sustainability-proxy", "robustness", "reproducibility",
    }
    assert {row["classification"] for row in rows} == {
        "requirement", "directional", "exploratory",
    }
    names = {row["metric_name"] for row in rows}
    assert {
        "unfinished_trips", "teleport_events", "standstill_vehicle_seconds",
        "completion_rate", "mean_duration_s", "p95_duration_s", "max_duration_s",
    } <= names
    assert all(row["confidence_method"] and row["multiple_testing_status"] for row in rows)
    unavailable = [row for row in rows if not row["observed"]]
    assert unavailable and all(row["metric_value"] is None for row in unavailable)
    assert all(row["exclusion_reason"] for row in unavailable)


def test_report_retains_null_negative_and_limitations() -> None:
    report = json.loads((ARTIFACTS / "evaluation-report.json").read_text(encoding="utf-8"))
    assert report["headline"]["basis"] == "paired/matched canonical evidence only"
    assert report["null_results"]
    assert report["negative_or_mixed_results"]
    assert report["confidence_inputs"]["common_seed_count"] == 1
    assert report["experiment_summary"]["invalid_or_failed_cell_count"] > 0
    text = (ARTIFACTS / "limitations.md").read_text(encoding="utf-8")
    assert "MISSING_REQUIRED_TRAFFIC_KPIS" in text
    assert "emission proxy" in text
    assert "Mixed result retained" in text
