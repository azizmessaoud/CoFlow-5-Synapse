from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4
from xml.etree import ElementTree

from coflow5.control import DeterministicSafetyMask, controlled_cross_plan
from coflow5.control.a1_controller import A1FlowController
from coflow5.sumo_adapter.signal_executor import (
    ExecutedSignalCommand,
    ImmutableSafetyLog,
    SafetyEvent,
    SignalExecutorRegistry,
)
from coflow5.sumo_adapter.smoke_backends import load_traci


@dataclass(frozen=True)
class PhysicalSignalTopology:
    controlled_links: tuple[tuple[str, str, str], ...]
    conflicting_link_pairs: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class NativeSafetyResult:
    events: tuple[SafetyEvent, ...]
    commands: tuple[ExecutedSignalCommand, ...]
    writer_count_by_signal: dict[str, int]
    simulation_begin: float
    simulation_end: float
    simulation_steps: int
    traci_version: str
    initial_signal_state: str
    final_signal_state: str
    topology: PhysicalSignalTopology


def load_physical_signal_topology(
    *, connection: Any, network_file: Path, signal_id: str
) -> PhysicalSignalTopology:
    """Join TraCI controlled links to SUMO request foes for one traffic light."""
    network = ElementTree.parse(network_file).getroot()
    traci_groups = connection.trafficlight.getControlledLinks(signal_id)
    if not traci_groups:
        raise RuntimeError(f"TraCI returned no controlled links for {signal_id}")

    lanes: dict[tuple[str, str], str] = {}
    for edge in network.findall("edge"):
        edge_id = edge.get("id")
        if edge_id is None:
            continue
        for lane in edge.findall("lane"):
            lane_index = lane.get("index")
            lane_id = lane.get("id")
            if lane_index is not None and lane_id is not None:
                lanes[(edge_id, lane_index)] = lane_id

    xml_links: dict[int, tuple[str, str, str]] = {}
    for link in network.findall("connection"):
        if link.get("tl") != signal_id:
            continue
        index = int(link.attrib["linkIndex"])
        xml_links[index] = (
            lanes[(link.attrib["from"], link.attrib["fromLane"])],
            lanes[(link.attrib["to"], link.attrib["toLane"])],
            link.attrib["via"],
        )
    expected_indexes = set(range(len(traci_groups)))
    if set(xml_links) != expected_indexes:
        raise RuntimeError(
            f"network link indexes for {signal_id} do not match TraCI: "
            f"network={sorted(xml_links)}, traci={sorted(expected_indexes)}"
        )

    controlled_links: list[tuple[str, str, str]] = []
    for index, group in enumerate(traci_groups):
        normalized = tuple(tuple(str(value) for value in link) for link in group)
        expected = xml_links[index]
        if expected not in normalized:
            raise RuntimeError(
                f"controlled-link mapping differs at {signal_id}/{index}: "
                f"network={expected}, traci={normalized}"
            )
        controlled_links.append(expected)

    junction = network.find(f"junction[@id='{signal_id}']")
    if junction is None:
        raise RuntimeError(f"network has no junction topology for signal {signal_id}")
    requests = junction.findall("request")
    if len(requests) != len(controlled_links):
        raise RuntimeError(
            f"junction request count differs from controlled links for {signal_id}"
        )

    conflicting_pairs: set[tuple[int, int]] = set()
    link_count = len(controlled_links)
    for request in requests:
        index = int(request.attrib["index"])
        foes = request.attrib["foes"]
        if len(foes) != link_count:
            raise RuntimeError(f"invalid foes width for {signal_id}/{index}: {foes}")
        # SUMO writes foe bits in reverse link-index order.
        for other_index in range(link_count):
            if index != other_index and foes[-1 - other_index] == "1":
                conflicting_pairs.add(tuple(sorted((index, other_index))))

    return PhysicalSignalTopology(
        controlled_links=tuple(controlled_links),
        conflicting_link_pairs=tuple(sorted(conflicting_pairs)),
    )


