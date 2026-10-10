from __future__ import annotations

import json
import os
import platform
import shutil
import sys
import uuid
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from coflow5.control.max_pressure import AdvisoryRequest
from coflow5.evidence.baseline_artifacts import _planned_trip_ids, _scenario_hash
from coflow5.sumo_adapter.max_pressure_trip_runner import (
    run_native_max_pressure_trip_scenario,
)

ABLATION_AGENTS = ("A2", "A3", "A4", "A5")
DEFAULT_SEEDS = (37, 41, 43, 47, 53)
HORIZON_SECONDS = 120.0


def _row(result: Any, *, agent: str, enabled: bool) -> dict[str, Any]:
    event_ids = sorted(
        str(item.event_id)
        for item in (*result.decisions, *result.safety_events, *result.executed_commands)
        if getattr(item, "event_id", None)
    )
    message_ids = sorted({
        str(message_id)
        for decision in result.decisions
        for message_id in decision.considered_message_ids
        if message_id
    })
    return {
        "agent": agent,
        "enabled": enabled,
        "run_id": result.run_id,
        "scenario_hash": result.scenario_hash,
        "seed": result.seed,
        "event_ids": event_ids,
        "message_ids": message_ids,
        "kpis": dict(result.kpis),
        "controller": "cooperative-max-pressure",
        "status": "completed",
    }


def capture_j0_ablation_runs(
    root: Path,
    *,
    seeds: Iterable[int] = DEFAULT_SEEDS,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Run native A1 with each specialist advisory source on and off."""
    root = root.resolve()
    selected_seeds = tuple(dict.fromkeys(int(seed) for seed in seeds))
    if len(selected_seeds) < 5:
        raise ValueError("J0 ablation capture requires at least five seeds")
    if platform.system() != "Windows" or sys.version_info[:2] != (3, 11):
        raise RuntimeError("J0 ablation capture requires native Windows Python 3.11")
    if not os.environ.get("SUMO_HOME") or not shutil.which("sumo"):
        raise RuntimeError("SUMO_HOME and native sumo.exe are required")

    scenario_hash = _scenario_hash(root)
    planned_trip_ids = _planned_trip_ids(root / "scenarios/baselines/baselines.rou.xml")
    rows: list[dict[str, Any]] = []
    for seed in selected_seeds:
        for agent in ABLATION_AGENTS:
            for enabled in (False, True):
                run_id = str(uuid.uuid4())
                advisories = (
                    (
                        AdvisoryRequest(
                            message_id=f"{agent.lower()}-ablation-{seed}",
                            run_id=run_id,
                            signal_id="J0",
                            requested_phase_id="NS_GREEN",
                            source=agent,
                            valid_from=0.0,
                            expires_at=HORIZON_SECONDS,
                            weight=0.5,
                        ),
                    )
                    if enabled
                    else ()
                )
                result = run_native_max_pressure_trip_scenario(
                    sumo_binary=shutil.which("sumo") or "sumo",
                    config=root / "scenarios/max-pressure/max-pressure.sumocfg",
                    network_file=root / "scenarios/safety-mask/safety.net.xml",
                    run_id=run_id,
                    scenario_hash=scenario_hash,
                    seed=seed,
                    planned_trip_ids=planned_trip_ids,
                    advisories=advisories,
                    horizon_seconds=HORIZON_SECONDS,
                )
                rows.append(_row(result, agent=agent, enabled=enabled))

    capture = {
        "schema_version": 1,
        "status": "captured_pending_audit",
        "scenario_hash": scenario_hash,
        "seeds": list(selected_seeds),
        "agents": list(ABLATION_AGENTS),
        "rows": rows,
        "claim_boundary": (
            "Native A1 advisory ablation evidence only; no deployment, "
            "lives-saved, or measured-air-quality claim."
        ),
    }
    destination = (output_dir or root / "harness/work/10e/artifacts") / "j0-ablations.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.with_name(f".{destination.name}.staging-{uuid.uuid4()}")
    staging.write_text(json.dumps(capture, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    staging.replace(destination)
    return capture
