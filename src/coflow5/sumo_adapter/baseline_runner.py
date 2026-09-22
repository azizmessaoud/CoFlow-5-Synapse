from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from coflow5.control import DeterministicSafetyMask, controlled_cross_plan
from coflow5.control.a1_controller import A1FlowController
from coflow5.control.baselines import BaselineController, BaselineObservation
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


@dataclass(frozen=True)
class BaselineTripResult:
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
class BaselineRunResult:
    run_id: str
    scenario_hash: str
    controller: str
    seed: int
    status: str
    failure_reason: str | None
    simulation_begin: float
    simulation_end: float
    simulation_steps: int
    planned_trips: int
    completed_trips: int
    unfinished_trips: int
    completion_rate: float
    mean_duration_s: float
    p95_duration_s: float
    max_duration_s: float
    mean_waiting_time_s: float
    p95_waiting_time_s: float
    max_waiting_time_s: float
    total_time_loss_s: float
    standstill_vehicle_seconds: int
    vehicles_with_standstill: int
    teleport_events: int
    max_active_vehicles: int
    safety_event_count: int
    accepted_signal_commands: int
    traci_version: str
    command: tuple[str, ...]
    trips: tuple[BaselineTripResult, ...]
    safety_events: tuple[SafetyEvent, ...]
    executed_commands: tuple[ExecutedSignalCommand, ...]
    writer_count_by_signal: dict[str, int]
    physically_conflicting_commands: int


class BaselineEvidenceValidationError(RuntimeError):
    """A native run returned evidence that cannot be reconciled safely."""


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = (len(ordered) - 1) * percentile
    lower = math.floor(rank)
    upper = math.ceil(rank)
    if lower == upper:
        return float(ordered[lower])
    fraction = rank - lower
    return float(ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction)


def _flow_identity(trip_id: str) -> tuple[str, int]:
    flow_id, separator, index = trip_id.rpartition(".")
    if not separator or not flow_id or not index.isdigit():
        raise BaselineEvidenceValidationError(f"unexpected SUMO flow trip id: {trip_id}")
    return flow_id, int(index)