def conflicting_green_pairs(
    signal_state: str, topology: PhysicalSignalTopology
) -> tuple[tuple[int, int], ...]:
    if len(signal_state) != len(topology.controlled_links):
        raise ValueError(
            f"signal state width {len(signal_state)} differs from controlled-link count "
            f"{len(topology.controlled_links)}"
        )
    green_indexes = {index for index, value in enumerate(signal_state) if value in {"G", "g"}}
    return tuple(
        pair for pair in topology.conflicting_link_pairs if set(pair) <= green_indexes
    )


def run_native_safety_scenario(
    *, sumo_binary: str, config: Path, network_file: Path, run_id: str, scenario_hash: str
) -> NativeSafetyResult:
    """Execute the controlled mask script against a real native TraCI connection."""
    traci = load_traci()
    label = f"coflow5-safety-{uuid4()}"
    command = [
        sumo_binary, "-c", str(config), "--seed", "37", "--no-step-log", "true",
        "--duration-log.disable", "true",
    ]
    traci.start(command, label=label, stdout=None)
    connection = traci.getConnection(label)
    log = ImmutableSafetyLog()
    registry = SignalExecutorRegistry()
    simulation_begin = float(connection.simulation.getTime())
    topology = load_physical_signal_topology(
        connection=connection, network_file=network_file, signal_id="J0"
    )
    initial_signal_state = str(connection.trafficlight.getRedYellowGreenState("J0"))
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
    controller = A1FlowController(executor)
    actions: dict[int, list[dict[str, Any]]] = {
        1: [dict(method="propose", proposal_id="p01-direct-green", phase_id="EW_GREEN")],
        2: [dict(method="human_override", proposal_id="p02-human-early-yellow", phase_id="NS_YELLOW")],
        5: [dict(method="human_override", proposal_id="p03-human-safe-yellow", phase_id="NS_YELLOW")],
        6: [dict(method="propose", proposal_id="p04-early-all-red", phase_id="ALL_RED_TO_EW")],
        7: [dict(method="propose", proposal_id="p05-safe-all-red", phase_id="ALL_RED_TO_EW")],
        8: [dict(
            method="propose", proposal_id="p06-pedestrian-active", phase_id="EW_GREEN",
            pedestrian_remaining_clearance={"north_south_crossing": 2.0},
        )],
        9: [dict(method="propose", proposal_id="p07-clearance-complete", phase_id="EW_GREEN")],
        10: [dict(method="propose", proposal_id="p08-conflicting-greens", phase_id="CONFLICTING_TEST")],
        11: [dict(method="propose", proposal_id="p09-direct-return", phase_id="NS_GREEN")],
        14: [dict(method="propose", proposal_id="p10-safe-ew-yellow", phase_id="EW_YELLOW")],
        15: [dict(method="propose", proposal_id="p11-second-early-all-red", phase_id="ALL_RED_TO_NS")],
        16: [
            dict(method="propose", proposal_id="p12-second-safe-all-red", phase_id="ALL_RED_TO_NS"),
            dict(method="propose", proposal_id="p13-early-green-after-all-red", phase_id="NS_GREEN"),
        ],
        17: [dict(method="human_override", proposal_id="p14-human-safe-green", phase_id="NS_GREEN")],
    }
    steps = 0
    try:
        for step in range(1, 21):
            connection.simulationStep()
            steps += 1
            simulation_time = float(connection.simulation.getTime())
            for action_spec in actions.get(step, []):
                action = dict(action_spec)
                method = getattr(controller, action.pop("method"))
                method(signal_id="J0", simulation_time=simulation_time, **action)
        simulation_end = float(connection.simulation.getTime())
        final_signal_state = str(connection.trafficlight.getRedYellowGreenState("J0"))
        traci_version = str(connection.getVersion()[1])
    finally:
        connection.close()
    return NativeSafetyResult(
        events=log.events,
        commands=log.commands,
        writer_count_by_signal=registry.writer_count_by_signal,
        simulation_begin=simulation_begin,
        simulation_end=simulation_end,
        simulation_steps=steps,
        traci_version=traci_version,
        initial_signal_state=initial_signal_state,
        final_signal_state=final_signal_state,
        topology=topology,
    )
