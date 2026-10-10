from coflow5.a3 import (
    PedestrianDemandConfig,
    generate_seeded_pedestrian_demand,
    summarize_pedestrian_demand,
)


def test_seeded_j0_demand_is_reproducible_and_reports_occupancy_and_wait() -> None:
    config = PedestrianDemandConfig(
        run_id="j0-pedestrian-seed-11",
        scenario_hash="sha256:" + "1" * 64,
        crossing_id="north_south_crossing",
        signal_id="J0",
        seed=11,
        pedestrian_count=5,
    )

    first = generate_seeded_pedestrian_demand(config)
    second = generate_seeded_pedestrian_demand(config)

    assert first == second
    assert len(first) == 5
    assert all(item.active_crossing for item in first)
    assert all(item.wait_seconds >= 0 for item in first)
    assert all(item.clearance_end > item.clearance_start for item in first)
    assert all(not item.clearance_truncated for item in first)
    assert {item.run_id for item in first} == {config.run_id}
    assert {item.scenario_hash for item in first} == {config.scenario_hash}
    assert len({item.occupancy_event_id for item in first}) == 5
    summary = summarize_pedestrian_demand(first)
    assert summary["pedestrian_count"] == 5
    assert summary["mean_wait_s"] <= summary["p95_wait_s"] <= summary["max_wait_s"]
    assert summary["clearance_truncations"] == 0


def test_seeded_demand_exposes_a3_state_with_remaining_clearance() -> None:
    config = PedestrianDemandConfig(
        run_id="j0-pedestrian-seed-17",
        scenario_hash="sha256:" + "2" * 64,
        crossing_id="north_south_crossing",
        signal_id="J0",
        seed=17,
        pedestrian_count=1,
    )

    observation = generate_seeded_pedestrian_demand(config)[0]
    state = observation.crossing_state(simulation_time=observation.clearance_start)

    assert state.active_crossing is True
    assert state.remaining_clearance_seconds > 0
    assert state.crossing_id == config.crossing_id
    assert state.signal_id == config.signal_id
