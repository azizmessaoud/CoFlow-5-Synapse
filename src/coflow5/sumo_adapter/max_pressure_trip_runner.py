from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence
from uuid import uuid4

from coflow5.control import DeterministicSafetyMask, controlled_cross_plan
from coflow5.control.a1_controller import A1FlowController
from coflow5.control.max_pressure import (
    AdvisoryRequest,
    CooperativeMaxPressureController,
    MaxPressureDecision,
    MaxPressureObservation,
    MovementPressure,
)
from coflow5.sumo_adapter.safety_runner import (
    conflicting_green_pairs,
    load_physical_signal_topology,
)
from coflow5.sumo_adapter.signal_executor import (
    ExecutedSignalCommand,
    ImmutableSafetyLog,
    SafetyEvent,
    SignalExecutorRegistry,
)
from coflow5.sumo_adapter.smoke_backends import load_traci


class MaxPressureTripEvidenceError(RuntimeError):
    """Native trip evidence is incomplete or internally inconsistent."""


@dataclass(frozen=True)
class MaxPressureTripResult:
    run_id: str
    scenario_hash: str
    controller: str
    seed: int
    trip_id: str
    flow_id: str
    flow_index: int
    trip_status: str
    departed_at_s: float | None
    arrived_at_s: float | None
    duration_s: float | None
    waiting_time_s: float | None
    time_loss_s: float | None
    standstill_seconds: int
    observed_at_s: float
    failure_reason: str | None


@dataclass(frozen=True)
class NativeMaxPressureTripRun:
    run_id: str
    scenario_hash: str
    seed: int
    simulation_begin: float
    simulation_end: float
    simulation_steps: int
    trips: tuple[MaxPressureTripResult, ...]
    kpis: Mapping[str, object]
    decisions: tuple[MaxPressureDecision, ...]
    safety_events: tuple[SafetyEvent, ...]
    executed_commands: tuple[ExecutedSignalCommand, ...]
    writer_count_by_signal: dict[str, int]
    physically_conflicting_commands: int
    max_active_vehicles: int
    teleport_events: int
    traci_version: str
    command: tuple[str, ...]


def linear_percentile(values: Sequence[float], percentile: float) -> float:
    """Linear interpolation at rank (n - 1) * percentile."""
    if not 0.0 <= percentile <= 1.0:
        raise ValueError("percentile must be in [0, 1]")
    if not values:
        return 0.0
    ordered = sorted(float(value) for value in values)
    if any(not math.isfinite(value) for value in ordered):
        raise ValueError("percentile values must be finite")
    rank = (len(ordered) - 1) * percentile
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return ordered[lower]
    fraction = rank - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def _flow_identity(trip_id: str) -> tuple[str, int]:
    flow_id, separator, index = trip_id.rpartition(".")
    if not separator or not flow_id or not index.isdigit():
        raise MaxPressureTripEvidenceError(f"unexpected SUMO flow trip id: {trip_id}")
    return flow_id, int(index)


