from pathlib import Path

from coflow5.evidence.max_pressure_trip_artifacts import generate_max_pressure_trip_artifacts


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    manifest = generate_max_pressure_trip_artifacts(root)
    audit = manifest["runtime_audit"]
    print(
        "Row 10b artifacts generated "
        f"run_id={manifest['run_id']} scenario_hash={manifest['scenario_hash']} "
        f"completed={audit['completed_trips']}/{audit['planned_trips']}"
    )
