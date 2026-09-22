from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coflow5.evidence import generate_bundle

if __name__ == "__main__":
    manifest = generate_bundle(ROOT)
    print(f"run_id={manifest['run_id']}")
    print(f"scenario_hash={manifest['scenario_hash']}")
    print(f"status={manifest['status']}")
    print(f"artifacts={ROOT / 'harness' / 'work' / '02-evidence-bundle' / 'artifacts'}")
