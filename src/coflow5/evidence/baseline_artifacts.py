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
from typing import Any, Iterable, Mapping
from xml.etree import ElementTree

import pyarrow as pa
import pyarrow.parquet as pq

from coflow5.control.baselines import ActuatedController, FixedTimeController
from coflow5.evidence.schemas import RunManifest
from coflow5.sumo_adapter.baseline_runner import (
    BaselineEvidenceValidationError,
    BaselineRunResult,
    BaselineTripResult,
    run_baseline_scenario,
)

SUMO_RELEASE = "1.27.1"
EVALUATION_SEED = 37
HORIZON_SECONDS = 120.0
SCENARIO_FILES = (
    "scenarios/safety-mask/safety.net.xml",
    "scenarios/baselines/baselines.rou.xml",
    "scenarios/baselines/baselines.tls.xml",
    "scenarios/baselines/baselines.sumocfg",
)
SCENARIO_IDENTITY_FILES = (
    "scenarios/safety-mask/safety.net.xml",
    "scenarios/baselines/baselines.rou.xml",
)

BASELINE_KPI_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("controller", pa.string()),
    ("seed", pa.int64()), ("status", pa.string()), ("failure_reason", pa.string()),
    ("planned_trips", pa.int64()), ("completed_trips", pa.int64()),
    ("unfinished_trips", pa.int64()), ("completion_rate", pa.float64()),
    ("mean_duration_s", pa.float64()), ("p95_duration_s", pa.float64()),
    ("max_duration_s", pa.float64()), ("mean_waiting_time_s", pa.float64()),
    ("p95_waiting_time_s", pa.float64()), ("max_waiting_time_s", pa.float64()),
    ("total_time_loss_s", pa.float64()), ("standstill_vehicle_seconds", pa.int64()),
    ("vehicles_with_standstill", pa.int64()), ("teleport_events", pa.int64()),
    ("simulation_steps", pa.int64()), ("max_active_vehicles", pa.int64()),
    ("safety_event_count", pa.int64()), ("accepted_signal_commands", pa.int64()),
])
BASELINE_TRIP_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("controller", pa.string()),
    ("seed", pa.int64()), ("trip_id", pa.string()), ("flow_id", pa.string()),
    ("flow_index", pa.int64()), ("trip_status", pa.string()),
    ("departed_at_s", pa.float64()), ("arrived_at_s", pa.float64()),
    ("duration_s", pa.float64()), ("waiting_time_s", pa.float64()),
    ("time_loss_s", pa.float64()), ("standstill_seconds", pa.int64()),
    ("observed_at_s", pa.float64()), ("failure_reason", pa.string()),
])
SAFETY_EVENT_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("event_id", pa.string()),
    ("proposal_id", pa.string()), ("signal_id", pa.string()),
    ("simulation_time", pa.float64()), ("recorded_at", pa.string()),
    ("source", pa.string()), ("requested_phase_id", pa.string()),
    ("accepted", pa.bool_()), ("reason_code", pa.string()),
    ("provenance", pa.string()),
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


