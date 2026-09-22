from __future__ import annotations

import hashlib
import importlib.metadata
import json
import math
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

import pyarrow as pa
import pyarrow.parquet as pq

from coflow5.a2 import A2EmergencyAgent, EmergencyPriorityPayload, RoadPosition
from coflow5.a3 import A3MultimodalAgent, CrossingStatePayload
from coflow5.control import (
    A1RequestArbitrator,
    ArbitrationContext,
    DeterministicSafetyMask,
    controlled_cross_plan,
)
from coflow5.evidence.schemas import RunManifest
from coflow5.messaging import InProcessMessageBoard, MessageEnvelope, thaw_json
from coflow5.sumo_adapter.cooperation_runner import (
    NativeCooperationResult,
    ScheduledA1Action,
    run_native_cooperation_scenario,
)
from coflow5.sumo_adapter.evidence_runner import NativeTraCIResult, run_native_traci_evidence

SUMO_RELEASE = "1.27.1"
EVALUATION_SEED = 43
SCENARIO_FILES = (
    "scenarios/safety-mask/safety.net.xml",
    "scenarios/cooperation/cooperation.rou.xml",
    "scenarios/cooperation/cooperation.tls.xml",
    "scenarios/cooperation/cooperation-reference.sumocfg",
    "scenarios/cooperation/cooperation-control.sumocfg",
)
SOURCE_FILES = (
    "scripts/generate_cooperation_artifacts.py",
    "src/coflow5/a2/emergency.py",
    "src/coflow5/a3/multimodal.py",
    "src/coflow5/control/request_arbitration.py",
    "src/coflow5/messaging/envelope.py",
    "src/coflow5/sumo_adapter/cooperation_runner.py",
    "src/coflow5/evidence/cooperation_artifacts.py",
)

MESSAGE_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("scenario_case", pa.string()),
    ("message_id", pa.string()), ("record_kind", pa.string()),
    ("source_agent", pa.string()), ("destination_or_topic", pa.string()),
    ("simulation_time", pa.float64()), ("expires_at", pa.float64()),
    ("priority_class", pa.string()), ("payload_type", pa.string()),
    ("payload_json", pa.string()), ("referenced_message_id", pa.string()),
    ("event_id", pa.string()), ("accepted", pa.bool_()),
    ("reason_code", pa.string()), ("provenance", pa.string()),
])
DECISION_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("scenario_case", pa.string()),
    ("event_id", pa.string()), ("referenced_message_id", pa.string()),
    ("reply_message_id", pa.string()), ("simulation_time", pa.float64()),
    ("recorded_at", pa.string()), ("source_agent", pa.string()),
    ("priority_class", pa.string()), ("accepted", pa.bool_()),
    ("selected_action", pa.string()), ("reason_code", pa.string()),
    ("safety_reason_code", pa.string()), ("constraints", pa.list_(pa.string())),
    ("provenance", pa.string()),
])
TRIP_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("scenario_case", pa.string()),
    ("trip_id", pa.string()), ("actor_type", pa.string()),
    ("baseline_duration_s", pa.float64()), ("observed_duration_s", pa.float64()),
    ("travel_effect_s", pa.float64()), ("waiting_time_s", pa.float64()),
    ("lateness_s", pa.float64()), ("headway_gap_s", pa.float64()),
    ("unfinished", pa.bool_()), ("evidence_basis", pa.string()),
])
KPI_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("metric_category", pa.string()),
    ("metric_name", pa.string()), ("metric_value", pa.float64()),
    ("unit", pa.string()), ("evidence_basis", pa.string()),
    ("claim_boundary", pa.string()),
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


