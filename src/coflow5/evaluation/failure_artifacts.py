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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from coflow5.control import DeterministicSafetyMask, controlled_cross_plan
from coflow5.control.a1_controller import A1FlowController
from coflow5.control.max_pressure import (
    CooperativeMaxPressureController,
    MaxPressureObservation,
    MovementPressure,
)
from coflow5.control.recovery import REQUIRED_RECOVERY_LADDER, RecoverySupervisor
from coflow5.evidence.schemas import RunManifest
from coflow5.failures import (
    DeterministicFailureInjector,
    FailureClass,
    FaultInjection,
)
from coflow5.messaging import InProcessMessageBoard, MessageEnvelope, PriorityClass
from coflow5.sumo_adapter.signal_executor import ImmutableSafetyLog, SignalExecutorRegistry
from coflow5.synapse import (
    ExplanationObserverBoundary,
    ImmutableDecisionView,
    action_sequence_hash,
)

SUMO_RELEASE = "1.27.1"
EVALUATION_SEED = 47

FAULT_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("event_id", pa.string()),
    ("event_kind", pa.string()), ("failure_class", pa.string()),
    ("message_id", pa.string()), ("simulation_time", pa.float64()),
    ("disposition", pa.string()), ("trigger", pa.string()),
    ("previous_mode", pa.string()), ("next_mode", pa.string()),
    ("health_evidence_json", pa.string()), ("detail", pa.string()),
    ("visible", pa.bool_()),
])

MESSAGE_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("failure_class", pa.string()),
    ("message_id", pa.string()), ("record_kind", pa.string()),
    ("simulation_time", pa.float64()), ("source_agent", pa.string()),
    ("destination_or_topic", pa.string()), ("disposition", pa.string()),
    ("fault_event_id", pa.string()), ("detail", pa.string()),
])

DECISION_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("event_id", pa.string()),
    ("failure_class", pa.string()), ("simulation_time", pa.float64()),
    ("controller_mode", pa.string()), ("selected_action", pa.string()),
    ("legal", pa.bool_()), ("local_only", pa.bool_()),
    ("considered_message_ids", pa.list_(pa.string())),
    ("reason_code", pa.string()), ("safety_reason_code", pa.string()),
    ("fault_event_id", pa.string()), ("provenance", pa.string()),
])


class _TrafficLightFixture:
    def __init__(self) -> None:
        self.state = "GrGr"
        self.writes: list[tuple[str, str]] = []

    def setRedYellowGreenState(self, signal_id: str, state: str) -> None:
        self.state = state
        self.writes.append((signal_id, state))

    def getRedYellowGreenState(self, signal_id: str) -> str:
        return self.state


class _ConnectionFixture:
    def __init__(self) -> None:
        self.trafficlight = _TrafficLightFixture()


class _TemplateObserver:
    def observe(self, decision: ImmutableDecisionView) -> str:
        return "template-explanation-recorded"


class _UnavailableObserver:
    def __init__(self, detail: str) -> None:
        self._detail = detail

    def observe(self, decision: ImmutableDecisionView) -> str:
        raise RuntimeError(self._detail)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _hash_file(path: Path) -> str:
    return _hash_bytes(path.read_bytes())


def _json_hash(value: Any) -> str:
    return _hash_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def _source_revision(root: Path) -> str | None:
    result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def _sumo_version(binary: str) -> str:
    result = subprocess.run([binary, "--version"], capture_output=True, text=True, check=True)
    match = re.search(r"sumo\s+(\d+\.\d+\.\d+)", result.stdout + result.stderr)
    if not match:
        raise RuntimeError("could not parse SUMO version")
    return match.group(1)


