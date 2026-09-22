from __future__ import annotations

import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from coflow5.evaluation import generate_evaluation_artifacts

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "harness/work/09-eval-harness/artifacts"
CONTROLLERS = {"fixed-time", "actuated", "cooperative-max-pressure"}


@pytest.fixture(scope="module", autouse=True)
def generated_row09_artifacts() -> None:
    generate_evaluation_artifacts(ROOT)


def test_required_controller_cells_have_common_scenario_and_seed() -> None:
    rows = pq.read_table(ARTIFACTS / "experiment-cells.parquet").to_pylist()
    core = [row for row in rows if row["cell_id"].startswith("core:")]
    assert {row["controller"] for row in core} == CONTROLLERS
    assert len({row["scenario_hash"] for row in core}) == 1
    assert {row["seed"] for row in core} == {37}
    assert len({row["cell_id"] for row in core}) == 3


def test_missing_max_pressure_trip_metrics_are_visible_not_imputed() -> None:
    cells = pq.read_table(ARTIFACTS / "experiment-cells.parquet").to_pylist()
    mp_cell = next(row for row in cells if row["cell_id"] == "core:cooperative-max-pressure:seed-37")
    assert mp_cell["source_status"] == "completed"
    assert mp_cell["cell_status"] == "invalid"
    assert mp_cell["reason_code"] == "MISSING_REQUIRED_TRAFFIC_KPIS"
    metrics = pq.read_table(ARTIFACTS / "run_kpis.parquet").to_pylist()
    mp_duration = next(
        row for row in metrics
        if row["controller"] == "cooperative-max-pressure"
        and row["metric_name"] == "mean_duration_s"
    )
    assert mp_duration["run_status"] == "invalid"
    assert mp_duration["metric_value"] is None
    assert mp_duration["exclusion_reason"] == "MISSING_REQUIRED_TRAFFIC_KPIS"


def test_only_completed_matched_evidence_enters_headline() -> None:
    report = json.loads((ARTIFACTS / "evaluation-report.json").read_text(encoding="utf-8"))
    cells = pq.read_table(ARTIFACTS / "experiment-cells.parquet").to_pylist()
    included = [row for row in cells if row["included_in_paired_headline"]]
    assert {row["controller"] for row in included} == {"fixed-time", "actuated"}
    assert all(row["cell_status"] == "completed" for row in included)
    assert report["headline"]["controller_cells"] == [
        "fixed-time", "actuated", "cooperative-max-pressure",
    ]
    assert report["claims"][0]["result"] == "mixed"
