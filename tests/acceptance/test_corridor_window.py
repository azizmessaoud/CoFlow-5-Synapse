from dataclasses import replace

import pytest

from coflow5.control.corridor_window import (
    SLOTS,
    CorridorDecisionWindow,
    CorridorState,
    EdgeFact,
    EmergencyRequest,
    JunctionSnapshot,
)
from coflow5.control.junction_graph import NeighbourObservation
from coflow5.control.recovery import REQUIRED_RECOVERY_LADDER, RecoveryMode

SLOT_MAP = {"A": "tls_101", "B": "tls_102", "C": "tls_103", "D": "tls_104"}


def _junction(**overrides) -> JunctionSnapshot:
    snapshot = JunctionSnapshot(
        current_phase_id="NS_GREEN",
        phase_entered_at=0.0,
        pressures={"NS_GREEN": 8.0, "EW_GREEN": 2.0},
        downstream_available={"NS_GREEN": True, "EW_GREEN": True},
        service_age_seconds={"NS_GREEN": 20.0, "EW_GREEN": 5.0},
        pedestrian_remaining_clearance={},
    )
    return replace(snapshot, **overrides)


def ambulance_at_A_world(**overrides) -> CorridorState:
    state = CorridorState(
        simulation_time=100.0,
        slot_map=SLOT_MAP,
        junctions={slot: _junction() for slot in SLOTS},
        neighbours=tuple(
            NeighbourObservation(
                SLOT_MAP[source], SLOT_MAP[target], "NS", 90.0, 110.0, 3.0, 0.2, 4.0,
            )
            for source, target in (("A", "B"), ("B", "C"), ("C", "D"))
        ),
        edges=(
            EdgeFact("A", "B", "NS_GREEN", occupancy=2.0, capacity=10.0),
            EdgeFact("B", "C", "NS_GREEN", occupancy=2.0, capacity=10.0),
            EdgeFact("C", "D", "NS_GREEN", occupancy=1.0, capacity=10.0),
        ),
        emergencies=(
            EmergencyRequest(
                vehicle_id="ambulance-1",
                route=("A", "B", "C", "D"),
                current_slot="A",
                requested_phase_id="NS_GREEN",
                eta_seconds=40.0,
                urgency=0.9,
                expires_at=180.0,
                inside_approach_of="A",
            ),
        ),
    )
    return replace(state, **overrides)


def test_ambulance_at_a_prepares_only_the_next_junction() -> None:
    record = CorridorDecisionWindow().decide(ambulance_at_A_world())

    assert record.actions["A"].kind == "active_priority"
    assert record.actions["A"].phase == "NS_GREEN"
    assert record.actions["B"].kind == "corridor_preparation"
    assert record.actions["C"].kind == "normal_or_protective"
    assert record.actions["D"].kind == "normal_or_protective"
    assert {action.approved_by for action in record.actions.values()} == {"A1"}
    assert record.emergency_handoff.status == "preparing"
    assert record.emergency_handoff.active_junction == "A"
    assert record.emergency_handoff.next_junction == "B"
    assert record.emergency_travel_time_seconds == 40.0
    assert record.civilian_delay_seconds > 0
    assert not hasattr(record, "deaths")
    assert record.recovery_mode is RecoveryMode.COOPERATIVE_MAX_PRESSURE
    assert record.recovery_ladder == REQUIRED_RECOVERY_LADDER


def test_blocked_exit_at_b_does_not_prepare_priority() -> None:
    base = ambulance_at_A_world()
    blocked = replace(
        base.junctions["B"],
        downstream_available={"NS_GREEN": False, "EW_GREEN": True},
    )
    state = replace(base, junctions={**base.junctions, "B": blocked})
    record = CorridorDecisionWindow().decide(state)

    assert record.actions["A"].kind == "active_priority"
    assert record.actions["B"].kind == "normal_or_protective"


