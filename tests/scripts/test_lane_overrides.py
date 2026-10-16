import copy
import hashlib
import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from scripts import lane_overrides as lo

SCENARIO = lo.ROOT / "scenarios" / "tunis-centre-6j"
NODES = lo.junction_nodes_from_selection()

# Ways incident to J1..J6 without an OSM lane-count tag in the 2026-10-15 snapshot.
UNTAGGED = {
    "10641392", "26013493", "26242831", "33803062", "39169970", "39170210", "56065135", "95132613",
    "100080972", "100081107", "106509679", "306643020", "545291183", "545291184", "577010717",
    "704802731", "1409299974", "1501192411",
}
OSM_TAGGED = {"10641416": "2", "10641456": "3", "26280306": "1"}


def data() -> dict:
    return lo.load()


def entries() -> dict:
    return {e["osm_way_id"]: e for e in data()["ways"]}


def manifest() -> dict:
    return json.loads((SCENARIO / "junctions.json").read_text(encoding="utf-8"))


def test_committed_overrides_are_valid_against_the_clipped_osm() -> None:
    assert lo.validate(data(), lo.CLIPPED_OSM, NODES) == []


def test_overrides_cover_exactly_the_junction_incident_ways() -> None:
    assert set(entries()) == set(lo.incident_ways(lo.CLIPPED_OSM, NODES)) == UNTAGGED | set(OSM_TAGGED)


def test_ways_without_evidence_stay_explicitly_unverified() -> None:
    for way_id in UNTAGGED:
        e = entries()[way_id]
        if e["status"] == "verified":
            continue                        # promoted with evidence; checked below
        assert e["status"] == "unverified", way_id
        assert all(e[k] is None for k in lo.LANE_FIELDS + lo.TURN_FIELDS), way_id
        assert e["evidence"] == [] and e["confidence"] is None, way_id


def test_osm_tagged_ways_match_their_osm_lane_tags() -> None:
    for way_id, lanes in OSM_TAGGED.items():
        e = entries()[way_id]
        if e["status"] == "osm_tagged":
            assert e["osm_lane_tags"] == {"lanes": lanes}


def test_every_verified_value_has_dated_reviewed_evidence() -> None:
    for e in data()["ways"]:
        if e["status"] == "verified":
            assert lo._evidence_ok(e["evidence"]), e["osm_way_id"]
            assert e["confidence"] in lo.CONFIDENCE and e["uniform_along_way"] is True


def test_legal_default_speed_never_replaces_an_osm_maxspeed() -> None:
    ways = lo.incident_ways(lo.CLIPPED_OSM, NODES)
    legal = {s["id"] for s in data()["legal_sources"]}
    for e in data()["ways"]:
        speed = e["maxspeed"]
        if ways[e["osm_way_id"]]["tags"].get("maxspeed"):
            assert speed["basis"] == "osm_tag", e["osm_way_id"]
        elif speed["basis"] == "legal_default":
            assert speed["source"] in legal and speed["kmh"] == 50


def _verified(entry: dict, **values) -> dict:
    e = copy.deepcopy(entry)
    e.update(status="verified", confidence="high", uniform_along_way=True, evidence=[{
        "type": "field_survey", "reference": "survey-2026-11-02-J1-01.jpg", "capture_date": "2026-11-02",
        "direction": "approach to J1, travelling along node order", "reviewer": "A. Surveyor"}])
    e.update(values)
    return e


def _swap(entry: dict) -> dict:
    d = data()
    d["ways"] = [entry if e["osm_way_id"] == entry["osm_way_id"] else e for e in d["ways"]]
    return d


def test_validator_accepts_a_fully_evidenced_one_way_override() -> None:
    e = _verified(entries()["26013493"], lanes=3, turn_lanes="left|through|through")
    assert lo.validate(_swap(e), lo.CLIPPED_OSM, NODES) == []


@pytest.mark.parametrize("change, message", [
    ({"evidence": []}, "verified needs evidence"),
    ({"confidence": None}, "confidence"),
    ({"uniform_along_way": None}, "uniform"),
    ({"lanes": None}, "one-way way needs lanes"),
    ({"lanes_forward": 2}, "not forward/backward"),
    ({"turn_lanes": "left|through"}, "one entry per lane"),
])
def test_validator_rejects_incomplete_one_way_overrides(change: dict, message: str) -> None:
    e = _verified(entries()["26013493"], lanes=3)
    e.update(change)
    assert any(message in p for p in lo.validate(_swap(e), lo.CLIPPED_OSM, NODES))


