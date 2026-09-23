from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping
from uuid import uuid4

from coflow5.control import DeterministicSafetyMask, controlled_cross_plan
from coflow5.control.a1_controller import A1FlowController
from coflow5.control.graph_max_pressure import GraphScoreDecision, score_graph_actions
from coflow5.control.junction_graph import JunctionGraph, NeighbourObservation, load_junction_graph
from coflow5.sumo_adapter.signal_executor import ImmutableSafetyLog, SignalExecutorRegistry
from coflow5.sumo_adapter.smoke_backends import load_traci


@dataclass(frozen=True)
class NativeGraphDecision:
    run_id: str
    scenario_hash: str
    graph_hash: str
    event_id: str
    signal_id: str
    simulation_time: float
    accepted_action: str
    reason_code: str


@dataclass(frozen=True)
class NativeGraphGrowthRun:
    run_id: str
    scenario_hash: str
    graph_hash: str
    simulation_steps: int
    decisions: tuple[NativeGraphDecision, ...]
    writer_count_by_signal: Mapping[str, int]
    safety_event_count: int
    accepted_command_count: int
    rejected_event_count: int
    traci_version: str
    command: tuple[str, ...]


ROUTES = (
    ("west0-east0", "W0_J0 J0_J1 J1_E0"),
    ("east1-west1", "E1_J3 J3_J2 J2_W1"),
    ("south0-north0", "S0_J0 J0_J2 J2_N0"),
    ("north1-south1", "N1_J3 J3_J1 J1_S1"),
)


def generate_od_routes(*, demand_scale: float, seed: int) -> tuple[str, tuple[str, ...]]:
    """Return deterministic explicit OD trips for fixture/native parity inspection."""
    if demand_scale not in {0.75, 1.0, 1.25, 1.5}:
        raise ValueError("demand scale is not in the sealed matrix")
    count = round(32 * demand_scale)
    rng = random.Random(seed)
    assignments = [index % len(ROUTES) for index in range(count)]
    rng.shuffle(assignments)
    rows = [
        '<?xml version="1.0" encoding="UTF-8"?>', "<routes>",
        '  <vType id="passenger" accel="2.6" decel="4.5" sigma="0" length="5" minGap="2.5" maxSpeed="13.9"/>',
    ]
    for route_id, edges in ROUTES:
        rows.append(f'  <route id="{route_id}" edges="{edges}"/>')
    trip_ids: list[str] = []
    for index, route_index in enumerate(assignments):
        trip_id = f"growth-{seed}-{int(demand_scale * 100):03d}.{index}"
        depart = index * 60.0 / count
        trip_ids.append(trip_id)
        rows.append(
            f'  <vehicle id="{trip_id}" type="passenger" route="{ROUTES[route_index][0]}" '
            f'depart="{depart:.3f}" departLane="best" departSpeed="max"/>'
        )
    rows.append("</routes>")
    return "\n".join(rows) + "\n", tuple(trip_ids)


def _phase_group(phase_id: str) -> str:
    return "NS" if phase_id.startswith("NS") or phase_id.endswith("NS") else "EW"


