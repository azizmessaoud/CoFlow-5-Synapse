from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
import os
import platform
import re
import shutil
import statistics
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
from pydantic import ValidationError

from coflow5.evidence.schemas import (
    PARQUET_SCHEMAS,
    DecisionEvent,
    EventRecord,
    FaultEvent,
    MessageRecord,
    RunKpiRecord,
    RunManifest,
    StateRecord,
    TransitionEvent,
    TripRecord,
)
from coflow5.smoke import FROZEN_SCENARIO_FILES, SEED, SUMO_RELEASE, file_hash, scenario_hash
from coflow5.sumo_adapter.evidence_runner import run_native_traci_evidence

SCHEMA_VERSION = 1
EXPECTED_PARQUETS = tuple(PARQUET_SCHEMAS)


class BundleValidationError(RuntimeError):
    def __init__(self, message: str, audit: dict[str, Any]) -> None:
        super().__init__(message)
        self.audit = audit


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _json_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return f"sha256:{hashlib.sha256(encoded).hexdigest()}"


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _source_revision(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=False
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _sumo_version(binary: str) -> str:
    result = subprocess.run([binary, "--version"], capture_output=True, text=True, check=True)
    match = re.search(r"(?:sumo|GUI)\s+(\d+\.\d+\.\d+)", result.stdout + result.stderr)
    if not match:
        raise RuntimeError(f"Could not parse SUMO version from {binary}")
    return match.group(1)


def _package_version(name: str) -> str:
    return importlib.metadata.version(name)


def _write_parquet(path: Path, rows: list[dict[str, Any]], schema: pa.Schema) -> None:
    table = pa.Table.from_pylist(rows, schema=schema)
    pq.write_table(table, path, compression="zstd", version="2.6")


def _identity(run_id: str, current_scenario_hash: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "scenario_hash": current_scenario_hash,
    }


def _percentile_95(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def generate_bundle(root: Path, output_dir: Path | None = None) -> dict[str, Any]:
    """Generate and atomically publish one finalized bundle from the frozen TraCI run."""
    root = root.resolve()
    if platform.system() != "Windows" or sys.version_info[:2] != (3, 11):
        raise RuntimeError("Row 02 requires native Windows Python 3.11")
    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home or not Path(sumo_home).is_dir():
        raise RuntimeError("SUMO_HOME must point to the native Eclipse SUMO installation")
    sumo_binary = shutil.which("sumo")
    if not sumo_binary:
        raise RuntimeError("Native sumo.exe must be on PATH")
    detected_sumo = _sumo_version(sumo_binary)
    if detected_sumo != SUMO_RELEASE:
        raise RuntimeError(f"Expected SUMO {SUMO_RELEASE}, found {detected_sumo}")

    output_dir = (output_dir or root / "harness" / "work" / "02-evidence-bundle" / "artifacts").resolve()
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    staging = output_dir.parent / f".{output_dir.name}.staging-{uuid.uuid4()}"
    staging.mkdir()
    run_id = str(uuid.uuid4())
    current_scenario_hash = scenario_hash(root)
    config = root / "scenarios" / "smoke" / "smoke.sumocfg"
    configuration = {
        "sumocfg_sha256": file_hash(config),
        "seed": SEED,
        "backend": "traci",
        "controller": "scenario-defined-no-actuation",
        "step_length_seconds": 1,
        "write_unfinished_tripinfo": True,
    }
    started_at = _utc_now()
    started_perf = time.perf_counter()
    try:
        native = run_native_traci_evidence(
            sumo_binary=sumo_binary,
            config=config,
            tripinfo_path=staging / "native-tripinfo.xml",
            seed=SEED,
        )
        finished_at = _utc_now()
        wall_seconds = time.perf_counter() - started_perf
        identity = _identity(run_id, current_scenario_hash)

        state_rows = [{**identity, **row} for row in native.states]
        trip_rows = [{**identity, **row} for row in native.trips]

        message_id = str(uuid.uuid4())
        lifecycle_payload = json.dumps(
            {"backend": "traci", "scenario": "frozen-smoke", "seed": SEED},
            sort_keys=True,
            separators=(",", ":"),
        )
        message_rows = [
            {
                **identity,
                "message_id": message_id,
                "record_kind": "message",
                "simulation_time": native.simulation_begin,
                "created_at": started_at,
                "source": "evidence-generator",
                "topic": "run.lifecycle",
                "payload_type": "native_run_started",
                "payload_json": lifecycle_payload,
                "disposition": None,
            },
            {
                **identity,
                "message_id": message_id,
                "record_kind": "disposition",
                "simulation_time": native.simulation_end,
                "created_at": finished_at,
                "source": "evidence-validator",
                "topic": "run.lifecycle",
                "payload_type": "native_run_started",
                "payload_json": lifecycle_payload,
                "disposition": "recorded",
            },
        ]
        event_rows = [
            {
                **identity,
                "event_id": str(uuid.uuid4()),
                "event_kind": "transition",
                "simulation_time": native.simulation_begin,
                "recorded_at": started_at,
                "reason_code": "NATIVE_TRACI_STARTED",
                "considered_message_ids": [message_id],
                "selected_action": None,
                "fault_code": None,
                "previous_mode": "pending",
                "next_mode": "running",
                "provenance": "native TraCI connection start",
            },
            {
                **identity,
                "event_id": str(uuid.uuid4()),
                "event_kind": "transition",
                "simulation_time": native.simulation_end,
                "recorded_at": finished_at,
                "reason_code": "MIN_EXPECTED_REACHED_ZERO",
                "considered_message_ids": [message_id],
                "selected_action": None,
                "fault_code": None,
                "previous_mode": "running",
                "next_mode": "completed",
                "provenance": "TraCI simulation.getMinExpectedNumber returned zero",
            },
        ]

        completed = [row for row in trip_rows if not row["unfinished"]]
        durations = [float(row["duration"]) for row in completed]
        waiting = [float(row["waiting_time_s"]) for row in completed]
        kpi_rows = [
            {
                **identity,
                "completed_trips": len(completed),
                "unfinished_trips": sum(bool(row["unfinished"]) for row in trip_rows),
                "mean_duration_s": statistics.fmean(durations) if durations else 0.0,
                "p95_duration_s": _percentile_95(durations),
                "max_duration_s": max(durations, default=0.0),
                "mean_waiting_time_s": statistics.fmean(waiting) if waiting else 0.0,
                "total_time_loss_s": sum(float(row["time_loss_s"]) for row in trip_rows),
                "simulation_steps": native.simulation_steps,
                "max_active_vehicles": max(
                    (int(row["active_vehicles"]) for row in state_rows), default=0
                ),
                "teleport_events": native.teleport_events,
            }
        ]

        rows_by_file = {
            "state.parquet": state_rows,
            "messages.parquet": message_rows,
            "decision_events.parquet": event_rows,
            "trips.parquet": trip_rows,
            "run_kpis.parquet": kpi_rows,
        }
        references: list[dict[str, Any]] = []
        for name, rows in rows_by_file.items():
            schema_name, arrow_schema, _ = PARQUET_SCHEMAS[name]
            path = staging / name
            _write_parquet(path, rows, arrow_schema)
            references.append(
                {
                    "path": name,
                    "sha256": _sha256(path),
                    "bytes": path.stat().st_size,
                    "rows": len(rows),
                    "schema_name": schema_name,
                    "schema_version": SCHEMA_VERSION,
                }
            )

        manifest = {
            "schema_version": SCHEMA_VERSION,
            "run_id": run_id,
            "scenario_hash": current_scenario_hash,
            "configuration_hash": _json_hash(configuration),
            "scenario_files": list(FROZEN_SCENARIO_FILES),
            "versions": {
                "python": platform.python_version(),
                "sumo": detected_sumo,
                "traci": _package_version("traci"),
                "coflow5": "0.1.0",
                "duckdb": _package_version("duckdb"),
                "pyarrow": _package_version("pyarrow"),
                "pydantic": _package_version("pydantic"),
            },
            "seeds": {"sumo": SEED},
            "status": "completed",
            "timings": {
                "started_at": started_at,
                "finished_at": finished_at,
                "wall_seconds": wall_seconds,
                "simulation_begin": native.simulation_begin,
                "simulation_end": native.simulation_end,
                "simulation_steps": native.simulation_steps,
            },
            "backend": "traci",
            "controller": "scenario-defined-no-actuation",
            "source_revision": _source_revision(root),
            "native_command": [sys.executable, str(root / "scripts" / "generate_evidence_bundle.py")],
            "artifact_references": references,
            "finalized_at": _utc_now(),
            "immutable": True,
        }
        RunManifest.model_validate(manifest)
        _write_json(staging / "run_manifest.json", manifest)
        audit = validate_bundle(staging)
        _write_json(staging / "join-audit.json", audit)
        (staging / "native-tripinfo.xml").unlink()

        if output_dir.exists():
            shutil.rmtree(output_dir)
        staging.replace(output_dir)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise


def _invalid_audit(bundle_dir: Path) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "valid": False,
        "bundle": ".",
        "run_id": None,
        "scenario_hash": None,
        "manifest_status": None,
        "artifact_checks": {"missing": 0, "corrupt": 0},
        "schema_checks": {"errors": 0, "checked": 0},
        "join_checks": {
            "missing": 0,
            "duplicate": 0,
            "cross_scenario": 0,
            "orphan": 0,
        },
        "row_counts": {},
        "errors": [],
    }


def validate_bundle(bundle_dir: Path) -> dict[str, Any]:
    """Return a zero-error join audit or reject the bundle as invalid for evaluation."""
    bundle_dir = bundle_dir.resolve()
    audit = _invalid_audit(bundle_dir)

    def fail(message: str, category: str = "schema") -> None:
        audit["errors"].append(message)
        if category == "missing":
            audit["artifact_checks"]["missing"] += 1
        elif category == "corrupt":
            audit["artifact_checks"]["corrupt"] += 1
        elif category == "schema":
            audit["schema_checks"]["errors"] += 1
        elif category in audit["join_checks"]:
            audit["join_checks"][category] += 1

    manifest_path = bundle_dir / "run_manifest.json"
    if not manifest_path.is_file():
        fail("missing run_manifest.json", "missing")
        raise BundleValidationError("Evidence bundle is invalid: missing manifest", audit)
    try:
        manifest = RunManifest.model_validate_json(manifest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError, ValidationError) as exc:
        fail(f"invalid run_manifest.json: {exc}")
        raise BundleValidationError("Evidence bundle is invalid: corrupt manifest", audit) from exc

    audit["run_id"] = manifest.run_id
    audit["scenario_hash"] = manifest.scenario_hash
    audit["manifest_status"] = manifest.status
    if manifest.status != "completed" or manifest.immutable is not True:
        fail("manifest must be completed and immutable")

    refs = {ref.path: ref for ref in manifest.artifact_references}
    if len(refs) != len(manifest.artifact_references):
        fail("duplicate artifact references", "duplicate")
    missing_refs = sorted(set(EXPECTED_PARQUETS) - set(refs))
    extra_refs = sorted(set(refs) - set(EXPECTED_PARQUETS))
    for name in missing_refs:
        fail(f"manifest omits {name}", "missing")
    if extra_refs:
        fail(f"manifest has unexpected references: {extra_refs}")

    tables: dict[str, pa.Table] = {}
    row_models = {
        "state.parquet": StateRecord,
        "messages.parquet": MessageRecord,
        "trips.parquet": TripRecord,
        "run_kpis.parquet": RunKpiRecord,
    }
    for name in EXPECTED_PARQUETS:
        path = bundle_dir / name
        ref = refs.get(name)
        if not path.is_file():
            fail(f"missing {name}", "missing")
            continue
        if ref is None:
            continue
        if _sha256(path) != ref.sha256 or path.stat().st_size != ref.bytes:
            fail(f"hash or size mismatch for {name}", "corrupt")
            continue
        try:
            table = pq.read_table(path)
        except Exception as exc:  # noqa: BLE001 - corrupt Parquet must become invalid evidence
            fail(f"unreadable {name}: {exc}", "corrupt")
            continue
        expected_schema = PARQUET_SCHEMAS[name][1]
        if not table.schema.equals(expected_schema, check_metadata=False):
            fail(f"schema mismatch for {name}")
            continue
        if table.num_rows != ref.rows:
            fail(f"row count mismatch for {name}", "corrupt")
            continue
        tables[name] = table
        audit["row_counts"][name] = table.num_rows
        audit["schema_checks"]["checked"] += 1

        try:
            if name == "decision_events.parquet":
                for row in table.to_pylist():
                    model = {
                        "decision": DecisionEvent,
                        "fault": FaultEvent,
                        "transition": TransitionEvent,
                    }.get(row["event_kind"], EventRecord)
                    model.model_validate(row)
            else:
                model = row_models[name]
                for row in table.to_pylist():
                    model.model_validate(row)
        except (ValidationError, ValueError, KeyError) as exc:
            fail(f"typed row validation failed for {name}: {exc}")

    if set(tables) == set(EXPECTED_PARQUETS):
        manifest_table = pa.table(
            {
                "run_id": [manifest.run_id],
                "scenario_hash": [manifest.scenario_hash],
                "status": [manifest.status],
            }
        )
        connection = duckdb.connect(":memory:")
        try:
            connection.register("manifest", manifest_table)
            for index, (name, table) in enumerate(tables.items()):
                table_name = f"evidence_{index}"
                connection.register(table_name, table)
                total, joined = connection.execute(
                    f"SELECT count(*), count(m.run_id) FROM {table_name} p "
                    "LEFT JOIN manifest m ON p.run_id=m.run_id "
                    "AND p.scenario_hash=m.scenario_hash AND m.status='completed'"
                ).fetchone()
                if total != joined:
                    fail(f"{name} has {total - joined} rows without exactly one valid manifest", "missing")
        finally:
            connection.close()

        for name, table in tables.items():
            for row in table.select(["run_id", "scenario_hash"]).to_pylist():
                if row["run_id"] != manifest.run_id:
                    fail(f"{name} contains cross-run identity", "orphan")
                if row["scenario_hash"] != manifest.scenario_hash:
                    fail(f"{name} contains cross-scenario identity", "cross_scenario")

        events = tables["decision_events.parquet"].to_pylist()
        event_ids = [row["event_id"] for row in events]
        duplicate_events = len(event_ids) - len(set(event_ids))
        for _ in range(duplicate_events):
            fail("duplicate event_id within run", "duplicate")

        messages = tables["messages.parquet"].to_pylist()
        publications = [row for row in messages if row["record_kind"] == "message"]
        publication_ids = [row["message_id"] for row in publications]
        duplicate_messages = len(publication_ids) - len(set(publication_ids))
        for _ in range(duplicate_messages):
            fail("duplicate message publication identifier", "duplicate")
        known_messages = set(publication_ids)
        for row in messages:
            if row["record_kind"] == "disposition" and row["message_id"] not in known_messages:
                fail("disposition references no same-run message", "orphan")
        for row in events:
            for message_id in row["considered_message_ids"] or []:
                if message_id not in known_messages:
                    fail("event references no same-run message", "orphan")

    if not audit["errors"]:
        audit["valid"] = True
        audit["audited_at"] = _utc_now()
        return audit
    raise BundleValidationError(
        "Evidence bundle is invalid and must not enter evaluation: " + "; ".join(audit["errors"]),
        audit,
    )
