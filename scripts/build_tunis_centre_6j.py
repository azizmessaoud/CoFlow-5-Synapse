"""Build the six-junction Tunis centre-ville SUMO network from committed OSM.

Input is the checked-in ``scenarios/tunis-showcase/tunis.osm.xml`` OSM extract.
The original country PBF is not in this checkout, so its date/checksum cannot
be independently verified here; the clipped XML is hash-recorded on each build. This script clips
it to the centre-ville box around the six junctions in
``scenarios/tunis-centre-6j/selection.json`` and signalises exactly
those six nodes, renamed J1..J6 (node and light ids). Every other OSM ``traffic_signals`` tag is removed
so the control hierarchy has one master per selected junction and nothing
else writes a light. Road demand is synthetic (randomTrips, fixed seed).

Evidence-backed lane counts and speeds from ``lane_overrides.json`` are written
onto a temporary copy of the clip before ``netconvert``; the committed
``tunis6j.osm.xml`` stays a plain OSM clip (see ``scripts/lane_overrides.py``).

    python scripts/build_tunis_centre_6j.py            # needs SUMO_HOME or the eclipse-sumo wheel
    python scripts/build_tunis_centre_6j.py --require-verified-lanes   # release build

Outputs go to ``scenarios/tunis-centre-6j/``.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import heapq
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_overrides  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SOURCE_OSM = ROOT / "scenarios" / "tunis-showcase" / "tunis.osm.xml"
JUNCTIONS = ROOT / "scenarios" / "tunis-centre-6j" / "selection.json"
SCENARIO = ROOT / "scenarios" / "tunis-centre-6j"
NETWORK_CONFIG = ROOT / "config" / "networks" / "tunis6j.yaml"
PREFIX = "tunis6j"

# left, bottom, right, top. The six junctions span lon 10.1785-10.1880 and
# lat 36.7947-36.8032; the box keeps about 250 m of approach road around them.
BBOX = (10.1755, 36.7925, 10.1910, 36.8055)
SEED = 20261016
END = 3600
YELLOW = 3
NEIGHBOUR_CUTOFF = 800.0  # m of road; a farther light is not a direct neighbour

NETCONVERT_OPTS = [
    "--proj.utm",
    "--geometry.remove",
    "--junctions.join",
    "--sidewalks.guess",
    "--crossings.guess",
    "--keep-edges.by-vclass", "passenger,pedestrian,bus",
    "--remove-edges.isolated",
    "--no-turnarounds", "true",
    "--tls.guess", "false",
    "--tls.yellow.time", str(YELLOW),
    "--output.street-names",
    "--output.original-names",
    "--osm.annotate-defaults",
]


def sumo_home() -> Path:
    env = os.environ.get("SUMO_HOME")
    if env:
        return Path(env)
    try:
        import sumo  # eclipse-sumo wheel
    except ImportError as error:
        raise SystemExit("set SUMO_HOME or pip install eclipse-sumo==1.27.1") from error
    return Path(sumo.SUMO_HOME)


def tool(home: Path, name: str) -> str:
    for candidate in (home / "bin" / f"{name}.exe", home / "bin" / name):
        if candidate.is_file():
            return str(candidate)
    raise SystemExit(f"{name} not found under {home / 'bin'}")


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, check=True)


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def lane_tag_coverage(source: Path, junction_node_ids: set[str]) -> dict:
    """Count OSM road ways with lane counts; uncovered values are importer defaults, not observations."""
    root = ET.parse(source).getroot()
    lane_keys = {"lanes", "lanes:forward", "lanes:backward", "lanes:both_ways"}
    counts: dict[str, dict[str, int]] = {}
    incident_ways = incident_tagged = 0
    for way in root.findall("way"):
        tags = {tag.get("k"): tag.get("v") for tag in way.findall("tag")}
        highway = tags.get("highway")
        if not highway:
            continue
        has_lane_tag = any(tags.get(key) for key in lane_keys)
        if any(node.get("ref") in junction_node_ids for node in way.findall("nd")):
            incident_ways += 1
            incident_tagged += int(has_lane_tag)
        row = counts.setdefault(highway, {"ways": 0, "ways_with_lane_count_tags": 0})
        row["ways"] += 1
        if has_lane_tag:
            row["ways_with_lane_count_tags"] += 1
    total = sum(row["ways"] for row in counts.values())
    tagged = sum(row["ways_with_lane_count_tags"] for row in counts.values())
    return {
        "road_ways": total,
        "ways_with_lane_count_tags": tagged,
        "ways_without_lane_count_tags": total - tagged,
        "six_junction_incident_ways": {
            "ways": incident_ways,
            "ways_with_lane_count_tags": incident_tagged,
            "ways_without_lane_count_tags": incident_ways - incident_tagged,
        },
        "by_highway": counts,
        "interpretation": "Explicit OSM lane tags are source data; missing lane counts are inferred by SUMO and are not verified real-world lane counts.",
    }


def validate_selection_coordinates(source: Path, selected: list[dict]) -> float:
    """Fail if a selected OSM node is absent or its stored WGS84 location has drifted."""
    nodes = {node.get("id"): node for node in ET.parse(source).getroot().findall("node")}
    errors = []
    for row in selected:
        node = nodes.get(str(row["node_id"]))
        if node is None:
            raise SystemExit(f"selected OSM junction {row['node_id']} is absent from {source}")
        lat = float(node.get("lat"))
        dlat = (lat - float(row["lat"])) * 111_320
        dlon = (float(node.get("lon")) - float(row["lon"])) * 111_320 * math.cos(math.radians(lat))
        errors.append(math.hypot(dlat, dlon))
    maximum = max(errors, default=0.0)
    if maximum > 0.25:
        raise SystemExit(f"selected junction coordinates drifted by up to {maximum:.2f} m; review selection.json")
    return maximum


def load_selection() -> list[dict]:
    data = json.loads(JUNCTIONS.read_text(encoding="utf-8"))
    selected = data["junctions"]
    if len(selected) != 6:
        raise SystemExit(f"expected 6 junctions, found {len(selected)}")
    return selected


def inside(lon: float, lat: float) -> bool:
    left, bottom, right, top = BBOX
    return left <= lon <= right and bottom <= lat <= top


def clip_osm(source: Path, output: Path, keep_ids: set[str]) -> dict:
    """Cut highway ways at the box edge and drop all OSM signal tags.

    A way that leaves and re-enters the box becomes several ways; the first
    run keeps the OSM way id, later runs get ``<way id><run:02d>``.
    """
    root = ET.parse(source).getroot()
    nodes = {node.get("id"): node for node in root.findall("node")}

    def node_inside(ref: str) -> bool:
        node = nodes.get(ref)
        return node is not None and inside(float(node.get("lon")), float(node.get("lat")))

    kept_ways = []
    for way in root.findall("way"):
        runs, current = [], []
        for nd in way.findall("nd"):
            if node_inside(nd.get("ref")):
                current.append(nd.get("ref"))
            elif current:
                runs.append(current)
                current = []
        if current:
            runs.append(current)
        tags = way.findall("tag")
        for index, refs in enumerate(run for run in runs if len(run) >= 2):
            way_id = way.get("id") if index == 0 else f"{way.get('id')}{index:02d}"
            copy = ET.Element("way", id=way_id)
            for ref in refs:
                ET.SubElement(copy, "nd", ref=ref)
            for tag in tags:
                ET.SubElement(copy, "tag", k=tag.get("k"), v=tag.get("v"))
            kept_ways.append(copy)
    used = {nd.get("ref") for way in kept_ways for nd in way.findall("nd")}
    missing = keep_ids - used
    if missing:
        raise SystemExit(f"selected junctions not on any clipped way: {sorted(missing)}")
    removed_signals = []
    out = ET.Element("osm", version="0.6", generator="coflow5-tunis-centre-6j")
    left, bottom, right, top = BBOX
    ET.SubElement(
        out, "bounds", minlat=str(bottom), minlon=str(left), maxlat=str(top), maxlon=str(right)
    )
    for node_id in sorted(used, key=int):
        node = nodes[node_id]
        copy = ET.SubElement(out, "node", id=node_id, lat=node.get("lat"), lon=node.get("lon"))
        for tag in node.findall("tag"):
            key, value = tag.get("k"), tag.get("v")
            if value == "traffic_signals" and key in {"highway", "crossing"}:
                removed_signals.append(node_id)
                continue
            if key.startswith("traffic_signals"):
                continue
            ET.SubElement(copy, "tag", k=key, v=value)
    for way in sorted(kept_ways, key=lambda item: int(item.get("id"))):
        out.append(way)
    ET.indent(out)
    output.write_bytes(ET.tostring(out, encoding="UTF-8", xml_declaration=True) + b"\n")
    return {
        "ways": len(kept_ways),
        "nodes": len(used),
        "osm_signals_removed": sorted(set(removed_signals), key=int),
    }


def way_names(source: Path) -> dict[str, list[str]]:
    """French street names (fallback: default name) meeting at each node."""
    root = ET.parse(source).getroot()
    names: dict[str, list[str]] = {}
    for way in root.findall("way"):
        tags = {tag.get("k"): tag.get("v") for tag in way.findall("tag")}
        name = tags.get("name:fr") or tags.get("name")
        if not name:
            continue
        for nd in way.findall("nd"):
            bucket = names.setdefault(nd.get("ref"), [])
            if name not in bucket:
                bucket.append(name)
    return names


def neighbours(net: Path, tls_ids: list[str], cutoff: float = NEIGHBOUR_CUTOFF) -> dict[str, list[str]]:
    """Signalised junctions first reached downstream within ``cutoff`` metres of road."""
    root = ET.parse(net).getroot()
    out_edges: dict[str, list[tuple[str, float]]] = {}
    for edge in root.findall("edge"):
        if edge.get("function"):
            continue
        length = float(edge.find("lane").get("length"))
        out_edges.setdefault(edge.get("from"), []).append((edge.get("to"), length))
    targets = set(tls_ids)
    result = {}
    for start in tls_ids:
        found, best, heap = set(), {start: 0.0}, [(0.0, start)]
        while heap:
            dist, node = heapq.heappop(heap)
            if dist > best.get(node, float("inf")):
                continue
            for nxt, length in out_edges.get(node, []):
                total = dist + length
                if total > cutoff or total >= best.get(nxt, float("inf")):
                    continue
                best[nxt] = total
                if nxt in targets:
                    found.add(nxt)
                elif nxt != start:
                    heapq.heappush(heap, (total, nxt))
        result[start] = sorted(found - {start})
    return result


def junction_spec(net: Path, selected: list[dict], names: dict[str, list[str]]) -> dict:
    root = ET.parse(net).getroot()
    junctions = {j.get("id"): j for j in root.findall("junction")}
    tls = {t.get("id"): t for t in root.findall("tlLogic")}
    tls_ids = [f"J{index}" for index in range(1, len(selected) + 1)]
    if sorted(tls) != sorted(tls_ids):
        raise SystemExit(f"expected exactly the six J1..J6 lights, found {sorted(tls)}")
    reach = neighbours(net, tls_ids)
    rows = []
    for tls_id, node in zip(tls_ids, selected):
        node_id = str(node["node_id"])
        junction = junctions[tls_id]
        phases = [phase.get("state") for phase in tls[tls_id].findall("phase")]
        rows.append(
            {
                "id": tls_id,
                "osm_node_id": node["node_id"],
                "tls_id": tls_id,
                "name": junction_name(tls_id, names.get(node_id, [])),
                "lon": node["lon"],
                "lat": node["lat"],
                "x": float(junction.get("x")),
                "y": float(junction.get("y")),
                "streets": names.get(node_id, []),
                "osm_highways": sorted(set(node["way_highways"])),
                "selection_reasons": node["reasons"],
                "incoming_lanes": sorted(set(junction.get("incLanes", "").split())),
                "signal_links": len(phases[0]) if phases else 0,
                "phases": phases,
                "downstream_neighbours": reach[tls_id],
            }
        )
    return {"junctions": rows}


def junction_name(tls_id: str, streets: list[str]) -> str:
    """Street names only: traffix's narrator already writes "J1 (<name>)"."""
    return " x ".join(streets[:2]) if streets else tls_id


