from pathlib import Path

from coflow5.evaluation.failure_artifacts import generate_failure_injection_artifacts


if __name__ == "__main__":
    manifest = generate_failure_injection_artifacts(Path(__file__).resolve().parents[1])
    print(f"run_id={manifest['run_id']}")
    print(f"scenario_hash={manifest['scenario_hash']}")