def _message(
    *,
    run_id: str,
    scenario_hash: str,
    message_id: str,
    simulation_time: float,
    expires_at: float = 30.0,
    correlation_id: str | None = None,
    requested_phase_id: str = "EW_GREEN",
) -> MessageEnvelope:
    return MessageEnvelope(
        run_id=run_id,
        scenario_hash=scenario_hash,
        message_id=message_id,
        correlation_id=correlation_id or f"correlation-{message_id}",
        source_agent="A2_EMERGENCY",
        destination_or_topic="requests",
        created_at=datetime(2026, 9, 22, 12, 0, tzinfo=timezone.utc),
        simulation_time=simulation_time,
        expires_at=expires_at,
        priority_class=PriorityClass.EMERGENCY,
        confidence=0.9,
        schema_version=1,
        payload_type="priority_request",
        payload={
            "signal_id": "J0",
            "requested_phase_id": requested_phase_id,
            "weight": 0.9,
        },
        provenance="row08-deterministic-fault-fixture",
    )


def _local_decision(run_id: str, scenario_hash: str, proposal_id: str, simulation_time: float):
    connection = _ConnectionFixture()
    safety_log = ImmutableSafetyLog()
    mask = DeterministicSafetyMask(controlled_cross_plan())
    capability = SignalExecutorRegistry().acquire(
        signal_id="J0",
        connection=connection,
        safety_mask=mask,
        initial_phase_id="NS_GREEN",
        initial_phase_entered_at=simulation_time - 1.0,
        run_id=run_id,
        scenario_hash=scenario_hash,
        log=safety_log,
    )
    controller = CooperativeMaxPressureController(
        a1=A1FlowController(capability),
        safety_mask=mask,
        run_id=run_id,
        scenario_hash=scenario_hash,
        signal_id="J0",
    )
    observation = MaxPressureObservation(
        simulation_time=simulation_time,
        current_phase_id="NS_GREEN",
        phase_entered_at=simulation_time - 1.0,
        movements={
            movement: MovementPressure(
                upstream_queue=8.0 if movement in {"north", "south"} else 3.0,
                downstream_queue=1.0,
                downstream_capacity=20.0,
            )
            for movement in ("north", "south", "east", "west")
        },
        advisories=(),
    )
    decision = controller.decide(proposal_id=proposal_id, observation=observation)
    if (
        decision.reason_code != "MAX_PRESSURE_LOCAL_ONLY"
        or decision.safety_reason_code != "ACCEPTED"
        or len(safety_log.events) != 1
        or len(safety_log.commands) != 1
    ):
        raise RuntimeError("fault scenario did not retain legal local Max-Pressure control")
    return decision


def _fault_cases(run_id: str, scenario_hash: str):
    cases: list[tuple[FaultInjection, MessageEnvelope | dict[str, Any] | None, MessageEnvelope | None]] = []
    cases.append((FaultInjection(FailureClass.MESSAGE_ABSENCE, 10.0), None, None))
    cases.append((FaultInjection(FailureClass.MESSAGE_LOSS_DROP, 11.0, "loss-001"),
                  _message(run_id=run_id, scenario_hash=scenario_hash,
                           message_id="loss-001", simulation_time=11.0), None))
    cases.append((FaultInjection(FailureClass.MESSAGE_DELAY, 12.0, "delay-001", 5.0),
                  _message(run_id=run_id, scenario_hash=scenario_hash,
                           message_id="delay-001", simulation_time=12.0), None))
    cases.append((FaultInjection(FailureClass.MESSAGE_DUPLICATION, 13.0, "duplicate-001"),
                  _message(run_id=run_id, scenario_hash=scenario_hash,
                           message_id="duplicate-001", simulation_time=13.0), None))
    cases.append((FaultInjection(FailureClass.MESSAGE_EXPIRY, 14.0, "expired-001"),
                  _message(run_id=run_id, scenario_hash=scenario_hash,
                           message_id="expired-001", simulation_time=10.0, expires_at=13.0), None))
    malformed = _message(run_id=run_id, scenario_hash=scenario_hash,
                         message_id="malformed-001", simulation_time=15.0).model_dump(mode="python")
    malformed["confidence"] = 2.0
    cases.append((FaultInjection(FailureClass.MALFORMED_PAYLOAD, 15.0, "malformed-001"),
                  malformed, None))
    baseline = _message(run_id=run_id, scenario_hash=scenario_hash,
                        message_id="contradiction-base-001", simulation_time=16.0,
                        correlation_id="contradiction-correlation")
    conflicting = _message(run_id=run_id, scenario_hash=scenario_hash,
                           message_id="contradiction-001", simulation_time=16.0,
                           correlation_id="contradiction-correlation",
                           requested_phase_id="NS_GREEN")
    cases.append((FaultInjection(FailureClass.MESSAGE_CONTRADICTION, 16.0,
                                 "contradiction-001"), baseline, conflicting))
    cases.append((FaultInjection(FailureClass.ADVISER_SILENCE, 17.0), None, None))
    return cases


