from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping
from uuid import uuid4

from coflow5.control import DeterministicSafetyMask, controlled_cross_plan
from coflow5.control.a1_controller import A1FlowController
from coflow5.control.max_pressure import (
    CooperativeMaxPressureController,
    MaxPressureDecision,
    MaxPressureObservation,
    MovementPressure,
)
from coflow5.sumo_adapter.signal_executor import (
    ExecutedSignalCommand,
    ImmutableSafetyLog,
    SafetyEvent,
    SignalExecutorRegistry,
)
from coflow5.sumo_adapter.smoke_backends import load_traci


@dataclass(frozen=True)
class ScheduledA1Action:
    simulation_time: float
    proposal_id: str
    phase_id: str
    pedestrian_remaining_clearance: Mapping[str, float] | None = None


@dataclass(frozen=True)
class NativeCooperationResult:
    trips: tuple[dict[str, Any], ...]
    simulation_begin: float
    simulation_end: float
    simulation_steps: int
    departed_total: int
    arrived_total: int
    teleport_events: int
    traci_version: str
    command: tuple[str, ...]
    safety_events: tuple[SafetyEvent, ...]
    executed_commands: tuple[ExecutedSignalCommand, ...]
    writer_count_by_signal: dict[str, int]
    max_pressure_decisions: tuple[MaxPressureDecision, ...]


def _trip_rows(path: Path) -> tuple[dict[str, Any], ...]:
    root = ET.parse(path).getroot()
    return tuple(
        {
            "trip_id": trip.attrib["id"],
            "depart": float(trip.attrib["depart"]),
            "arrival": float(trip.attrib["arrival"]),
            "duration": float(trip.attrib["duration"]),
            "route_length_m": float(trip.attrib["routeLength"]),
            "waiting_time_s": float(trip.attrib["waitingTime"]),
            "time_loss_s": float(trip.attrib["timeLoss"]),
            "depart_delay_s": float(trip.attrib["departDelay"]),
            "unfinished": float(trip.attrib["arrival"]) < 0,
        }
        for trip in root.findall("tripinfo")
    )


def run_native_cooperation_scenario(
    *,
    sumo_binary: str,
    config: Path,
    tripinfo_path: Path,
    run_id: str,
    scenario_hash: str,
    seed: int,
    actions: tuple[ScheduledA1Action, ...],
) -> NativeCooperationResult:
    """Run row 07 through native TraCI and the sole A1 signal capability."""
    if len({action.proposal_id for action in actions}) != len(actions):
        raise ValueError("scheduled A1 proposal ids must be unique")
    ordered = tuple(sorted(actions, key=lambda item: (item.simulation_time, item.proposal_id)))
    if ordered != actions:
        raise ValueError("scheduled A1 actions must be in deterministic time order")

    traci = load_traci()
    label = f"coflow5-cooperation-{uuid4()}"
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
        "--tripinfo-output",
        str(tripinfo_path),
        "--tripinfo-output.write-unfinished",
        "true",
    )
    traci.start(list(command), label=label, stdout=None)
    connection = traci.getConnection(label)
    log = ImmutableSafetyLog()
    registry = SignalExecutorRegistry()
    simulation_begin = float(connection.simulation.getTime())
    safety_mask = DeterministicSafetyMask(controlled_cross_plan())
    executor = registry.acquire(
        signal_id="J0",
        connection=connection,
        safety_mask=safety_mask,
        initial_phase_id="NS_GREEN",
        initial_phase_entered_at=simulation_begin,
        run_id=run_id,
        scenario_hash=scenario_hash,
        log=log,
    )
    a1 = A1FlowController(executor)
    max_pressure = CooperativeMaxPressureController(
        a1=a1,
        safety_mask=safety_mask,
        run_id=run_id,
        scenario_hash=scenario_hash,
        signal_id="J0",
    )
    max_pressure_decisions: list[MaxPressureDecision] = []
    action_index = 0
    departed_total = 0
    arrived_total = 0
    teleport_events = 0
    steps = 0
    phase_entered_at = simulation_begin
    final_scheduled_time = ordered[-1].simulation_time if ordered else simulation_begin
    try:
        while connection.simulation.getMinExpectedNumber() > 0:
            connection.simulationStep()
            steps += 1
            now = float(connection.simulation.getTime())
            departed_total += int(connection.simulation.getDepartedNumber())
            arrived_total += int(connection.simulation.getArrivedNumber())
            teleport_events += int(connection.simulation.getStartingTeleportNumber())
            while action_index < len(ordered) and ordered[action_index].simulation_time <= now:
                action = ordered[action_index]
                if action.simulation_time != now:
                    raise RuntimeError(
                        f"missed scheduled A1 action {action.proposal_id} at {action.simulation_time}"
                    )
                previous_phase = executor.current_phase_id
                event = a1.propose(
                    proposal_id=action.proposal_id,
                    signal_id="J0",
                    phase_id=action.phase_id,
                    simulation_time=now,
                    pedestrian_remaining_clearance=action.pedestrian_remaining_clearance,
                )
                if not event.accepted:
                    raise RuntimeError(
                        f"scheduled A1 action {action.proposal_id} failed safety: {event.reason_code}"
                    )
                if executor.current_phase_id != previous_phase:
                    phase_entered_at = now
                action_index += 1

            if action_index == len(ordered) and now > final_scheduled_time:
                incoming = {
                    "north": "N_in_0", "east": "E_in_0",
                    "south": "S_in_0", "west": "W_in_0",
                }
                downstream = {
                    "north": "S_out_0", "east": "W_out_0",
                    "south": "N_out_0", "west": "E_out_0",
                }
                movements: dict[str, MovementPressure] = {}
                for movement_id, incoming_lane in incoming.items():
                    downstream_lane = downstream[movement_id]
                    capacity = max(1.0, float(connection.lane.getLength(downstream_lane)) / 7.5)
                    movements[movement_id] = MovementPressure(
                        upstream_queue=float(
                            connection.lane.getLastStepHaltingNumber(incoming_lane)
                        ),
                        downstream_queue=float(
                            connection.lane.getLastStepVehicleNumber(downstream_lane)
                        ),
                        downstream_capacity=capacity,
                    )
                previous_phase = executor.current_phase_id
                decision = max_pressure.decide(
                    proposal_id=f"max-pressure-local-{steps:04d}",
                    observation=MaxPressureObservation(
                        simulation_time=now,
                        current_phase_id=previous_phase,
                        phase_entered_at=phase_entered_at,
                        movements=movements,
                    ),
                )
                max_pressure_decisions.append(decision)
                if executor.current_phase_id != previous_phase:
                    phase_entered_at = now
            if steps > 300:
                raise RuntimeError("row 07 native scenario exceeded the 300-step safety bound")
        simulation_end = float(connection.simulation.getTime())
        traci_version = str(connection.getVersion()[1])
    finally:
        connection.close(False)

    if action_index != len(ordered):
        raise RuntimeError("native scenario ended before every scheduled A1 action")
    if not tripinfo_path.is_file():
        raise RuntimeError(f"native TraCI run did not produce tripinfo: {tripinfo_path}")
    return NativeCooperationResult(
        trips=_trip_rows(tripinfo_path),
        simulation_begin=simulation_begin,
        simulation_end=simulation_end,
        simulation_steps=steps,
        departed_total=departed_total,
        arrived_total=arrived_total,
        teleport_events=teleport_events,
        traci_version=traci_version,
        command=command,
        safety_events=log.events,
        executed_commands=log.commands,
        writer_count_by_signal=registry.writer_count_by_signal,
        max_pressure_decisions=tuple(max_pressure_decisions),
    )
