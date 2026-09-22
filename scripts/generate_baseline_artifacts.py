from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coflow5.evidence.baseline_artifacts import generate_baseline_artifacts

if __name__ == "__main__":
    comparison = generate_baseline_artifacts(ROOT)
    print(f"paired={comparison['all_cells_paired']}")
    print(f"seeds={comparison['common_evaluation_seeds']}")
    print(f"artifacts={ROOT / 'harness/work/04-baselines/artifacts'}")
