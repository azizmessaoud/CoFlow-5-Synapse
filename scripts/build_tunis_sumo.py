"""Build the wider Tunis SUMO showcase from its committed OSM extract.

By default, use the checked-in ``scenarios/tunis-showcase/tunis.osm.xml`` so
network builds are reproducible and do not depend on a machine-local PBF path.
To refresh roads, first clip a Geofabrik Tunisia PBF with ``clip_tunis_osm.py``
(or pass ``--pbf`` when pyosmium is installed), then run this builder.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCENARIO = ROOT / "scenarios" / "tunis-showcase"
OSM = SCENARIO / "tunis.osm.xml"
# left, bottom, right, top (WGS84)
BBOX = (10.127879, 36.787714, 10.233358, 36.820741)
JUNCTION_IDS = ("5294059357", "287386655", "287837812", "287863982", "387151856", "517939913")
def sumo_paths() -> tuple[str, str]:
    home = os.environ.get("SUMO_HOME")
    if home:
        root = Path(home)
        netconvert = next((p for p in (root / "bin/netconvert", root / "bin/netconvert.exe") if p.is_file()), None)
        random_trips = root / "tools/randomTrips.py"
        if netconvert and random_trips.is_file():
            return str(netconvert), str(random_trips)
    try:
        import sumo
    except ImportError as error:
        raise SystemExit("SUMO was not found. Set SUMO_HOME or install eclipse-sumo==1.27.1") from error
    root = Path(sumo.SUMO_HOME)
    netconvert = next((p for p in (root / "bin/netconvert", root / "bin/netconvert.exe") if p.is_file()), None)
    random_trips = root / "tools/randomTrips.py"
    if not netconvert or not random_trips.is_file():
        raise SystemExit(f"SUMO tools are incomplete under {root}")
    return str(netconvert), str(random_trips)


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def write_provenance(
    source_osm: Path,
    source_pbf: Path | None = None,
    source_pbf_data_as_of: str | None = None,
) -> Path:
    """Record exactly which OSM snapshot was imported and where it came from."""
    manifest = {
        "scenario": "tunis-showcase",
        "status": "showcase_only",
        "captured_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "aoi_bbox_wgs84": list(BBOX),
        "aoi_bbox_order": "left,bottom,right,top",
        "roads": {
            "source": "OpenStreetMap contributors via Geofabrik Tunisia extract",
            "source_url": "https://download.geofabrik.de/africa/tunisia.html",
            "license": "Open Database License (ODbL)",
            "imported_osm_xml": source_osm.name,
            "imported_osm_xml_sha256": sha256(source_osm),
            "original_pbf": source_pbf.name if source_pbf else None,
            "original_pbf_sha256": sha256(source_pbf) if source_pbf else None,
            "original_pbf_data_as_of_utc": source_pbf_data_as_of,
            "source_limit": None if source_pbf else "Original country PBF not supplied; only the clipped OSM XML hash can be verified.",
            "geometry_and_lane_tags": "OSM road geometry and available lane attributes imported by SUMO netconvert; inferred attributes are not field-survey evidence.",
        },
        "traffic_demand": "synthetic randomTrips; fixed seed 20261010; not observed Tunis traffic",
        "claim_boundary": "showcase only; verify changes, closures, lane markings and transit operations locally before operational use",
    }
    target = SCENARIO / "tunis.source.json"
    target.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return target


def write_gui_overlay(net: Path) -> tuple[Path, Path]:
    root = ET.parse(net).getroot()
    locations = {j.get("id"): (j.get("x"), j.get("y")) for j in root.findall("junction")
                 if j.get("id") in JUNCTION_IDS}
    missing = [jid for jid in JUNCTION_IDS if jid not in locations]
    if missing:
        raise RuntimeError(f"selected Tunis junctions missing from SUMO network: {missing}")
    poi = SCENARIO / "tunis-junctions.add.xml"
    with poi.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write("<additional>\n")
        for index, jid in enumerate(JUNCTION_IDS, 1):
            x, y = locations[jid]
            stream.write(f'  <poi id="tunis-j{index}" x="{x}" y="{y}" type="selected-junction" '
                         f'color="1,0.2,0.1" layer="100" lonLat="false" name="Tunis J{index} ({jid})"/>\n')
        stream.write("</additional>\n")
    junctions = root.findall("junction")
    cx = (min(float(j.get("x", 0)) for j in junctions) + max(float(j.get("x", 0)) for j in junctions)) / 2
    cy = (min(float(j.get("y", 0)) for j in junctions) + max(float(j.get("y", 0)) for j in junctions)) / 2
    settings = SCENARIO / "tunis.settings.xml"
    settings.write_text(f'<viewsettings>\n  <viewport x="{cx:.2f}" y="{cy:.2f}" zoom="100"/>\n'
                        '  <delay value="100"/>\n  <scheme name="real world"/>\n</viewsettings>\n', encoding="utf-8")
    return poi, settings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-osm", type=Path, default=OSM, help="clipped OSM XML (default: committed Tunis extract)")
    parser.add_argument("--pbf", type=Path, help="optional source PBF; clip it to the showcase bounds before importing")
    parser.add_argument("--pbf-data-as-of", help="Geofabrik OSM data timestamp, in ISO 8601 UTC")
    parser.add_argument("--force", action="store_true", help="rebuild network and synthetic routes")
    args = parser.parse_args()
    source = args.source_osm
    if args.pbf:
        source = OSM
        try:
            import osmium  # noqa: F401
        except ImportError as error:
            raise SystemExit("--pbf requires pyosmium; install it with: python -m pip install osmium") from error
        run([sys.executable, str(ROOT / "scripts/clip_tunis_osm.py"), "--input", str(args.pbf),
             "--output", str(OSM), "--bbox", *(str(value) for value in BBOX)])
    if not source.is_file():
        raise SystemExit(f"OSM XML not found: {source}. Use --source-osm or provide --pbf.")
    netconvert, random_trips = sumo_paths()
    SCENARIO.mkdir(parents=True, exist_ok=True)
    net = SCENARIO / "tunis.net.xml"
    routes = SCENARIO / "tunis.rou.xml"
    if args.force or not net.is_file():
        run([netconvert, "--osm-files", str(source), "--proj.utm", "--ramps.guess", "--tls.guess",
             "--osm.annotate-defaults",
             "--no-turnarounds", "true", "--output-file", str(net)])
    if args.force or not routes.is_file():
        trips = SCENARIO / "tunis.trips.xml"
        run([sys.executable, random_trips, "-n", str(net), "-r", str(routes), "-o", str(trips), "--seed", "20261010",
             "--begin", "0", "--end", "600", "--period", "3", "--min-distance", "100",
             "--validate", "--remove-loops"])
        trips.unlink(missing_ok=True)
    poi, settings = write_gui_overlay(net)
    provenance = write_provenance(source, args.pbf, args.pbf_data_as_of)
    config = SCENARIO / "tunis.sumocfg"
    config.write_text(f'<configuration>\n  <input>\n    <net-file value="{net.name}"/>\n'
                      f'    <route-files value="{routes.name}"/>\n    <additional-files value="{poi.name}"/>\n'
                      f'    <gui-settings-file value="{settings.name}"/>\n  </input>\n'
                      '  <time><begin value="0"/><end value="600"/><step-length value="1"/></time>\n'
                      '  <processing><time-to-teleport value="-1"/></processing>\n'
                      '  <report><no-step-log value="true"/></report>\n</configuration>\n', encoding="utf-8")
    print(f"Built Tunis SUMO scenario: {config}")
    print(f"Data provenance: {provenance}")
    print("Road geometry and tagged attributes are from OpenStreetMap; traffic demand is synthetic.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