def _percentile(values: Iterable[float], percentile: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    rank = (len(ordered) - 1) * percentile
    lower, upper = math.floor(rank), math.ceil(rank)
    if lower == upper:
        return float(ordered[lower])
    fraction = rank - lower
    return float(ordered[lower] * (1 - fraction) + ordered[upper] * fraction)


def _message_row(message: MessageEnvelope, scenario_case: str) -> dict[str, Any]:
    payload = thaw_json(message.payload)
    assert isinstance(payload, dict)
    is_reply = message.payload_type == "request_decision_reply"
    return {
        "schema_version": 1,
        "run_id": message.run_id,
        "scenario_hash": message.scenario_hash,
        "scenario_case": scenario_case,
        "message_id": message.message_id,
        "record_kind": "reply" if is_reply else "request",
        "source_agent": message.source_agent,
        "destination_or_topic": message.destination_or_topic,
        "simulation_time": message.simulation_time,
        "expires_at": message.expires_at,
        "priority_class": message.priority_class.value,
        "payload_type": message.payload_type,
        "payload_json": json.dumps(payload, sort_keys=True, separators=(",", ":")),
        "referenced_message_id": payload.get("referenced_message_id") if is_reply else None,
        "event_id": payload.get("event_id") if is_reply else None,
        "accepted": payload.get("accepted") if is_reply else None,
        "reason_code": payload.get("reason_code") if is_reply else None,
        "provenance": message.provenance,
    }


def _actor_type(trip_id: str) -> str:
    if trip_id.startswith("emergency-"):
        return "emergency"
    if trip_id.startswith("bus-"):
        return "transit"
    return "civilian"


def _scenario_case(trip_id: str) -> str:
    if trip_id == "emergency-conflict":
        return "crossing_emergency_conflict"
    if trip_id.startswith("emergency-"):
        return "two_emergencies"
    if trip_id == "bus-early":
        return "early_bus"
    if trip_id.startswith("bus-"):
        return "late_bus"
    return "network_externality"


def _trip_rows(
    run_id: str,
    scenario_hash: str,
    reference: NativeTraCIResult,
    observed: NativeCooperationResult,
) -> list[dict[str, Any]]:
    baseline = {str(row["trip_id"]): row for row in reference.trips}
    controlled = {str(row["trip_id"]): row for row in observed.trips}
    if set(baseline) != set(controlled):
        raise RuntimeError("paired native TraCI runs produced different trip identities")
    bus_arrivals = {
        trip_id: float(row["arrival"])
        for trip_id, row in controlled.items()
        if trip_id in {"bus-late", "bus-following"} and not row["unfinished"]
    }
    observed_headway_gap = 0.0
    if set(bus_arrivals) == {"bus-late", "bus-following"}:
        observed_headway_gap = abs(
            (bus_arrivals["bus-following"] - bus_arrivals["bus-late"]) - 20.0
        )
    rows: list[dict[str, Any]] = []
    for trip_id in sorted(controlled):
        base = baseline[trip_id]
        control = controlled[trip_id]
        unfinished = bool(base["unfinished"] or control["unfinished"])
        baseline_duration = None if base["unfinished"] else float(base["duration"])
        observed_duration = None if control["unfinished"] else float(control["duration"])
        effect = (
            None if baseline_duration is None or observed_duration is None
            else observed_duration - baseline_duration
        )
        rows.append({
            "schema_version": 1,
            "run_id": run_id,
            "scenario_hash": scenario_hash,
            "scenario_case": _scenario_case(trip_id),
            "trip_id": trip_id,
            "actor_type": _actor_type(trip_id),
            "baseline_duration_s": baseline_duration,
            "observed_duration_s": observed_duration,
            "travel_effect_s": effect,
            "waiting_time_s": float(control["waiting_time_s"]),
            "lateness_s": float(control["time_loss_s"]),
            "headway_gap_s": observed_headway_gap if trip_id in bus_arrivals else 0.0,
            "unfinished": unfinished,
            "evidence_basis": (
                "paired-native-traci-tripinfo; same scenario_hash and seed; "
                "reference=static; observed=A1-safety-gated-cooperation"
            ),
        })
    return rows


def _kpi_rows(
    run_id: str,
    scenario_hash: str,
    trips: list[dict[str, Any]],
    *,
    pedestrian_waits: tuple[float, ...],
    remaining_clearance: float,
    requested_transit_externality: float,
    recovery_completed: bool,
) -> list[dict[str, Any]]:
    completed = [row for row in trips if not row["unfinished"]]
    emergency = [row for row in completed if row["actor_type"] == "emergency"]
    civilian = [row for row in completed if row["actor_type"] == "civilian"]
    transit = [row for row in completed if row["actor_type"] == "transit"]
    emergency_durations = [float(row["observed_duration_s"]) for row in emergency]
    emergency_effects = [float(row["travel_effect_s"]) for row in emergency]
    civilian_positive_delay = sum(max(0.0, float(row["travel_effect_s"])) for row in civilian)
    transit_lateness = [float(row["lateness_s"]) for row in transit]
    headway_gap = max((float(row["headway_gap_s"]) for row in transit), default=0.0)
    native_basis = "paired native TraCI tripinfo over identical demand, scenario_hash, and seed"
    pedestrian_basis = "typed A3 simulated crossing state; not a roadside measurement"
    request_basis = "typed A3 request estimate; not a causal traffic-effect estimate"
    metrics = (
        ("emergency", "emergency_mean_travel_time_s", sum(emergency_durations) / len(emergency_durations), "seconds", native_basis),
        ("emergency", "emergency_travel_effect_s", sum(emergency_effects) / len(emergency_effects), "seconds_vs_native_reference", native_basis),
        ("externality", "civilian_delay_externality_s", civilian_positive_delay, "seconds", native_basis),
        ("pedestrian", "pedestrian_mean_wait_s", sum(pedestrian_waits) / len(pedestrian_waits), "seconds", pedestrian_basis),
        ("pedestrian", "pedestrian_p95_wait_s", _percentile(pedestrian_waits, 0.95), "seconds", pedestrian_basis),
        ("pedestrian", "pedestrian_max_wait_s", max(pedestrian_waits), "seconds", pedestrian_basis),
        ("pedestrian", "pedestrian_remaining_clearance_s", remaining_clearance, "seconds", pedestrian_basis),
        ("pedestrian", "pedestrian_clearance_truncations", 0.0, "count", "A1 request decisions plus native safety-event reconciliation"),
        ("transit", "transit_lateness_s", sum(transit_lateness) / len(transit_lateness), "seconds_time_loss", native_basis),
        ("transit", "transit_headway_regularity_s", headway_gap, "absolute_gap_seconds", native_basis),
        ("externality", "transit_other_traffic_externality_s", requested_transit_externality, "seconds", request_basis),
        ("authority", "specialist_signal_writes", 0.0, "count", "native writer registry and forbidden-import scan"),
        ("recovery", "post_passage_recovery_completed", float(recovery_completed), "boolean", "native A1 safety-gated NS-yellow/all-red/EW-green sequence"),
    )
    boundary = (
        "Simulation only; no lives-saved claim, no measured-air-quality claim, "
        "and no real-world casualty interpretation."
    )
    return [{
        "schema_version": 1,
        "run_id": run_id,
        "scenario_hash": scenario_hash,
        "metric_category": category,
        "metric_name": name,
        "metric_value": value,
        "unit": unit,
        "evidence_basis": basis,
        "claim_boundary": boundary,
    } for category, name, value, unit, basis in metrics]


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


def generate_cooperation_artifacts(root: Path, output_dir: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    destination = (output_dir or root / "harness/work/07-a2-a3/artifacts").resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    for pattern in (f".{destination.name}.staging-*", f".{destination.name}.previous-*"):
        for stale in destination.parent.glob(pattern):
            shutil.rmtree(stale, ignore_errors=True)
    if platform.system() != "Windows" or sys.version_info[:2] != (3, 11):
        raise RuntimeError("row 07 requires native Windows Python 3.11")
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
    scenario_hash = _scenario_hash(root)
    board = InProcessMessageBoard(capacity=64)
    a2 = A2EmergencyAgent(board)
    a3 = A3MultimodalAgent(board)
    arbitrator = A1RequestArbitrator(
        transport=board, safety_mask=DeterministicSafetyMask(controlled_cross_plan())
    )
    request_messages: list[MessageEnvelope] = []
    reply_messages: list[MessageEnvelope] = []
    decisions: list[Any] = []
    rounds: list[Any] = []
    created = datetime(2026, 9, 22, 12, 0, tzinfo=timezone.utc)

    def keep(result: Any) -> None:
        if result is None or not result.accepted or result.message is None:
            raise RuntimeError("required specialist request was not accepted by transport")
        request_messages.append(result.message)

    def arbitrate(time_value: float, phase: str, phase_entered_at: float) -> None:
        result = arbitrator.arbitrate(ArbitrationContext(
            run_id=run_id,
            scenario_hash=scenario_hash,
            signal_id="J0",
            simulation_time=time_value,
            current_phase_id=phase,
            phase_entered_at=phase_entered_at,
            flow_requested_phase_id=phase,
            downstream_feasible_by_movement={
                "north": True, "east": True, "pedestrian_east_west": True,
            },
        ))
        rounds.append(result)
        decisions.extend(result.decisions)
        reply_messages.extend(result.replies)

    try:
        crossing_payload = CrossingStatePayload(
            scenario_case="crossing_emergency_conflict",
            crossing_id="north_south_crossing",
            signal_id="J0",
            active_crossing=True,
            remaining_clearance_seconds=8.0,
            requested_movement="pedestrian_east_west",
            requested_phase_id="NS_GREEN",
            expected_benefit_seconds=8.0,
            civilian_delay_externality_seconds=2.0,
        )
        keep(a3.publish_crossing_state(
            run_id=run_id, scenario_hash=scenario_hash, message_id="crossing-active-001",
            correlation_id="crossing-conflict", created_at=created, simulation_time=10.0,
            expires_at=15.0, payload=crossing_payload,
        ))
        keep(a2.publish_priority_request(
            run_id=run_id, scenario_hash=scenario_hash, message_id="emergency-conflict-001",
            correlation_id="crossing-conflict", created_at=created, simulation_time=10.0,
            payload=EmergencyPriorityPayload(
                scenario_case="crossing_emergency_conflict", vehicle_id="emergency-conflict",
                signal_id="J0", position=RoadPosition(edge_id="E_in", lane_id="E_in_0", distance_m=80),
                route=("E_in", "W_out"), next_controlled_junctions=("J0",), eta_seconds=8,
                urgency=1.0, expected_benefit_seconds=18,
                civilian_delay_externality_seconds=5, requested_movement="east",
                requested_phase_id="EW_GREEN", downstream_available=True, request_expires_at=15,
            ),
        ))
        arbitrate(10.0, "NS_GREEN", 0.0)

        for suffix, externality in (("alpha", 4.0), ("beta", 6.0)):
            keep(a2.publish_priority_request(
                run_id=run_id, scenario_hash=scenario_hash,
                message_id=f"emergency-{suffix}", correlation_id=f"two-emergencies-{suffix}",
                created_at=created, simulation_time=20.0,
                payload=EmergencyPriorityPayload(
                    scenario_case="two_emergencies", vehicle_id=f"emergency-{suffix}",
                    signal_id="J0", position=RoadPosition(
                        edge_id="N_in", lane_id="N_in_0", distance_m=60),
                    route=("N_in", "S_out"), next_controlled_junctions=("J0",), eta_seconds=6,
                    urgency=0.9, expected_benefit_seconds=14,
                    civilian_delay_externality_seconds=externality, requested_movement="north",
                    requested_phase_id="NS_GREEN", downstream_available=True, request_expires_at=25,
                ),
            ))
        keep(a2.publish_priority_request(
            run_id=run_id, scenario_hash=scenario_hash, message_id="emergency-blocked-001",
            correlation_id="blocked-downstream", created_at=created, simulation_time=20.0,
            payload=EmergencyPriorityPayload(
                scenario_case="blocked_downstream", vehicle_id="emergency-blocked",
                signal_id="J0", position=RoadPosition(edge_id="E_in", lane_id="E_in_0", distance_m=40),
                route=("E_in", "W_out"), next_controlled_junctions=("J0",), eta_seconds=4,
                urgency=1.0, expected_benefit_seconds=20,
                civilian_delay_externality_seconds=8, requested_movement="east",
                requested_phase_id="EW_GREEN", downstream_available=False, request_expires_at=25,
            ),
        ))
        arbitrate(20.0, "NS_GREEN", 0.0)

        keep(a3.publish_pedestrian_deadline(
            run_id=run_id, scenario_hash=scenario_hash, message_id="ped-deadline-001",
            correlation_id="pedestrian-deadline", created_at=created, simulation_time=30.0,
            expires_at=35.0, scenario_case="pedestrian_deadline",
            crossing_id="east_west_crossing", signal_id="J0", wait_age_seconds=50,
            deadline_seconds=60, requested_movement="pedestrian_east_west",
            requested_phase_id="EW_GREEN", expected_benefit_seconds=10,
            civilian_delay_externality_seconds=3,
        ))
        arbitrate(30.0, "EW_GREEN", 29.0)

        keep(a3.publish_transit_priority(
            run_id=run_id, scenario_hash=scenario_hash, message_id="late-bus-001",
            correlation_id="late-bus", created_at=created, simulation_time=40.0,
            expires_at=45.0, scenario_case="late_bus", vehicle_id="bus-late",
            signal_id="J0", schedule_deviation_seconds=90, observed_headway_seconds=370,
            target_headway_seconds=300, requested_movement="east", requested_phase_id="EW_GREEN",
            expected_benefit_seconds=35, other_traffic_externality_seconds=3,
        ))
        arbitrate(40.0, "EW_GREEN", 29.0)

        early = a3.publish_transit_priority(
            run_id=run_id, scenario_hash=scenario_hash, message_id="early-bus-forbidden",
            correlation_id="early-bus", created_at=created, simulation_time=50.0,
            expires_at=55.0, scenario_case="early_bus", vehicle_id="bus-early",
            signal_id="J0", schedule_deviation_seconds=-10, observed_headway_seconds=300,
            target_headway_seconds=300, requested_movement="east", requested_phase_id="EW_GREEN",
            expected_benefit_seconds=10, other_traffic_externality_seconds=2,
        )
        if early is not None:
            raise RuntimeError("early/on-time bus incorrectly published transit priority")

        request_by_id = {message.message_id: message for message in request_messages}
        request_case = {
            message_id: str(message.payload["scenario_case"])
            for message_id, message in request_by_id.items()
        }
        message_rows = [_message_row(message, request_case[message.message_id])
                        for message in request_messages]
        for reply in reply_messages:
            referenced = str(reply.payload["referenced_message_id"])
            message_rows.append(_message_row(reply, request_case[referenced]))
        decision_rows = []
        for decision in decisions:
            value = asdict(decision)
            value["schema_version"] = 1
            value["scenario_case"] = request_case[decision.referenced_message_id]
            decision_rows.append(value)

        request_actions = (
            ScheduledA1Action(10.0, "request-round-10", rounds[0].selected_action,
                              {"north_south_crossing": 8.0}),
            ScheduledA1Action(20.0, "request-round-20", rounds[1].selected_action),
            ScheduledA1Action(30.0, "request-round-30", rounds[2].selected_action),
            ScheduledA1Action(40.0, "request-round-40", rounds[3].selected_action),
        )
        recovery_actions = (
            ScheduledA1Action(26.0, "post-emergency-recovery-yellow", "NS_YELLOW"),
            ScheduledA1Action(28.0, "post-emergency-recovery-all-red", "ALL_RED_TO_EW"),
            ScheduledA1Action(29.0, "post-emergency-recovery-general-flow", "EW_GREEN"),
            ScheduledA1Action(50.0, "balanced-flow-return-yellow", "EW_YELLOW"),
            ScheduledA1Action(52.0, "balanced-flow-return-all-red", "ALL_RED_TO_NS"),
            ScheduledA1Action(53.0, "balanced-flow-return-ns", "NS_GREEN"),
        )
        actions = tuple(sorted((*request_actions, *recovery_actions),
                               key=lambda item: (item.simulation_time, item.proposal_id)))
        reference = run_native_traci_evidence(
            sumo_binary=sumo_binary,
            config=root / "scenarios/cooperation/cooperation-reference.sumocfg",
            tripinfo_path=staging / "reference-tripinfo.xml",
            seed=EVALUATION_SEED,
        )
        native = run_native_cooperation_scenario(
            sumo_binary=sumo_binary,
            config=root / "scenarios/cooperation/cooperation-control.sumocfg",
            tripinfo_path=staging / "controlled-tripinfo.xml",
            run_id=run_id,
            scenario_hash=scenario_hash,
            seed=EVALUATION_SEED,
            actions=actions,
        )
        trip_rows = _trip_rows(run_id, scenario_hash, reference, native)
        recovery_ids = {action.proposal_id for action in recovery_actions[:3]}
        recovery_commands = {
            command.proposal_id: command.phase_id for command in native.executed_commands
            if command.proposal_id in recovery_ids
        }
        recovery_completed = recovery_commands == {
            "post-emergency-recovery-yellow": "NS_YELLOW",
            "post-emergency-recovery-all-red": "ALL_RED_TO_EW",
            "post-emergency-recovery-general-flow": "EW_GREEN",
        }
        kpi_rows = _kpi_rows(
            run_id, scenario_hash, trip_rows,
            pedestrian_waits=(50.0,), remaining_clearance=8.0,
            requested_transit_externality=3.0,
            recovery_completed=recovery_completed,
        )

        pq.write_table(pa.Table.from_pylist(message_rows, schema=MESSAGE_SCHEMA),
                       staging / "messages.parquet", compression="zstd")
        pq.write_table(pa.Table.from_pylist(decision_rows, schema=DECISION_SCHEMA),
                       staging / "decision_events.parquet", compression="zstd")
        pq.write_table(pa.Table.from_pylist(trip_rows, schema=TRIP_SCHEMA),
                       staging / "trips.parquet", compression="zstd")
        pq.write_table(pa.Table.from_pylist(kpi_rows, schema=KPI_SCHEMA),
                       staging / "cooperation-kpis.parquet", compression="zstd")

        request_ids = set(request_by_id)
        decision_request_ids = {row["referenced_message_id"] for row in decision_rows}
        replies = [row for row in message_rows if row["record_kind"] == "reply"]
        reply_request_ids = {row["referenced_message_id"] for row in replies}
        event_ids = [row["event_id"] for row in decision_rows]
        control_event_ids = {event.event_id for event in native.safety_events}
        control_command_ids = {command.event_id for command in native.executed_commands}
        by_request = {row["referenced_message_id"]: row for row in decision_rows}
        if not (
            request_ids == decision_request_ids == reply_request_ids
            and len(event_ids) == len(set(event_ids))
            and {row["event_id"] for row in replies} == set(event_ids)
            and by_request["emergency-conflict-001"]["reason_code"] == "REJECTED_PEDESTRIAN_CLEARANCE"
            and by_request["emergency-alpha"]["accepted"] is True
            and by_request["emergency-beta"]["reason_code"] == "REJECTED_SAME_TIER_TIEBREAK"
            and by_request["emergency-blocked-001"]["reason_code"] == "REJECTED_DOWNSTREAM_BLOCKED"
            and "early-bus-forbidden" not in request_ids
            and recovery_completed
            and native.writer_count_by_signal == {"J0": 1}
            and len(native.safety_events) == len(native.executed_commands) >= len(actions)
            and control_event_ids == control_command_ids
            and bool(native.max_pressure_decisions)
            and all(
                decision.reason_code == "MAX_PRESSURE_LOCAL_ONLY"
                and not decision.considered_message_ids
                for decision in native.max_pressure_decisions
            )
            and all(event.accepted and event.reason_code == "ACCEPTED" for event in native.safety_events)
            and reference.departed_total == reference.arrived_total == len(reference.trips)
            and native.departed_total == native.arrived_total == len(native.trips)
            and reference.teleport_events == native.teleport_events == 0
            and all("native-traci" in row["evidence_basis"] for row in trip_rows)
        ):
            raise RuntimeError("row 07 request, safety, recovery, or native evidence audit failed")

        for temporary in (staging / "reference-tripinfo.xml", staging / "controlled-tripinfo.xml"):
            temporary.unlink()
        references = []
        for name, rows, schema_name in (
            ("messages.parquet", len(message_rows), "cooperation_message"),
            ("decision_events.parquet", len(decision_rows), "request_decision"),
            ("trips.parquet", len(trip_rows), "paired_native_cooperation_trip"),
            ("cooperation-kpis.parquet", len(kpi_rows), "cooperation_kpi"),
        ):
            path = staging / name
            references.append({
                "path": name, "sha256": _hash_file(path), "bytes": path.stat().st_size,
                "rows": rows, "schema_name": schema_name, "schema_version": 1,
            })
        finished_at = _now()
        source_hashes = {relative: _hash_file(root / relative) for relative in SOURCE_FILES}
        manifest = {
            "schema_version": 1,
            "run_id": run_id,
            "scenario_hash": scenario_hash,
            "configuration_hash": _json_hash({
                "controller": "cooperative-max-pressure",
                "arbitration": "deterministic-v1",
                "seed": EVALUATION_SEED,
                "request_actions": [asdict(action) for action in request_actions],
                "post_passage_recovery": [asdict(action) for action in recovery_actions[:3]],
                "reference": "native-static-same-demand",
            }),
            "scenario_files": list(SCENARIO_FILES),
            "versions": {
                "python": platform.python_version(), "sumo": detected_sumo,
                "traci": importlib.metadata.version("traci"), "coflow5": "0.1.0",
                "duckdb": importlib.metadata.version("duckdb"),
                "pyarrow": importlib.metadata.version("pyarrow"),
                "pydantic": importlib.metadata.version("pydantic"),
            },
            "seeds": {"sumo": EVALUATION_SEED, "evaluation": EVALUATION_SEED},
            "status": "completed",
            "timings": {
                "started_at": started_at, "finished_at": finished_at,
                "wall_seconds": time.perf_counter() - started_perf,
                "simulation_begin": native.simulation_begin,
                "simulation_end": native.simulation_end,
                "simulation_steps": native.simulation_steps,
            },
            "backend": "traci",
            "controller": "cooperative-max-pressure",
            "source_revision": None,
            "source_hashes": source_hashes,
            "native_command": [sys.executable, str(root / "scripts/generate_cooperation_artifacts.py")],
            "sumo_command": list(native.command),
            "artifact_references": references,
            "finalized_at": _now(),
            "immutable": True,
        }
        RunManifest.model_validate(manifest)
        (staging / "run_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        _publish_directory(staging, destination)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
