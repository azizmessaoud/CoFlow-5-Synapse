from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import uuid4

from coflow5.sumo_adapter.smoke_backends import load_traci


@dataclass(frozen=True)
class NativeTraCIResult:
    states: tuple[dict[str, Any], ...]
    trips: tuple[dict[str, Any], ...]
    simulation_steps: int
    simulation_begin: float
    simulation_end: float
    departed_total: int
    arrived_total: int
    teleport_events: int
    traci_version: str


def _trip_rows(tripinfo_path: Path) -> tuple[dict[str, Any], ...]:
    root = ET.parse(tripinfo_path).getroot()
    rows: list[dict[str, Any]] = []
    for trip in root.findall("tripinfo"):
        arrival = float(trip.attrib["arrival"])
        rows.append(
            {
                "trip_id": trip.attrib["id"],
                "depart": float(trip.attrib["depart"]),
                "arrival": arrival,
                "duration": float(trip.attrib["duration"]),
                "route_length_m": float(trip.attrib["routeLength"]),
                "waiting_time_s": float(trip.attrib["waitingTime"]),
                "time_loss_s": float(trip.attrib["timeLoss"]),
                "depart_delay_s": float(trip.attrib["departDelay"]),
                "unfinished": arrival < 0,
            }
        )
    return tuple(rows)


def run_native_traci_evidence(
    sumo_binary: str,
    config: Path,
    tripinfo_path: Path,
    seed: int,
) -> NativeTraCIResult:
    """Run one native scenario and return only observations measured through TraCI.

    SUMO bindings are loaded lazily by ``load_traci`` so importing this module never
    imports either ``traci`` or ``libsumo`` at module load.
    """
    traci = load_traci()
    label = f"coflow5-evidence-{uuid4()}"
    command = [
        sumo_binary,
        "-c",
        str(config),
        "--seed",
        str(seed),
        "--no-step-log",
        "true",
        "--tripinfo-output",
        str(tripinfo_path),
        "--tripinfo-output.write-unfinished",
        "true",
    ]
    traci.start(command, label=label, stdout=None)
    connection = traci.getConnection(label)
    states: list[dict[str, Any]] = []
    departed_total = 0
    arrived_total = 0
    teleport_events = 0
    steps = 0
    simulation_begin = float(connection.simulation.getTime())
    traci_version = str(connection.getVersion()[1])
    try:
        while connection.simulation.getMinExpectedNumber() > 0:
            connection.simulationStep()
            steps += 1
            if steps > 10000:
                raise RuntimeError("Frozen smoke scenario exceeded the 10,000-step safety bound")
            vehicle_ids = tuple(connection.vehicle.getIDList())
            departed = int(connection.simulation.getDepartedNumber())
            arrived = int(connection.simulation.getArrivedNumber())
            starting_teleports = int(connection.simulation.getStartingTeleportNumber())
            ending_teleports = int(connection.simulation.getEndingTeleportNumber())
            departed_total += departed
            arrived_total += arrived
            teleport_events += starting_teleports
            speeds = [max(0.0, float(connection.vehicle.getSpeed(item))) for item in vehicle_ids]
            waiting = [max(0.0, float(connection.vehicle.getWaitingTime(item))) for item in vehicle_ids]
            states.append(
                {
                    "simulation_time": float(connection.simulation.getTime()),
                    "min_expected_vehicles": int(connection.simulation.getMinExpectedNumber()),
                    "loaded_vehicles": int(connection.simulation.getLoadedNumber()),
                    "departed_vehicles": departed,
                    "arrived_vehicles": arrived,
                    "active_vehicles": len(vehicle_ids),
                    "halting_vehicles": sum(speed < 0.1 for speed in speeds),
                    "mean_speed_mps": sum(speeds) / len(speeds) if speeds else 0.0,
                    "total_waiting_seconds": sum(waiting),
                    "starting_teleports": starting_teleports,
                    "ending_teleports": ending_teleports,
                }
            )
    finally:
        simulation_end = float(connection.simulation.getTime())
        connection.close()

    if not tripinfo_path.is_file():
        raise RuntimeError(f"TraCI run did not produce tripinfo: {tripinfo_path}")
    return NativeTraCIResult(
        states=tuple(states),
        trips=_trip_rows(tripinfo_path),
        simulation_steps=steps,
        simulation_begin=simulation_begin,
        simulation_end=simulation_end,
        departed_total=departed_total,
        arrived_total=arrived_total,
        teleport_events=teleport_events,
        traci_version=traci_version,
    )
