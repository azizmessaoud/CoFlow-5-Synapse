import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_native_ablation_capture_contains_all_matched_cells() -> None:
    capture = json.loads(
        (ROOT / "harness/work/10e/artifacts/j0-ablations.json").read_text(
            encoding="utf-8"
        )
    )

    assert capture["status"] == "captured_pending_audit"
    assert capture["seeds"] == [37, 41, 43, 47, 53]
    assert len(capture["rows"]) == 40
    assert {
        (row["agent"], row["enabled"])
        for row in capture["rows"]
    } == {
        (agent, enabled)
        for agent in ("A2", "A3", "A4", "A5")
        for enabled in (False, True)
    }
    assert all(row["run_id"] for row in capture["rows"])
    assert all(row["scenario_hash"] == capture["scenario_hash"] for row in capture["rows"])
    assert all(isinstance(row["kpis"], dict) and row["kpis"] for row in capture["rows"])
    assert all(row["event_ids"] for row in capture["rows"])
