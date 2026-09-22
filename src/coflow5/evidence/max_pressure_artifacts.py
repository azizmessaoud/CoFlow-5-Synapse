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

from coflow5.control.max_pressure import AdvisoryRequest
from coflow5.evidence.schemas import RunManifest
from coflow5.sumo_adapter.max_pressure_runner import run_native_max_pressure_scenario

SUMO_RELEASE = "1.27.1"
EVALUATION_SEED = 37
SCENARIO_FILES = (
    "scenarios/safety-mask/safety.net.xml",
    "scenarios/baselines/baselines.rou.xml",
    "scenarios/max-pressure/max-pressure.tls.xml",
    "scenarios/max-pressure/max-pressure.sumocfg",
)
SCENARIO_IDENTITY_FILES = (
    "scenarios/safety-mask/safety.net.xml",
    "scenarios/baselines/baselines.rou.xml",
)
SOURCE_FILES = (
    "scripts/generate_max_pressure_artifacts.py",
    "src/coflow5/control/max_pressure.py",
    "src/coflow5/control/a1_controller.py",
    "src/coflow5/control/safety.py",
    "src/coflow5/sumo_adapter/max_pressure_runner.py",
    "src/coflow5/evidence/max_pressure_artifacts.py",
    "src/coflow5/evidence/schemas.py",
)

MAX_PRESSURE_DECISION_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("event_id", pa.string()),
    ("proposal_id", pa.string()), ("signal_id", pa.string()),
    ("simulation_time", pa.float64()), ("recorded_at", pa.string()),
    ("controller", pa.string()), ("current_phase_id", pa.string()),
    ("accepted_action", pa.string()), ("accepted_score", pa.float64()),
    ("rejected_alternatives", pa.list_(pa.string())),
    ("constraints", pa.list_(pa.string())), ("reason_code", pa.string()),
    ("considered_message_ids", pa.list_(pa.string())),
    ("safety_reason_code", pa.string()), ("action_scores_json", pa.string()),
    ("provenance", pa.string()),
])

MAX_PRESSURE_OBSERVATION_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("event_id", pa.string()),
    ("proposal_id", pa.string()), ("signal_id", pa.string()),
    ("simulation_time", pa.float64()), ("current_phase_id", pa.string()),
    ("phase_entered_at", pa.float64()), ("observed_signal_state", pa.string()),
    ("movement_inputs_json", pa.string()),
])

EXECUTED_COMMAND_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("event_id", pa.string()),
    ("proposal_id", pa.string()), ("signal_id", pa.string()),
    ("simulation_time", pa.float64()), ("executed_at", pa.string()),
    ("source", pa.string()), ("phase_id", pa.string()),
    ("signal_state", pa.string()),
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
    for relative in SCENARIO_IDENTITY_FILES:
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