def test_person_still_crossing_refuses_the_conflicting_green() -> None:
    base = ambulance_at_A_world()
    crossing = replace(
        base.junctions["A"],
        pedestrian_remaining_clearance={"east_west_crossing": 4.0},
    )
    record = CorridorDecisionWindow().decide(replace(base, junctions={**base.junctions, "A": crossing}))

    assert record.actions["A"].kind == "normal_or_protective"
    assert record.actions["A"].phase != "NS_GREEN"
    assert "REJECTED_PEDESTRIAN_CLEARANCE" in record.reason_codes


def test_stale_neighbour_at_c_is_ignored() -> None:
    base = ambulance_at_A_world()
    neighbours = tuple(
        sample if sample.to_signal_id != "tls_103" else replace(sample, observed_at=1.0, expires_at=2.0)
        for sample in base.neighbours
    )
    record = CorridorDecisionWindow().decide(replace(base, neighbours=neighbours))

    assert "C" in record.stale_neighbours
    assert record.actions["C"].freshness == "stale_ignored"
    assert record.actions["C"].kind == "normal_or_protective"
    assert record.actions["A"].kind == "active_priority"
    assert record.actions["B"].kind == "corridor_preparation"


def test_handoff_moves_active_priority_to_the_junction_the_ambulance_entered() -> None:
    base = ambulance_at_A_world()
    moved = replace(
        base.emergencies[0],
        current_slot="B",
        passed_slots=frozenset({"A"}),
        inside_approach_of="B",
        entered_link_toward="B",
    )
    record = CorridorDecisionWindow().decide(replace(base, emergencies=(moved,)))

    assert record.actions["B"].kind == "active_priority"
    assert record.actions["A"].kind == "normal_or_protective"
    assert record.actions["C"].kind == "corridor_preparation"
    assert record.actions["D"].kind == "normal_or_protective"
    assert record.emergency_handoff.active_junction == "B"


def test_second_handoff_prepares_only_the_following_junction() -> None:
    base = ambulance_at_A_world()
    moved = replace(
        base.emergencies[0],
        current_slot="C",
        passed_slots=frozenset({"A", "B"}),
        inside_approach_of="C",
    )
    record = CorridorDecisionWindow().decide(replace(base, emergencies=(moved,)))

    assert record.actions["C"].kind == "active_priority"
    assert record.actions["D"].kind == "corridor_preparation"
    assert record.actions["B"].kind == "normal_or_protective"


def test_two_emergencies_keep_a_single_active_priority() -> None:
    base = ambulance_at_A_world()
    other = EmergencyRequest(
        vehicle_id="ambulance-2",
        route=("C", "D"),
        current_slot="C",
        requested_phase_id="NS_GREEN",
        eta_seconds=15.0,
        urgency=0.2,
        expires_at=180.0,
        inside_approach_of="C",
    )
    record = CorridorDecisionWindow().decide(replace(base, emergencies=(*base.emergencies, other)))

    active = [slot for slot, action in record.actions.items() if action.kind == "active_priority"]
    assert active == ["A"]
    assert "emergency_arbitrated" in record.reason_codes


def test_no_emergency_leaves_every_junction_on_local_control() -> None:
    record = CorridorDecisionWindow().decide(ambulance_at_A_world(emergencies=()))

    assert {action.kind for action in record.actions.values()} == {"normal_or_protective"}
    assert record.emergency_handoff.status == "normal"
    assert record.emergency_travel_time_seconds == 0.0


def test_slot_map_must_name_four_signals() -> None:
    state = ambulance_at_A_world()
    broken = replace(state, slot_map={"A": "tls_101", "B": "tls_101", "C": "tls_103", "D": "tls_104"})
    with pytest.raises(ValueError, match="four signal"):
        CorridorDecisionWindow().decide(broken)


def test_window_does_not_carry_a_traci_connection() -> None:
    window = CorridorDecisionWindow()
    assert not hasattr(window, "traci")
    assert callable(window.decide)