def _planned_trip_ids(route_file: Path) -> tuple[str, ...]:
    root = ElementTree.parse(route_file).getroot()
    trip_ids = [vehicle.attrib["id"] for vehicle in root.findall("vehicle")]
    for flow in root.findall("flow"):
        flow_id = flow.attrib["id"]
        count = int(flow.attrib["number"])
        trip_ids.extend(f"{flow_id}.{index}" for index in range(count))
    if len(trip_ids) != len(set(trip_ids)):
        raise BaselineEvidenceValidationError("planned trip ids are not unique")
    return tuple(trip_ids)


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(dict(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _failure_reason(exc: Exception) -> str:
    detail = str(exc).strip()
    return f"{type(exc).__name__}: {detail}" if detail else type(exc).__name__


def _native_command(sumo_binary: str, config: Path, seed: int) -> tuple[str, ...]:
    return (
        sumo_binary, "-c", str(config), "--seed", str(seed),
        "--no-step-log", "true", "--duration-log.disable", "true",
        "--time-to-teleport", "-1",
    )


def _terminal_result(
    *, controller: str, run_id: str, scenario_hash: str, seed: int,
    planned_trip_ids: tuple[str, ...], status: str, failure_reason: str,
    traci_version: str, command: tuple[str, ...],
) -> BaselineRunResult:
    trips = []
    for trip_id in planned_trip_ids:
        flow_id, separator, index = trip_id.rpartition(".")
        if not separator or not flow_id or not index.isdigit():
            flow_id, index = trip_id, "0"
        trips.append(BaselineTripResult(
            run_id=run_id, scenario_hash=scenario_hash, controller=controller, seed=seed,
            trip_id=trip_id, flow_id=flow_id, flow_index=int(index),
            trip_status="run-failed", departed_at_s=None, arrived_at_s=None,
            duration_s=None, waiting_time_s=None, time_loss_s=None,
            standstill_seconds=0, observed_at_s=0.0, failure_reason=failure_reason,
        ))
    return BaselineRunResult(
        run_id=run_id, scenario_hash=scenario_hash, controller=controller, seed=seed,
        status=status, failure_reason=failure_reason, simulation_begin=0.0,
        simulation_end=0.0, simulation_steps=0, planned_trips=len(planned_trip_ids),
        completed_trips=0, unfinished_trips=len(planned_trip_ids), completion_rate=0.0,
        mean_duration_s=0.0, p95_duration_s=0.0, max_duration_s=0.0,
        mean_waiting_time_s=0.0, p95_waiting_time_s=0.0,
        max_waiting_time_s=0.0, total_time_loss_s=0.0,
        standstill_vehicle_seconds=0, vehicles_with_standstill=0,
        teleport_events=0, max_active_vehicles=0, safety_event_count=0,
        accepted_signal_commands=0, traci_version=traci_version, command=command,
        trips=tuple(trips), safety_events=(), executed_commands=(),
        writer_count_by_signal={}, physically_conflicting_commands=0,
    )


def _validate_native_result(
    result: BaselineRunResult, planned_trip_ids: tuple[str, ...]
) -> None:
    errors: list[str] = []
    trips = result.trips
    planned_set = set(planned_trip_ids)
    trip_ids = [row.trip_id for row in trips]
    if len(trips) != len(planned_trip_ids) or set(trip_ids) != planned_set:
        errors.append("trip rows do not exactly cover planned flow ids")
    if len(trip_ids) != len(set(trip_ids)):
        errors.append("duplicate trip ids")
    if any(row.run_id != result.run_id or row.scenario_hash != result.scenario_hash for row in trips):
        errors.append("trip identity mismatch")
    allowed_statuses = {"completed", "active-at-horizon", "not-departed"}
    if any(row.trip_status not in allowed_statuses for row in trips):
        errors.append("invalid successful trip status")
    completed = sum(row.trip_status == "completed" for row in trips)
    if completed != result.completed_trips:
        errors.append("completed trip count mismatch")
    if len(trips) - completed != result.unfinished_trips:
        errors.append("unfinished trip count mismatch")
    if result.status != "completed" or result.failure_reason is not None:
        errors.append("native result is not a clean completed terminal result")

    event_ids = [event.event_id for event in result.safety_events]
    accepted_ids = {event.event_id for event in result.safety_events if event.accepted}
    rejected_ids = {event.event_id for event in result.safety_events if not event.accepted}
    command_ids = {command.event_id for command in result.executed_commands}
    if len(event_ids) != len(set(event_ids)):
        errors.append("duplicate safety event ids")
    if accepted_ids != command_ids:
        errors.append("accepted event and command ids do not reconcile")
    if rejected_ids & command_ids:
        errors.append("rejected event was executed")
    if rejected_ids:
        errors.append("successful baseline contains rejected command proposal")
    if result.writer_count_by_signal != {"J0": 1}:
        errors.append("baseline did not prove exactly one J0 writer")
    if result.physically_conflicting_commands:
        errors.append("physically conflicting command was executed")
    if len(result.safety_events) != result.safety_event_count:
        errors.append("safety event count mismatch")
    if len(result.executed_commands) != result.accepted_signal_commands:
        errors.append("accepted command count mismatch")
    if any(
        row.run_id != result.run_id or row.scenario_hash != result.scenario_hash
        for row in (*result.safety_events, *result.executed_commands)
    ):
        errors.append("safety identity mismatch")
    if errors:
        raise BaselineEvidenceValidationError("; ".join(errors))


def build_baseline_comparison(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Retain every terminal status while aggregating only explicit completed pairs."""
    materialized = [dict(row) for row in rows]
    labels = ("fixed-time", "actuated")
    statuses = ("completed", "failed", "invalid")
    cells: dict[tuple[str, int], list[dict[str, Any]]] = {}
    for row in materialized:
        status = str(row["status"])
        reason = row.get("failure_reason")
        if status in {"failed", "invalid"} and not (isinstance(reason, str) and reason.strip()):
            raise BaselineEvidenceValidationError("terminal failed/invalid row lacks failure_reason")
        cells.setdefault((str(row["scenario_hash"]), int(row["seed"])), []).append(row)

    pair_cells: list[dict[str, Any]] = []
    metric_deltas: list[dict[str, Any]] = []
    metric_names = (
        "mean_duration_s", "p95_duration_s", "mean_waiting_time_s",
        "p95_waiting_time_s", "standstill_vehicle_seconds", "teleport_events",
        "completion_rate", "unfinished_trips",
    )
    for (scenario_hash, seed), cell_rows in sorted(cells.items()):
        by_controller = {str(row["controller"]): row for row in cell_rows}
        missing = [label for label in labels if label not in by_controller]
        completed_pair = not missing and all(
            by_controller[label]["status"] == "completed" for label in labels
        )
        pair_cells.append({
            "scenario_hash": scenario_hash,
            "seed": seed,
            "controller_labels": sorted(by_controller),
            "missing_controller_labels": missing,
            "complete_pair": not missing,
            "included_in_metric_comparison": completed_pair,
            "exclusion_reason": None if completed_pair else (
                "missing-controller" if missing else "non-completed-status"
            ),
        })
        if completed_pair:
            fixed = by_controller["fixed-time"]
            actuated = by_controller["actuated"]
            metric_deltas.append({
                "scenario_hash": scenario_hash,
                "seed": seed,
                "actuated_minus_fixed": {
                    name: float(actuated[name]) - float(fixed[name]) for name in metric_names
                },
            })

    visible_runs = [{
        "run_id": row["run_id"], "scenario_hash": row["scenario_hash"],
        "seed": int(row["seed"]), "controller": row["controller"],
        "status": row["status"], "failure_reason": row.get("failure_reason"),
        "unfinished_trips": int(row.get("unfinished_trips", 0)),
        "completion_rate": float(row.get("completion_rate", 0.0)),
    } for row in materialized]
    status_counts = {
        status: sum(row["status"] == status for row in materialized) for status in statuses
    }
    return {
        "schema_version": 1,
        "comparison_scope": "fixed-time-versus-actuated-only",
        "controller_labels": list(labels),
        "pairing_keys": ["scenario_hash", "seed"],
        "common_evaluation_seeds": sorted({int(row["seed"]) for row in materialized}),
        "matched_scenario_hashes": sorted({str(row["scenario_hash"]) for row in materialized}),
        "pair_cells": pair_cells,
        "all_cells_paired": bool(pair_cells) and all(cell["complete_pair"] for cell in pair_cells),
        "visible_runs": visible_runs,
        "status_counts": status_counts,
        "failed_run_count": status_counts["failed"],
        "invalid_run_count": status_counts["invalid"],
        "unfinished_trip_count": sum(int(row.get("unfinished_trips", 0)) for row in materialized),
        "metric_definitions": {
            "tail": "P95 and maximum over completed-trip raw duration and waiting-time rows",
            "standstill": "sum of trip-level seconds with speed below 0.1 m/s",
            "teleports": "SUMO starting-teleport events; zero remains visible",
            "completion": "completed trips divided by all 84 planned flow IDs",
            "unfinished": "active-at-horizon plus not-departed trip rows",
            "failed_invalid": "both labels stay visible; non-completed cells are explicitly excluded from deltas",
        },
        "metric_deltas": metric_deltas,
        "claim_boundary": "No learned-controller or specialist value claim is made by this artifact.",
    }


def _kpi_row(result: BaselineRunResult) -> dict[str, Any]:
    source = asdict(result)
    return {name: source.get(name) for name in BASELINE_KPI_SCHEMA.names} | {"schema_version": 1}


def _artifact_reference(path: Path, rows: int, schema_name: str) -> dict[str, Any]:
    return {
        "path": path.name, "sha256": _hash_file(path), "bytes": path.stat().st_size,
        "rows": rows, "schema_name": schema_name, "schema_version": 1,
    }


def _run_audit(result: BaselineRunResult) -> dict[str, Any]:
    event_ids = [event.event_id for event in result.safety_events]
    accepted_ids = {event.event_id for event in result.safety_events if event.accepted}
    rejected_ids = {event.event_id for event in result.safety_events if not event.accepted}
    command_ids = {command.event_id for command in result.executed_commands}
    one_writer = result.writer_count_by_signal == {"J0": 1}
    completed_valid = (
        result.status == "completed"
        and one_writer
        and not rejected_ids
        and accepted_ids == command_ids
        and len(event_ids) == len(set(event_ids))
        and result.physically_conflicting_commands == 0
    )
    return {
        "run_id": result.run_id,
        "scenario_hash": result.scenario_hash,
        "controller": result.controller,
        "status": result.status,
        "failure_reason": result.failure_reason,
        "actual_traci_execution": result.status == "completed",
        "writer_count_by_signal": result.writer_count_by_signal,
        "one_writer_per_signal": one_writer,
        "event_count": len(event_ids),
        "accepted_count": len(accepted_ids),
        "rejected_count": len(rejected_ids),
        "executed_command_count": len(command_ids),
        "duplicate_event_ids": len(event_ids) - len(set(event_ids)),
        "accepted_without_command": len(accepted_ids - command_ids),
        "command_without_accepted_event": len(command_ids - accepted_ids),
        "rejected_executed_actions": len(rejected_ids & command_ids),
        "illegal_executed_actions": len(rejected_ids & command_ids) + result.physically_conflicting_commands,
        "physically_conflicting_executed_actions": result.physically_conflicting_commands,
        "safety_reconciliation_valid": completed_valid if result.status == "completed" else None,
    }


def _publish_directory(staging: Path, destination: Path) -> None:
    backup = destination.parent / f".{destination.name}.previous-{uuid.uuid4()}"
    moved_old = False
    try:
        if destination.exists():
            destination.replace(backup)
            moved_old = True
        staging.replace(destination)
    except Exception:
        if moved_old and backup.exists() and not destination.exists():
            backup.replace(destination)
        raise
    else:
        if moved_old:
            shutil.rmtree(backup, ignore_errors=True)


def generate_baseline_artifacts(root: Path, output_dir: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    if platform.system() != "Windows" or sys.version_info[:2] != (3, 11):
        raise RuntimeError("row 04 requires native Windows Python 3.11")
    if not os.environ.get("SUMO_HOME"):
        raise RuntimeError("SUMO_HOME is required")
    sumo_binary = shutil.which("sumo")
    if not sumo_binary:
        raise RuntimeError("native sumo.exe is required")
    detected_sumo = _sumo_version(sumo_binary)
    if detected_sumo != SUMO_RELEASE:
        raise RuntimeError(f"expected SUMO {SUMO_RELEASE}, found {detected_sumo}")

    destination = (output_dir or root / "harness/work/04-baselines/artifacts").resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    for pattern in (f".{destination.name}.staging-*", f".{destination.name}.previous-*"):
        for stale in destination.parent.glob(pattern):
            shutil.rmtree(stale, ignore_errors=True)
    staging = destination.parent / f".{destination.name}.staging-{uuid.uuid4()}"
    staging.mkdir()
    scenario_hash = _scenario_hash(root)
    planned_trip_ids = _planned_trip_ids(root / "scenarios/baselines/baselines.rou.xml")
    controllers = (FixedTimeController(), ActuatedController())
    started_at: dict[str, str] = {}
    finished_at: dict[str, str] = {}
    wall_seconds: dict[str, float] = {}
    results: list[BaselineRunResult] = []
    config = root / "scenarios/baselines/baselines.sumocfg"
    network = root / "scenarios/safety-mask/safety.net.xml"
    traci_package_version = importlib.metadata.version("traci")
    try:
        for controller in controllers:
            run_id = str(uuid.uuid4())
            started_at[controller.label] = _now()
            run_started_perf = time.perf_counter()
            try:
                result = run_baseline_scenario(
                    sumo_binary=sumo_binary,
                    config=config,
                    network_file=network,
                    controller=controller,
                    run_id=run_id,
                    scenario_hash=scenario_hash,
                    seed=EVALUATION_SEED,
                    planned_trip_ids=planned_trip_ids,
                    horizon_seconds=HORIZON_SECONDS,
                )
                _validate_native_result(result, planned_trip_ids)
            except Exception as exc:
                status = "invalid" if isinstance(exc, BaselineEvidenceValidationError) else "failed"
                result = _terminal_result(
                    controller=controller.label, run_id=run_id, scenario_hash=scenario_hash,
                    seed=EVALUATION_SEED, planned_trip_ids=planned_trip_ids,
                    status=status, failure_reason=_failure_reason(exc),
                    traci_version=traci_package_version,
                    command=_native_command(sumo_binary, config, EVALUATION_SEED),
                )
            finally:
                wall_seconds[controller.label] = time.perf_counter() - run_started_perf
                finished_at[controller.label] = _now()
            results.append(result)

        kpi_rows = [_kpi_row(result) for result in results]
        trip_rows = [
            {"schema_version": 1, **asdict(trip)}
            for result in results for trip in result.trips
        ]
        event_rows = [
            {"schema_version": 1, **asdict(event)}
            for result in results for event in result.safety_events
        ]
        command_rows = [
            {"schema_version": 1, **asdict(command)}
            for result in results for command in result.executed_commands
        ]
        pq.write_table(
            pa.Table.from_pylist(kpi_rows, schema=BASELINE_KPI_SCHEMA),
            staging / "run_kpis.parquet", compression="zstd",
        )
        pq.write_table(
            pa.Table.from_pylist(trip_rows, schema=BASELINE_TRIP_SCHEMA),
            staging / "baseline_trips.parquet", compression="zstd",
        )
        pq.write_table(
            pa.Table.from_pylist(event_rows, schema=SAFETY_EVENT_SCHEMA),
            staging / "safety_events.parquet", compression="zstd",
        )
        pq.write_table(
            pa.Table.from_pylist(command_rows, schema=EXECUTED_COMMAND_SCHEMA),
            staging / "executed_commands.parquet", compression="zstd",
        )
        audit = {
            "schema_version": 1,
            "scenario_hash": scenario_hash,
            "seed": EVALUATION_SEED,
            "planned_trip_ids": list(planned_trip_ids),
            "planned_trip_count": len(planned_trip_ids),
            "runs": [_run_audit(result) for result in results],
        }
        _write_json(staging / "baseline-audit.json", audit)

        references = [
            _artifact_reference(staging / "run_kpis.parquet", len(kpi_rows), "paired_baseline_run_kpi"),
            _artifact_reference(staging / "baseline_trips.parquet", len(trip_rows), "baseline_trip_evidence"),
            _artifact_reference(staging / "safety_events.parquet", len(event_rows), "baseline_safety_event"),
            _artifact_reference(staging / "executed_commands.parquet", len(command_rows), "baseline_executed_command"),
            _artifact_reference(staging / "baseline-audit.json", len(results), "baseline_reconciliation_audit"),
        ]
        kpi_reference = references[0]
        version_record = {
            "python": platform.python_version(), "sumo": detected_sumo,
            "traci": traci_package_version, "coflow5": "0.1.0",
            "duckdb": importlib.metadata.version("duckdb"),
            "pyarrow": importlib.metadata.version("pyarrow"),
            "pydantic": importlib.metadata.version("pydantic"),
        }
        manifests: list[dict[str, Any]] = []
        for result in results:
            configuration = {
                "controller": result.controller, "seed": result.seed,
                "horizon_seconds": HORIZON_SECONDS,
                "safety_plan": "controlled-cross-v1",
            }
            manifest = {
                "schema_version": 1, "run_id": result.run_id,
                "scenario_hash": result.scenario_hash,
                "configuration_hash": _json_hash(configuration),
                "scenario_files": list(SCENARIO_FILES), "versions": version_record,
                "seeds": {"sumo": result.seed, "evaluation": result.seed},
                "status": result.status, "failure_reason": result.failure_reason,
                "timings": {
                    "started_at": started_at[result.controller],
                    "finished_at": finished_at[result.controller],
                    "wall_seconds": wall_seconds[result.controller],
                    "simulation_begin": result.simulation_begin,
                    "simulation_end": result.simulation_end,
                    "simulation_steps": result.simulation_steps,
                },
                "backend": "traci", "controller": result.controller,
                "source_revision": _source_revision(root),
                "native_command": list(result.command),
                "artifact_references": references,
                "finalized_at": _now(), "immutable": True,
            }
            RunManifest.model_validate(manifest)
            manifests.append(manifest)
            _write_json(staging / f"{result.controller}-run_manifest.json", manifest)

        comparison = build_baseline_comparison(kpi_rows)
        comparison.update({
            "generated_at": _now(),
            "manifest_run_ids": [manifest["run_id"] for manifest in manifests],
            "kpi_artifact": kpi_reference,
            "artifact_references": references,
        })
        if not comparison["all_cells_paired"]:
            raise BaselineEvidenceValidationError(
                f"baseline labels are not paired: {comparison['pair_cells']}"
            )
        _write_json(staging / "baseline-comparison.json", comparison)
        _publish_directory(staging, destination)
        return comparison
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
