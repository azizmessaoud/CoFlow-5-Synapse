from pathlib import Path

from coflow5.evidence.j0_matched_capture import capture_j0_matched_runs


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    capture = capture_j0_matched_runs(root)
    print(
        f"captured={len(capture['runs'])} runs "
        f"seeds={capture['seeds']} scenario_hash={capture['scenario_hash']}"
    )
