from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coflow5.evidence.graph_growth_artifacts import generate_graph_growth_artifacts


if __name__ == "__main__":
    manifest = generate_graph_growth_artifacts(ROOT)
    print(manifest["run_id"])
    print(f"matrix_run_count={manifest['matrix_run_count']}")
    print(f"native_smoke_status={manifest['native_smoke_status']}")
