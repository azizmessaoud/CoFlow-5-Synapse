from __future__ import annotations

import importlib.metadata

from hypothesis import given, settings, strategies as st

from coflow5.control import (
    ActionProposal,
    DeterministicSafetyMask,
    SafetyReason,
    SignalSnapshot,
    controlled_cross_plan,
)

MASK = DeterministicSafetyMask(controlled_cross_plan())
FINITE_TIME = st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False)
BELOW_MIN_GREEN = st.floats(min_value=0.0, max_value=4.999999, allow_nan=False, allow_infinity=False)
BELOW_YELLOW = st.floats(min_value=0.0, max_value=1.999999, allow_nan=False, allow_infinity=False)
BELOW_ALL_RED = st.floats(min_value=0.0, max_value=0.999999, allow_nan=False, allow_infinity=False)


def test_hypothesis_is_contract_pinned_version() -> None:
    assert importlib.metadata.version("hypothesis") == "6.138.4"


@given(entered=FINITE_TIME, elapsed=BELOW_MIN_GREEN)
@settings(max_examples=100, deadline=None)
def test_minimum_green_rejects_every_value_below_boundary(entered: float, elapsed: float) -> None:
    decision = MASK.evaluate(
        ActionProposal("property", "J0", "NS_YELLOW"),
        SignalSnapshot("NS_GREEN", entered), entered + elapsed,
    )
    assert not decision.accepted
    assert decision.reason is SafetyReason.MINIMUM_GREEN


@given(entered=FINITE_TIME)
@settings(max_examples=50, deadline=None)
def test_minimum_green_accepts_exact_boundary(entered: float) -> None:
    assert MASK.evaluate(
        ActionProposal("boundary", "J0", "NS_YELLOW"),
        SignalSnapshot("NS_GREEN", entered), entered + 5.0,
    ).accepted


@given(entered=FINITE_TIME, elapsed=BELOW_YELLOW)
@settings(max_examples=100, deadline=None)
def test_yellow_clearance_rejects_every_value_below_boundary(entered: float, elapsed: float) -> None:
    decision = MASK.evaluate(
        ActionProposal("property", "J0", "ALL_RED_TO_EW"),
        SignalSnapshot("NS_YELLOW", entered), entered + elapsed,
    )
    assert decision.reason is SafetyReason.YELLOW_MINIMUM


@given(entered=FINITE_TIME, elapsed=BELOW_ALL_RED)
@settings(max_examples=100, deadline=None)
def test_all_red_rejects_every_value_below_boundary(entered: float, elapsed: float) -> None:
    decision = MASK.evaluate(
        ActionProposal("property", "J0", "EW_GREEN"),
        SignalSnapshot("ALL_RED_TO_EW", entered), entered + elapsed,
    )
    assert decision.reason is SafetyReason.ALL_RED_MINIMUM


@given(remaining=st.floats(min_value=1e-9, max_value=120.0, allow_nan=False, allow_infinity=False))
@settings(max_examples=100, deadline=None)
def test_positive_remaining_pedestrian_clearance_always_blocks_conflicting_green(
    remaining: float,
) -> None:
    decision = MASK.evaluate(
        ActionProposal("pedestrian", "J0", "EW_GREEN"),
        SignalSnapshot(
            "ALL_RED_TO_EW", 0.0, {"north_south_crossing": remaining}
        ),
        1.0,
    )
    assert not decision.accepted
    assert decision.reason is SafetyReason.PEDESTRIAN_CLEARANCE


@given(
    phase_id=st.sampled_from(tuple(controlled_cross_plan().phases)),
    entered=FINITE_TIME,
    elapsed=st.floats(min_value=0.0, max_value=20.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=250, deadline=None)
def test_no_conflicting_phase_can_ever_be_accepted(
    phase_id: str, entered: float, elapsed: float
) -> None:
    decision = MASK.evaluate(
        ActionProposal("conflict", "J0", "CONFLICTING_TEST"),
        SignalSnapshot(phase_id, entered), entered + elapsed,
    )
    assert not decision.accepted
    assert decision.reason is SafetyReason.CONFLICTING_GREENS



@given(
    bad=st.sampled_from((float("nan"), float("inf"), float("-inf"))),
    field=st.sampled_from(("simulation_time", "phase_entered_at", "clearance")),
)
@settings(max_examples=20, deadline=None)
def test_non_finite_values_always_fail_closed(bad: float, field: str) -> None:
    simulation_time = bad if field == "simulation_time" else 5.0
    entered = bad if field == "phase_entered_at" else 0.0
    clearance = bad if field == "clearance" else 0.0
    decision = MASK.evaluate(
        ActionProposal("non-finite", "J0", "NS_YELLOW"),
        SignalSnapshot("NS_GREEN", entered, {"north_south_crossing": clearance}),
        simulation_time,
    )
    assert decision.accepted is False
    assert decision.reason is SafetyReason.NON_FINITE_INPUT
