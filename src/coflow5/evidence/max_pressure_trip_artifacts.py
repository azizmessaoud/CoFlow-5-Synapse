from __future__ import annotations

import hashlib
import importlib.metadata
import json
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
from typing import Any, Mapping
from xml.etree import ElementTree

import pyarrow as pa
import pyarrow.parquet as pq

from coflow5.control.max_pressure import AdvisoryRequest
from coflow5.evidence.baseline_artifacts import BASELINE_KPI_SCHEMA, BASELINE_TRIP_SCHEMA
from coflow5.sumo_adapter.max_pressure_trip_runner import run_native_max_pressure_trip_scenario

TRIP_SCHEMA = BASELINE_TRIP_SCHEMA
RUN_KPI_SCHEMA = BASELINE_KPI_SCHEMA
SUMO_RELEASE = "1.27.1"
SEED = 37
HORIZON_SECONDS = 120.0
CONTRACT_PATH = "harness/work/10b-max-pressure-trip-kpis/contract.json"
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
    "scripts/generate_max_pressure_trip_artifacts.py",
    "src/coflow5/evidence/max_pressure_trip_artifacts.py",
    "src/coflow5/sumo_adapter/max_pressure_trip_runner.py",
    "src/coflow5/control/max_pressure.py",
    "src/coflow5/control/a1_controller.py",
    "src/coflow5/control/safety.py",
    "src/coflow5/sumo_adapter/safety_runner.py",
    "src/coflow5/sumo_adapter/smoke_backends.py",
    "src/coflow5/evidence/baseline_artifacts.py",
)
PROTECTED_PACK_NAMES = (
    "02-evidence-bundle", "03-safety-mask", "04-baselines", "05-max-pressure",
    "06-message-board", "07-a2-a3", "08-failure-injection", "09-eval-harness",
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _json_hash(value: Mapping[str, Any]) -> str:
    payload = json.dumps(dict(value), sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(dict(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _scenario_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for relative in SCENARIO_IDENTITY_FILES:
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update((root / relative).read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def _planned_trip_ids(route_file: Path) -> tuple[str, ...]:
    xml = ElementTree.parse(route_file).getroot()
    ids = [vehicle.attrib["id"] for vehicle in xml.findall("vehicle")]
    for flow in xml.findall("flow"):
        ids.extend(f"{flow.attrib['id']}.{index}" for index in range(int(flow.attrib["number"])))
    if not ids or len(ids) != len(set(ids)):
        raise RuntimeError("planned trip IDs must be non-empty and unique")
    return tuple(ids)


def _sumo_version(binary: str) -> str:
    result = subprocess.run([binary, "--version"], capture_output=True, text=True, check=True)
    match = re.search(r"sumo\s+(\d+\.\d+\.\d+)", result.stdout + result.stderr)
    if not match:
        raise RuntimeError("could not parse SUMO version")
    return match.group(1)


def _source_revision(root: Path) -> str | None:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def _artifact_reference(path: Path, rows: int, schema_name: str) -> dict[str, Any]:
    return {
        "path": path.name,
        "sha256": _hash(path),
        "bytes": path.stat().st_size,
        "rows": rows,
        "schema_name": schema_name,
        "schema_version": 1,
    }


def _publish_atomic(staging: Path, destination: Path) -> None:
    backup = destination.parent / f".{destination.name}.previous-{uuid.uuid4()}"
    moved = False
    try:
        if destination.exists():
            destination.replace(backup)
            moved = True
        staging.replace(destination)
    except Exception:
        if moved and backup.exists() and not destination.exists():
            backup.replace(destination)
        raise
    else:
        if moved:
            shutil.rmtree(backup, ignore_errors=True)


def _forbid_protected_destination(root: Path, destination: Path) -> None:
    protected = [
        (root / "harness/work" / name).resolve()
        for name in PROTECTED_PACK_NAMES
    ]
    if any(destination == path or path in destination.parents for path in protected):
        raise ValueError("Row 10b generator cannot write into protected Rows 02-09")


def _row05_source_drift(root: Path) -> list[dict[str, Any]]:
    manifest = json.loads(
        (root / "harness/work/05-max-pressure/artifacts/run_manifest.json").read_text(encoding="utf-8")
    )
    drift: list[dict[str, Any]] = []
    for relative, frozen in manifest.get("source_hashes", {}).items():
        current = _hash(root / relative)
        if current == frozen:
            continue
        source = (root / relative).read_text(encoding="utf-8")
        approved = (
            relative == "src/coflow5/sumo_adapter/max_pressure_runner.py"
            and "sumo_extra_args: Sequence[str] = ()" in source
            and "*tuple(sumo_extra_args)" in source
        )
        drift.append({
            "path": relative,
            "frozen_hash": frozen,
            "current_hash": current,
            "approved_default_empty_launch_hook": approved,
            "effect": "default invocation remains unchanged; optional GUI pacing arguments may be appended",
        })
    return drift


def _comparison_row(row: Mapping[str, Any]) -> dict[str, Any]:
    names = (
        "run_id", "scenario_hash", "controller", "seed", "status",
        "planned_trips", "completed_trips", "unfinished_trips", "completion_rate",
        "mean_duration_s", "p95_duration_s", "max_duration_s",
        "mean_waiting_time_s", "p95_waiting_time_s", "max_waiting_time_s",
        "total_time_loss_s", "standstill_vehicle_seconds", "teleport_events",
    )
    return {name: row[name] for name in names}


def generate_max_pressure_trip_artifacts(
    root: Path, output_dir: Path | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    if platform.system() != "Windows" or sys.version_info[:2] != (3, 11):
        raise RuntimeError("Row 10b requires native Windows Python 3.11")
    sumo_binary = shutil.which("sumo")
    if not sumo_binary:
        raise RuntimeError("native sumo.exe is required")
    detected_sumo = _sumo_version(sumo_binary)
    if detected_sumo != SUMO_RELEASE:
        raise RuntimeError(f"expected SUMO {SUMO_RELEASE}, found {detected_sumo}")

    destination = (output_dir or root / "harness/work/10b-max-pressure-trip-kpis/artifacts").resolve()
    _forbid_protected_destination(root, destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    for pattern in (f".{destination.name}.staging-*", f".{destination.name}.previous-*"):
        for stale in destination.parent.glob(pattern):
            shutil.rmtree(stale, ignore_errors=True)
    staging = destination.parent / f".{destination.name}.staging-{uuid.uuid4()}"
    staging.mkdir()

    contract_path = root / CONTRACT_PATH
    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    locked = dict(contract["locked_inputs"])
    before = {relative: _hash(root / relative) for relative in locked}
    if before != locked:
        changed = sorted(relative for relative in locked if before.get(relative) != locked[relative])
        shutil.rmtree(staging, ignore_errors=True)
        raise RuntimeError(f"locked input hash mismatch: {changed}")

    scenario_hash = _scenario_hash(root)
    parity = contract["parity"]
    planned_trip_ids = _planned_trip_ids(root / "scenarios/baselines/baselines.rou.xml")
    if scenario_hash != parity["scenario_hash"] or len(planned_trip_ids) != parity["planned_trip_count"]:
        shutil.rmtree(staging, ignore_errors=True)
        raise RuntimeError("scenario identity or planned trip count does not match sealed parity")

    contract_hash = _hash(contract_path)
    run_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"coflow5:{contract_hash}:{scenario_hash}:{SEED}"))
    advisory = AdvisoryRequest(
        message_id="row05-advisory-0001",
        run_id=run_id,
        signal_id="J0",
        requested_phase_id="NS_YELLOW",
        source="A2_EMERGENCY",
        valid_from=6.0,
        expires_at=12.0,
        weight=1.0,
    )
    started_at = _now()
    started_perf = time.perf_counter()
    try:
        native = run_native_max_pressure_trip_scenario(
            sumo_binary=sumo_binary,
            config=root / "scenarios/max-pressure/max-pressure.sumocfg",
            network_file=root / "scenarios/safety-mask/safety.net.xml",
            run_id=run_id,
            scenario_hash=scenario_hash,
            seed=SEED,
            planned_trip_ids=planned_trip_ids,
            advisories=(advisory,),
            horizon_seconds=HORIZON_SECONDS,
        )
        finished_at = _now()
        trip_rows = [{"schema_version": 1, **asdict(row)} for row in native.trips]
        kpi_row = dict(native.kpis)
        pq.write_table(pa.Table.from_pylist(trip_rows, schema=TRIP_SCHEMA), staging / "trips.parquet", compression="zstd")
        pq.write_table(pa.Table.from_pylist([kpi_row], schema=RUN_KPI_SCHEMA), staging / "run_kpis.parquet", compression="zstd")

        baseline_rows = pq.read_table(root / "harness/work/04-baselines/artifacts/run_kpis.parquet").to_pylist()
        baseline_by = {row["controller"]: row for row in baseline_rows}
        fixed_manifest = json.loads((root / "harness/work/04-baselines/artifacts/fixed-time-run_manifest.json").read_text(encoding="utf-8"))
        actuated_manifest = json.loads((root / "harness/work/04-baselines/artifacts/actuated-run_manifest.json").read_text(encoding="utf-8"))
        parity_pass = (
            set(baseline_by) == {"fixed-time", "actuated"}
            and all(row["scenario_hash"] == scenario_hash and row["seed"] == SEED for row in baseline_rows)
            and kpi_row["scenario_hash"] == scenario_hash
            and kpi_row["seed"] == SEED
            and fixed_manifest["scenario_hash"] == actuated_manifest["scenario_hash"] == scenario_hash
            and fixed_manifest["seeds"]["evaluation"] == actuated_manifest["seeds"]["evaluation"] == SEED
            and all(row["planned_trips"] == len(planned_trip_ids) for row in (*baseline_rows, kpi_row))
        )
        if not parity_pass:
            raise RuntimeError("three-controller parity validation failed")
        comparison = {
            "schema_version": 1,
            "parity_pass": True,
            "pairing_keys": ["scenario_hash", "seed"],
            "scenario_hash": scenario_hash,
            "seed": SEED,
            "configured_horizon_seconds": HORIZON_SECONDS,
            "controller_rows": [
                _comparison_row(baseline_by["fixed-time"]),
                _comparison_row(baseline_by["actuated"]),
                _comparison_row(kpi_row),
            ],
            "one_seed_only": True,
            "significance_test_performed": False,
            "winner_claim": None,
            "advisory_fixture": {
                "message_id": advisory.message_id,
                "source": advisory.source,
                "valid_from": advisory.valid_from,
                "expires_at": advisory.expires_at,
                "limitation": "Max-Pressure reproduces the bounded Row 05 advisory fixture; baselines have no specialist request.",
            },
            "metric_definitions": {
                "completion": "completed divided by all 84 planned trips",
                "tail": "linear P95 at rank (n - 1) * 0.95 over completed-trip values",
                "time_loss": "sum over completed trips; unfinished trips remain visible separately",
            },
            "claim_boundary": "One matched seed is insufficient for a winner or significance claim; report observed differences only.",
        }
        _write_json(staging / "matched-comparison.json", comparison)

        drift = _row05_source_drift(root)
        if len(drift) != 1 or not drift[0]["approved_default_empty_launch_hook"]:
            raise RuntimeError(f"unexpected frozen Row 05 source drift: {drift}")
        after = {relative: _hash(root / relative) for relative in locked}
        input_audit = {
            "schema_version": 1,
            "contract_hash": contract_hash,
            "locked_input_count": len(locked),
            "locked_input_hashes": before,
            "all_locked_input_hashes_match": before == locked,
            "locked_inputs_unchanged_during_generation": after == before,
            "scenario_hash": scenario_hash,
            "seed": SEED,
            "configured_horizon_seconds": HORIZON_SECONDS,
            "planned_trip_count": len(planned_trip_ids),
            "planned_trip_ids_match_locked_baselines": {
                row["trip_id"] for row in pq.read_table(root / "harness/work/04-baselines/artifacts/baseline_trips.parquet").to_pylist()
            } == set(planned_trip_ids),
            "row05_frozen_source_drift_count": len(drift),
            "row05_frozen_source_drift": drift,
            "row05_artifacts_modified": False,
            "claim_boundary": "Frozen Row 05 is referenced and disclosed; it is never regenerated by Row 10b.",
        }
        if not input_audit["locked_inputs_unchanged_during_generation"]:
            raise RuntimeError("locked inputs changed during generation")
        _write_json(staging / "input-audit.json", input_audit)

        event_ids = {decision.event_id for decision in native.decisions}
        safety_ids = {event.event_id for event in native.safety_events}
        command_ids = {command.event_id for command in native.executed_commands}
        runtime_audit = {
            "actual_traci_execution": True,
            "writer_count_by_signal": native.writer_count_by_signal,
            "decision_count": len(native.decisions),
            "safety_event_count": len(native.safety_events),
            "accepted_command_count": len(native.executed_commands),
            "event_sets_match": event_ids == safety_ids == command_ids,
            "rejected_or_conflicting_executed_commands": native.physically_conflicting_commands + sum(not event.accepted for event in native.safety_events),
            "reinforcement_learning_required": False,
            "advisory_message_count": 1,
            "planned_trips": len(native.trips),
            "completed_trips": kpi_row["completed_trips"],
            "unfinished_trips": kpi_row["unfinished_trips"],
        }
        if not runtime_audit["event_sets_match"] or runtime_audit["rejected_or_conflicting_executed_commands"]:
            raise RuntimeError("native safety/command reconciliation failed")

        references = [
            _artifact_reference(staging / "trips.parquet", len(trip_rows), "max_pressure_trip_evidence"),
            _artifact_reference(staging / "run_kpis.parquet", 1, "max_pressure_run_kpi"),
            _artifact_reference(staging / "matched-comparison.json", 3, "three_controller_matched_comparison"),
            _artifact_reference(staging / "input-audit.json", len(locked), "locked_input_audit"),
        ]
        source_hashes = {relative: _hash(root / relative) for relative in SOURCE_FILES}
        manifest = {
            "schema_version": 1,
            "run_id": run_id,
            "scenario_hash": scenario_hash,
            "configuration_hash": _json_hash({
                "controller": "cooperative-max-pressure",
                "seed": SEED,
                "horizon_seconds": HORIZON_SECONDS,
                "safety_plan": "controlled-cross-v1",
                "advisory_fixture": "row05-advisory-0001",
            }),
            "contract_hash": contract_hash,
            "scenario_files": list(SCENARIO_FILES),
            "versions": {
                "python": platform.python_version(),
                "sumo": detected_sumo,
                "traci": importlib.metadata.version("traci"),
                "coflow5": "0.1.0",
                "pyarrow": importlib.metadata.version("pyarrow"),
                "pydantic": importlib.metadata.version("pydantic"),
            },
            "seeds": {"sumo": SEED, "evaluation": SEED},
            "configured_horizon_seconds": HORIZON_SECONDS,
            "status": "completed",
            "failure_reason": None,
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
            "native_command": [sys.executable, str(root / "scripts/generate_max_pressure_trip_artifacts.py")],
            "sumo_command": list(native.command),
            "runtime_audit": runtime_audit,
            "locked_input_hashes": locked,
            "artifact_references": references,
            "finalized_at": _now(),
            "immutable": True,
            "claim_boundary": comparison["claim_boundary"],
        }
        _write_json(staging / "run_manifest.json", manifest)
        _publish_atomic(staging, destination)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
