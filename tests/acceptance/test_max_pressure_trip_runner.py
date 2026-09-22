from __future__ import annotations

import pytest

from coflow5.sumo_adapter.max_pressure_trip_runner import (
    MaxPressureTripEvidenceError,
    build_trip_rows,
    compute_run_kpis,
    linear_percentile,
)

RUN_ID = "row10b-unit"
SCENARIO_HASH = "sha256:" + "b" * 64


def test_build_trip_rows_preserves_completed_active_and_not_departed() -> None:
    rows = build_trip_rows(
        run_id=RUN_ID,
        scenario_hash=SCENARIO_HASH,
        seed=37,
        planned_trip_ids=("north-demand.0", "north-demand.1", "north-demand.2"),
        departed_at={"north-demand.0": 1.0, "north-demand.1": 3.0},
        arrived_at={"north-demand.0": 11.0},
        latest_wait={"north-demand.0": 4.0, "north-demand.1": 7.0},
        latest_time_loss={"north-demand.0": 5.0, "north-demand.1": 9.0},
        standstill_seconds={"north-demand.0": 2, "north-demand.1": 6},
        observed_at=20.0,
    )
    by_id = {row.trip_id: row for row in rows}
    assert set(by_id) == {"north-demand.0", "north-demand.1", "north-demand.2"}
    assert by_id["north-demand.0"].trip_status == "completed"
    assert by_id["north-demand.0"].duration_s == 10.0
    assert by_id["north-demand.1"].trip_status == "active-at-horizon"
    assert by_id["north-demand.1"].duration_s == 17.0
    assert by_id["north-demand.2"].trip_status == "not-departed"
    assert by_id["north-demand.2"].duration_s is None


def test_run_kpis_recompute_from_completed_rows_without_hiding_unfinished() -> None:
    rows = build_trip_rows(
        run_id=RUN_ID,
        scenario_hash=SCENARIO_HASH,
        seed=37,
        planned_trip_ids=("flow.0", "flow.1", "flow.2", "flow.3"),
        departed_at={"flow.0": 0.0, "flow.1": 1.0, "flow.2": 2.0},
        arrived_at={"flow.0": 10.0, "flow.1": 21.0},
        latest_wait={"flow.0": 2.0, "flow.1": 6.0, "flow.2": 9.0},
        latest_time_loss={"flow.0": 3.0, "flow.1": 7.0, "flow.2": 11.0},
        standstill_seconds={"flow.0": 1, "flow.1": 4, "flow.2": 8},
        observed_at=30.0,
    )
    kpi = compute_run_kpis(
        rows,
        run_id=RUN_ID,
        scenario_hash=SCENARIO_HASH,
        seed=37,
        simulation_steps=30,
        max_active_vehicles=3,
        teleport_events=0,
        safety_event_count=30,
        accepted_signal_commands=30,
    )
    assert kpi["planned_trips"] == 4
    assert kpi["completed_trips"] == 2 and kpi["unfinished_trips"] == 2
    assert kpi["completion_rate"] == 0.5
    assert kpi["mean_duration_s"] == 15.0
    assert kpi["p95_duration_s"] == pytest.approx(19.5)
    assert kpi["mean_waiting_time_s"] == 4.0
    assert kpi["p95_waiting_time_s"] == pytest.approx(5.8)
    assert kpi["total_time_loss_s"] == 10.0
    assert kpi["standstill_vehicle_seconds"] == 13
    assert kpi["vehicles_with_standstill"] == 3


def test_trip_input_validation_and_percentile_rule_are_explicit() -> None:
    assert linear_percentile([0.0, 10.0, 20.0], 0.95) == pytest.approx(19.0)
    with pytest.raises(MaxPressureTripEvidenceError, match="unique"):
        build_trip_rows(
            run_id=RUN_ID,
            scenario_hash=SCENARIO_HASH,
            seed=37,
            planned_trip_ids=("flow.0", "flow.0"),
            departed_at={}, arrived_at={}, latest_wait={}, latest_time_loss={},
            standstill_seconds={}, observed_at=20.0,
        )