def run_baseline_scenario(
    *,
    sumo_binary: str,
    config: Path,
    network_file: Path,
    controller: BaselineController,
    run_id: str,
    scenario_hash: str,
    seed: int,
    planned_trip_ids: tuple[str, ...],
    horizon_seconds: float,
) -> BaselineRunResult:
    """Run one controller through native TraCI and the sole A1 write capability."""
    traci = load_traci()
    label = f"coflow5-{controller.label}-{uuid4()}"
    command = (
        sumo_binary,
        "-c",
        str(config),
        "--seed",
        str(seed),
        "--no-step-log",
        "true",
        "--duration-log.disable",
        "true",
        "--time-to-teleport",
        "-1",
    )
    traci.start(list(command), label=label, stdout=None)
    connection = traci.getConnection(label)
    log = ImmutableSafetyLog()
    registry = SignalExecutorRegistry()
    simulation_begin = float(connection.simulation.getTime())
    topology = load_physical_signal_topology(
        connection=connection, network_file=network_file, signal_id="J0"
    )
    executor = registry.acquire(
        signal_id="J0",
        connection=connection,
        safety_mask=DeterministicSafetyMask(controlled_cross_plan()),
        initial_phase_id="NS_GREEN",
        initial_phase_entered_at=simulation_begin,
        run_id=run_id,
        scenario_hash=scenario_hash,
        log=log,
    )
    a1 = A1FlowController(executor)
    phase_entered_at = simulation_begin
    proposal_number = 0
    departed_at: dict[str, float] = {}
    arrived_at: dict[str, float] = {}
    latest_wait: dict[str, float] = {}
    latest_time_loss: dict[str, float] = {}
    standstill_seconds: dict[str, int] = {}
    teleport_events = 0
    max_active = 0
    steps = 0
    lane_ids = {
        "north": "N_in_0",
        "east": "E_in_0",
        "south": "S_in_0",
        "west": "W_in_0",
    }
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
                latest_wait[vehicle_id] = float(
                    connection.vehicle.getAccumulatedWaitingTime(vehicle_id)
                )
                latest_time_loss[vehicle_id] = float(connection.vehicle.getTimeLoss(vehicle_id))
                if speed < 0.1:
                    standstill_seconds[vehicle_id] = standstill_seconds.get(vehicle_id, 0) + 1
            for vehicle_id in connection.simulation.getArrivedIDList():
                arrived_at[str(vehicle_id)] = now
            teleport_events += len(connection.simulation.getStartingTeleportIDList())

            halting = {
                approach: int(connection.lane.getLastStepHaltingNumber(lane_id))
                for approach, lane_id in lane_ids.items()
            }
            observation = BaselineObservation(
                simulation_time=now,
                current_phase_id=executor.current_phase_id,
                phase_elapsed_seconds=now - phase_entered_at,
                halting_by_approach=halting,
            )
            requested_phase = controller.propose_phase(observation)
            if requested_phase is not None:
                previous_phase = executor.current_phase_id
                proposal_number += 1
                event = a1.propose(
                    proposal_id=f"{controller.label}-{seed}-{proposal_number:04d}",
                    signal_id="J0",
                    phase_id=requested_phase,
                    simulation_time=now,
                )
                if not event.accepted:
                    raise BaselineEvidenceValidationError(
                        f"baseline policy proposed rejected phase {requested_phase}: "
                        f"{event.reason_code}"
                    )
                if executor.current_phase_id != previous_phase:
                    phase_entered_at = now
            if connection.simulation.getMinExpectedNumber() <= 0:
                break
        simulation_end = float(connection.simulation.getTime())
        traci_version = str(connection.getVersion()[1])
    finally:
        connection.close(False)

    trip_rows: list[BaselineTripResult] = []
    for trip_id in planned_trip_ids:
        flow_id, flow_index = _flow_identity(trip_id)
        depart = departed_at.get(trip_id)
        arrival = arrived_at.get(trip_id)
        if arrival is not None:
            trip_status = "completed"
            duration = max(0.0, arrival - (depart if depart is not None else arrival))
            wait = latest_wait.get(trip_id, 0.0)
            time_loss = latest_time_loss.get(trip_id, 0.0)
        elif depart is not None:
            trip_status = "active-at-horizon"
            duration = max(0.0, simulation_end - depart)
            wait = latest_wait.get(trip_id, 0.0)
            time_loss = latest_time_loss.get(trip_id, 0.0)
        else:
            trip_status = "not-departed"
            duration = None
            wait = None
            time_loss = None
        trip_rows.append(BaselineTripResult(
            run_id=run_id,
            scenario_hash=scenario_hash,
            controller=controller.label,
            seed=seed,
            trip_id=trip_id,
            flow_id=flow_id,
            flow_index=flow_index,
            trip_status=trip_status,
            departed_at_s=depart,
            arrived_at_s=arrival,
            duration_s=duration,
            waiting_time_s=wait,
            time_loss_s=time_loss,
            standstill_seconds=standstill_seconds.get(trip_id, 0),
            observed_at_s=simulation_end,
            failure_reason=None,
        ))

    completed_rows = [row for row in trip_rows if row.trip_status == "completed"]
    durations = [float(row.duration_s) for row in completed_rows if row.duration_s is not None]
    waits = [float(row.waiting_time_s) for row in completed_rows if row.waiting_time_s is not None]
    time_losses = [
        float(row.time_loss_s) for row in completed_rows if row.time_loss_s is not None
    ]
    conflicting_commands = sum(
        bool(conflicting_green_pairs(command.signal_state, topology))
        for command in log.commands
    )
    completed = len(completed_rows)
    planned_trips = len(planned_trip_ids)
    unfinished = planned_trips - completed
    return BaselineRunResult(
        run_id=run_id,
        scenario_hash=scenario_hash,
        controller=controller.label,
        seed=seed,
        status="completed",
        failure_reason=None,
        simulation_begin=simulation_begin,
        simulation_end=simulation_end,
        simulation_steps=steps,
        planned_trips=planned_trips,
        completed_trips=completed,
        unfinished_trips=unfinished,
        completion_rate=completed / planned_trips if planned_trips else 1.0,
        mean_duration_s=sum(durations) / len(durations) if durations else 0.0,
        p95_duration_s=_percentile(durations, 0.95),
        max_duration_s=max(durations, default=0.0),
        mean_waiting_time_s=sum(waits) / len(waits) if waits else 0.0,
        p95_waiting_time_s=_percentile(waits, 0.95),
        max_waiting_time_s=max(waits, default=0.0),
        total_time_loss_s=sum(time_losses),
        standstill_vehicle_seconds=sum(row.standstill_seconds for row in trip_rows),
        vehicles_with_standstill=sum(row.standstill_seconds > 0 for row in trip_rows),
        teleport_events=teleport_events,
        max_active_vehicles=max_active,
        safety_event_count=len(log.events),
        accepted_signal_commands=len(log.commands),
        traci_version=traci_version,
        command=command,
        trips=tuple(trip_rows),
        safety_events=log.events,
        executed_commands=log.commands,
        writer_count_by_signal=registry.writer_count_by_signal,
        physically_conflicting_commands=conflicting_commands,
    )