def rename_junctions(netconvert: str, raw: Path, work: Path, labels: dict[str, str],
                     names: dict[str, str]) -> Path:
    """Plain-XML round trip that renames the six OSM nodes (and their lights) to J1..J6.

    traffix3 treats a light's id and its node's id as the same thing, so both
    are renamed together. Each node also gets a ``name`` param for the GUI,
    the decision log narrator and the dashboard.
    """
    run([netconvert, "--sumo-net-file", str(raw), "--plain-output-prefix", str(work / "plain")])
    pattern = re.compile(r'(?<=["\s])(' + "|".join(labels) + r')(?=["\s])')
    for suffix in ("nod", "edg", "con", "tll"):
        path = work / f"plain.{suffix}.xml"
        text = pattern.sub(lambda match: labels[match.group(1)], path.read_text(encoding="utf-8"))
        if suffix == "nod":
            for label, name in names.items():
                text = re.sub(
                    rf'(<node id="{label}"[^>]*?)/>',
                    lambda match: f'{match.group(1)}>\n        <param key="name" '
                                  f'value="{escape(name, {chr(34): "&quot;"})}"/>\n    </node>',
                    text,
                    count=1,
                )
        path.write_text(text, encoding="utf-8")
    return work / "plain.netccfg"


def write_bus_stops(home: Path, net: Path, spec: dict) -> None:
    """Community-published TRANSTU-attributed stop/line geometry and which stops sit before each light."""
    sys.path.insert(0, str(home / "tools"))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from import_transtu_lines import build

    _, stops = build(str(net), fetch=False)
    for row in spec["junctions"]:
        row["bus_stops"] = sorted(k for k, st in stops.items() if st.get("junction") == row["tls_id"])


