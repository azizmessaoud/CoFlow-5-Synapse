import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_j0_completion_bundle_records_native_and_fixture_sources() -> None:
    bundle = json.loads(
        (ROOT / "harness/work/10e/artifacts/j0-completion-bundle.json").read_text(
            encoding="utf-8"
        )
    )

    assert bundle["status"] == "pass"
    assert bundle["audit"]["pass_gate"] is True
    assert bundle["audit"]["matched_seeds"] == [37, 41, 43, 47, 53]
    assert {
        row["failure_kind"] for row in bundle["recovery_events"]
    } == {"specialist", "controller", "communication", "forecast", "synapse"}
    assert bundle["forecast_provenance"]["message_id"] == "eco-001"
