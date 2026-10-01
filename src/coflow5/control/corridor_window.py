"""One decision for four junctions.

SUMO stays outside. A TraCI runner builds this snapshot, calls decide, and
writes only the phases in the record. This module never opens a connection.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Mapping

from coflow5.control.graph_max_pressure import score_graph_actions
from coflow5.control.junction_graph import NeighbourObservation
from coflow5.control.recovery import REQUIRED_RECOVERY_LADDER, RecoveryMode
from coflow5.control.safety import (
    ActionProposal,
    DeterministicSafetyMask,
    ProposalSource,
    SafetyReason,
    SignalSnapshot,
    controlled_cross_plan,
)

Slot = Literal["A", "B", "C", "D"]
SLOTS: tuple[Slot, ...] = ("A", "B", "C", "D")
ActionKind = Literal["active_priority", "corridor_preparation", "normal_or_protective"]
Freshness = Literal["fresh", "stale_ignored", "unavailable"]
_GRAPH = "corridor-window"
_APPROVER = "A1"


@dataclass(frozen=True)
class EdgeFact:
    from_slot: Slot
    to_slot: Slot
    phase_id: str
    occupancy: float
    capacity: float
    closed: bool = False

    @property
    def blocked(self) -> bool:
        return self.closed or self.capacity <= 0 or self.occupancy >= self.capacity


@dataclass(frozen=True)
class JunctionSnapshot:
    current_phase_id: str
    phase_entered_at: float
    pressures: Mapping[str, float]
    downstream_available: Mapping[str, bool]
    service_age_seconds: Mapping[str, float]
    pedestrian_remaining_clearance: Mapping[str, float]


@dataclass(frozen=True)
class EmergencyRequest:
    vehicle_id: str
    route: tuple[Slot, ...]
    current_slot: Slot
    requested_phase_id: str
    eta_seconds: float
    urgency: float
    expires_at: float
    passed_slots: frozenset[Slot] = frozenset()
    inside_approach_of: Slot | None = None
    entered_link_toward: Slot | None = None


@dataclass(frozen=True)
class CorridorState:
    simulation_time: float
    slot_map: Mapping[Slot, str]
    junctions: Mapping[Slot, JunctionSnapshot]
    neighbours: tuple[NeighbourObservation, ...] = ()
    edges: tuple[EdgeFact, ...] = ()
    emergencies: tuple[EmergencyRequest, ...] = ()
    prior_plan: Mapping[Slot, str] | None = None


@dataclass(frozen=True)
class JunctionAction:
    kind: ActionKind
    signal_id: str
    phase: str
    approved_by: str
    reason: str
    freshness: Freshness


@dataclass(frozen=True)
class EmergencyHandoff:
    active_junction: Slot | None
    next_junction: Slot | None
    status: Literal["active", "preparing", "normal"]


@dataclass(frozen=True)
class CorridorRecord:
    actions: Mapping[Slot, JunctionAction]
    emergency_handoff: EmergencyHandoff
    reason_codes: tuple[str, ...]
    stale_neighbours: tuple[Slot, ...]
    recovery_mode: RecoveryMode
    recovery_ladder: tuple[RecoveryMode, ...]
    emergency_travel_time_seconds: float
    civilian_delay_seconds: float


class CorridorDecisionWindow:
    def __init__(self) -> None:
        self._mask = DeterministicSafetyMask(controlled_cross_plan())

    def decide(self, state: CorridorState) -> CorridorRecord:
        self._require_four(state)
        reasons: list[str] = []
        stale = self._stale_slots(state)
        if stale:
            reasons.append("stale_neighbour_ignored")
        winner = self._select_emergency(state.emergencies, state.simulation_time, reasons)
        active = self._active_slot(winner) if winner is not None else None
        nxt = self._next_slot(winner.route, active) if winner is not None and active is not None else None
        actions = {
            slot: self._action_for(state, slot, winner, active, nxt, stale, reasons)
            for slot in SLOTS
        }
        status: Literal["active", "preparing", "normal"] = "normal"
        if any(item.kind == "corridor_preparation" for item in actions.values()):
            status = "preparing"
        elif any(item.kind == "active_priority" for item in actions.values()):
            status = "active"
        delay = sum(
            pressure
            for slot in SLOTS
            for phase, pressure in state.junctions[slot].pressures.items()
            if phase != actions[slot].phase
        )
        active_now = active if any(item.kind == "active_priority" for item in actions.values()) else None
        return CorridorRecord(
            actions=actions,
            emergency_handoff=EmergencyHandoff(
                active_now,
                nxt if status != "normal" else None,
                status,
            ),
            reason_codes=tuple(dict.fromkeys(reasons)),
            stale_neighbours=stale,
            recovery_mode=REQUIRED_RECOVERY_LADDER[0],
            recovery_ladder=REQUIRED_RECOVERY_LADDER,
            emergency_travel_time_seconds=0.0 if winner is None else winner.eta_seconds,
            civilian_delay_seconds=delay,
        )

    def _require_four(self, state: CorridorState) -> None:
        if tuple(state.slot_map) != SLOTS or len(set(state.slot_map.values())) != 4:
            raise ValueError("slot map must bind A, B, C, and D to four signal ids")
        if set(state.junctions) != set(SLOTS):
            raise ValueError("a corridor window needs all four junctions")

    def _stale_slots(self, state: CorridorState) -> tuple[Slot, ...]:
        by_signal = {signal: slot for slot, signal in state.slot_map.items()}
        found: list[Slot] = []
        for sample in state.neighbours:
            if not sample.observed_at <= state.simulation_time <= sample.expires_at:
                slot = by_signal.get(sample.to_signal_id)
                if slot is not None and slot not in found:
                    found.append(slot)
        return tuple(found)

    def _select_emergency(
        self,
        requests: tuple[EmergencyRequest, ...],
        simulation_time: float,
        reasons: list[str],
    ) -> EmergencyRequest | None:
        live = tuple(item for item in requests if item.expires_at >= simulation_time)
        if len(requests) > len(live):
            reasons.append("expired_request_ignored")
        if not live:
            return None
        ordered = sorted(live, key=lambda item: (-item.urgency, item.eta_seconds, item.vehicle_id))
        if len(ordered) > 1:
            reasons.append("emergency_arbitrated")
        return ordered[0]

    def _active_slot(self, request: EmergencyRequest) -> Slot | None:
        slot = request.current_slot
        if request.inside_approach_of == slot or request.entered_link_toward == slot:
            return slot
        if slot not in request.route:
            return None
        index = request.route.index(slot)
        previous = request.route[index - 1] if index else None
        if previous is not None and previous in request.passed_slots:
            return slot
        if slot not in request.passed_slots:
            return slot
        return None

    def _next_slot(self, route: tuple[Slot, ...], active: Slot | None) -> Slot | None:
        if active is None or active not in route:
            return None
        index = route.index(active) + 1
        return route[index] if index < len(route) else None

    def _action_for(
        self,
        state: CorridorState,
        slot: Slot,
        winner: EmergencyRequest | None,
        active: Slot | None,
        nxt: Slot | None,
        stale: tuple[Slot, ...],
        reasons: list[str],
    ) -> JunctionAction:
        signal_id = state.slot_map[slot]
        junction = state.junctions[slot]
        downstream = self._downstream(state, slot, junction)
        if winner is not None and slot == active:
            return self._priority(state, slot, signal_id, junction, winner, downstream, reasons)
        preparing = (
            winner is not None
            and slot == nxt
            and slot not in stale
            and not self._exit_blocked(state, slot, winner.requested_phase_id, downstream)
        )
        if preparing:
            reasons.append(f"{slot}_preparing")
            phase = state.prior_plan.get(slot, junction.current_phase_id) if state.prior_plan else junction.current_phase_id
            phase = self._accepted_phase(state, signal_id, junction, phase)
            return JunctionAction(
                "corridor_preparation", signal_id, phase, _APPROVER,
                "future_plan_not_emergency_green", "fresh",
            )
        phase, freshness = self._scored_phase(state, slot, signal_id, junction, downstream, stale)
        return JunctionAction(
            "normal_or_protective", signal_id, phase, _APPROVER,
            "cooperative_max_pressure", freshness,
        )

    def _priority(
        self,
        state: CorridorState,
        slot: Slot,
        signal_id: str,
        junction: JunctionSnapshot,
        request: EmergencyRequest,
        downstream: Mapping[str, bool],
        reasons: list[str],
    ) -> JunctionAction:
        phase = request.requested_phase_id
        if self._exit_blocked(state, slot, phase, downstream):
            reasons.append("exit_blocked")
            scored, freshness = self._scored_phase(state, slot, signal_id, junction, downstream, ())
            return JunctionAction(
                "normal_or_protective", signal_id, scored, _APPROVER, "exit_blocked", freshness,
            )
        decision = self._mask_phase(state, signal_id, junction, phase)
        if not decision.accepted:
            reasons.append(decision.reason.value)
            hold, freshness = self._scored_phase(state, slot, signal_id, junction, downstream, ())
            if hold == phase:
                hold = self._accepted_phase(state, signal_id, junction, junction.current_phase_id)
            return JunctionAction(
                "normal_or_protective", signal_id, hold, _APPROVER, decision.reason.value, freshness,
            )
        reasons.append(f"ambulance_at_{slot}")
        return JunctionAction("active_priority", signal_id, phase, _APPROVER, "ambulance_priority", "fresh")

    def _exit_blocked(
        self, state: CorridorState, slot: Slot, phase_id: str, downstream: Mapping[str, bool],
    ) -> bool:
        if phase_id in downstream and not downstream[phase_id]:
            return True
        return any(edge.from_slot == slot and edge.phase_id == phase_id and edge.blocked for edge in state.edges)

    def _downstream(self, state: CorridorState, slot: Slot, junction: JunctionSnapshot) -> dict[str, bool]:
        available = dict(junction.downstream_available)
        for edge in state.edges:
            if edge.from_slot == slot and edge.blocked:
                available[edge.phase_id] = False
        return available

    def _scored_phase(
        self,
        state: CorridorState,
        slot: Slot,
        signal_id: str,
        junction: JunctionSnapshot,
        downstream: Mapping[str, bool],
        stale: tuple[Slot, ...],
    ) -> tuple[str, Freshness]:
        samples = tuple(sample for sample in state.neighbours if sample.to_signal_id == signal_id)
        fresh = tuple(
            sample for sample in samples
            if sample.observed_at <= state.simulation_time <= sample.expires_at
        )
        if slot in stale:
            freshness: Freshness = "stale_ignored"
        elif fresh:
            freshness = "fresh"
        else:
            freshness = "unavailable"
        scored = score_graph_actions(
            expected_graph_hash=_GRAPH,
            observation_graph_hash=_GRAPH,
            simulation_time=state.simulation_time,
            current_phase_id=junction.current_phase_id,
            local_pressures=junction.pressures,
            downstream_available=downstream,
            service_age_seconds=junction.service_age_seconds,
            neighbours=fresh or None,
        )
        return self._accepted_phase(state, signal_id, junction, scored.accepted_action), freshness

    def _accepted_phase(
        self, state: CorridorState, signal_id: str, junction: JunctionSnapshot, preferred: str,
    ) -> str:
        if self._mask_phase(state, signal_id, junction, preferred).accepted:
            return preferred
        candidates = [junction.current_phase_id, *sorted(junction.pressures)]
        legal = self._mask.plan.legal_transitions.get(junction.current_phase_id, frozenset())
        for phase_id in (*candidates, *sorted(legal)):
            if self._mask_phase(state, signal_id, junction, phase_id).accepted:
                return phase_id
        return junction.current_phase_id

    def _mask_phase(self, state: CorridorState, signal_id: str, junction: JunctionSnapshot, phase_id: str):
        return self._mask.evaluate(
            ActionProposal(f"{signal_id}:{phase_id}", signal_id, phase_id, ProposalSource.A1_FLOW),
            SignalSnapshot(
                junction.current_phase_id,
                junction.phase_entered_at,
                junction.pedestrian_remaining_clearance,
            ),
            state.simulation_time,
        )