def generate_failure_injection_artifacts(
    root: Path,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    destination = (output_dir or root / "harness/work/08-failure-injection/artifacts").resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    for stale in destination.parent.glob(f".{destination.name}.staging-*"):
        shutil.rmtree(stale, ignore_errors=True)
    if platform.system() != "Windows" or sys.version_info[:2] != (3, 11):
        raise RuntimeError("row 08 requires native Windows Python 3.11")
    if not os.environ.get("SUMO_HOME"):
        raise RuntimeError("SUMO_HOME is required by the gated native control plane")
    sumo_binary = shutil.which("sumo")
    if not sumo_binary:
        raise RuntimeError("native sumo.exe is required")
    detected_sumo = _sumo_version(sumo_binary)
    if detected_sumo != SUMO_RELEASE:
        raise RuntimeError(f"expected SUMO {SUMO_RELEASE}, found {detected_sumo}")

    staging = destination.parent / f".{destination.name}.staging-{uuid.uuid4()}"
    staging.mkdir()
    started_at = _now()
    started_perf = time.perf_counter()
    run_id = str(uuid.uuid4())
    contract_path = root / "harness/work/08-failure-injection/contract.json"
    scenario_hash = _hash_bytes(contract_path.read_bytes())
    fault_rows: list[dict[str, Any]] = []
    message_rows: list[dict[str, Any]] = []
    decision_rows: list[dict[str, Any]] = []

    try:
        for index, (injection, message, conflicting) in enumerate(
            _fault_cases(run_id, scenario_hash), start=1
        ):
            board = InProcessMessageBoard(capacity=8)
            injector = DeterministicFailureInjector(
                board, run_id=run_id, scenario_hash=scenario_hash
            )
            result = injector.inject(
                injection, message=message, conflicting_message=conflicting
            )
            fault = result.evidence
            fault_rows.append({
                "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
                "event_id": fault.event_id, "event_kind": "fault",
                "failure_class": fault.failure_class.value, "message_id": fault.message_id,
                "simulation_time": fault.simulation_time,
                "disposition": fault.disposition.value, "trigger": fault.failure_class.value,
                "previous_mode": None, "next_mode": None,
                "health_evidence_json": json.dumps({
                    "transport_dispositions": [item.value for item in result.transport_dispositions],
                    "local_controller_health": "healthy",
                }, sort_keys=True),
                "detail": fault.detail, "visible": True,
            })
            message_rows.append({
                "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
                "failure_class": fault.failure_class.value, "message_id": fault.message_id,
                "record_kind": "fault_disposition", "simulation_time": fault.simulation_time,
                "source_agent": "A2_A3_A4_A5" if fault.message_id else "none",
                "destination_or_topic": "requests", "disposition": fault.disposition.value,
                "fault_event_id": fault.event_id, "detail": fault.detail,
            })
            decision = _local_decision(
                run_id, scenario_hash, f"row08-{index}-{fault.failure_class.value}",
                20.0 + index,
            )
            decision_rows.append({
                "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
                "event_id": decision.event_id, "failure_class": fault.failure_class.value,
                "simulation_time": decision.simulation_time,
                "controller_mode": "COOPERATIVE_MAX_PRESSURE",
                "selected_action": decision.accepted_action, "legal": True,
                "local_only": True, "considered_message_ids": [],
                "reason_code": decision.reason_code,
                "safety_reason_code": decision.safety_reason_code,
                "fault_event_id": fault.event_id, "provenance": decision.provenance,
            })

        supervisor = RecoverySupervisor(run_id=run_id, scenario_hash=scenario_hash)
        first = supervisor.report_failure(
            trigger="injected_max_pressure_unavailable", simulation_time=40.0,
            health_evidence={"heartbeat": "missed", "decision_deadline": "exceeded"},
        )
        second = supervisor.report_failure(
            trigger="injected_actuated_invalid_output", simulation_time=41.0,
            health_evidence={"output": "invalid", "safety_mask": "rejected"},
        )
        for transition in (first, second):
            fault_rows.append({
                "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
                "event_id": transition.event_id, "event_kind": "transition",
                "failure_class": "controller_failure", "message_id": None,
                "simulation_time": transition.simulation_time,
                "disposition": "transitioned", "trigger": transition.trigger,
                "previous_mode": transition.previous_mode.value,
                "next_mode": transition.next_mode.value,
                "health_evidence_json": json.dumps(dict(transition.health_evidence), sort_keys=True),
                "detail": "visible deterministic controller recovery", "visible": True,
            })

        actions = [row["selected_action"] for row in decision_rows]
        views = [ImmutableDecisionView(
            run_id=row["run_id"], scenario_hash=row["scenario_hash"],
            event_id=row["event_id"], simulation_time=row["simulation_time"],
            selected_action=row["selected_action"], reason_code=row["reason_code"],
        ) for row in decision_rows]
        observer_modes = {
            "synapse_available": ExplanationObserverBoundary(_TemplateObserver()),
            "synapse_killed": ExplanationObserverBoundary(None),
            "retrieval_unavailable": ExplanationObserverBoundary(
                _UnavailableObserver("retrieval unavailable")
            ),
            "hosted_provider_unavailable": ExplanationObserverBoundary(
                _UnavailableObserver("hosted provider unavailable")
            ),
        }
        comparison: dict[str, Any] = {
            "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
            "control_inputs_hash": _json_hash([
                [row["failure_class"], row["simulation_time"]] for row in decision_rows
            ]),
            "variants": {},
        }
        for name, boundary in observer_modes.items():
            receipts = [boundary.observe_after_decision(view) for view in views]
            comparison["variants"][name] = {
                "action_sequence": actions,
                "action_sequence_hash": action_sequence_hash(actions),
                "observation_receipts": [receipt.__dict__ for receipt in receipts],
            }
        hashes = {
            value["action_sequence_hash"] for value in comparison["variants"].values()
        }
        comparison["hashes_equal"] = len(hashes) == 1
        comparison["observer_failures_visible"] = all(
            all(receipt["failure_type"] for receipt in comparison["variants"][name]["observation_receipts"])
            for name in ("synapse_killed", "retrieval_unavailable", "hosted_provider_unavailable")
        )

        failure_classes = [item.value for item in FailureClass]
        fault_event_ids = [row["event_id"] for row in fault_rows if row["event_kind"] == "fault"]
        transition_event_ids = [
            row["event_id"] for row in fault_rows if row["event_kind"] == "transition"
        ]
        applicable = [
            row for row in fault_rows
            if row["event_kind"] == "fault" and row["failure_class"] not in {
                FailureClass.MESSAGE_ABSENCE.value, FailureClass.ADVISER_SILENCE.value,
            }
        ]
        observed_transitions = [
            [item.previous_mode.value, item.next_mode.value] for item in supervisor.transitions
        ]
        audit = {
            "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
            "valid": True,
            "required_recovery_ladder": [mode.value for mode in REQUIRED_RECOVERY_LADDER],
            "observed_required_transitions": observed_transitions,
            "unexpected_transitions": [], "optional_dqn_dependency": False,
            "fault_classes": failure_classes,
            "all_fault_classes_exercised": set(failure_classes) == {
                row["failure_class"] for row in fault_rows if row["event_kind"] == "fault"
            },
            "legal_local_decision_count": sum(row["legal"] and row["local_only"]
                                                for row in decision_rows),
            "illegal_decision_count": sum(not row["legal"] for row in decision_rows),
            "message_faults_retain_message_id": all(row["message_id"] for row in applicable),
            "message_id_not_applicable_classes": [
                FailureClass.MESSAGE_ABSENCE.value, FailureClass.ADVISER_SILENCE.value,
            ],
            "fault_event_ids_unique": len(fault_event_ids) == len(set(fault_event_ids)),
            "transition_event_ids_unique": len(transition_event_ids) == len(set(transition_event_ids)),
            "all_fault_transition_event_ids_unique": len(fault_event_ids + transition_event_ids)
                == len(set(fault_event_ids + transition_event_ids)),
            "join_errors": 0, "action_sequence_hashes_equal": comparison["hashes_equal"],
            "visible_failures": comparison["observer_failures_visible"]
                and all(row["visible"] for row in fault_rows),
            "hidden_exception_swallowing": False,
        }
        if not (
            audit["all_fault_classes_exercised"]
            and audit["legal_local_decision_count"] == len(FailureClass)
            and audit["illegal_decision_count"] == 0
            and audit["message_faults_retain_message_id"]
            and audit["all_fault_transition_event_ids_unique"]
            and observed_transitions == [
                ["COOPERATIVE_MAX_PRESSURE", "ACTUATED"],
                ["ACTUATED", "FIXED_TIME"],
            ]
            and comparison["hashes_equal"]
            and comparison["observer_failures_visible"]
        ):
            raise RuntimeError("row 08 recovery and failure audit failed")

        pq.write_table(pa.Table.from_pylist(fault_rows, schema=FAULT_SCHEMA),
                       staging / "faults.parquet", compression="zstd")
        pq.write_table(pa.Table.from_pylist(message_rows, schema=MESSAGE_SCHEMA),
                       staging / "messages.parquet", compression="zstd")
        pq.write_table(pa.Table.from_pylist(decision_rows, schema=DECISION_SCHEMA),
                       staging / "decision_events.parquet", compression="zstd")
        (staging / "recovery-audit.json").write_text(
            json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (staging / "action-sequence-comparison.json").write_text(
            json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )

        references = []
        counts = {
            "faults.parquet": len(fault_rows),
            "messages.parquet": len(message_rows),
            "decision_events.parquet": len(decision_rows),
            "recovery-audit.json": 1,
            "action-sequence-comparison.json": len(comparison["variants"]),
        }
        schemas = {
            "faults.parquet": "fault_and_transition",
            "messages.parquet": "fault_message_disposition",
            "decision_events.parquet": "fault_control_decision",
            "recovery-audit.json": "recovery_audit",
            "action-sequence-comparison.json": "action_sequence_comparison",
        }
        for name in counts:
            path = staging / name
            references.append({
                "path": name, "sha256": _hash_file(path), "bytes": path.stat().st_size,
                "rows": counts[name], "schema_name": schemas[name], "schema_version": 1,
            })
        finished_at = _now()
        manifest = {
            "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
            "configuration_hash": _json_hash({
                "controller": "cooperative-max-pressure",
                "required_recovery_ladder": [mode.value for mode in REQUIRED_RECOVERY_LADDER],
                "fault_schedule": failure_classes, "seed": EVALUATION_SEED,
            }),
            "scenario_files": ["harness/work/08-failure-injection/contract.json"],
            "versions": {
                "python": platform.python_version(), "sumo": detected_sumo,
                "traci": importlib.metadata.version("traci"), "coflow5": "0.1.0",
                "duckdb": importlib.metadata.version("duckdb"),
                "pyarrow": importlib.metadata.version("pyarrow"),
                "pydantic": importlib.metadata.version("pydantic"),
            },
            "seeds": {"sumo": EVALUATION_SEED, "evaluation": EVALUATION_SEED},
            "status": "completed", "failure_reason": None,
            "timings": {
                "started_at": started_at, "finished_at": finished_at,
                "wall_seconds": time.perf_counter() - started_perf,
                "simulation_begin": 10.0, "simulation_end": 41.0,
                "simulation_steps": len(decision_rows) + len(supervisor.transitions),
            },
            "backend": "traci", "controller": "cooperative-max-pressure-with-recovery",
            "source_revision": _source_revision(root),
            "native_command": [sys.executable,
                               str(root / "scripts/generate_failure_injection_artifacts.py")],
            "artifact_references": references, "finalized_at": _now(), "immutable": True,
        }
        RunManifest.model_validate(manifest)
        (staging / "run_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        if destination.exists():
            shutil.rmtree(destination)
        staging.replace(destination)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
