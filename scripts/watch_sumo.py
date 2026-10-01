"""Open SUMO GUI scenes, or attach live A1 through the existing runner."""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path
from statistics import fmean
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMO_HOME = Path(r"C:\Program Files (x86)\Eclipse\Sumo")
SCENES = {
    "smoke": ROOT / "scenarios" / "smoke" / "smoke.sumocfg",
    "safety": ROOT / "scenarios" / "safety-mask" / "safety.sumocfg",
    "baselines": ROOT / "scenarios" / "baselines" / "baselines.sumocfg",
    "max-pressure": ROOT / "scenarios" / "max-pressure" / "max-pressure.sumocfg",
    "graph-growth": ROOT / "scenarios" / "graph-growth" / "graph-growth.sumocfg",
    "demo": ROOT / "scenarios" / "watch" / "watch.sumocfg",
}
EVALUATION_REPORT = ROOT / "harness" / "work" / "09-eval-harness" / "artifacts" / "evaluation-report.json"
MAX_PRESSURE_FOLLOWUP_GATE = ROOT / "harness" / "work" / "10b-max-pressure-trip-kpis" / "gate.json"
MAX_PRESSURE_FOLLOWUP_COMPARISON = ROOT / "harness" / "work" / "10b-max-pressure-trip-kpis" / "artifacts" / "matched-comparison.json"


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


def _number(value: str | None) -> float | None:
    try:
        parsed = float(value) if value is not None else None
    except (TypeError, ValueError):
        return None
    return parsed if parsed is not None and math.isfinite(parsed) else None


def _config_value(config: Path, tag: str) -> str | None:
    element = ET.parse(config).getroot().find(f".//{tag}")
    return element.get("value") if element is not None else None


def planned_trips(route_file: Path) -> int | None:
    if not route_file.is_file():
        return None
    root = ET.parse(route_file).getroot()
    total = len(root.findall("vehicle"))
    for flow in root.findall("flow"):
        number = _number(flow.get("number"))
        if number is not None:
            total += int(number)
            continue
        begin = _number(flow.get("begin"))
        end = _number(flow.get("end"))
        period = _number(flow.get("period"))
        if begin is not None and end is not None and period is not None and period > 0:
            total += max(0, math.ceil((end - begin) / period))
            continue
        vehicles_per_hour = _number(flow.get("vehsPerHour"))
        if begin is not None and end is not None and vehicles_per_hour is not None:
            total += max(0, math.ceil((end - begin) * vehicles_per_hour / 3600))
            continue
        return None
    return total


def tripinfo_summary(tripinfo: Path) -> dict[str, float | int | None]:
    if not tripinfo.is_file():
        return {"completed": None, "mean_waiting": None, "max_waiting": None}
    try:
        rows = ET.parse(tripinfo).getroot().findall("tripinfo")
    except ET.ParseError:
        return {"completed": None, "mean_waiting": None, "max_waiting": None}
    completed = sum(
        1
        for row in rows
        if (arrival := _number(row.get("arrival"))) is not None and arrival >= 0
    )
    waits = [value for row in rows if (value := _number(row.get("waitingTime"))) is not None]
    return {
        "completed": completed,
        "mean_waiting": fmean(waits) if waits else None,
        "max_waiting": max(waits) if waits else None,
    }


