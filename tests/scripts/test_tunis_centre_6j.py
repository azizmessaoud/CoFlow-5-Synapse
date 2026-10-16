import json
import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCENARIO = ROOT / "scenarios" / "tunis-centre-6j"
SELECTION = ROOT / "scenarios" / "tunis-centre-6j" / "selection.json"
NETS = ("tunis6j.net.xml", "tunis6j_actuated.net.xml")


def spec() -> dict:
    return json.loads((SCENARIO / "junctions.json").read_text(encoding="utf-8"))


def test_six_junctions_follow_row_14_selection() -> None:
    selected = json.loads(SELECTION.read_text(encoding="utf-8"))["junctions"]
    rows = spec()["junctions"]
    assert [row["id"] for row in rows] == ["J1", "J2", "J3", "J4", "J5", "J6"]
    assert [row["osm_node_id"] for row in rows] == [node["node_id"] for node in selected]


@pytest.mark.parametrize("net_name", NETS)
def test_only_the_six_junctions_are_signalised(net_name: str) -> None:
    root = ET.parse(SCENARIO / net_name).getroot()
    tls_ids = sorted(logic.get("id") for logic in root.findall("tlLogic"))
    assert tls_ids == sorted(row["tls_id"] for row in spec()["junctions"])
    signal_junctions = {j.get("id") for j in root.findall("junction") if j.get("type") == "traffic_light"}
    assert signal_junctions == set(tls_ids)


def test_actuated_variant_uses_actuated_plans() -> None:
    root = ET.parse(SCENARIO / "tunis6j_actuated.net.xml").getroot()
    assert {logic.get("type") for logic in root.findall("tlLogic")} == {"actuated"}


def test_lights_are_named_j1_to_j6_after_their_osm_nodes() -> None:
    rows = spec()["junctions"]
    assert [row["tls_id"] for row in rows] == ["J1", "J2", "J3", "J4", "J5", "J6"]
    assert all(row["name"] and row["osm_node_id"] for row in rows)


def test_every_junction_has_phases_and_neighbours() -> None:
    for row in spec()["junctions"]:
        assert row["phases"] and all(len(state) == row["signal_links"] for state in row["phases"])
        assert row["downstream_neighbours"], row["id"]


def test_junction_bus_stops_match_the_stop_file() -> None:
    stops = ET.parse(SCENARIO / "tunis6j.stops.xml").getroot().findall("busStop")
    before = {stop.get("id"): stop.find("param").get("value") for stop in stops}
    for row in spec()["junctions"]:
        assert row["bus_stops"] == sorted(s for s, j in before.items() if j == row["tls_id"])


def test_lane_counts_follow_osm_tags() -> None:
    """Roads keep the lanes OSM gives them: no motorway ramp lanes invented in the city centre."""
    osm = ET.parse(SCENARIO / "tunis6j.osm.xml").getroot()
    ways = {w.get("id"): {t.get("k"): t.get("v") for t in w.findall("tag")} for w in osm.findall("way")}
    root = ET.parse(SCENARIO / "tunis6j.net.xml").getroot()
    wrong = []
    for edge in root.findall("edge"):
        eid = edge.get("id")
        if edge.get("function"):
            continue
        assert "Ramp" not in eid, f"{eid}: ramp edge guessed in the city centre"
        tags = ways.get(eid.lstrip("-").split("#")[0], {})
        if tags.get("oneway") != "yes" or not tags.get("lanes", "").isdigit():
            continue
        lanes = [l for l in edge.findall("lane") if "passenger" in (l.get("allow") or "passenger")
                 and "passenger" not in (l.get("disallow") or "")]
        if len(lanes) != int(tags["lanes"]):
            wrong.append(f"{eid} {tags.get('name')}: OSM {tags['lanes']} lanes, SUMO {len(lanes)}")
    assert not wrong, wrong


def test_demand_is_labelled_synthetic_and_claims_stay_showcase_only() -> None:
    manifest = spec()
    assert manifest["status"] == "showcase_only"
    assert manifest["road_demand"].startswith("synthetic")
    assert "no lives saved" in manifest["claim_boundary"]


@pytest.mark.parametrize("config", ["tunis6j.sumocfg", "tunis6j_actuated.sumocfg"])
def test_config_references_committed_files(config: str) -> None:
    root = ET.parse(SCENARIO / config).getroot()
    for element in root.find("input"):
        for name in element.get("value").split(","):
            assert (SCENARIO / name).is_file(), name


def sumo_binary() -> str | None:
    home = os.environ.get("SUMO_HOME")
    if not home:
        try:
            import sumo
        except ImportError:
            return None
        home = sumo.SUMO_HOME
    for name in ("sumo.exe", "sumo"):
        if (Path(home) / "bin" / name).is_file():
            return str(Path(home) / "bin" / name)
    return shutil.which("sumo")


def test_traci_can_drive_each_junction_light() -> None:
    traci = pytest.importorskip("traci")
    binary = sumo_binary()
    if binary is None:
        pytest.skip("SUMO is not installed")
    rows = spec()["junctions"]
    traci.start([binary, "-c", str(SCENARIO / "tunis6j.sumocfg"), "--end", "180", "--no-warnings", "true"])
    try:
        assert sorted(traci.trafficlight.getIDList()) == sorted(row["tls_id"] for row in rows)
        for _ in range(60):
            traci.simulationStep()
        for row in rows:
            last = len(traci.trafficlight.getAllProgramLogics(row["tls_id"])[0].phases) - 1
            traci.trafficlight.setPhase(row["tls_id"], last)
        traci.simulationStep()
        for row in rows:
            assert traci.trafficlight.getRedYellowGreenState(row["tls_id"]) == row["phases"][-1]
        while traci.simulation.getTime() < 180:
            traci.simulationStep()
        assert traci.simulation.getArrivedNumber() >= 0
        assert traci.vehicle.getIDCount() > 0
    finally:
        traci.close()