def build_trip_rows(
    *,
    run_id: str,
    scenario_hash: str,
    seed: int,
    planned_trip_ids: Sequence[str],
    departed_at: Mapping[str, float],
    arrived_at: Mapping[str, float],
    latest_wait: Mapping[str, float],
    latest_time_loss: Mapping[str, float],
    standstill_seconds: Mapping[str, int],
    observed_at: float,
) -> tuple[MaxPressureTripResult, ...]:
    planned = tuple(planned_trip_ids)
    if not run_id or not scenario_hash:
        raise MaxPressureTripEvidenceError("run and scenario identity are required")
    if len(planned) != len(set(planned)):
        raise MaxPressureTripEvidenceError("planned trip ids must be unique")
    if not math.isfinite(observed_at) or observed_at < 0:
        raise MaxPressureTripEvidenceError("observed_at must be finite and non-negative")
    unknown = (set(departed_at) | set(arrived_at)) - set(planned)
    if unknown:
        raise MaxPressureTripEvidenceError(f"observed unknown trip ids: {sorted(unknown)}")

    rows: list[MaxPressureTripResult] = []
    for trip_id in planned:
        flow_id, flow_index = _flow_identity(trip_id)
        depart = departed_at.get(trip_id)
        arrival = arrived_at.get(trip_id)
        if arrival is not None:
            if depart is None or arrival < depart:
                raise MaxPressureTripEvidenceError(f"invalid completed trip times: {trip_id}")
            status = "completed"
            duration = arrival - depart
            wait = float(latest_wait.get(trip_id, 0.0))
            time_loss = float(latest_time_loss.get(trip_id, 0.0))
        elif depart is not None:
            if observed_at < depart:
                raise MaxPressureTripEvidenceError(f"trip departs after horizon: {trip_id}")
            status = "active-at-horizon"
            duration = observed_at - depart
            wait = float(latest_wait.get(trip_id, 0.0))
            time_loss = float(latest_time_loss.get(trip_id, 0.0))
        else:
            status = "not-departed"
            duration = None
            wait = None
            time_loss = None
        numeric = [value for value in (depart, arrival, duration, wait, time_loss) if value is not None]
        if any(not math.isfinite(float(value)) or float(value) < 0 for value in numeric):
            raise MaxPressureTripEvidenceError(f"trip metrics must be finite and non-negative: {trip_id}")
        standstill = int(standstill_seconds.get(trip_id, 0))
        if standstill < 0:
            raise MaxPressureTripEvidenceError(f"negative standstill seconds: {trip_id}")
        rows.append(MaxPressureTripResult(
            run_id=run_id,
            scenario_hash=scenario_hash,
            controller="cooperative-max-pressure",
            seed=seed,
            trip_id=trip_id,
            flow_id=flow_id,
            flow_index=flow_index,
            trip_status=status,
            departed_at_s=depart,
            arrived_at_s=arrival,
            duration_s=duration,
            waiting_time_s=wait,
            time_loss_s=time_loss,
            standstill_seconds=standstill,
            observed_at_s=observed_at,
            failure_reason=None,
        ))
    return tuple(rows)


def compute_run_kpis(
    trips: Sequence[MaxPressureTripResult],
    *,
    run_id: str,
    scenario_hash: str,
    seed: int,
    simulation_steps: int,
    max_active_vehicles: int,
    teleport_events: int,
    safety_event_count: int,
    accepted_signal_commands: int,
) -> dict[str, object]:
    rows = tuple(trips)
    if not rows or len({row.trip_id for row in rows}) != len(rows):
        raise MaxPressureTripEvidenceError("trip rows must be non-empty and unique")
    if any(
        row.run_id != run_id
        or row.scenario_hash != scenario_hash
        or row.seed != seed
        or row.controller != "cooperative-max-pressure"
        for row in rows
    ):
        raise MaxPressureTripEvidenceError("trip identity mismatch")
    allowed = {"completed", "active-at-horizon", "not-departed"}
    if any(row.trip_status not in allowed for row in rows):
        raise MaxPressureTripEvidenceError("unsupported trip status")
    completed = tuple(row for row in rows if row.trip_status == "completed")
    durations = [float(row.duration_s) for row in completed if row.duration_s is not None]
    waits = [float(row.waiting_time_s) for row in completed if row.waiting_time_s is not None]
    losses = [float(row.time_loss_s) for row in completed if row.time_loss_s is not None]
    if len(durations) != len(completed) or len(waits) != len(completed) or len(losses) != len(completed):
        raise MaxPressureTripEvidenceError("completed trip metrics are incomplete")
    planned = len(rows)
    completed_count = len(completed)
    return {
        "schema_version": 1,
        "run_id": run_id,
        "scenario_hash": scenario_hash,
        "controller": "cooperative-max-pressure",
        "seed": seed,
        "status": "completed",
        "failure_reason": None,
        "planned_trips": planned,
        "completed_trips": completed_count,
        "unfinished_trips": planned - completed_count,
        "completion_rate": completed_count / planned,
        "mean_duration_s": sum(durations) / len(durations) if durations else 0.0,
        "p95_duration_s": linear_percentile(durations, 0.95),
        "max_duration_s": max(durations, default=0.0),
        "mean_waiting_time_s": sum(waits) / len(waits) if waits else 0.0,
        "p95_waiting_time_s": linear_percentile(waits, 0.95),
        "max_waiting_time_s": max(waits, default=0.0),
        "total_time_loss_s": sum(losses),
        "standstill_vehicle_seconds": sum(row.standstill_seconds for row in rows),
        "vehicles_with_standstill": sum(row.standstill_seconds > 0 for row in rows),
        "teleport_events": int(teleport_events),
        "simulation_steps": int(simulation_steps),
        "max_active_vehicles": int(max_active_vehicles),
        "safety_event_count": int(safety_event_count),
        "accepted_signal_commands": int(accepted_signal_commands),
    }


