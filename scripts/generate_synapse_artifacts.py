from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coflow5.evidence.synapse_artifacts import generate_synapse_artifacts


if __name__ == "__main__":
    manifest = generate_synapse_artifacts(ROOT)
    print(manifest["run_id"])
    print(f"source_event_id={manifest['source_event_id']}")
    print(f"status={manifest['status']}")