def run_native_graph_growth_smoke(
    *, sumo_binary: str, config: Path, network_file: Path,
    run_id: str, scenario_hash: str, seed: int = 37, horizon_seconds: float = 30.0,
) -> NativeGraphGrowthRun:
    """Exercise one safe A1 executor per signal through TraCI; no evaluation claim."""
    graph: JunctionGraph = load_junction_graph(network_file)
    traci = load_traci()
    label = f"coflow5-graph-growth-{uuid4()}"
    command = (
        sumo_binary, "-c", str(config), "--seed", str(seed),
        "--no-step-log", "true", "--duration-log.disable", "true",
        "--time-to-teleport", "-1",
    )
    traci.start(list(command), label=label, stdout=None)
    connection = traci.getConnection(label)
    log = ImmutableSafetyLog()
    registry = SignalExecutorRegistry()
    mask = DeterministicSafetyMask(controlled_cross_plan())
    start = float(connection.simulation.getTime())
    executors: dict[str, object] = {}
    controllers: dict[str, A1FlowController] = {}
    last_service = {(node.signal_id, group): start for node in graph.nodes for group in ("NS", "EW")}
    controlled: dict[str, tuple[tuple[str, str], ...]] = {}
    for node in graph.nodes:
        groups = connection.trafficlight.getControlledLinks(node.signal_id)
        if len(groups) != 4:
            connection.close(False)
            raise RuntimeError(f"{node.signal_id} must expose four controlled links")
        controlled[node.signal_id] = tuple((str(group[0][0]), str(group[0][1])) for group in groups)
        executor = registry.acquire(
            signal_id=node.signal_id, connection=connection, safety_mask=mask,
            initial_phase_id="NS_GREEN", initial_phase_entered_at=start,
            run_id=run_id, scenario_hash=scenario_hash, log=log,
        )
        executors[node.signal_id] = executor
        controllers[node.signal_id] = A1FlowController(executor)

    decisions: list[NativeGraphDecision] = []
    steps = 0
    try:
        while float(connection.simulation.getTime()) < horizon_seconds:
            connection.simulationStep()
            steps += 1
            now = float(connection.simulation.getTime())
            lane_queues = {
                lane: float(connection.lane.getLastStepHaltingNumber(lane))
                for node in graph.nodes for lane in (*node.incoming_lane_ids, *node.outgoing_lane_ids)
            }
            for node in graph.nodes:
                signal_id = node.signal_id
                executor = executors[signal_id]
                current = executor.current_phase_id
                links = controlled[signal_id]
                ns_pressure = sum(lane_queues[a] - lane_queues[b] for a, b in (links[0], links[2]))
                ew_pressure = sum(lane_queues[a] - lane_queues[b] for a, b in (links[1], links[3]))
                legal = tuple(sorted(phase for phase in mask.plan.legal_transitions[current] if phase != "CONFLICTING_TEST"))
                local = {phase: (ns_pressure if _phase_group(phase) == "NS" else ew_pressure) for phase in legal}
                available: dict[str, bool] = {}
                ages: dict[str, float] = {}
                for phase in legal:
                    indexes = (0, 2) if _phase_group(phase) == "NS" else (1, 3)
                    available[phase] = any(lane_queues[links[index][1]] < 12.0 for index in indexes)
                    ages[phase] = now - last_service[(signal_id, _phase_group(phase))]
                neighbours: list[NeighbourObservation] = []
                for edge in graph.edges:
                    if edge.from_signal_id != signal_id:
                        continue
                    queue = sum(lane_queues[lane] for lane in edge.connecting_lane_ids)
                    horizontal = edge.from_signal_id in {"J0", "J2"} and edge.to_signal_id in {"J1", "J3"} or edge.from_signal_id in {"J1", "J3"} and edge.to_signal_id in {"J0", "J2"}
                    neighbours.append(NeighbourObservation(
                        from_signal_id=signal_id, to_signal_id=edge.to_signal_id,
                        movement_group="EW" if horizontal else "NS",
                        observed_at=now, expires_at=now + 5.0,
                        queue_vehicles=queue,
                        occupancy_ratio=min(1.0, queue / edge.storage_capacity_vehicles),
                        predicted_discharge_vehicles=max(0.0, 2.0 - queue * 0.25),
                    ))
                scored: GraphScoreDecision = score_graph_actions(
                    expected_graph_hash=graph.graph_hash, observation_graph_hash=graph.graph_hash,
                    simulation_time=now, current_phase_id=current, local_pressures=local,
                    downstream_available=available, service_age_seconds=ages, neighbours=neighbours,
                )
                event = controllers[signal_id].propose(
                    proposal_id=f"graph-smoke-{seed}-{steps:04d}-{signal_id}",
                    signal_id=signal_id, phase_id=scored.accepted_action, simulation_time=now,
                )
                if event.accepted:
                    last_service[(signal_id, _phase_group(scored.accepted_action))] = now
                decisions.append(NativeGraphDecision(
                    run_id=run_id, scenario_hash=scenario_hash, graph_hash=graph.graph_hash,
                    event_id=event.event_id, signal_id=signal_id, simulation_time=now,
                    accepted_action=scored.accepted_action, reason_code=scored.reason_code,
                ))
        version = str(connection.getVersion()[1])
    finally:
        connection.close(False)
    event_ids = {row.event_id for row in log.events}
    command_ids = {row.event_id for row in log.commands}
    decision_ids = {row.event_id for row in decisions}
    if event_ids != command_ids or event_ids != decision_ids:
        raise RuntimeError("native graph decision, safety, and command joins differ")
    expected_writers = {node.signal_id: 1 for node in graph.nodes}
    if registry.writer_count_by_signal != expected_writers:
        raise RuntimeError("native graph runner did not retain one A1 writer per signal")
    return NativeGraphGrowthRun(
        run_id=run_id, scenario_hash=scenario_hash, graph_hash=graph.graph_hash,
        simulation_steps=steps, decisions=tuple(decisions),
        writer_count_by_signal=registry.writer_count_by_signal,
        safety_event_count=len(log.events), accepted_command_count=len(log.commands),
        rejected_event_count=sum(not event.accepted for event in log.events),
        traci_version=version, command=command,
    )