def test_validator_rejects_evidence_without_capture_date() -> None:
    e = _verified(entries()["26013493"], lanes=2)
    e["evidence"][0]["capture_date"] = "unknown"
    assert any("evidence" in p for p in lo.validate(_swap(e), lo.CLIPPED_OSM, NODES))


def test_two_way_override_needs_consistent_directional_counts() -> None:
    base = entries()["26242831"]           # Avenue de France, two-way
    assert base["oneway"] is False
    ok = _verified(base, lanes=3, lanes_forward=2, lanes_backward=1)
    assert lo.validate(_swap(ok), lo.CLIPPED_OSM, NODES) == []
    bad = _verified(base, lanes=4, lanes_forward=2, lanes_backward=1)
    assert any("!=" in p for p in lo.validate(_swap(bad), lo.CLIPPED_OSM, NODES))
    missing = _verified(base, lanes=3)
    assert any("lanes_forward and lanes_backward" in p for p in lo.validate(_swap(missing), lo.CLIPPED_OSM, NODES))


def test_unverified_entry_with_a_value_is_rejected() -> None:
    e = copy.deepcopy(entries()["26013493"])
    e["lanes"] = 2
    assert any("leave them null" in p for p in lo.validate(_swap(e), lo.CLIPPED_OSM, NODES))


def test_entry_for_a_way_that_does_not_touch_a_junction_is_rejected() -> None:
    d = data()
    stray = copy.deepcopy(d["ways"][0])
    stray["osm_way_id"] = "1"
    d["ways"].append(stray)
    assert any("way 1:" in p for p in lo.validate(d, lo.CLIPPED_OSM, NODES))


def test_apply_writes_verified_lanes_and_speeds_to_a_copy_only(tmp_path: Path) -> None:
    before = lo.CLIPPED_OSM.read_bytes()
    e = _verified(entries()["26013493"], lanes=3, turn_lanes="left|through|through")
    out = tmp_path / "patched.osm.xml"
    report = lo.apply(_swap(e), lo.CLIPPED_OSM, out)
    assert lo.CLIPPED_OSM.read_bytes() == before
    ways = {w.get("id"): {t.get("k"): t.get("v") for t in w.findall("tag")}
            for w in ET.parse(out).getroot().findall("way")}
    assert ways["26013493"]["lanes"] == "3" and ways["26013493"]["turn:lanes"] == "left|through|through"
    assert report["lanes_applied_to_ways"] == ["26013493"] and report["needs_osm_turn_lanes"]
    for way_id in UNTAGGED - {"26013493"}:
        assert "lanes" not in ways[way_id], way_id
    assert ways["1409299974"]["maxspeed"] == "50"          # OSM's own tag, untouched


def test_strict_check_fails_until_every_way_is_verified(capsys) -> None:
    assert lo.main([]) == 0
    expected = 0 if all(e["status"] == "verified" for e in data()["ways"]) else 1
    assert lo.main(["--strict"]) == expected
    assert "STRICT" in capsys.readouterr().out or expected == 0


def test_manifest_records_override_checksum_and_coverage() -> None:
    record = manifest()["sources"]["lane_overrides"]
    assert record["sha256"] == lo.sha256(lo.OVERRIDES)
    assert record["coverage"] == lo.coverage(data())
    status = manifest()["validation"]["lane_count_status"]
    assert f"{record['coverage']['verified']['count']} of 21" in status


@pytest.mark.parametrize("net_name", ["tunis6j.net.xml", "tunis6j_actuated.net.xml"])
def test_built_networks_carry_the_override_values(net_name: str) -> None:
    assert lo.check_net(data(), SCENARIO / net_name) == []


@pytest.mark.parametrize("path, key", [
    ("scenarios/tunis-showcase/tunis.osm.xml", ("sources", "osm", "sha256")),
    ("scenarios/tunis-centre-6j/selection.json", ("sources", "junction_selection", "sha256")),
    ("scenarios/tunis-centre-6j/lane_overrides.json", ("sources", "lane_overrides", "sha256")),
])
def test_hashed_sources_are_lf_and_match_the_manifest(path: str, key: tuple) -> None:
    """.gitattributes keeps these LF on Windows, so the recorded SHA-256 holds on every OS."""
    raw = (lo.ROOT / path).read_bytes()
    assert b"\r\n" not in raw, f"{path} has CRLF; check .gitattributes"
    record = manifest()
    for part in key:
        record = record[part]
    assert record == "sha256:" + hashlib.sha256(raw).hexdigest()
