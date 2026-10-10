"""Build the runnable Tunis showcase SUMO scenario from the supplied PBF."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PBF = Path(r"C:\Users\dell\Downloads\ai agent prototype\tunisia-261009.osm.pbf")
SCENARIO = ROOT / "scenarios" / "tunis-showcase"
BBOX = (10.170, 36.790, 10.190, 36.805)


def wsl_path(path: Path) -> str:
    drive = path.drive.rstrip(":").lower()
    return f"/mnt/{drive}{path.as_posix()[2:]}"


def run(command: list[str], *, cwd: Path | None = None) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=cwd, check=True)


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
            "--junctions.join", "--ramps.guess", "--tls.guess",
            "--no-turnarounds", "--output-file", str(net),
        ])
    if args.force or not routes.is_file():
        run([
            "py", "-3.11", str(random_trips), "-n", str(net),
            "-r", str(routes), "--seed", "20261010", "--begin", "0",
            "--end", "600", "--period", "3", "--min-distance", "100",
            "--validate", "--remove-loops",
        ])
    config = SCENARIO / "tunis.sumocfg"
    config.write_text(
        """<configuration>
  <input>
    <net-file value="tunis.net.xml"/>
    <route-files value="tunis.rou.xml"/>
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
