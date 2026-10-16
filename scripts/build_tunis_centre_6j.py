"""Build the six-junction Tunis centre-ville SUMO network from committed OSM.

Input is the already-clipped ``scenarios/tunis-showcase/tunis.osm.xml`` (OSM
highways from the hash-verified Geofabrik PBF, see row 14). This script clips
it to the centre-ville box around the six junctions in
``harness/work/14-tunis-showcase/junctions.json`` and signalises exactly
those six nodes as J1..J6. Every other OSM ``traffic_signals`` tag is removed
so the control hierarchy has one master per selected junction and nothing
else writes a light. Road demand is synthetic (randomTrips, fixed seed).

    python scripts/build_tunis_centre_6j.py            # needs SUMO_HOME or the eclipse-sumo wheel

Outputs go to ``scenarios/tunis-centre-6j/``.
"""

from __future__ import annotations

import argparse
import hashlib
import heapq
import json
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
SOURCE_OSM = ROOT / "scenarios" / "tunis-showcase" / "tunis.osm.xml"
JUNCTIONS = ROOT / "harness" / "work" / "14-tunis-showcase" / "junctions.json"
SCENARIO = ROOT / "scenarios" / "tunis-centre-6j"
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
    "--ramps.guess",
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
    node_to_tls = {}
    for node in selected:
        node_id = str(node["node_id"])
        if node_id in tls:
            node_to_tls[node_id] = node_id
            continue
        owner = next(
            (
                j.get("id")
                for j in junctions.values()
                if j.get("type") == "traffic_light" and node_id in j.get("id", "").split("_")
            ),
            None,
        )
        if owner is None:
            raise SystemExit(f"junction {node_id} is not signalised in {net.name}")
        node_to_tls[node_id] = owner
    tls_ids = [node_to_tls[str(node["node_id"])] for node in selected]
    if sorted(tls) != sorted(tls_ids):
        raise SystemExit(f"expected exactly the six selected TLS, found {sorted(tls)}")
    reach = neighbours(net, tls_ids)
    label = {tls_id: f"J{index}" for index, tls_id in enumerate(tls_ids, start=1)}
    rows = []
    for index, node in enumerate(selected, start=1):
        node_id = str(node["node_id"])
        tls_id = node_to_tls[node_id]
        junction = junctions[tls_id]
        logic = tls[tls_id]
        phases = [phase.get("state") for phase in logic.findall("phase")]
        rows.append(
            {
                "id": f"J{index}",
                "osm_node_id": node["node_id"],
                "tls_id": tls_id,
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
                "downstream_neighbours": sorted(label[n] for n in reach[tls_id]),
            }
        )
    return {"junctions": rows}


def write_bus_stops(net: Path, spec: dict) -> None:
    """One bus stop on the longest bus-legal approach of each junction.

    Same layout as traffix3's ``<network>.stops.xml`` so its demand generator
    and runner pick the stops up next to ``<network>.net.xml``.
    """
    root = ET.parse(net).getroot()
    edges = {edge.get("id"): edge for edge in root.findall("edge") if not edge.get("function")}
    lines = ["<additional>"]
    for row in spec["junctions"]:
        best = None
        for edge in edges.values():
            if edge.get("to") != row["tls_id"]:
                continue
            for lane in edge.findall("lane"):
                allowed = lane.get("allow")
                disallowed = lane.get("disallow", "")
                bus_ok = ("bus" in allowed.split()) if allowed else ("bus" not in disallowed.split())
                length = float(lane.get("length"))
                if bus_ok and length >= 20 and (best is None or length > best[1]):
                    best = (lane.get("id"), length, edge.get("id"))
        if best is None:
            raise SystemExit(f"{row['id']} has no bus-legal approach of at least 20 m")
        lane_id, length, edge_id = best
        # 30 m short of the stop line on long approaches; roundabout arms are short.
        end = length - 30 if length >= 60 else length - 5
        name = f"{row['id']} " + " / ".join(row["streets"][:2])
        lines.append(
            f'  <busStop id="stop_{row["id"]}" lane="{lane_id}" startPos="{max(0.0, end - 20):.1f}" '
            f'endPos="{end:.1f}" name="{escape(name, {chr(34): "&quot;"})}">'
            f'<param key="junction" value="{row["tls_id"]}"/></busStop>'
        )
        row["bus_stop"] = {"id": f"stop_{row['id']}", "edge": edge_id, "lane": lane_id}
    lines.append("</additional>")
    (SCENARIO / f"{PREFIX}.stops.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")


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
    (SCENARIO / f"{PREFIX}.settings.xml").write_text(
        f"""<viewsettings>
  <viewport x="{(min(xs) + max(xs)) / 2:.2f}" y="{(min(ys) + max(ys)) / 2:.2f}" zoom="350"/>
  <delay value="50"/>
  <scheme name="real world"/>
</viewsettings>
""",
        encoding="utf-8",
    )


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
    args = parser.parse_args()
    home = sumo_home()
    netconvert = tool(home, "netconvert")
    random_trips = str(home / "tools" / "randomTrips.py")
    selected = load_selection()
    node_ids = [str(node["node_id"]) for node in selected]
    SCENARIO.mkdir(parents=True, exist_ok=True)

    osm = SCENARIO / f"{PREFIX}.osm.xml"
    clip = clip_osm(args.source_osm, osm, set(node_ids))
    print(f"clipped ways={clip['ways']} nodes={clip['nodes']} "
          f"osm_signals_removed={len(clip['osm_signals_removed'])}")

    common = [
        netconvert, "--osm-files", str(osm), *NETCONVERT_OPTS,
        "--junctions.join-exclude", ",".join(node_ids),
        "--tls.set", ",".join(node_ids),
    ]
    net = SCENARIO / f"{PREFIX}.net.xml"
    actuated = SCENARIO / f"{PREFIX}_actuated.net.xml"
    run([*common, "--tls.default-type", "static", "--output-file", str(net)])
    run([*common, "--tls.default-type", "actuated", "--output-file", str(actuated)])

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

    spec = junction_spec(net, selected, way_names(osm))
    write_bus_stops(net, spec)
    write_overlay(spec)
    write_configs()
    manifest = {
        "id": "tunis-centre-6j",
        "status": "showcase_only",
        "aoi": {"name": "Tunis centre-ville, six selected junctions",
                "bbox": list(BBOX), "bbox_order": "left,bottom,right,top"},
        "sources": {
            "osm": {
                "path": str(args.source_osm.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(args.source_osm),
                "identity": "Geofabrik Tunisia OSM PBF, clipped in row 14 (pbf-source.json)",
            },
            "junction_selection": {
                "path": str(JUNCTIONS.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256(JUNCTIONS),
            },
        },
        "network": {
            "signalised_junctions": [row["tls_id"] for row in spec["junctions"]],
            "osm_signals_removed": clip["osm_signals_removed"],
            "signal_rule": "only J1..J6 carry traffic lights; other OSM signals are dropped "
                           "so each light has exactly one master",
            "netconvert_options": NETCONVERT_OPTS,
            "sumo_version": "1.27.1",
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
