from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from coflow5.evidence.schemas import RunManifest
from coflow5.sumo_adapter.safety_runner import (
    conflicting_green_pairs,
    run_native_safety_scenario,
)

SUMO_RELEASE = "1.27.1"
SCENARIO_FILES = (
    "scenarios/safety-mask/safety.nod.xml",
    "scenarios/safety-mask/safety.edg.xml",
    "scenarios/safety-mask/safety.con.xml",
    "scenarios/safety-mask/safety.net.xml",
    "scenarios/safety-mask/safety.tls.xml",
    "scenarios/safety-mask/safety.rou.xml",
    "scenarios/safety-mask/safety.sumocfg",
)

DECISION_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()), ("scenario_hash", pa.string()),
    ("event_id", pa.string()), ("proposal_id", pa.string()), ("signal_id", pa.string()),
    ("simulation_time", pa.float64()), ("recorded_at", pa.string()), ("source", pa.string()),
    ("requested_phase_id", pa.string()), ("accepted", pa.bool_()),
    ("reason_code", pa.string()), ("provenance", pa.string()),
])
EXECUTED_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()), ("scenario_hash", pa.string()),
    ("event_id", pa.string()), ("proposal_id", pa.string()), ("signal_id", pa.string()),
    ("simulation_time", pa.float64()), ("executed_at", pa.string()), ("source", pa.string()),
    ("phase_id", pa.string()), ("signal_state", pa.string()),
])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def _hash_file(path: Path) -> str:
    return _hash_bytes(path.read_bytes())


def _json_hash(value: Any) -> str:
    return _hash_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def _scenario_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for relative in SCENARIO_FILES:
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update((root / relative).read_bytes())
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def _sumo_version(binary: str) -> str:
    result = subprocess.run([binary, "--version"], capture_output=True, text=True, check=True)
    match = re.search(r"sumo\s+(\d+\.\d+\.\d+)", result.stdout + result.stderr)
    if not match:
        raise RuntimeError("could not parse SUMO version")
    return match.group(1)