def _max_pressure_followup_sentence(
    gate_path: Path, comparison_path: Path,
) -> str | None:
    try:
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        comparison = json.loads(comparison_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    if not (
        gate.get("pass") is True
        and gate.get("openDeltas") == 0
        and gate.get("decidedBy") == "tests-and-files"
        and comparison.get("parity_pass") is True
        and comparison.get("one_seed_only") is True
        and comparison.get("significance_test_performed") is False
        and comparison.get("winner_claim") is None
    ):
        return None
    rows = [
        row for row in comparison.get("controller_rows", [])
        if row.get("controller") == "cooperative-max-pressure"
    ]
    if len(rows) != 1:
        return None
    row = rows[0]
    completed = _number(str(row.get("completed_trips")))
    planned = _number(str(row.get("planned_trips")))
    mean_wait = _number(str(row.get("mean_waiting_time_s")))
    p95_wait = _number(str(row.get("p95_waiting_time_s")))
    if None in (completed, planned, mean_wait, p95_wait):
        return None
    return (
        "Row 10b later measured cooperative Max-Pressure: "
        f"{int(completed)}/{int(planned)} trips completed, "
        f"mean wait {mean_wait:.2f} s, and P95 wait {p95_wait:.2f} s. "
        "This is one seed with a bounded advisory absent from baselines, "
        "so no winner is established."
    )


def evaluation_sentences(
    report_path: Path = EVALUATION_REPORT,
    followup_gate_path: Path = MAX_PRESSURE_FOLLOWUP_GATE,
    followup_comparison_path: Path = MAX_PRESSURE_FOLLOWUP_COMPARISON,
) -> tuple[str, str]:
    missing = "not in this watch run"
    if not report_path.is_file():
        return missing, missing
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return missing, missing
    claims = {claim.get("claim_id"): claim for claim in report.get("claims", [])}
    baseline = claims.get("paired-mixed-baseline-result", {}).get("text") or missing
    followup = _max_pressure_followup_sentence(
        followup_gate_path, followup_comparison_path
    )
    if followup is not None:
        return str(baseline), followup
    max_pressure = claims.get("max-pressure-kpi-gap")
    gap = (
        "Max-Pressure trip KPIs are still missing."
        if max_pressure and max_pressure.get("result") == "not-established"
        else missing
    )
    return str(baseline), gap


def _display(value: float | int | str | None, *, decimals: int = 2) -> str:
    if value is None:
        return "not in this watch run"
    if isinstance(value, float):
        return f"{value:.{decimals}f}"
    return str(value)


def build_watch_report(
    *, config: Path, route_file: Path, tripinfo: Path,
    evaluation_report: Path = EVALUATION_REPORT,
    controller: str = "fixed-time watch scene",
    scene_note: str = "This window is a visual scene. It is not the matched Row 04 or Row 05 evidence.",
) -> str:
    observed = tripinfo_summary(tripinfo)
    baseline_sentence, max_pressure_sentence = evaluation_sentences(evaluation_report)
    begin = _config_value(config, "begin")
    end = _config_value(config, "end")
    seed = _config_value(config, "seed")
    completed = _display(observed["completed"], decimals=0)
    planned = _display(planned_trips(route_file), decimals=0)
    return "\n".join((
        "",
        "=== Watch run page ===",
        "This is the SUMO window. The browser list is a saved record and is not this picture.",
        f"Controller: {controller}",
        f"Seed: {_display(seed)}",
        f"Simulation time: {_display(begin)} to {_display(end)} seconds",
        f"Trips completed / planned: {completed} / {planned}",
        f"Mean waiting seconds: {_display(observed['mean_waiting'])}",
        f"Max waiting seconds: {_display(observed['max_waiting'])}",
        "Safety violations: none recorded in this watch scene",
        "Limitations:",
        "- " + scene_note,
        f"- {baseline_sentence} {max_pressure_sentence}",
        "- No lives saved. No measured air quality. No winner announced.",
    ))


def gui_command(scene: str, tripinfo: Path) -> list[str]:
    config = SCENES[scene]
    return [
        require_gui(), "-c", str(config), "--start", "true", "--delay", "1000",
        "--quit-on-end", "true", "--tripinfo-output", str(tripinfo),
        "--tripinfo-output.write-unfinished", "true",
    ]


def demo_command(tripinfo: Path) -> list[str]:
    return gui_command("demo", tripinfo)


def _route_file(config: Path) -> Path:
    route_value = _config_value(config, "route-files")
    if not route_value:
        raise SystemExit(f"{config.name} has no route file")
    return config.parent / route_value.split(",")[0].strip()


def watch_paced(scene: str, *, intro: str, controller: str, scene_note: str) -> int:
    config = SCENES[scene]
    route_file = _route_file(config)
    if not config.is_file() or not route_file.is_file():
        raise SystemExit(f"{scene} scene is missing")
    print(intro)
    with tempfile.TemporaryDirectory(prefix=f"coflow5-{scene}-") as directory:
        tripinfo = Path(directory) / "tripinfo.xml"
        exit_code = subprocess.call(gui_command(scene, tripinfo), cwd=config.parent)
        page = build_watch_report(
            config=config, route_file=route_file, tripinfo=tripinfo,
            controller=controller, scene_note=scene_note,
        )
        print(page)
    return exit_code


def watch_demo() -> int:
    return watch_paced(
        "demo",
        intro="Watch scene. This is not the Row 05 evidence run.",
        controller="fixed-time watch scene",
        scene_note="This window is a visual scene. It is not the matched Row 04 or Row 05 evidence.",
    )


def watch_graph_growth() -> int:
    return watch_paced(
        "graph-growth",
        intro="Four-junction picture. This is not one of the 80 saved browser rows.",
        controller="fixed-time four-junction scene",
        scene_note="The browser list is the saved comparison. This window is only the road picture.",
    )


def watch_a1() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    from coflow5.evidence.max_pressure_artifacts import EVALUATION_SEED, _scenario_hash
    from coflow5.sumo_adapter.max_pressure_runner import run_native_max_pressure_scenario

    config = SCENES["max-pressure"]
    print("Starting sumo-gui with TraCI A1 at one simulation second per wall-clock second.")
    result = run_native_max_pressure_scenario(
        sumo_binary=require_gui(),
        config=config,
        run_id=f"watch-a1-{uuid.uuid4()}",
        scenario_hash=_scenario_hash(ROOT),
        seed=EVALUATION_SEED,
        sumo_extra_args=("--delay", "1000"),
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
    if args.scene == "demo":
        return watch_demo()
    if args.scene == "graph-growth":
        return watch_graph_growth()
    return watch_scene(args.scene)


if __name__ == "__main__":
    raise SystemExit(main())
