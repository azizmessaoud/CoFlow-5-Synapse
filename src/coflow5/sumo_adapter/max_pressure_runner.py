from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence
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
from coflow5.sumo_adapter.signal_executor import (
    ExecutedSignalCommand,
    ImmutableSafetyLog,
    SafetyEvent,
    SignalExecutorRegistry,
)
from coflow5.sumo_adapter.smoke_backends import load_traci


@dataclass(frozen=True)
class NativeMovementObservation:
    movement_id: str
    incoming_lane_id: str
    downstream_lane_id: str
    upstream_queue: float
    downstream_queue: float
    downstream_capacity: float


@dataclass(frozen=True)
class NativeMaxPressureObservation:
    run_id: str
    scenario_hash: str
    event_id: str
    proposal_id: str
    signal_id: str
    simulation_time: float
    current_phase_id: str
    phase_entered_at: float
    observed_signal_state: str
    movements: tuple[NativeMovementObservation, ...]


@dataclass(frozen=True)
class NativeMaxPressureResult:
    run_id: str
    scenario_hash: str
    decisions: tuple[MaxPressureDecision, ...]
    observations: tuple[NativeMaxPressureObservation, ...]
    safety_events: tuple[SafetyEvent, ...]
    executed_commands: tuple[ExecutedSignalCommand, ...]
    safety_event_count: int
    accepted_command_count: int
    writer_count_by_signal: dict[str, int]
    simulation_begin: float
    simulation_end: float
    simulation_steps: int
    traci_version: str
    command: tuple[str, ...]


def run_native_max_pressure_scenario(
    *,
    sumo_binary: str,
    config: Path,
    run_id: str,
    scenario_hash: str,
    seed: int,
    advisories: Sequence[AdvisoryRequest] = (),
    horizon_seconds: float = 120.0,
    sumo_extra_args: Sequence[str] = (),
) -> NativeMaxPressureResult:
    """Run cooperative Max-Pressure through the sole A1 TraCI write capability."""
    traci = load_traci()
    label = f"coflow5-max-pressure-{uuid4()}"
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
        *tuple(sumo_extra_args),
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
    controller = CooperativeMaxPressureController(
        a1=A1FlowController(executor),
        safety_mask=safety_mask,
        run_id=run_id,
        scenario_hash=scenario_hash,
        signal_id="J0",
    )
    incoming_lanes = {
        "north": "N_in_0",
        "east": "E_in_0",
        "south": "S_in_0",
        "west": "W_in_0",
    }
    downstream_lanes = {
        "north": "S_out_0",
        "east": "W_out_0",
        "south": "N_out_0",
        "west": "E_out_0",
    }
    phase_entered_at = simulation_begin
    decisions: list[MaxPressureDecision] = []
    observations: list[NativeMaxPressureObservation] = []
    steps = 0
    try:
        while float(connection.simulation.getTime()) < horizon_seconds:
            connection.simulationStep()
            steps += 1
            now = float(connection.simulation.getTime())
            movements: dict[str, MovementPressure] = {}
            raw_movements: list[NativeMovementObservation] = []
            for movement_id, incoming_lane in incoming_lanes.items():
                downstream_lane = downstream_lanes[movement_id]
                lane_length = float(connection.lane.getLength(downstream_lane))
                capacity = max(1.0, lane_length / 7.5)
                upstream_queue = float(
                    connection.lane.getLastStepHaltingNumber(incoming_lane)
                )
                downstream_queue = float(
                    connection.lane.getLastStepVehicleNumber(downstream_lane)
                )
                movements[movement_id] = MovementPressure(
                    upstream_queue=upstream_queue,
                    downstream_queue=downstream_queue,
                    downstream_capacity=capacity,
                )
                raw_movements.append(NativeMovementObservation(
                    movement_id=movement_id,
                    incoming_lane_id=incoming_lane,
                    downstream_lane_id=downstream_lane,
                    upstream_queue=upstream_queue,
                    downstream_queue=downstream_queue,
                    downstream_capacity=capacity,
                ))
            previous_phase = executor.current_phase_id
            proposal_id = f"max-pressure-{seed}-{steps:04d}"
            observed_signal_state = str(
                connection.trafficlight.getRedYellowGreenState("J0")
            )
            decision = controller.decide(
                proposal_id=proposal_id,
                observation=MaxPressureObservation(
                    simulation_time=now,
                    current_phase_id=previous_phase,
                    phase_entered_at=phase_entered_at,
                    movements=movements,
                    advisories=tuple(advisories),
                ),
            )
            decisions.append(decision)
            observations.append(NativeMaxPressureObservation(
                run_id=run_id,
                scenario_hash=scenario_hash,
                event_id=decision.event_id,
                proposal_id=proposal_id,
                signal_id="J0",
                simulation_time=now,
                current_phase_id=previous_phase,
                phase_entered_at=phase_entered_at,
                observed_signal_state=observed_signal_state,
                movements=tuple(sorted(raw_movements, key=lambda item: item.movement_id)),
            ))
            if executor.current_phase_id != previous_phase:
                phase_entered_at = now
            if connection.simulation.getMinExpectedNumber() <= 0:
                break
        simulation_end = float(connection.simulation.getTime())
        traci_version = str(connection.getVersion()[1])
    finally:
        connection.close(False)
    return NativeMaxPressureResult(
        run_id=run_id,
        scenario_hash=scenario_hash,
        decisions=tuple(decisions),
        observations=tuple(observations),
        safety_events=log.events,
        executed_commands=log.commands,
        safety_event_count=len(log.events),
        accepted_command_count=len(log.commands),
        writer_count_by_signal=registry.writer_count_by_signal,
        simulation_begin=simulation_begin,
        simulation_end=simulation_end,
        simulation_steps=steps,
        traci_version=traci_version,
        command=command,
    )