def run_native_max_pressure_trip_scenario(
    *,
    sumo_binary: str,
    config: Path,
    network_file: Path,
    run_id: str,
    scenario_hash: str,
    seed: int,
    planned_trip_ids: Sequence[str],
    advisories: Sequence[AdvisoryRequest] = (),
    horizon_seconds: float = 120.0,
) -> NativeMaxPressureTripRun:
    """Run A1 Max-Pressure through TraCI while retaining all planned trips."""
    traci = load_traci()
    label = f"coflow5-max-pressure-trips-{uuid4()}"
    command = (
        sumo_binary, "-c", str(config), "--seed", str(seed),
        "--no-step-log", "true", "--duration-log.disable", "true",
        "--time-to-teleport", "-1",
    )
    traci.start(list(command), label=label, stdout=None)
    connection = traci.getConnection(label)
    log = ImmutableSafetyLog()
    registry = SignalExecutorRegistry()
    simulation_begin = float(connection.simulation.getTime())
    topology = load_physical_signal_topology(
        connection=connection, network_file=network_file, signal_id="J0"
    )
    safety_mask = DeterministicSafetyMask(controlled_cross_plan())
    executor = registry.acquire(
        signal_id="J0", connection=connection, safety_mask=safety_mask,
        initial_phase_id="NS_GREEN", initial_phase_entered_at=simulation_begin,
        run_id=run_id, scenario_hash=scenario_hash, log=log,
    )
    controller = CooperativeMaxPressureController(
        a1=A1FlowController(executor), safety_mask=safety_mask,
        run_id=run_id, scenario_hash=scenario_hash, signal_id="J0",
    )
    incoming_lanes = {
        "north": "N_in_0", "east": "E_in_0",
        "south": "S_in_0", "west": "W_in_0",
    }
    downstream_lanes = {
        "north": "S_out_0", "east": "W_out_0",
        "south": "N_out_0", "west": "E_out_0",
    }
    phase_entered_at = simulation_begin
    decisions: list[MaxPressureDecision] = []
    departed_at: dict[str, float] = {}
    arrived_at: dict[str, float] = {}
    latest_wait: dict[str, float] = {}
    latest_time_loss: dict[str, float] = {}
    standstill_seconds: dict[str, int] = {}
    teleport_events = 0
    max_active = 0
    steps = 0
    try:
        while float(connection.simulation.getTime()) < horizon_seconds:
            connection.simulationStep()
            steps += 1
            now = float(connection.simulation.getTime())
            for vehicle_id in connection.simulation.getDepartedIDList():
                departed_at[str(vehicle_id)] = now
            active_ids = tuple(str(value) for value in connection.vehicle.getIDList())
            max_active = max(max_active, len(active_ids))
            for vehicle_id in active_ids:
                speed = float(connection.vehicle.getSpeed(vehicle_id))
                latest_wait[vehicle_id] = float(connection.vehicle.getAccumulatedWaitingTime(vehicle_id))
                latest_time_loss[vehicle_id] = float(connection.vehicle.getTimeLoss(vehicle_id))
                if speed < 0.1:
                    standstill_seconds[vehicle_id] = standstill_seconds.get(vehicle_id, 0) + 1
            for vehicle_id in connection.simulation.getArrivedIDList():
                arrived_at[str(vehicle_id)] = now
            teleport_events += len(connection.simulation.getStartingTeleportIDList())

            movements: dict[str, MovementPressure] = {}
            for movement_id, incoming_lane in incoming_lanes.items():
                downstream_lane = downstream_lanes[movement_id]
                lane_length = float(connection.lane.getLength(downstream_lane))
                movements[movement_id] = MovementPressure(
                    upstream_queue=float(connection.lane.getLastStepHaltingNumber(incoming_lane)),
                    downstream_queue=float(connection.lane.getLastStepVehicleNumber(downstream_lane)),
                    downstream_capacity=max(1.0, lane_length / 7.5),
                )
            previous_phase = executor.current_phase_id
            decision = controller.decide(
                proposal_id=f"max-pressure-trip-{seed}-{steps:04d}",
                observation=MaxPressureObservation(
                    simulation_time=now,
                    current_phase_id=previous_phase,
                    phase_entered_at=phase_entered_at,
                    movements=movements,
                    advisories=tuple(advisories),
                ),
            )
            decisions.append(decision)
            if executor.current_phase_id != previous_phase:
                phase_entered_at = now
            if connection.simulation.getMinExpectedNumber() <= 0:
                break
        simulation_end = float(connection.simulation.getTime())
        traci_version = str(connection.getVersion()[1])
    finally:
        connection.close(False)

    trips = build_trip_rows(
        run_id=run_id,
        scenario_hash=scenario_hash,
        seed=seed,
        planned_trip_ids=planned_trip_ids,
        departed_at=departed_at,
        arrived_at=arrived_at,
        latest_wait=latest_wait,
        latest_time_loss=latest_time_loss,
        standstill_seconds=standstill_seconds,
        observed_at=simulation_end,
    )
    event_ids = {decision.event_id for decision in decisions}
    safety_ids = {event.event_id for event in log.events}
    command_ids = {command_row.event_id for command_row in log.commands}
    if not decisions or event_ids != safety_ids or event_ids != command_ids:
        raise MaxPressureTripEvidenceError("decision, safety, and command event sets do not match")
    if any(not event.accepted for event in log.events):
        raise MaxPressureTripEvidenceError("a rejected safety event cannot be an executed matched run")
    conflicting = sum(
        bool(conflicting_green_pairs(command_row.signal_state, topology))
        for command_row in log.commands
    )
    if registry.writer_count_by_signal != {"J0": 1} or conflicting:
        raise MaxPressureTripEvidenceError("single-writer or physical-conflict validation failed")
    kpis = compute_run_kpis(
        trips,
        run_id=run_id,
        scenario_hash=scenario_hash,
        seed=seed,
        simulation_steps=steps,
        max_active_vehicles=max_active,
        teleport_events=teleport_events,
        safety_event_count=len(log.events),
        accepted_signal_commands=len(log.commands),
    )
    return NativeMaxPressureTripRun(
        run_id=run_id,
        scenario_hash=scenario_hash,
        seed=seed,
        simulation_begin=simulation_begin,
        simulation_end=simulation_end,
        simulation_steps=steps,
        trips=trips,
        kpis=kpis,
        decisions=tuple(decisions),
        safety_events=log.events,
        executed_commands=log.commands,
        writer_count_by_signal=registry.writer_count_by_signal,
        physically_conflicting_commands=conflicting,
        max_active_vehicles=max_active,
        teleport_events=teleport_events,
        traci_version=traci_version,
        command=command,
    )
