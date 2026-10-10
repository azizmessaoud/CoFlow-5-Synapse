import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_native_capture_contains_three_controller_rows_for_five_matched_seeds() -> None:
    capture = json.loads(
        (ROOT / "harness/work/10e/artifacts/matched-runs.json").read_text(
            encoding="utf-8"
        )
    )
    assert capture["status"] == "captured_pending_audit"
    assert capture["seeds"] == [37, 41, 43, 47, 53]
    assert len(capture["runs"]) == 15
    for seed in capture["seeds"]:
        rows = [row for row in capture["runs"] if row["seed"] == seed]
        assert {row["controller"] for row in rows} == {
            "fixed-time",
            "actuated",
            "cooperative-max-pressure",
        }
        assert {row["scenario_hash"] for row in rows} == {capture["scenario_hash"]}