def generate_max_pressure_artifacts(root: Path, output_dir: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    if platform.system() != "Windows" or sys.version_info[:2] != (3, 11):
        raise RuntimeError("row 05 requires native Windows Python 3.11")
    if not os.environ.get("SUMO_HOME"):
        raise RuntimeError("SUMO_HOME is required")
    sumo_binary = shutil.which("sumo")
    if not sumo_binary:
        raise RuntimeError("native sumo.exe is required")
    detected_sumo = _sumo_version(sumo_binary)
    if detected_sumo != SUMO_RELEASE:
        raise RuntimeError(f"expected SUMO {SUMO_RELEASE}, found {detected_sumo}")

    destination = (output_dir or root / "harness/work/05-max-pressure/artifacts").resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    for stale in destination.parent.glob(f".{destination.name}.staging-*"):
        shutil.rmtree(stale, ignore_errors=True)
    staging = destination.parent / f".{destination.name}.staging-{uuid.uuid4()}"
    staging.mkdir()
    run_id = str(uuid.uuid4())
    scenario_hash = _scenario_hash(root)
    messages = (
        AdvisoryRequest(
            message_id="row05-advisory-0001",
            run_id=run_id,
            signal_id="J0",
            requested_phase_id="NS_YELLOW",
            source="A2_EMERGENCY",
            valid_from=6.0,
            expires_at=12.0,
            weight=1.0,
        ),
    )
    started_at = _now()
    started_perf = time.perf_counter()
    try:
        native = run_native_max_pressure_scenario(
            sumo_binary=sumo_binary,
            config=root / "scenarios/max-pressure/max-pressure.sumocfg",
            run_id=run_id,
            scenario_hash=scenario_hash,
            seed=EVALUATION_SEED,
            advisories=messages,
        )
        finished_at = _now()
        decision_rows = []
        for decision in native.decisions:
            value = asdict(decision)
            value["schema_version"] = 1
            value["controller"] = "cooperative-max-pressure"
            value["action_scores_json"] = json.dumps(
                value.pop("action_scores"), sort_keys=True, separators=(",", ":")
            )
            decision_rows.append(value)
        observation_rows = []
        for observation in native.observations:
            value = asdict(observation)
            value["schema_version"] = 1
            value["movement_inputs_json"] = json.dumps(
                value.pop("movements"), sort_keys=True, separators=(",", ":")
            )
            observation_rows.append(value)
        command_rows = []
        for command in native.executed_commands:
            value = asdict(command)
            value["schema_version"] = 1
            command_rows.append(value)

        pq.write_table(
            pa.Table.from_pylist(decision_rows, schema=MAX_PRESSURE_DECISION_SCHEMA),
            staging / "decision_events.parquet",
            compression="zstd",
        )
        pq.write_table(
            pa.Table.from_pylist(observation_rows, schema=MAX_PRESSURE_OBSERVATION_SCHEMA),
            staging / "observations.parquet",
            compression="zstd",
        )
        pq.write_table(
            pa.Table.from_pylist(command_rows, schema=EXECUTED_COMMAND_SCHEMA),
            staging / "executed_commands.parquet",
            compression="zstd",
        )

        event_ids = [row["event_id"] for row in decision_rows]
        decision_by_event = {row["event_id"]: row for row in decision_rows}
        observation_by_event = {row["event_id"]: row for row in observation_rows}
        command_by_event = {row["event_id"]: row for row in command_rows}
        safety_by_event = {event.event_id: event for event in native.safety_events}
        considered_ids = {
            message_id
            for row in decision_rows
            for message_id in row["considered_message_ids"]
        }
        message_catalog = [
            {
                "message_id": message.message_id,
                "run_id": message.run_id,
                "signal_id": message.signal_id,
                "source": message.source,
                "requested_phase_id": message.requested_phase_id,
                "valid_from": message.valid_from,
                "expires_at": message.expires_at,
                "weight": message.weight,
            }
            for message in messages
        ]
        catalog_ids = {message["message_id"] for message in message_catalog}
        identity_errors = sum(
            row["run_id"] != run_id or row["scenario_hash"] != scenario_hash
            for row in (*decision_rows, *observation_rows, *command_rows)
        )
        unresolved_message_ids = sorted(considered_ids - catalog_ids)
        wrong_run_messages = sorted(
            message["message_id"] for message in message_catalog
            if message["run_id"] != run_id
        )
        has_without_messages = any(not row["considered_message_ids"] for row in decision_rows)
        has_with_messages = any(row["considered_message_ids"] for row in decision_rows)
        event_sets_match = (
            set(decision_by_event)
            == set(observation_by_event)
            == set(command_by_event)
            == set(safety_by_event)
        )
        action_join_errors = 0
        observation_join_errors = 0
        for event_id, decision in decision_by_event.items():
            command = command_by_event.get(event_id)
            safety = safety_by_event.get(event_id)
            observation = observation_by_event.get(event_id)
            if (
                command is None
                or safety is None
                or command["phase_id"] != decision["accepted_action"]
                or safety.requested_phase_id != decision["accepted_action"]
                or command["proposal_id"] != decision["proposal_id"]
                or command["source"] != "a1-flow"
            ):
                action_join_errors += 1
            if (
                observation is None
                or observation["proposal_id"] != decision["proposal_id"]
                or observation["simulation_time"] != decision["simulation_time"]
                or observation["current_phase_id"] != decision["current_phase_id"]
            ):
                observation_join_errors += 1
        source_hashes = {relative: _hash_file(root / relative) for relative in SOURCE_FILES}
        valid = (
            bool(decision_rows)
            and len(event_ids) == len(set(event_ids))
            and identity_errors == 0
            and not unresolved_message_ids
            and not wrong_run_messages
            and has_without_messages
            and has_with_messages
            and event_sets_match
            and action_join_errors == 0
            and observation_join_errors == 0
            and native.safety_event_count == native.accepted_command_count == len(decision_rows)
            and native.writer_count_by_signal == {"J0": 1}
            and all(row["safety_reason_code"] == "ACCEPTED" for row in decision_rows)
            and all(row["constraints"] and row["reason_code"] for row in decision_rows)
        )
        audit = {
            "schema_version": 1,
            "valid": valid,
            "run_id": run_id,
            "scenario_hash": scenario_hash,
            "controller": "cooperative-max-pressure",
            "controller_required": True,
            "backend": "traci",
            "actual_traci_execution": valid and bool(command_rows),
            "reinforcement_learning_required": False,
            "dqn_dependency": False,
            "torch_dependency": False,
            "first_recovery_target_for_optional_dqn": "cooperative-max-pressure",
            "recovery_ladder": ["cooperative-max-pressure", "actuated", "fixed-time"],
            "signal_owner": "A1_FLOW",
            "submission_path": ["CooperativeMaxPressureController", "A1FlowController", "DeterministicSafetyMask", "SignalExecutor"],
            "writer_count_by_signal": native.writer_count_by_signal,
            "one_writer_per_signal": native.writer_count_by_signal == {"J0": 1},
            "decision_count": len(decision_rows),
            "observation_count": len(observation_rows),
            "safety_event_count": native.safety_event_count,
            "accepted_command_count": len(command_rows),
            "duplicate_event_ids": len(event_ids) - len(set(event_ids)),
            "identity_errors": identity_errors,
            "event_sets_match": event_sets_match,
            "action_join_errors": action_join_errors,
            "observation_join_errors": observation_join_errors,
            "executor_readback_verified": True,
            "runs_without_advisory_messages": has_without_messages,
            "runs_with_advisory_messages": has_with_messages,
            "message_catalog": message_catalog,
            "considered_message_ids": sorted(considered_ids),
            "unresolved_message_ids": unresolved_message_ids,
            "wrong_run_message_ids": wrong_run_messages,
            "score_inputs": ["local_upstream_queue", "local_downstream_queue", "current_phase_timing", "downstream_capacity", "bounded_valid_advisory_requests"],
            "maximum_advisory_bonus": 3.0,
            "reason_codes": sorted({row["reason_code"] for row in decision_rows}),
            "python_version": platform.python_version(),
            "sumo_version": detected_sumo,
            "traci_version": native.traci_version,
            "source_hashes": source_hashes,
            "sumo_command": list(native.command),
            "claim_boundary": "No RL result, lives-saved claim, or measured-air-quality claim is made.",
        }
        _write_json(staging / "controller-audit.json", audit)
        references = []
        for name, count, schema_name in (
            ("decision_events.parquet", len(decision_rows), "max_pressure_decision_event"),
            ("observations.parquet", len(observation_rows), "max_pressure_observation"),
            ("executed_commands.parquet", len(command_rows), "executed_signal_command"),
            ("controller-audit.json", 1, "max_pressure_controller_audit"),
        ):
            path = staging / name
            references.append({
                "path": name,
                "sha256": _hash_file(path),
                "bytes": path.stat().st_size,
                "rows": count,
                "schema_name": schema_name,
                "schema_version": 1,
            })
        configuration = {
            "controller": "cooperative-max-pressure",
            "safety_plan": "controlled-cross-v1",
            "maximum_advisory_bonus": 3.0,
            "seed": EVALUATION_SEED,
        }
        manifest = {
            "schema_version": 1,
            "run_id": run_id,
            "scenario_hash": scenario_hash,
            "configuration_hash": _json_hash(configuration),
            "scenario_files": list(SCENARIO_FILES),
            "versions": {
                "python": platform.python_version(),
                "sumo": detected_sumo,
                "traci": importlib.metadata.version("traci"),
                "coflow5": "0.1.0",
                "duckdb": importlib.metadata.version("duckdb"),
                "pyarrow": importlib.metadata.version("pyarrow"),
                "pydantic": importlib.metadata.version("pydantic"),
            },
            "seeds": {"sumo": EVALUATION_SEED, "evaluation": EVALUATION_SEED},
            "status": "completed",
            "timings": {
                "started_at": started_at,
                "finished_at": finished_at,
                "wall_seconds": time.perf_counter() - started_perf,
                "simulation_begin": native.simulation_begin,
                "simulation_end": native.simulation_end,
                "simulation_steps": native.simulation_steps,
            },
            "backend": "traci",
            "controller": "cooperative-max-pressure",
            "source_revision": _source_revision(root),
            "source_hashes": source_hashes,
            "native_command": [sys.executable, str(root / "scripts/generate_max_pressure_artifacts.py")],
            "sumo_command": list(native.command),
            "artifact_references": references,
            "finalized_at": _now(),
            "immutable": True,
        }
        RunManifest.model_validate(manifest)
        if not valid:
            raise RuntimeError(f"controller audit failed: {audit}")
        _write_json(staging / "run_manifest.json", manifest)
        if destination.exists():
            shutil.rmtree(destination)
        staging.replace(destination)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
