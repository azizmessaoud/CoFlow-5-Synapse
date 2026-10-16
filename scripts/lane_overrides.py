"""Evidence-backed lane and speed overrides for the six-junction Tunis network.

``scenarios/tunis-centre-6j/lane_overrides.json`` lists every OSM way that
touches J1..J6. Each entry says what is known about its lanes and where that
knowledge comes from:

* ``verified``    lane counts observed in the field, in an authoritative plan,
                  or in dated geolocated street-level imagery; every value has
                  evidence and the builder writes it onto the clipped OSM
                  before ``netconvert``.
* ``osm_tagged``  OSM already carries a lane count; it is used as source data
                  but no independent evidence corroborates it yet.
* ``unverified``  no evidence; lane values stay ``null`` and SUMO's importer
                  default is used. Defaults are never copied into this file.

Speeds are separate: ``maxspeed.basis`` is ``osm_tag`` (OSM already has it),
``legal_default`` (the national urban limit, applied because no sign or
municipal decision is known) or ``posted_sign`` (observed). The overrides are
applied to a temporary copy of the clipped OSM, so ``tunis6j.osm.xml`` stays a
faithful OSM clip and project corrections are not passed off as OSM data.

    python scripts/lane_overrides.py            # report coverage
    python scripts/lane_overrides.py --strict   # exit 1 while any incident way is not verified
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OVERRIDES = ROOT / "scenarios" / "tunis-centre-6j" / "lane_overrides.json"
CLIPPED_OSM = ROOT / "scenarios" / "tunis-centre-6j" / "tunis6j.osm.xml"

STATUSES = {"verified", "osm_tagged", "unverified"}
EVIDENCE_TYPES = {"field_survey", "authoritative_plan", "street_level_imagery"}
CONFIDENCE = {"high", "medium", "low"}
SPEED_BASES = {"osm_tag", "legal_default", "posted_sign"}
LANE_FIELDS = ("lanes", "lanes_forward", "lanes_backward")
TURN_FIELDS = ("turn_lanes", "turn_lanes_forward", "turn_lanes_backward")
OSM_KEYS = {
    "lanes": "lanes", "lanes_forward": "lanes:forward", "lanes_backward": "lanes:backward",
    "turn_lanes": "turn:lanes", "turn_lanes_forward": "turn:lanes:forward",
    "turn_lanes_backward": "turn:lanes:backward",
}
OSM_LANE_KEYS = ("lanes", "lanes:forward", "lanes:backward", "lanes:both_ways")


class OverrideError(ValueError):
    pass


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path = OVERRIDES) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def incident_ways(osm: Path, junction_nodes: dict[str, str]) -> dict[str, dict]:
    """OSM highway ways touching a J node: tags, junctions and travel sense at each."""
    out = {}
    for way in ET.parse(osm).getroot().findall("way"):
        tags = {tag.get("k"): tag.get("v") for tag in way.findall("tag")}
        if not tags.get("highway"):
            continue
        refs = [nd.get("ref") for nd in way.findall("nd")]
        touches = {}
        for ref in refs:
            if ref in junction_nodes:
                # Travel towards the node along node order is "forward" when the node is
                # after the way's start; travel away along node order leaves it "forward".
                position = "end" if ref == refs[-1] else "start" if ref == refs[0] else "mid"
                touches[junction_nodes[ref]] = position
        if touches:
            out[way.get("id")] = {"tags": tags, "junctions": touches}
    return out


def _turn_count(value: str) -> int:
    return len(value.split("|"))


def _is_iso_date(value) -> bool:
    try:
        date.fromisoformat(str(value)[:10])
        return True
    except ValueError:
        return False


def validate(data: dict, osm: Path, junction_nodes: dict[str, str]) -> list[str]:
    """Every rule the file must satisfy; returns a list of problems (empty = valid)."""
    problems = []
    ways = incident_ways(osm, junction_nodes)
    entries = {str(e["osm_way_id"]): e for e in data.get("ways", [])}
    if len(entries) != len(data.get("ways", [])):
        problems.append("duplicate osm_way_id entries")
    for missing in sorted(set(ways) - set(entries), key=int):
        problems.append(f"way {missing} touches {sorted(ways[missing]['junctions'])} but has no entry")
    legal = {s["id"] for s in data.get("legal_sources", [])}
    for way_id, e in entries.items():
        where = f"way {way_id}"
        if way_id not in ways:
            problems.append(f"{where}: not a highway way incident to J1..J6 in {osm.name}")
            continue
        source = ways[way_id]
        tags = source["tags"]
        if sorted(e.get("junctions", [])) != sorted(source["junctions"]):
            problems.append(f"{where}: junctions {e.get('junctions')} != OSM {sorted(source['junctions'])}")
        oneway = tags.get("oneway") in {"yes", "1", "true"} or tags.get("junction") == "roundabout"
        if e.get("oneway") != oneway:
            problems.append(f"{where}: oneway={e.get('oneway')} but OSM says {oneway}")
        status = e.get("status")
        if status not in STATUSES:
            problems.append(f"{where}: status {status!r} not in {sorted(STATUSES)}")
            continue
        values = {k: e.get(k) for k in LANE_FIELDS + TURN_FIELDS}
        osm_has_lanes = any(tags.get(k) for k in OSM_LANE_KEYS)
        if status == "unverified":
            set_values = [k for k, v in values.items() if v is not None]
            if set_values:
                problems.append(f"{where}: unverified but sets {set_values}; leave them null")
            if osm_has_lanes:
                problems.append(f"{where}: OSM has a lane tag; use status osm_tagged")
        elif status == "osm_tagged":
            if not osm_has_lanes:
                problems.append(f"{where}: osm_tagged but OSM carries no lane-count tag")
            if any(v is not None for v in values.values()):
                problems.append(f"{where}: osm_tagged entries take lane values from OSM, not this file")
        else:
            problems += [f"{where}: {p}" for p in _validate_verified(e, oneway)]
        speed = e.get("maxspeed")
        if speed is not None:
            basis = speed.get("basis")
            if basis not in SPEED_BASES:
                problems.append(f"{where}: maxspeed.basis {basis!r} not in {sorted(SPEED_BASES)}")
            elif basis == "osm_tag" and str(speed.get("kmh")) != tags.get("maxspeed"):
                problems.append(f"{where}: maxspeed osm_tag {speed.get('kmh')} != OSM {tags.get('maxspeed')}")
            elif basis == "legal_default":
                if tags.get("maxspeed"):
                    problems.append(f"{where}: OSM already has maxspeed; do not replace it with a legal default")
                if speed.get("source") not in legal:
                    problems.append(f"{where}: legal_default needs a source id from legal_sources")
            elif basis == "posted_sign" and not _evidence_ok(speed.get("evidence", [])):
                problems.append(f"{where}: posted_sign speed needs dated evidence with a reviewer")
    return problems


def _evidence_ok(evidence: list[dict]) -> bool:
    return bool(evidence) and all(
        ev.get("type") in EVIDENCE_TYPES and ev.get("reference") and ev.get("reviewer")
        and ev.get("direction") and _is_iso_date(ev.get("capture_date"))
        for ev in evidence
    )


def _validate_verified(e: dict, oneway: bool) -> list[str]:
    problems = []
    if not _evidence_ok(e.get("evidence", [])):
        problems.append("verified needs evidence items with type, reference, capture_date, direction, reviewer")
    if e.get("confidence") not in CONFIDENCE:
        problems.append(f"confidence must be one of {sorted(CONFIDENCE)}")
    if e.get("uniform_along_way") is not True:
        problems.append("counts must be confirmed uniform along the way (else split the way first)")
    lanes, fwd, bwd = e.get("lanes"), e.get("lanes_forward"), e.get("lanes_backward")
    for name, value in (("lanes", lanes), ("lanes_forward", fwd), ("lanes_backward", bwd)):
        if value is not None and (not isinstance(value, int) or value < 1):
            problems.append(f"{name} must be a positive integer")
    if oneway:
        if lanes is None:
            problems.append("one-way way needs lanes")
        if fwd is not None or bwd is not None or e.get("turn_lanes_backward"):
            problems.append("one-way way takes lanes/turn_lanes only, not forward/backward")
        if e.get("turn_lanes") and lanes and _turn_count(e["turn_lanes"]) != lanes:
            problems.append("turn_lanes must list one entry per lane")
    else:
        if fwd is None or bwd is None:
            problems.append("two-way way needs lanes_forward and lanes_backward (OSM node order)")
        elif lanes is not None and lanes != fwd + bwd:
            problems.append(f"lanes {lanes} != lanes_forward {fwd} + lanes_backward {bwd}")
        for field, count in (("turn_lanes_forward", fwd), ("turn_lanes_backward", bwd)):
            if e.get(field) and count and _turn_count(e[field]) != count:
                problems.append(f"{field} must list one entry per lane")
        if e.get("turn_lanes"):
            problems.append("two-way way uses turn_lanes_forward/backward, not turn_lanes")
    for lane in e.get("restricted_lanes", []):
        if not lane.get("vehicle_class") or not lane.get("direction"):
            problems.append("restricted_lanes items need vehicle_class and direction")
    return problems


def apply(data: dict, clipped: Path, output: Path) -> dict:
    """Write ``clipped`` plus verified lane values and speeds to ``output``; report what changed."""
    tree = ET.parse(clipped)
    by_id = {way.get("id"): way for way in tree.getroot().findall("way")}
    applied_lanes, applied_speeds, not_applied, turn_lanes = [], [], [], False
    for e in data["ways"]:
        way = by_id[str(e["osm_way_id"])]
        tags = {tag.get("k"): tag for tag in way.findall("tag")}

        def put(key: str, value) -> None:
            if key in tags:
                tags[key].set("v", str(value))
            else:
                tags[key] = ET.SubElement(way, "tag", k=key, v=str(value))

        if e["status"] == "verified":
            for field, key in OSM_KEYS.items():
                if e.get(field) is not None:
                    put(key, e[field])
                    turn_lanes |= field.startswith("turn")
            applied_lanes.append(str(e["osm_way_id"]))
            if e.get("restricted_lanes"):
                not_applied.append({"osm_way_id": str(e["osm_way_id"]), "field": "restricted_lanes",
                                    "reason": "recorded; mapping to SUMO lane permissions not implemented"})
        speed = e.get("maxspeed")
        if speed and speed["basis"] in {"legal_default", "posted_sign"}:
            put("maxspeed", speed["kmh"])
            applied_speeds.append({"osm_way_id": str(e["osm_way_id"]), "kmh": speed["kmh"],
                                   "basis": speed["basis"]})
    ET.indent(tree.getroot())
    output.write_bytes(ET.tostring(tree.getroot(), encoding="UTF-8", xml_declaration=True) + b"\n")
    return {"lanes_applied_to_ways": applied_lanes, "speeds_applied": applied_speeds,
            "recorded_not_applied": not_applied, "needs_osm_turn_lanes": turn_lanes}


def check_net(data: dict, net: Path) -> list[str]:
    """Generated SUMO edges must carry the verified lane counts and applied speeds."""
    edges: dict[str, list[ET.Element]] = {}
    for edge in ET.parse(net).getroot().findall("edge"):
        if edge.get("function"):
            continue
        # --output.original-names stores the OSM way id per lane
        orig = {p.get("value") for p in edge.iter("param") if p.get("key") == "origId"}
        for way_id in sorted(set(" ".join(orig).split())):
            edges.setdefault(way_id, []).append(edge)
    problems = []
    for e in data["ways"]:
        way_id = str(e["osm_way_id"])
        found = edges.get(way_id, [])
        if not found:
            problems.append(f"way {way_id}: no SUMO edge with this origId")
            continue
        speed = e.get("maxspeed")
        if speed and speed["basis"] in {"legal_default", "posted_sign"}:
            for edge in found:
                for lane in edge.findall("lane"):
                    if lane.get("allow") != "pedestrian" and abs(float(lane.get("speed")) * 3.6 - speed["kmh"]) > 0.5:
                        problems.append(f"way {way_id}: edge {edge.get('id')} speed "
                                        f"{float(lane.get('speed')) * 3.6:.0f} km/h != {speed['kmh']}")
                        break
        if e["status"] != "verified":
            continue
        for edge in found:
            vehicle_lanes = sum(1 for lane in edge.findall("lane") if lane.get("allow") != "pedestrian")
            backward = edge.get("id").startswith("-")
            want = e["lanes"] if e["oneway"] else e["lanes_backward" if backward else "lanes_forward"]
            if vehicle_lanes != want:
                problems.append(f"way {way_id}: edge {edge.get('id')} has {vehicle_lanes} vehicle lanes, verified {want}")
    return problems


def coverage(data: dict) -> dict:
    counts = {status: [] for status in sorted(STATUSES)}
    for e in data["ways"]:
        counts[e["status"]].append(str(e["osm_way_id"]))
    return {status: {"count": len(ids), "osm_way_ids": ids} for status, ids in counts.items()}


def junction_nodes_from_selection() -> dict[str, str]:
    selection = json.loads((ROOT / "scenarios" / "tunis-centre-6j" / "selection.json").read_text(encoding="utf-8"))
    return {str(row["node_id"]): f"J{i}" for i, row in enumerate(selection["junctions"], start=1)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--overrides", type=Path, default=OVERRIDES)
    parser.add_argument("--osm", type=Path, default=CLIPPED_OSM)
    parser.add_argument("--strict", action="store_true",
                        help="release check: fail unless every junction-incident way is verified")
    args = parser.parse_args(argv)
    data = load(args.overrides)
    problems = validate(data, args.osm, junction_nodes_from_selection())
    for problem in problems:
        print("INVALID", problem)
    cov = coverage(data)
    print(" ".join(f"{status}={row['count']}" for status, row in cov.items()), f"({len(data['ways'])} ways)")
    if problems:
        return 2
    if args.strict and cov["verified"]["count"] != len(data["ways"]):
        pending = cov["unverified"]["osm_way_ids"] + cov["osm_tagged"]["osm_way_ids"]
        print("STRICT: not lane-verified:", ", ".join(sorted(pending, key=int)))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
