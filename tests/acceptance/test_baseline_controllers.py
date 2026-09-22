from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pyarrow.parquet as pq
import pytest

import coflow5.evidence.baseline_artifacts as baseline_artifacts
from coflow5.control.baselines import (
    ActuatedController,
    BaselineObservation,
    FixedTimeController,
)

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "harness/work/04-baselines/artifacts"


@pytest.fixture(scope="session", autouse=True)
def generated_baseline_evidence() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/generate_baseline_artifacts.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "paired=True" in result.stdout


def _observation(phase: str, elapsed: float, ns: int, ew: int) -> BaselineObservation:
    return BaselineObservation(
        simulation_time=elapsed,
        current_phase_id=phase,
        phase_elapsed_seconds=elapsed,
        halting_by_approach={"north": ns, "south": 0, "east": ew, "west": 0},
    )


def test_fixed_time_and_actuated_policies_are_deterministic_and_distinct() -> None:
    fixed = FixedTimeController(green_seconds=15)
    actuated = ActuatedController(minimum_green_seconds=5, maximum_green_seconds=25)
    demand = _observation("NS_GREEN", 6, ns=0, ew=4)
    assert fixed.propose_phase(demand) is None
    assert actuated.propose_phase(demand) == "NS_YELLOW"
    assert fixed.propose_phase(_observation("NS_GREEN", 15, 4, 0)) == "NS_YELLOW"
    assert actuated.propose_phase(_observation("NS_GREEN", 25, 4, 0)) == "NS_YELLOW"
    assert fixed.propose_phase(_observation("NS_YELLOW", 2, 0, 0)) == "ALL_RED_TO_EW"
    assert actuated.propose_phase(_observation("ALL_RED_TO_EW", 1, 0, 0)) == "EW_GREEN"


def test_baseline_policies_have_no_raw_sumo_or_signal_write_capability() -> None:
    path = ROOT / "src/coflow5/control/baselines.py"
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_roots.add(node.module.split(".")[0])
    assert not ({"traci", "libsumo"} & imported_roots)
    assert "trafficlight" not in source.lower()
    assert ".set" not in source


def test_real_traci_runs_share_scenario_seed_and_use_safe_a1_commands() -> None:
    manifests = [
        json.loads((ARTIFACTS / f"{label}-run_manifest.json").read_text(encoding="utf-8"))
        for label in ("fixed-time", "actuated")
    ]
    assert {manifest["controller"] for manifest in manifests} == {"fixed-time", "actuated"}
    assert len({manifest["scenario_hash"] for manifest in manifests}) == 1
    assert {manifest["seeds"]["evaluation"] for manifest in manifests} == {37}
    assert all(manifest["backend"] == "traci" for manifest in manifests)
    assert all(manifest["status"] == "completed" for manifest in manifests)
    rows = pq.read_table(ARTIFACTS / "run_kpis.parquet").to_pylist()
    assert len(rows) == 2
    assert all(row["safety_event_count"] == row["accepted_signal_commands"] for row in rows)
    assert all(row["accepted_signal_commands"] > 0 for row in rows)


def test_comparison_reports_mean_tail_standstill_teleport_and_completion() -> None:
    comparison = json.loads(
        (ARTIFACTS / "baseline-comparison.json").read_text(encoding="utf-8")
    )
    rows = pq.read_table(ARTIFACTS / "run_kpis.parquet").to_pylist()
    required = {
        "mean_duration_s", "p95_duration_s", "max_duration_s",
        "mean_waiting_time_s", "p95_waiting_time_s", "max_waiting_time_s",
        "standstill_vehicle_seconds", "teleport_events", "completed_trips",
        "unfinished_trips", "completion_rate", "status", "failure_reason",
    }
    assert required <= set(rows[0])
    assert comparison["all_cells_paired"] is True
    assert comparison["failed_run_count"] == 0
    assert comparison["invalid_run_count"] == 0
    assert "failed_invalid" in comparison["metric_definitions"]
    assert all(0.0 <= row["completion_rate"] <= 1.0 for row in rows)



def test_injected_runner_failures_atomically_replace_old_success(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    destination = tmp_path / "artifacts"
    destination.mkdir()
    stale_success = destination / "old-success.json"
    stale_success.write_text('{"status":"completed"}\n', encoding="utf-8")

    monkeypatch.setenv("SUMO_HOME", str(tmp_path / "sumo"))
    monkeypatch.setattr(baseline_artifacts.platform, "system", lambda: "Windows")
    monkeypatch.setattr(baseline_artifacts.shutil, "which", lambda _name: "sumo.exe")
    monkeypatch.setattr(
        baseline_artifacts, "_sumo_version", lambda _binary: baseline_artifacts.SUMO_RELEASE
    )

    def injected_failure(**kwargs: object) -> object:
        controller = kwargs["controller"]
        message = f"injected {controller.label} runner failure"
        if controller.label == "actuated":
            raise baseline_artifacts.BaselineEvidenceValidationError(message)
        raise RuntimeError(message)

    monkeypatch.setattr(baseline_artifacts, "run_baseline_scenario", injected_failure)
    comparison = baseline_artifacts.generate_baseline_artifacts(ROOT, destination)

    assert not stale_success.exists()
    assert {path.name for path in destination.iterdir()} >= {
        "fixed-time-run_manifest.json",
        "actuated-run_manifest.json",
        "run_kpis.parquet",
        "baseline-comparison.json",
        "baseline_trips.parquet",
        "safety_events.parquet",
        "executed_commands.parquet",
        "baseline-audit.json",
    }
    rows = pq.read_table(destination / "run_kpis.parquet").to_pylist()
    failed_trips = pq.read_table(destination / "baseline_trips.parquet").to_pylist()
    assert len(failed_trips) == 168
    assert {row["trip_status"] for row in failed_trips} == {"run-failed"}
    assert all(row["failure_reason"] for row in failed_trips)
    assert {row["controller"] for row in failed_trips} == {"fixed-time", "actuated"}
    assert {row["controller"] for row in rows} == {"fixed-time", "actuated"}
    assert {row["controller"]: row["status"] for row in rows} == {
        "fixed-time": "failed",
        "actuated": "invalid",
    }
    assert all(row["failure_reason"] for row in rows)
    assert comparison["failed_run_count"] == 1
    assert comparison["invalid_run_count"] == 1
    assert comparison["metric_deltas"] == []
    assert comparison["pair_cells"][0]["included_in_metric_comparison"] is False
    assert comparison["pair_cells"][0]["exclusion_reason"] == "non-completed-status"
    expected_status = {"fixed-time": "failed", "actuated": "invalid"}
    for label in ("fixed-time", "actuated"):
        manifest = json.loads(
            (destination / f"{label}-run_manifest.json").read_text(encoding="utf-8")
        )
        assert manifest["status"] == expected_status[label]
        assert manifest["failure_reason"]
