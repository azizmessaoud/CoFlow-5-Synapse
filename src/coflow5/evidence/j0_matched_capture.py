from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import sys
import uuid
from collections.abc import Iterable
from dataclasses import asdict
from pathlib import Path
from typing import Any

from coflow5.control.baselines import ActuatedController, FixedTimeController
from coflow5.evidence.baseline_artifacts import _planned_trip_ids, _scenario_hash
from coflow5.sumo_adapter.baseline_runner import run_baseline_scenario
from coflow5.sumo_adapter.max_pressure_trip_runner import (
    run_native_max_pressure_trip_scenario,
)

DEFAULT_SEEDS = (37, 41, 43, 47, 53)
HORIZON_SECONDS = 120.0


def _hash_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _run_row(result: Any, *, controller: str | None = None) -> dict[str, Any]:
    if controller == "cooperative-max-pressure":
        return {
            **dict(result.kpis),
            "run_id": result.run_id,
            "scenario_hash": result.scenario_hash,
            "seed": result.seed,
            "controller": controller,
            "status": "completed",
        }
    row = asdict(result)
    row.pop("trips", None)
    row["status"] = str(row.get("status", "completed"))
    return row


def _atomic_write(path: Path, value: dict[str, Any]) -> None:
    staging = path.parent / f".{path.name}.staging-{uuid.uuid4()}"
    staging.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    staging.replace(path)


def capture_j0_matched_runs(
    root: Path,
    *,
    seeds: Iterable[int] = DEFAULT_SEEDS,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Capture native three-controller rows for every declared J0 seed.

    This writes a summary beside the immutable per-run evidence produced by the
    native runners. It never overwrites the locked Row 04 or Row 05 packs.
    """
    root = root.resolve()
    selected_seeds = tuple(dict.fromkeys(int(seed) for seed in seeds))
    if len(selected_seeds) < len(DEFAULT_SEEDS):
        raise ValueError("J0 completion capture requires at least five seeds")
    if any(seed < 0 for seed in selected_seeds):
        raise ValueError("J0 seeds must be non-negative")
    if platform.system() != "Windows" or sys.version_info[:2] != (3, 11):
        raise RuntimeError("J0 matched capture requires native Windows Python 3.11")
    if not os.environ.get("SUMO_HOME"):
        raise RuntimeError("SUMO_HOME is required")
    sumo_binary = shutil.which("sumo")
    if not sumo_binary:
        raise RuntimeError("native sumo.exe is required")

    scenario_hash = _scenario_hash(root)
    planned_trip_ids = _planned_trip_ids(root / "scenarios/baselines/baselines.rou.xml")
    rows: list[dict[str, Any]] = []
    for seed in selected_seeds:
        seed_dir = (output_dir or root / "harness/work/10e/artifacts") / f"seed-{seed}"
        seed_dir.mkdir(parents=True, exist_ok=True)
        for controller in (FixedTimeController(), ActuatedController()):
            result = run_baseline_scenario(
                sumo_binary=sumo_binary,
                config=root / "scenarios/baselines/baselines.sumocfg",
                network_file=root / "scenarios/safety-mask/safety.net.xml",
                controller=controller,
                run_id=str(uuid.uuid4()),
                scenario_hash=scenario_hash,
                seed=seed,
                planned_trip_ids=planned_trip_ids,
                horizon_seconds=HORIZON_SECONDS,
            )
            rows.append(_run_row(result))
        result = run_native_max_pressure_trip_scenario(
            sumo_binary=sumo_binary,
            config=root / "scenarios/max-pressure/max-pressure.sumocfg",
            network_file=root / "scenarios/safety-mask/safety.net.xml",
            run_id=str(uuid.uuid4()),
            scenario_hash=scenario_hash,
            seed=seed,
            planned_trip_ids=planned_trip_ids,
            horizon_seconds=HORIZON_SECONDS,
        )
        rows.append(_run_row(result, controller="cooperative-max-pressure"))

    capture = {
        "schema_version": 1,
        "status": "captured_pending_audit",
        "scenario_hash": scenario_hash,
        "seeds": list(selected_seeds),
        "controllers": ["fixed-time", "actuated", "cooperative-max-pressure"],
        "planned_trip_count": len(planned_trip_ids),
        "runs": rows,
        "source_inputs": {
            "baselines_routes": _hash_file(root / "scenarios/baselines/baselines.rou.xml"),
            "network": _hash_file(root / "scenarios/safety-mask/safety.net.xml"),
        },
        "claim_boundary": (
            "Native SUMO observations only; no deployment, lives-saved, or "
            "measured-air-quality claim."
        ),
    }
    destination = (output_dir or root / "harness/work/10e/artifacts") / "matched-runs.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(destination, capture)
    return capture
