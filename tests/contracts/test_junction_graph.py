from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from coflow5.control.graph_max_pressure import (
    GRAPH_IDENTITY_MISMATCH_LOCAL_ONLY,
    GRAPH_NEIGHBOUR_STALE_LOCAL_ONLY,
    GRAPH_NEIGHBOUR_UNAVAILABLE_LOCAL_ONLY,
    GRAPH_NEIGHBOUR_USED,
    score_graph_actions,
)
from coflow5.control.junction_graph import GraphIdentityError, NeighbourObservation, load_junction_graph
from coflow5.sumo_adapter.graph_growth_runner import generate_od_routes

ROOT = Path(__file__).resolve().parents[2]
NETWORK = ROOT / "scenarios/graph-growth/graph-growth.net.xml"


def test_four_signal_graph_is_immutable_hashed_and_identity_checked(tmp_path: Path) -> None:
    graph = load_junction_graph(NETWORK)
    assert [node.signal_id for node in graph.nodes] == ["J0", "J1", "J2", "J3"]
    assert all(node.executor_owner == "A1" for node in graph.nodes)
    assert len(graph.edges) == 8
    assert all(len(graph.adjacency[node.signal_id]) == 2 for node in graph.nodes)
    assert all(len(node.incoming_lane_ids) == len(node.outgoing_lane_ids) == 4 for node in graph.nodes)
    assert graph.graph_hash.startswith("sha256:") and len(graph.graph_hash) == 71
    assert load_junction_graph(NETWORK, expected_graph_hash=graph.graph_hash) == graph
    with pytest.raises(GraphIdentityError, match="graph hash"):
        load_junction_graph(NETWORK, expected_graph_hash="sha256:" + "0" * 64)
    with pytest.raises((FrozenInstanceError, AttributeError)):
        graph.nodes[0].signal_id = "other"  # type: ignore[misc]
    with pytest.raises(TypeError):
        graph.adjacency["J0"] = ()  # type: ignore[index]


def test_od_generation_is_frozen_and_accounts_for_each_scale() -> None:
    for scale, expected in ((0.75, 24), (1.0, 32), (1.25, 40), (1.5, 48)):
        first, ids = generate_od_routes(demand_scale=scale, seed=37)
        second, second_ids = generate_od_routes(demand_scale=scale, seed=37)
        assert first == second and ids == second_ids and len(ids) == expected
        assert len(set(ids)) == expected and first.count("<vehicle ") == expected
    with pytest.raises(ValueError):
        generate_od_routes(demand_scale=2.0, seed=37)


def test_bounded_graph_terms_and_all_fallbacks_are_exact_local_only() -> None:
    graph = load_junction_graph(NETWORK)
    local = {"EW_GREEN": 4.0, "NS_GREEN": 6.0}
    available = {key: True for key in local}
    ages = {key: 45.0 for key in local}
    fresh = NeighbourObservation(
        "J0", "J1", "NS", 9.0, 15.0, 2.0, 0.25, 9.0,
    )
    used = score_graph_actions(
        expected_graph_hash=graph.graph_hash, observation_graph_hash=graph.graph_hash,
        simulation_time=10.0, current_phase_id="NS_GREEN", local_pressures=local,
        downstream_available=available, service_age_seconds=ages, neighbours=(fresh,),
    )
    assert used.reason_code == GRAPH_NEIGHBOUR_USED
    assert used.used_neighbour_ids == ("J1",)
    assert all(0 <= score.one_hop_discharge_bonus <= 2 for score in used.scores)
    assert all(0 <= score.service_age_bonus <= 2 for score in used.scores)
    assert all(0 <= score.switch_penalty <= 1 for score in used.scores)

    stale = NeighbourObservation("J0", "J1", "NS", 1.0, 2.0, 2.0, 0.25, 9.0)
    cases = (
        (graph.graph_hash, (stale,), GRAPH_NEIGHBOUR_STALE_LOCAL_ONLY),
        (graph.graph_hash, None, GRAPH_NEIGHBOUR_UNAVAILABLE_LOCAL_ONLY),
        ("sha256:" + "0" * 64, (fresh,), GRAPH_IDENTITY_MISMATCH_LOCAL_ONLY),
    )
    for observed_hash, neighbours, reason in cases:
        result = score_graph_actions(
            expected_graph_hash=graph.graph_hash, observation_graph_hash=observed_hash,
            simulation_time=10.0, current_phase_id="NS_GREEN", local_pressures=local,
            downstream_available=available, service_age_seconds=ages, neighbours=neighbours,
        )
        assert result.reason_code == reason
        assert result.accepted_action == "NS_GREEN"
        assert all(score.total == score.local_pressure for score in result.scores)
        assert result.used_neighbour_ids == ()


def test_downstream_hard_mask_cannot_be_overridden_by_graph_bonus() -> None:
    graph = load_junction_graph(NETWORK)
    fresh = NeighbourObservation("J0", "J1", "EW", 9.0, 15.0, 0.0, 0.0, 100.0)
    result = score_graph_actions(
        expected_graph_hash=graph.graph_hash, observation_graph_hash=graph.graph_hash,
        simulation_time=10.0, current_phase_id="NS_GREEN",
        local_pressures={"EW_GREEN": 100.0, "NS_GREEN": 1.0},
        downstream_available={"EW_GREEN": False, "NS_GREEN": True},
        service_age_seconds={"EW_GREEN": 90.0, "NS_GREEN": 0.0}, neighbours=(fresh,),
    )
    assert result.accepted_action == "NS_GREEN"
