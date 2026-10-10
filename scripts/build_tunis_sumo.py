"""Build the runnable Tunis showcase SUMO scenario from the supplied PBF."""

from __future__ import annotations

import argparse
import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PBF = Path(r"C:\Users\dell\Downloads\ai agent prototype\tunisia-261009.osm.pbf")
SCENARIO = ROOT / "scenarios" / "tunis-showcase"
BBOX = (10.170, 36.790, 10.190, 36.805)
JUNCTION_IDS = (
    "5294059357",
    "287386655",
    "287837812",
    "287863982",
    "387151856",
    "517939913",
)


def wsl_path(path: Path) -> str:
    drive = path.drive.rstrip(":").lower()
    return f"/mnt/{drive}{path.as_posix()[2:]}"


def run(command: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


def write_gui_overlay(net: Path) -> tuple[Path, Path]:
    root = ET.parse(net).getroot()
    locations = {
        junction.get("id"): (junction.get("x"), junction.get("y"))
        for junction in root.findall("junction")
        if junction.get("id") in JUNCTION_IDS
    }
    missing = [junction_id for junction_id in JUNCTION_IDS if junction_id not in locations]
    if missing:
        raise RuntimeError(f"selected Tunis junctions missing from SUMO network: {missing}")
    poi = SCENARIO / "tunis-junctions.add.xml"
    with poi.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write("<additional>\n")
        for index, junction_id in enumerate(JUNCTION_IDS, start=1):
            x, y = locations[junction_id]
            stream.write(
                f'  <poi id="tunis-j{index}" x="{x}" y="{y}" '
                f'type="selected-junction" color="1,0.2,0.1" layer="100" '
                f'lonLat="false" name="Tunis J{index} ({junction_id})"/>\n'
            )
        stream.write("</additional>\n")
    center_x = sum(float(locations[junction_id][0]) for junction_id in JUNCTION_IDS) / 6
    center_y = sum(float(locations[junction_id][1]) for junction_id in JUNCTION_IDS) / 6
    settings = SCENARIO / "tunis.settings.xml"
    settings.write_text(
        f"""<viewsettings>
  <viewport x="{center_x:.2f}" y="{center_y:.2f}" zoom="0.8"/>
  <delay value="100"/>
  <scheme name="real world"/>
</viewsettings>
""",
        encoding="utf-8",
    )
    return poi, settings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pbf", type=Path, default=PBF)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if not args.pbf.is_file():
        raise SystemExit(f"PBF not found: {args.pbf}")
    sumo_home = Path(os.environ.get("SUMO_HOME", r"C:\Program Files (x86)\Eclipse\Sumo"))
    netconvert = sumo_home / "bin" / "netconvert.exe"
    random_trips = sumo_home / "tools" / "randomTrips.py"
    if not netconvert.is_file() or not random_trips.is_file():
        raise SystemExit("SUMO_HOME must point to an installation with netconvert and randomTrips.py")
    SCENARIO.mkdir(parents=True, exist_ok=True)
    osm = SCENARIO / "tunis.osm.xml"
    net = SCENARIO / "tunis.net.xml"
    routes = SCENARIO / "tunis.rou.xml"
    if args.force or not osm.is_file():
        run([
            "wsl.exe", "python3", wsl_path(ROOT / "scripts" / "clip_tunis_osm.py"),
            "--input", wsl_path(args.pbf), "--output", wsl_path(osm),
            "--bbox", *(str(value) for value in BBOX),
        ])
    if args.force or not net.is_file():
        run([
            str(netconvert), "--osm-files", str(osm), "--proj.utm",
            "--ramps.guess", "--tls.guess",
            "--no-turnarounds", "--output-file", str(net),
        ])
    if args.force or not routes.is_file():
        run([
            "py", "-3.11", str(random_trips), "-n", str(net),
            "-r", str(routes), "--seed", "20261010", "--begin", "0",
            "--end", "600", "--period", "3", "--min-distance", "100",
            "--validate", "--remove-loops",
        ])
    poi, settings = write_gui_overlay(net)
    config = SCENARIO / "tunis.sumocfg"
    config.write_text(
        f"""<configuration>
  <input>
    <net-file value="tunis.net.xml"/>
    <route-files value="tunis.rou.xml"/>
    <additional-files value="{poi.name}"/>
    <gui-settings-file value="{settings.name}"/>
  </input>
  <time><begin value="0"/><end value="600"/><step-length value="1"/></time>
  <processing><time-to-teleport value="-1"/></processing>
  <report><no-step-log value="true"/></report>
</configuration>
""",
        encoding="utf-8",
    )
    print(f"Built Tunis SUMO scenario: {config}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
