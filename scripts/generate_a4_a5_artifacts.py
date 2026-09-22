from pathlib import Path

from coflow5.evidence.a4_a5_artifacts import generate_a4_a5_artifacts


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    manifest = generate_a4_a5_artifacts(root)
    print(
        "Row 10 artifacts generated "
        f"run_id={manifest['run_id']} scenario_hash={manifest['scenario_hash']}"
    )