def write_overlay(spec: dict) -> None:
    lines = ["<additional>"]
    for row in spec["junctions"]:
        title = " / ".join(row["streets"][:2]) or row["tls_id"]
        lines.append(
            f'  <poi id="{row["id"]}" x="{row["x"]:.2f}" y="{row["y"]:.2f}" '
            f'type="coflow-junction" color="1,0.2,0.1" layer="100" '
            f'name="{escape(row["id"] + " " + title, {chr(34): "&quot;"})}"/>'
        )
    lines.append("</additional>")
    (SCENARIO / f"{PREFIX}.poi.add.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    xs = [row["x"] for row in spec["junctions"]]
    ys = [row["y"] for row in spec["junctions"]]
    settings = SCENARIO / f"{PREFIX}.settings.xml"
    settings.write_text(
        f"""<viewsettings>
  <viewport x="{(min(xs) + max(xs)) / 2:.2f}" y="{(min(ys) + max(ys)) / 2:.2f}" zoom="130"/>
  <delay value="50"/>
  <scheme name="real world"/>
</viewsettings>
""",
        encoding="utf-8",
    )
    basemap = SCENARIO / f"{PREFIX}.basemap.json"
    if basemap.is_file():                   # keep the street-map decal from scripts/build_basemap.py
        from build_basemap import add_decal
        add_decal(str(SCENARIO / f"{PREFIX}.net.xml"), json.loads(basemap.read_text(encoding="utf-8")))


def write_configs() -> None:
    for variant, net in (("", f"{PREFIX}.net.xml"), ("_actuated", f"{PREFIX}_actuated.net.xml")):
        (SCENARIO / f"{PREFIX}{variant}.sumocfg").write_text(
            f"""<configuration>
  <input>
    <net-file value="{net}"/>
    <route-files value="{PREFIX}.rou.xml,{PREFIX}.ped.rou.xml"/>
    <additional-files value="{PREFIX}.stops.xml,{PREFIX}.poi.add.xml"/>
    <gui-settings-file value="{PREFIX}.settings.xml"/>
  </input>
  <time><begin value="0"/><end value="{END}"/><step-length value="1"/></time>
  <processing>
    <time-to-teleport value="300"/>
    <ignore-route-errors value="true"/>
  </processing>
  <report><no-step-log value="true"/></report>
</configuration>
""",
            encoding="utf-8",
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--source-osm", type=Path, default=SOURCE_OSM)
    parser.add_argument("--source-pbf", type=Path, help="original country PBF used to create --source-osm")
    parser.add_argument("--source-pbf-data-as-of", help="Geofabrik's OSM data timestamp, in ISO 8601 UTC")
    parser.add_argument("--require-verified-lanes", action="store_true",
                        help="release check: refuse to build while any J1..J6 incident way lacks lane evidence")
    args = parser.parse_args()
    if args.source_pbf and not args.source_pbf.is_file():
        raise SystemExit(f"source PBF not found: {args.source_pbf}")
    home = sumo_home()
    netconvert = tool(home, "netconvert")
    random_trips = str(home / "tools" / "randomTrips.py")
    selected = load_selection()
    node_ids = [str(node["node_id"]) for node in selected]
    SCENARIO.mkdir(parents=True, exist_ok=True)

    osm = SCENARIO / f"{PREFIX}.osm.xml"
    clip = clip_osm(args.source_osm, osm, set(node_ids))
    coordinate_error = validate_selection_coordinates(osm, selected)
    lane_coverage = lane_tag_coverage(osm, set(node_ids))
    overrides = lane_overrides.load(lane_overrides.OVERRIDES)
    problems = lane_overrides.validate(overrides, osm, {node_id: f"J{i}" for i, node_id in enumerate(node_ids, start=1)})
    if problems:
        raise SystemExit("lane_overrides.json is invalid:\n  " + "\n  ".join(problems))
    override_coverage = lane_overrides.coverage(overrides)
    if args.require_verified_lanes and override_coverage["verified"]["count"] != len(overrides["ways"]):
        raise SystemExit(f"--require-verified-lanes: {len(overrides['ways']) - override_coverage['verified']['count']} "
                         "junction-incident ways have no lane evidence; see lane_overrides.json")
    print(f"clipped ways={clip['ways']} nodes={clip['nodes']} "
          f"osm_signals_removed={len(clip['osm_signals_removed'])}")

    net = SCENARIO / f"{PREFIX}.net.xml"
    actuated = SCENARIO / f"{PREFIX}_actuated.net.xml"
    names = way_names(osm)
    labels = {node_id: f"J{index}" for index, node_id in enumerate(node_ids, start=1)}
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        raw = work / "raw.net.xml"
        patched = work / "tunis6j.overridden.osm.xml"
        applied = lane_overrides.apply(overrides, osm, patched)
        extra = ["--osm.turn-lanes", "true"] if applied["needs_osm_turn_lanes"] else []
        run([
            netconvert, "--osm-files", str(patched), *NETCONVERT_OPTS, *extra,
            "--junctions.join-exclude", ",".join(node_ids),
            "--tls.set", ",".join(node_ids),
            "--tls.default-type", "static", "--output-file", str(raw),
        ])
        config = rename_junctions(
            netconvert, raw, work, labels,
            {label: junction_name(label, names.get(node_id, [])) for node_id, label in labels.items()},
        )
        run([netconvert, "-c", str(config), "--output-file", str(net)])
    run([
        netconvert, "--sumo-net-file", str(net), "--tls.rebuild",
        "--tls.default-type", "actuated", "--output-file", str(actuated),
    ])

    py = sys.executable
    run([
        py, random_trips, "-n", str(net), "-r", str(SCENARIO / f"{PREFIX}.rou.xml"),
        "-o", str(SCENARIO / f"{PREFIX}.trips.xml"),
        "--seed", str(SEED), "--begin", "0", "--end", str(END), "--period", "1.2",
        "--fringe-factor", "10", "--min-distance", "300", "--validate", "--remove-loops",
        "--prefix", "veh", "--trip-attributes", 'departLane="best" departSpeed="max"',
    ])
    run([
        py, random_trips, "-n", str(net), "-r", str(SCENARIO / f"{PREFIX}.ped.rou.xml"),
        "-o", str(SCENARIO / f"{PREFIX}.ped.trips.xml"),
        "--seed", str(SEED + 1), "--begin", "0", "--end", str(END), "--period", "4",
        "--pedestrians", "--max-distance", "800", "--prefix", "ped",
    ])
    for leftover in SCENARIO.glob("*.trips.xml"):
        leftover.unlink()
    for leftover in SCENARIO.glob("*.rou.alt.xml"):
        leftover.unlink()

    for built in (net, actuated):
        mismatch = lane_overrides.check_net(overrides, built)
        if mismatch:
            raise SystemExit(f"{built.name} does not carry the override values:\n  " + "\n  ".join(mismatch))

    spec = junction_spec(net, selected, names)
    write_bus_stops(home, net, spec)
    write_overlay(spec)
    write_configs()
    # The PBF is not in the checkout; without --source-pbf its identity comes from the
    # committed selection.json (recorded when the PBF was downloaded), labelled as such.
    pbf = json.loads(JUNCTIONS.read_text(encoding="utf-8"))["aoi"]["source"]
    manifest = {
        "id": "tunis-centre-6j",
        "status": "showcase_only",
        "aoi": {"name": "Tunis centre-ville, six selected junctions",
                "bbox": list(BBOX), "bbox_order": "left,bottom,right,top"},
        "sources": {
            "osm": {
                "path": str(args.source_osm.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(args.source_osm),
                "identity": "OpenStreetMap contributor data, clipped from the Geofabrik Tunisia extract",
                "source_url": "https://download.geofabrik.de/africa/tunisia.html",
                "source_pbf_filename": args.source_pbf.name if args.source_pbf else pbf["filename"],
                "source_pbf_sha256": sha256(args.source_pbf) if args.source_pbf else pbf["sha256"],
                "source_pbf_data_as_of": args.source_pbf_data_as_of or pbf["data_as_of_utc"],
                "source_pbf_retrieved_at_utc": (
                    datetime.fromtimestamp(args.source_pbf.stat().st_mtime, timezone.utc).isoformat()
                    if args.source_pbf else pbf["downloaded_at_utc"]
                ),
                "source_pbf_identity_from": (
                    "hashed in this build" if args.source_pbf
                    else "selection.json aoi.source; PBF not present, not re-hashed in this build"
                ),
            },
            "junction_selection": {
                "path": str(JUNCTIONS.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(JUNCTIONS),
            },
            "lane_overrides": {
                "path": str(lane_overrides.OVERRIDES.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(lane_overrides.OVERRIDES),
                "schema": overrides["schema"],
                "applied_before_netconvert": "to a temporary copy of tunis6j.osm.xml; the committed clip is unmodified OSM",
                "coverage": override_coverage,
                "lanes_applied_to_ways": applied["lanes_applied_to_ways"],
                "speeds_applied": applied["speeds_applied"],
                "recorded_not_applied": applied["recorded_not_applied"],
                "legal_sources": [{key: src[key] for key in ("id", "url", "retrieved_utc", "limits_of_use")}
                                  for src in overrides["legal_sources"]],
            },
        },
        "network": {
            "signalised_junctions": [row["tls_id"] for row in spec["junctions"]],
            "osm_signals_removed": clip["osm_signals_removed"],
            "signal_rule": "only J1..J6 carry traffic lights; other OSM signals are dropped "
                           "so each light has exactly one master",
            "netconvert_options": NETCONVERT_OPTS,
            "sumo_version": "1.27.1",
            "lane_tag_coverage": lane_coverage,
        },
        "validation": {
            "selected_junctions_checked": len(selected),
            "selected_junction_coordinate_max_error_m": round(coordinate_error, 4),
            "coordinate_tolerance_m": 0.25,
            "lane_count_status": (
                f"{override_coverage['verified']['count']} of {len(overrides['ways'])} junction-incident ways "
                f"lane-verified with evidence; {override_coverage['osm_tagged']['count']} use uncorroborated OSM "
                f"lane tags; {override_coverage['unverified']['count']} use SUMO importer defaults, which are "
                "not real-world lane counts"
            ),
            "speed_status": "junction-incident ways without an OSM maxspeed use Tunisia's 50 km/h urban legal "
                            "default (lane_overrides.json legal_sources); posted signs and road-specific "
                            "30/70 km/h decisions are not verified; all other roads keep SUMO type defaults",
        },
        "road_demand": f"synthetic: randomTrips seed={SEED}, period=1.2 s, fringe-factor=10, "
                       f"{END} s; pedestrians seed={SEED + 1}, period=4 s",
        "claim_boundary": "showcase only; no deployment validation, no measured air quality, "
                          "no lives saved",
        "junctions": spec["junctions"],
    }
    (SCENARIO / "junctions.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"built {SCENARIO.relative_to(ROOT)} with "
          f"{', '.join(row['id'] + '=' + row['tls_id'] for row in spec['junctions'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
