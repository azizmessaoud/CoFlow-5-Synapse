"""Open sumo-gui, or attach live A1 through TraCI. Not the row-01 smoke gate."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMO_HOME = Path(r"C:\Program Files (x86)\Eclipse\Sumo")
SCENES = {
    "smoke": ROOT / "scenarios" / "smoke" / "smoke.sumocfg",
    "safety": ROOT / "scenarios" / "safety-mask" / "safety.sumocfg",
    "baselines": ROOT / "scenarios" / "baselines" / "baselines.sumocfg",
    "max-pressure": ROOT / "scenarios" / "max-pressure" / "max-pressure.sumocfg",
}


def prepare_env() -> None:
    if not os.environ.get("SUMO_HOME"):
        os.environ["SUMO_HOME"] = str(DEFAULT_SUMO_HOME)
    bin_dir = Path(os.environ["SUMO_HOME"]) / "bin"
    os.environ["PATH"] = str(bin_dir) + os.pathsep + os.environ.get("PATH", "")


def require_gui() -> str:
    gui = shutil.which("sumo-gui")
    if not gui:
        raise SystemExit("sumo-gui.exe is not on PATH. Set SUMO_HOME, then retry.")
    return gui


def watch_scene(name: str) -> int:
    config = SCENES[name]
    if not config.is_file():
        raise SystemExit(f"missing {config}")
    print(f"Opening {config}. Press Play in sumo-gui. A1 is not attached.")
    return subprocess.call([require_gui(), "-c", str(config)], cwd=config.parent)


def watch_a1() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    from coflow5.evidence.max_pressure_artifacts import EVALUATION_SEED, _scenario_hash
    from coflow5.sumo_adapter.max_pressure_runner import run_native_max_pressure_scenario

    config = SCENES["max-pressure"]
    print("Starting sumo-gui with TraCI A1. Press Play if the window waits.")
    result = run_native_max_pressure_scenario(
        sumo_binary=require_gui(),
        config=config,
        run_id=f"watch-a1-{uuid.uuid4()}",
        scenario_hash=_scenario_hash(ROOT),
        seed=EVALUATION_SEED,
    )
    print(f"steps={result.simulation_steps}")
    print(f"accepted_commands={result.accepted_command_count}")
    print("This watch run did not rewrite harness/work/05-max-pressure/artifacts.")
    return 0


def main() -> int:
    prepare_env()
    parser = argparse.ArgumentParser(description="Watch SUMO scenes or live A1.")
    parser.add_argument("scene", choices=(*SCENES, "a1"))
    args = parser.parse_args()
    if args.scene == "a1":
        return watch_a1()
    return watch_scene(args.scene)


if __name__ == "__main__":
    raise SystemExit(main())