def _source_revision(root: Path) -> str | None:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def generate_safety_artifacts(root: Path, output_dir: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    if platform.system() != "Windows" or sys.version_info[:2] != (3, 11):
        raise RuntimeError("row 03 requires native Windows Python 3.11")
    if not os.environ.get("SUMO_HOME"):
        raise RuntimeError("SUMO_HOME is required")
    sumo_binary = shutil.which("sumo")
    if not sumo_binary:
        raise RuntimeError("native sumo.exe is required")
    detected_sumo = _sumo_version(sumo_binary)
    if detected_sumo != SUMO_RELEASE:
        raise RuntimeError(f"expected SUMO {SUMO_RELEASE}, found {detected_sumo}")

    destination = (output_dir or root / "harness/work/03-safety-mask/artifacts").resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = destination.parent / f".{destination.name}.staging-{uuid.uuid4()}"
    staging.mkdir()
    run_id = str(uuid.uuid4())
    scenario_hash = _scenario_hash(root)
    started_at = _now()
    started_perf = time.perf_counter()
    try:
        native = run_native_safety_scenario(
            sumo_binary=sumo_binary,
            config=root / "scenarios/safety-mask/safety.sumocfg",
            network_file=root / "scenarios/safety-mask/safety.net.xml",
            run_id=run_id,
            scenario_hash=scenario_hash,
        )
        finished_at = _now()
        decision_rows = [{"schema_version": 1, **asdict(event)} for event in native.events]
        command_rows = [{"schema_version": 1, **asdict(command)} for command in native.commands]
        pq.write_table(pa.Table.from_pylist(decision_rows, schema=DECISION_SCHEMA), staging / "decision_events.parquet", compression="zstd")
        pq.write_table(pa.Table.from_pylist(command_rows, schema=EXECUTED_SCHEMA), staging / "executed_commands.parquet", compression="zstd")

        event_ids = [row["event_id"] for row in decision_rows]
        command_event_ids = [row["event_id"] for row in command_rows]
        rejected_ids = {row["event_id"] for row in decision_rows if not row["accepted"]}
        accepted_ids = {row["event_id"] for row in decision_rows if row["accepted"]}
        command_ids = set(command_event_ids)
        identity_errors = sum(
            row["run_id"] != run_id or row["scenario_hash"] != scenario_hash
            for row in decision_rows + command_rows
        )
        rejected_executed = rejected_ids & command_ids
        physical_conflict_details = []
        for row in command_rows:
            conflicts = conflicting_green_pairs(row["signal_state"], native.topology)
            if conflicts:
                physical_conflict_details.append({
                    "event_id": row["event_id"],
                    "signal_id": row["signal_id"],
                    "signal_state": row["signal_state"],
                    "conflicting_link_pairs": [list(pair) for pair in conflicts],
                })
        physical_illegal_ids = {row["event_id"] for row in physical_conflict_details}
        illegal_executed_ids = rejected_executed | physical_illegal_ids
        duplicate_event_ids = len(event_ids) - len(set(event_ids))
        one_writer_per_signal = (
            set(native.writer_count_by_signal) == {"J0"}
            and all(value == 1 for value in native.writer_count_by_signal.values())
        )
        audit = {
            "schema_version": 1,
            "valid": (
                not illegal_executed_ids
                and accepted_ids == command_ids
                and identity_errors == 0
                and duplicate_event_ids == 0
                and one_writer_per_signal
            ),
            "run_id": run_id,
            "scenario_hash": scenario_hash,
            "backend": "traci",
            "actual_traci_execution": True,
            "python_version": platform.python_version(),
            "sumo_version": detected_sumo,
            "traci_version": native.traci_version,
            "signal_ids": ["J0"],
            "controlled_link_mapping_validated": True,
            "controlled_links": [list(link) for link in native.topology.controlled_links],
            "conflicting_link_pairs": [
                list(pair) for pair in native.topology.conflicting_link_pairs
            ],
            "writer_count_by_signal": native.writer_count_by_signal,
            "one_writer_per_signal": one_writer_per_signal,
            "proposal_count": len(decision_rows),
            "event_count": len(event_ids),
            "accepted_count": len(accepted_ids),
            "rejected_count": len(rejected_ids),
            "executed_command_count": len(command_rows),
            "duplicate_event_ids": duplicate_event_ids,
            "identity_errors": identity_errors,
            "accepted_without_command": len(accepted_ids - command_ids),
            "command_without_accepted_event": len(command_ids - accepted_ids),
            "illegal_executed_actions": len(illegal_executed_ids),
            "physically_conflicting_executed_actions": len(physical_conflict_details),
            "physical_conflict_details": physical_conflict_details,
            "rejected_executed_event_ids": sorted(rejected_executed),
            "reason_codes": sorted({row["reason_code"] for row in decision_rows}),
            "human_override_events": sum(row["source"] == "human-override" for row in decision_rows),
            "initial_signal_state": native.initial_signal_state,
            "final_signal_state": native.final_signal_state,
            "sole_writer_component": "A1-owned adapter SignalExecutor",
        }
        _write_json(staging / "safety-audit.json", audit)
        references = []
        for name, rows, schema_name in (
            ("decision_events.parquet", len(decision_rows), "safety_decision_event"),
            ("executed_commands.parquet", len(command_rows), "executed_signal_command"),
            ("safety-audit.json", 1, "safety_audit"),
        ):
            path = staging / name
            references.append({
                "path": name, "sha256": _hash_file(path), "bytes": path.stat().st_size,
                "rows": rows, "schema_name": schema_name, "schema_version": 1,
            })
        configuration = {
            "controller": "a1-deterministic-safety-mask",
            "minimum_green_seconds": 5.0, "yellow_seconds": 2.0, "all_red_seconds": 1.0,
            "sumo_seed": 37,
        }
        manifest = {
            "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
            "configuration_hash": _json_hash(configuration), "scenario_files": list(SCENARIO_FILES),
            "versions": {
                "python": platform.python_version(), "sumo": detected_sumo,
                "traci": importlib.metadata.version("traci"), "coflow5": "0.1.0",
                "duckdb": importlib.metadata.version("duckdb"),
                "pyarrow": importlib.metadata.version("pyarrow"),
                "pydantic": importlib.metadata.version("pydantic"),
            },
            "seeds": {"sumo": 37}, "status": "completed",
            "timings": {
                "started_at": started_at, "finished_at": finished_at,
                "wall_seconds": time.perf_counter() - started_perf,
                "simulation_begin": native.simulation_begin, "simulation_end": native.simulation_end,
                "simulation_steps": native.simulation_steps,
            },
            "backend": "traci", "controller": "a1-deterministic-safety-mask",
            "source_revision": _source_revision(root),
            "native_command": [sys.executable, str(root / "scripts/generate_safety_artifacts.py")],
            "artifact_references": references, "finalized_at": _now(), "immutable": True,
        }
        RunManifest.model_validate(manifest)
        if not audit["valid"]:
            raise RuntimeError(f"safety audit failed: {audit}")
        _write_json(staging / "run_manifest.json", manifest)
        if destination.exists():
            shutil.rmtree(destination)
        staging.replace(destination)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
