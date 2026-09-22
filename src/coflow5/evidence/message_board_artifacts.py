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
from collections import Counter
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from coflow5.evidence.schemas import RunManifest
from coflow5.messaging import (
    InProcessMessageBoard,
    MessageDisposition,
    MessageEnvelope,
    read_a1_advisories,
)
from coflow5.sumo_adapter.max_pressure_runner import run_native_max_pressure_scenario

SUMO_RELEASE = "1.27.1"
EVALUATION_SEED = 41
SCENARIO_FILES = (
    "scenarios/safety-mask/safety.net.xml",
    "scenarios/baselines/baselines.rou.xml",
    "scenarios/baselines/baselines.tls.xml",
    "scenarios/baselines/baselines.sumocfg",
)
ROW06_RUNTIME_SOURCES = (
    "src/coflow5/messaging/envelope.py",
    "src/coflow5/messaging/board.py",
    "src/coflow5/messaging/a1_advisories.py",
    "src/coflow5/evidence/message_board_artifacts.py",
    "scripts/generate_message_board_artifacts.py",
)

MESSAGE_SCHEMA = pa.schema([
    ("evidence_schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("message_id", pa.string()),
    ("record_kind", pa.string()), ("correlation_id", pa.string()),
    ("source_agent", pa.string()), ("destination_or_topic", pa.string()),
    ("created_at", pa.string()), ("simulation_time", pa.float64()),
    ("expires_at", pa.float64()), ("ttl_seconds", pa.float64()),
    ("priority_class", pa.string()), ("confidence", pa.float64()),
    ("schema_version", pa.int16()), ("payload_type", pa.string()),
    ("payload_json", pa.string()), ("provenance", pa.string()),
    ("disposition", pa.string()), ("disposition_reason", pa.string()),
    ("disposition_sequence", pa.int64()), ("recorded_at", pa.string()),
])

DECISION_SCHEMA = pa.schema([
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

REQUIRED_DISPOSITIONS = (
    "duplicate", "expired", "malformed", "unsupported", "contradictory",
    "out_of_order", "unavailable", "empty",
)


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


def _message_values(
    *,
    run_id: str,
    scenario_hash: str,
    message_id: str,
    correlation_id: str,
    simulation_time: float,
    expires_at: float,
    topic: str = "requests",
    requested_phase_id: str = "NS_YELLOW",
    confidence: float = 1.0,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "scenario_hash": scenario_hash,
        "message_id": message_id,
        "correlation_id": correlation_id,
        "source_agent": "A2_EMERGENCY",
        "destination_or_topic": topic,
        "created_at": datetime.now(timezone.utc),
        "simulation_time": simulation_time,
        "expires_at": expires_at,
        "priority_class": "emergency",
        "confidence": confidence,
        "schema_version": 1,
        "payload_type": "priority_request",
        "payload": {
            "signal_id": "J0",
            "requested_phase_id": requested_phase_id,
            "weight": min(confidence, 1.0),
        },
        "provenance": "row06-message-board-fixture",
    }


def _publication_row(raw: dict[str, Any]) -> dict[str, Any]:
    priority = raw["priority_class"]
    if hasattr(priority, "value"):
        priority = priority.value
    created_at = raw["created_at"]
    if isinstance(created_at, datetime):
        created_at = created_at.isoformat()
    return {
        "evidence_schema_version": 1,
        "run_id": raw["run_id"],
        "scenario_hash": raw["scenario_hash"],
        "message_id": raw["message_id"],
        "record_kind": "message",
        "correlation_id": raw["correlation_id"],
        "source_agent": raw["source_agent"],
        "destination_or_topic": raw["destination_or_topic"],
        "created_at": created_at,
        "simulation_time": float(raw["simulation_time"]),
        "expires_at": float(raw["expires_at"]),
        "ttl_seconds": float(raw["expires_at"] - raw["simulation_time"]),
        "priority_class": str(priority),
        "confidence": float(raw["confidence"]),
        "schema_version": int(raw["schema_version"]),
        "payload_type": raw["payload_type"],
        "payload_json": json.dumps(raw["payload"], sort_keys=True, separators=(",", ":")),
        "provenance": raw["provenance"],
        "disposition": None,
        "disposition_reason": None,
        "disposition_sequence": None,
        "recorded_at": None,
    }


def generate_message_board_artifacts(
    root: Path,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    destination = (output_dir or root / "harness/work/06-message-board/artifacts").resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    for stale in destination.parent.glob(f".{destination.name}.staging-*"):
        shutil.rmtree(stale, ignore_errors=True)

    if platform.system() != "Windows" or sys.version_info[:2] != (3, 11):
        raise RuntimeError("row 06 requires native Windows Python 3.11")
    if not os.environ.get("SUMO_HOME"):
        raise RuntimeError("SUMO_HOME is required")
    sumo_binary = shutil.which("sumo")
    if not sumo_binary:
        raise RuntimeError("native sumo.exe is required")
    detected_sumo = _sumo_version(sumo_binary)
    if detected_sumo != SUMO_RELEASE:
        raise RuntimeError(f"expected SUMO {SUMO_RELEASE}, found {detected_sumo}")

    staging = destination.parent / f".{destination.name}.staging-{uuid.uuid4()}"
    staging.mkdir()
    run_id = str(uuid.uuid4())
    scenario_hash = _scenario_hash(root)
    started_at = _now()
    started_perf = time.perf_counter()

    board = InProcessMessageBoard(capacity=16)
    publications: dict[str, dict[str, Any]] = {}

    def attempt(raw: dict[str, Any], *, valid_at: float | None = None):
        publications.setdefault(raw["message_id"], raw)
        return board.publish(raw, valid_at=valid_at)

    try:
        empty_read = board.read(
            "requests", valid_at=0.0, run_id=run_id, scenario_hash=scenario_hash
        )
        primary_raw = _message_values(
            run_id=run_id, scenario_hash=scenario_hash,
            message_id="row06-request-accepted", correlation_id="window-6",
            simulation_time=6.0, expires_at=12.0,
        )
        primary = MessageEnvelope.model_validate(primary_raw)
        attempt(primary_raw, valid_at=6.0)
        attempt(primary_raw, valid_at=6.0)
        attempt(_message_values(
            run_id=run_id, scenario_hash=scenario_hash,
            message_id="row06-request-expired", correlation_id="expired-window",
            simulation_time=0.0, expires_at=1.0,
        ), valid_at=2.0)
        attempt(_message_values(
            run_id=run_id, scenario_hash=scenario_hash,
            message_id="row06-request-unsupported", correlation_id="unsupported-window",
            simulation_time=6.0, expires_at=12.0, topic="not-a-topic",
        ), valid_at=6.0)
        attempt(_message_values(
            run_id=run_id, scenario_hash=scenario_hash,
            message_id="row06-request-contradictory", correlation_id="window-6",
            simulation_time=6.0, expires_at=12.0, requested_phase_id="NS_GREEN",
        ), valid_at=6.0)
        attempt(_message_values(
            run_id=run_id, scenario_hash=scenario_hash,
            message_id="row06-request-out-of-order", correlation_id="old-window",
            simulation_time=5.0, expires_at=12.0,
        ), valid_at=5.0)
        attempt(_message_values(
            run_id=run_id, scenario_hash=scenario_hash,
            message_id="row06-request-from-future", correlation_id="future-window",
            simulation_time=20.0, expires_at=30.0,
        ), valid_at=10.0)
        attempt(_message_values(
            run_id=run_id, scenario_hash=scenario_hash,
            message_id="row06-request-malformed", correlation_id="malformed-window",
            simulation_time=7.0, expires_at=12.0, confidence=2.0,
        ), valid_at=7.0)

        board.set_available(False)
        unavailable_read = board.read(
            "requests", valid_at=6.0, run_id=run_id, scenario_hash=scenario_hash
        )
        board.set_available(True)
        advisory_read = read_a1_advisories(
            board, run_id=run_id, scenario_hash=scenario_hash,
            signal_id="J0", valid_at=6.0,
        )
        if [item.message_id for item in advisory_read.advisories] != [primary.message_id]:
            raise RuntimeError("board did not expose exactly one idempotent accepted advisory")

        native = run_native_max_pressure_scenario(
            sumo_binary=sumo_binary,
            config=root / "scenarios/baselines/baselines.sumocfg",
            run_id=run_id,
            scenario_hash=scenario_hash,
            seed=EVALUATION_SEED,
            advisories=advisory_read.advisories,
        )
        finished_at = _now()

        decision_rows: list[dict[str, Any]] = []
        for decision in native.decisions:
            row = asdict(decision)
            row["schema_version"] = 1
            row["controller"] = "cooperative-max-pressure"
            row["action_scores_json"] = json.dumps(
                row.pop("action_scores"), sort_keys=True, separators=(",", ":")
            )
            decision_rows.append(row)
        pq.write_table(
            pa.Table.from_pylist(decision_rows, schema=DECISION_SCHEMA),
            staging / "decision_events.parquet",
            compression="zstd",
        )

        message_rows = [_publication_row(raw) for raw in publications.values()]
        for record in board.audit_log:
            if record.message_id is None:
                continue
            base = _publication_row(publications[record.message_id])
            base.update({
                "record_kind": "disposition",
                "disposition": record.disposition.value,
                "disposition_reason": record.reason,
                "disposition_sequence": record.sequence,
                "recorded_at": record.recorded_at.isoformat(),
            })
            message_rows.append(base)
        pq.write_table(
            pa.Table.from_pylist(message_rows, schema=MESSAGE_SCHEMA),
            staging / "messages.parquet",
            compression="zstd",
        )

        publication_ids = set(publications)
        disposition_ids = {
            row["message_id"] for row in message_rows if row["record_kind"] == "disposition"
        }
        considered_ids = {
            message_id
            for row in decision_rows
            for message_id in row["considered_message_ids"]
        }
        identity_errors = sum(
            row["run_id"] != run_id or row["scenario_hash"] != scenario_hash
            for row in message_rows + decision_rows
        )
        unresolved_considered = sorted(considered_ids - publication_ids)
        unresolved_dispositions = sorted(disposition_ids - publication_ids)
        counts = Counter(record.disposition.value for record in board.audit_log)
        future_publication_rejected = any(
            record.disposition is MessageDisposition.OUT_OF_ORDER
            and "future" in record.reason
            for record in board.audit_log
        )
        metadata_bounded = all(
            size <= board.metadata_capacity for size in board.metadata_sizes.values()
        )
        empty_legal = sum(
            not row["considered_message_ids"]
            and row["reason_code"] == "MAX_PRESSURE_LOCAL_ONLY"
            and row["safety_reason_code"] == "ACCEPTED"
            for row in decision_rows
        )
        required_present = set(REQUIRED_DISPOSITIONS) <= set(counts)
        valid = (
            bool(decision_rows)
            and identity_errors == 0
            and not unresolved_considered
            and not unresolved_dispositions
            and considered_ids == {primary.message_id}
            and required_present
            and future_publication_rejected
            and metadata_bounded
            and empty_read.disposition is MessageDisposition.EMPTY
            and unavailable_read.disposition is MessageDisposition.UNAVAILABLE
            and empty_legal > 0
            and native.safety_event_count == native.accepted_command_count == len(decision_rows)
            and native.writer_count_by_signal == {"J0": 1}
        )
        audit = {
            "schema_version": 1,
            "valid": valid,
            "run_id": run_id,
            "scenario_hash": scenario_hash,
            "transport": "in-process",
            "transport_interface": "MessageTransport",
            "capacity": board.capacity,
            "final_storage_size": board.storage_size,
            "metadata_capacity": board.metadata_capacity,
            "metadata_sizes": board.metadata_sizes,
            "metadata_bounded": metadata_bounded,
            "future_publication_rejected_as_out_of_order": future_publication_rejected,
            "publication_count": len(publication_ids),
            "message_row_count": len(message_rows),
            "decision_count": len(decision_rows),
            "identity_errors": identity_errors,
            "required_dispositions": list(REQUIRED_DISPOSITIONS),
            "disposition_counts": dict(sorted(counts.items())),
            "unresolved_considered_message_ids": unresolved_considered,
            "unresolved_disposition_message_ids": unresolved_dispositions,
            "considered_message_ids": sorted(considered_ids),
            "duplicate_arbitration_count": sum(
                len(row["considered_message_ids"])
                - len(set(row["considered_message_ids"]))
                for row in decision_rows
            ),
            "unique_arbitration_message_ids": len(considered_ids),
            "empty_board_read_disposition": empty_read.disposition.value,
            "unavailable_board_read_disposition": unavailable_read.disposition.value,
            "unavailable_board_continues_local_max_pressure": (
                unavailable_read.messages == () and empty_legal > 0
            ),
            "empty_board_legal_decision_count": empty_legal,
            "a1_signal_owner": "A1_FLOW",
            "one_writer_per_signal": native.writer_count_by_signal == {"J0": 1},
            "controller": "cooperative-max-pressure",
            "recovery_ladder": ["cooperative-max-pressure", "actuated", "fixed-time"],
            "external_broker_required": False,
            "redis_required": False,
            "kafka_required": False,
            "claim_boundary": "No lives-saved or measured-air-quality claim is made.",
        }
        _write_json(staging / "message-audit.json", audit)

        references = []
        for name, rows, schema_name in (
            ("messages.parquet", len(message_rows), "message_envelope_and_disposition"),
            ("decision_events.parquet", len(decision_rows), "max_pressure_decision_event"),
            ("message-audit.json", 1, "message_board_audit"),
        ):
            path = staging / name
            references.append({
                "path": name,
                "sha256": _hash_file(path),
                "bytes": path.stat().st_size,
                "rows": rows,
                "schema_name": schema_name,
                "schema_version": 1,
            })
        configuration = {
            "transport": "in-process",
            "capacity": board.capacity,
            "controller": "cooperative-max-pressure",
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
            "source_hashes": {
                relative: _hash_file(root / relative)
                for relative in ROW06_RUNTIME_SOURCES
            },
            "native_command": [sys.executable, str(root / "scripts/generate_message_board_artifacts.py")],
            "sumo_command": list(native.command),
            "artifact_references": references,
            "finalized_at": _now(),
            "immutable": True,
        }
        RunManifest.model_validate(manifest)
        if not valid:
            raise RuntimeError(f"message board audit failed: {audit}")
        _write_json(staging / "run_manifest.json", manifest)
        if destination.exists():
            shutil.rmtree(destination)
        staging.replace(destination)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
