from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from coflow5.evidence.message_board_artifacts import generate_message_board_artifacts

if __name__ == "__main__":
    manifest = generate_message_board_artifacts(ROOT)
    print(f"run_id={manifest['run_id']}")
    print(f"scenario_hash={manifest['scenario_hash']}")
    print(f"artifacts={ROOT / 'harness/work/06-message-board/artifacts'}")
