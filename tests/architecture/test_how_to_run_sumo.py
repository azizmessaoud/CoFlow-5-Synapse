from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_how_to_run_doc_names_both_run_actions() -> None:
    text = (ROOT / "docs" / "how-to-run-sumo.md").read_text(encoding="utf-8")
    assert "watch_sumo.py smoke" in text
    assert "generate_max_pressure_artifacts.py" in text
    assert "run_native_smoke.py" in text
    assert "row 10" in text.lower() or "**row 10**" in text.lower()


def test_watch_sumo_help_lists_scenes_without_sumo() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "watch_sumo.py"), "-h"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    for scene in ("smoke", "safety", "baselines", "max-pressure", "a1"):
        assert scene in result.stdout
