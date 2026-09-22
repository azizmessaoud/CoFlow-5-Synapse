from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from pathlib import Path

import pytest

from coflow5.smoke import FROZEN_SCENARIO_FILES, scenario_hash

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "harness" / "work" / "01-smoke-test" / "artifacts"


@pytest.fixture(scope="session", autouse=True)
def generated_smoke_evidence() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_native_smoke.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def load_json(name: str) -> dict:
    return json.loads((ARTIFACTS / name).read_text(encoding="utf-8"))


def test_native_windows_python_311_and_exact_sumo_release() -> None:
    toolchain = load_json("toolchain.json")
    assert platform.system() == "Windows"
    assert sys.version_info[:2] == (3, 11)
    assert toolchain["python_version"].startswith("3.11.")
    assert toolchain["sumo_version"] == "1.27.1"
    assert toolchain["sumo_gui_version"] == "1.27.1"
    assert Path(toolchain["sumo_home"]).is_dir()
    assert toolchain["traci_file"].endswith("traci\\__init__.py") or toolchain["traci_file"].endswith("traci/__init__.py")
    assert toolchain["package_versions"]["libsumo"] == "1.27.1"


def test_frozen_headless_run_emits_join_identity() -> None:
    manifest = load_json("run_manifest.json")
    assert manifest["status"] == "completed"
    assert manifest["run_id"]
    assert manifest["scenario_hash"] == scenario_hash(ROOT, FROZEN_SCENARIO_FILES)
    assert manifest["scenario_files"] == list(FROZEN_SCENARIO_FILES)
    log = (ARTIFACTS / "headless.log").read_text(encoding="utf-8")
    assert f"run_id={manifest['run_id']}" in log
    assert f"scenario_hash={manifest['scenario_hash']}" in log
    assert "exit_code=0" in log


def test_traci_and_libsumo_measurements_are_comparable() -> None:
    throughput = load_json("throughput.json")
    assert throughput["scenario_hash"] == load_json("run_manifest.json")["scenario_hash"]
    assert throughput["comparison"]["same_scenario"] is True
    assert throughput["comparison"]["same_seed"] is True
    for backend in ("traci", "libsumo"):
        measurement = throughput["measurements"][backend]
        assert measurement["simulation_steps"] > 0
        assert measurement["wall_seconds"] > 0
        assert measurement["simulation_steps_per_wall_second"] > 0
        assert measurement["peak_memory_bytes"] > 0
        assert measurement["artifact_bytes"] > 0
    assert throughput["units"] == {
        "throughput": "simulation_steps/second",
        "peak_memory": "bytes",
        "artifact_size": "bytes",
    }


def test_gui_diagnosis_is_documented_but_not_a_batch_dependency() -> None:
    diagnosis = (ARTIFACTS / "gui-diagnosis.md").read_text(encoding="utf-8")
    assert "sumo-gui" in diagnosis
    assert "Exit code: `0`" in diagnosis
    assert "not a batch dependency" in diagnosis.lower()
    assert load_json("run_manifest.json")["native_command"][0].lower().endswith("python.exe")
    assert "docker" not in " ".join(load_json("run_manifest.json")["native_command"]).lower()
    assert "wsl" not in " ".join(load_json("run_manifest.json")["native_command"]).lower()


def test_all_contract_artifacts_exist_and_parse() -> None:
    expected = {"toolchain.json", "run_manifest.json", "throughput.json", "headless.log", "gui-diagnosis.md"}
    assert expected <= {path.name for path in ARTIFACTS.iterdir()}
    for name in ("toolchain.json", "run_manifest.json", "throughput.json"):
        assert load_json(name)
