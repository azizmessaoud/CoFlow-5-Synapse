from __future__ import annotations

import random
from dataclasses import dataclass
from statistics import mean

from pydantic import BaseModel, Field

from coflow5.a3.multimodal import CrossingStatePayload


class PedestrianDemandConfig(BaseModel):
    run_id: str = Field(min_length=1)
    scenario_hash: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    crossing_id: str = Field(min_length=1)
    signal_id: str = Field(min_length=1)
    seed: int
    pedestrian_count: int = Field(gt=0, le=1000)


@dataclass(frozen=True)
class PedestrianDemandObservation:
    run_id: str
    scenario_hash: str
    crossing_id: str
    signal_id: str
    pedestrian_id: str
    arrival_time: float
    clearance_start: float
    clearance_end: float
    wait_seconds: float
    clearance_truncated: bool

    @property
    def occupancy_event_id(self) -> str:
        return f"{self.run_id}:{self.pedestrian_id}:occupancy"

    @property
    def active_crossing(self) -> bool:
        return self.clearance_end > self.clearance_start

    def crossing_state(self, *, simulation_time: float) -> CrossingStatePayload:
        if not self.clearance_start <= simulation_time < self.clearance_end:
            raise ValueError("crossing state requested outside pedestrian occupancy")
        return CrossingStatePayload(
            scenario_case="j0_seeded_pedestrian_demand",
            crossing_id=self.crossing_id,
            signal_id=self.signal_id,
            active_crossing=True,
            remaining_clearance_seconds=self.clearance_end - simulation_time,
            requested_movement="pedestrian_north_south",
            requested_phase_id="NS_GREEN",
        )


def generate_seeded_pedestrian_demand(
    config: PedestrianDemandConfig,
) -> tuple[PedestrianDemandObservation, ...]:
    """Generate deterministic J0 crossing occupancy for a controlled run.

    This is a controlled demand fixture, not a roadside measurement. Each
    pedestrian receives a complete clearance interval; A1 may not truncate it.
    """
    rng = random.Random(config.seed)
    arrivals = sorted(
        round(5.0 + rng.uniform(0.0, 20.0), 3)
        for _ in range(config.pedestrian_count)
    )
    observations: list[PedestrianDemandObservation] = []
    previous_clearance_end = 0.0
    for index, arrival_time in enumerate(arrivals, start=1):
        clearance_start = max(arrival_time, previous_clearance_end)
        clearance_end = clearance_start + 8.0
        observations.append(
            PedestrianDemandObservation(
                run_id=config.run_id,
                scenario_hash=config.scenario_hash,
                crossing_id=config.crossing_id,
                signal_id=config.signal_id,
                pedestrian_id=f"ped-{index:03d}",
                arrival_time=arrival_time,
                clearance_start=clearance_start,
                clearance_end=clearance_end,
                wait_seconds=clearance_start - arrival_time,
                clearance_truncated=False,
            )
        )
        previous_clearance_end = clearance_end
    return tuple(observations)


def summarize_pedestrian_demand(
    observations: tuple[PedestrianDemandObservation, ...],
) -> dict[str, float]:
    if not observations:
        raise ValueError("cannot summarize empty pedestrian demand")
    waits = sorted(item.wait_seconds for item in observations)
    rank = (len(waits) - 1) * 0.95
    lower, upper = int(rank), int(rank + 0.999999)
    p95 = waits[lower] if lower == upper else waits[lower] + (waits[upper] - waits[lower]) * (rank - lower)
    return {
        "pedestrian_count": float(len(observations)),
        "mean_wait_s": mean(waits),
        "p95_wait_s": p95,
        "max_wait_s": max(waits),
        "clearance_truncations": float(sum(item.clearance_truncated for item in observations)),
    }
