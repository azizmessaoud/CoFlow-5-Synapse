from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / ".scratch" / "coflow5-graph-growth" / "spec.md"
QUEUE = ROOT / "harness" / "queue.tsv"


def source() -> str:
    assert SPEC.is_file()
    return SPEC.read_text(encoding="utf-8")


def test_current_gap_and_roadwayvr_boundary_are_explicit() -> None:
    text = source()
    for fact in (
        "Measured A1 controls one signal",
        "84 planned trips, seed 37, 120-second horizon",
        "Fixed completed 71, actuated 84, Max-Pressure 70",
        "Demand-growth robustness is not established",
        "No multi-junction scenario exists",
    ):
        assert fact in text
    for reusable in (
        "`SUMO_HOME`, `traci.start`, labelled step loop, `simulationStep`",
        "Vehicle/lane telemetry and `vehicle.getNextTLS`",
        "`sumo-gui`, delay, and GUI schema",
    ):
        assert reusable in text
    for rejected in (
        "Hard-coded detector, edge, and TLS IDs",
        "`trafficlight.setPhase` or `setPhaseDuration` from tutorial logic",
        "Emergency shortening to `0.1` seconds",
        "Online Q-learning/DQL during the evaluated episode",
        "Queue-only reward and best plot",
    ):
        assert rejected in text
    assert "No RoadwayVR source file is copied" in text
    assert "keep RoadwayVR out of runtime dependencies" in text


def test_graph_contract_and_a1_failure_behavior_preserve_authority() -> None:
    text = source()
    for contract in (
        "JunctionNode",
        "GraphEdge",
        "NeighbourObservation",
        "JunctionGraphObservation",
        "GraphFrame",
        "graph_hash",
        "stale_neighbour_ids",
        "unavailable_neighbour_ids",
    ):
        assert contract in text
    for invariant in (
        "A1 remains the only signal-writing agent",
        "Each controlled signal has exactly one A1 executor",
        "cooperative Max-Pressure -> actuated -> fixed-time",
        "A full downstream lane remains a hard mask",
        "No stale graph input can stop A1 or authorize an action",
        "`GRAPH_NEIGHBOUR_STALE_LOCAL_ONLY`",
        "`GRAPH_NEIGHBOUR_UNAVAILABLE_LOCAL_ONLY`",
        "`GRAPH_IDENTITY_MISMATCH_LOCAL_ONLY`",
        "`DOWNSTREAM_BLOCKED`",
    ):
        assert invariant in text
    assert "Do not add NetworkX initially" in text


def test_growth_matrix_metrics_and_null_result_are_contracted() -> None:
    text = source()
    for value in (
        "synthetic **2x2 grid with four controlled junctions**",
        "`low=0.75`, `base=1.00`, `growth=1.25`, `surge=1.50`",
        "Five fixed paired seeds",
        "Fixed-time; actuated; local cooperative Max-Pressure; graph-aware cooperative Max-Pressure",
        "4 demand levels x 5 seeds x 4 controllers = 80 paired runs",
        "unfinished trips retained",
    ):
        assert value in text
    for family in (
        "| Safety |",
        "| Liveness |",
        "| Demand growth |",
        "| Journey |",
        "| Junction |",
        "| Graph |",
        "| Agents |",
        "| Runtime |",
    ):
        assert family in text
    assert "Performance is reported, not gated to “graph-aware wins.”" in text
    assert "A null or negative graph result is acceptable" in text


def test_agents_and_graphical_interface_are_bounded_and_read_only() -> None:
    text = source()
    for agent in (
        "| A1 Flow | One-hop graph-aware cooperative Max-Pressure",
        "| A2 Emergency | Shortest feasible corridor",
        "| A3 Multimodal | Transit route subgraph",
        "| A4 Situation | Graph residuals and spatial consistency",
        "| A5 Sustainability | Optional link stop/emission-proxy",
        "| Synapse | Graph evidence explainer",
    ):
        assert agent in text
    assert "The agentic property is **cooperation under explicit authority**, not five chatbots" in text
    assert "React remains Row 13 after Synapse and API" in text
    assert "It reads precomputed `GraphFrame` artifacts through a read-only API" in text
    assert "No “manual phase” button is exposed" in text
    assert "it is not a React-to-TraCI shortcut" in text


def test_next_executable_row_is_bounded_and_queued() -> None:
    text = source()
    queue = QUEUE.read_text(encoding="utf-8")
    assert "10e-graph-growth-spec\tspec\tactive\t" in queue or "10e-graph-growth-spec\tspec\tgated\t" in queue
    assert "10f-graph-growth-benchmark\tcontrol\ttodo\t" in queue
    assert "## 9. Next executable row — 10f graph-growth benchmark" in text
    for test_path in (
        "tests/contracts/test_junction_graph.py",
        "tests/acceptance/test_graph_growth_runner.py",
        "tests/contracts/test_graph_growth_evidence.py",
        "tests/architecture/test_forbidden_imports.py",
        "tests/scripts/test_watch_sumo.py",
    ):
        assert test_path in text
    for artifact in (
        "run_manifest.json",
        "graph.json",
        "demand_cells.json",
        "graph_frames.parquet",
        "decision_events.parquet",
        "trips.parquet",
        "run_kpis.parquet",
        "matched_growth_comparison.json",
        "growth_report.md",
    ):
        assert artifact in text
    for forbidden in ("NetworkX", "TensorFlow", "PyTorch", "GNN", "DQN", "WebSocket", "React"):
        assert forbidden in text[text.index("### Stop conditions") :]
    assert "Rows 05 and 10b remain immutable reference evidence" in text
    assert "does not improve the paired growth cells, keep local cooperative Max-Pressure" in text
