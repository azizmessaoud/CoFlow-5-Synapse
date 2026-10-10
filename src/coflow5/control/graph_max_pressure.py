from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping, Sequence

from coflow5.control.junction_graph import NeighbourObservation

GRAPH_NEIGHBOUR_USED = "GRAPH_NEIGHBOUR_USED"
GRAPH_NEIGHBOUR_STALE_LOCAL_ONLY = "GRAPH_NEIGHBOUR_STALE_LOCAL_ONLY"
GRAPH_NEIGHBOUR_UNAVAILABLE_LOCAL_ONLY = "GRAPH_NEIGHBOUR_UNAVAILABLE_LOCAL_ONLY"
GRAPH_IDENTITY_MISMATCH_LOCAL_ONLY = "GRAPH_IDENTITY_MISMATCH_LOCAL_ONLY"


@dataclass(frozen=True)
class GraphActionScore:
    phase_id: str
    total: float
    local_pressure: float
    one_hop_discharge_bonus: float
    service_age_bonus: float
    switch_penalty: float
    downstream_available: bool


@dataclass(frozen=True)
class GraphScoreDecision:
    accepted_action: str
    reason_code: str
    scores: tuple[GraphActionScore, ...]
    used_neighbour_ids: tuple[str, ...]


def score_graph_actions(
    *,
    expected_graph_hash: str,
    observation_graph_hash: str | None,
    simulation_time: float,
    current_phase_id: str,
    local_pressures: Mapping[str, float],
    downstream_available: Mapping[str, bool],
    service_age_seconds: Mapping[str, float],
    neighbours: Sequence[NeighbourObservation] | None,
    one_hop_bound: float = 2.0,
    service_age_bound: float = 2.0,
    switch_penalty_bound: float = 1.0,
) -> GraphScoreDecision:
    """Score legal candidates; invalid graph data becomes exact local-only scoring."""
    if not expected_graph_hash or not math.isfinite(simulation_time):
        raise ValueError("finite time and expected graph identity are required")
    phases = tuple(sorted(local_pressures))
    if not phases or set(phases) != set(downstream_available) or set(phases) != set(service_age_seconds):
        raise ValueError("all action maps must contain the same non-empty phase set")
    values = (*local_pressures.values(), *service_age_seconds.values(), one_hop_bound,
              service_age_bound, switch_penalty_bound)
    if not all(math.isfinite(float(value)) for value in values) or min(
        one_hop_bound, service_age_bound, switch_penalty_bound
    ) < 0:
        raise ValueError("graph score inputs and bounds must be finite and non-negative")
    selectable = {phase for phase in phases if downstream_available[phase] or phase == current_phase_id}
    if not selectable:
        raise RuntimeError("no live action after downstream hard mask")

    fresh: tuple[NeighbourObservation, ...] = ()
    if observation_graph_hash != expected_graph_hash:
        reason = GRAPH_IDENTITY_MISMATCH_LOCAL_ONLY
    elif neighbours is None or not neighbours:
        reason = GRAPH_NEIGHBOUR_UNAVAILABLE_LOCAL_ONLY
    else:
        fresh = tuple(item for item in neighbours if item.observed_at <= simulation_time <= item.expires_at)
        if not fresh:
            reason = GRAPH_NEIGHBOUR_STALE_LOCAL_ONLY
        elif len(fresh) != len(tuple(neighbours)):
            reason = GRAPH_NEIGHBOUR_STALE_LOCAL_ONLY
            fresh = ()
        else:
            reason = GRAPH_NEIGHBOUR_USED

    graph_enabled = reason == GRAPH_NEIGHBOUR_USED
    scores: list[GraphActionScore] = []
    for phase_id in phases:
        movement_group = "NS" if phase_id.startswith("NS") or phase_id.endswith("NS") else "EW"
        raw_discharge = sum(
            max(0.0, item.predicted_discharge_vehicles) * (1.0 - item.occupancy_ratio)
            for item in fresh if item.movement_group == movement_group
        )
        one_hop = min(one_hop_bound, raw_discharge) if graph_enabled else 0.0
        age = min(service_age_bound, max(0.0, service_age_seconds[phase_id]) / 30.0) if graph_enabled else 0.0
        switch = (
            min(switch_penalty_bound, switch_penalty_bound)
            if graph_enabled and phase_id != current_phase_id else 0.0
        )
        scores.append(GraphActionScore(
            phase_id=phase_id,
            total=float(local_pressures[phase_id]) + one_hop + age - switch,
            local_pressure=float(local_pressures[phase_id]),
            one_hop_discharge_bonus=one_hop,
            service_age_bonus=age,
            switch_penalty=switch,
            downstream_available=bool(downstream_available[phase_id]),
        ))
    accepted = min(
        (score for score in scores if score.phase_id in selectable),
        key=lambda score: (-score.total, score.phase_id),
    )
    return GraphScoreDecision(
        accepted_action=accepted.phase_id,
        reason_code=reason,
        scores=tuple(sorted(scores, key=lambda score: (score.phase_id != accepted.phase_id, score.phase_id))),
        used_neighbour_ids=tuple(sorted({item.to_signal_id for item in fresh})) if graph_enabled else (),
    )
