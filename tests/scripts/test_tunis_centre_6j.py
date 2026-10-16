import json
import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCENARIO = ROOT / "scenarios" / "tunis-centre-6j"
SELECTION = ROOT / "harness" / "work" / "14-tunis-showcase" / "junctions.json"
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


def test_every_junction_has_phases_neighbours_and_a_bus_stop() -> None:
    stops = ET.parse(SCENARIO / "tunis6j.stops.xml").getroot().findall("busStop")
    stop_junctions = {
        stop.find("param").get("value") for stop in stops if stop.find("param").get("key") == "junction"
    }
    for row in spec()["junctions"]:
        assert row["phases"] and all(len(state) == row["signal_links"] for state in row["phases"])
        assert row["downstream_neighbours"], row["id"]
        assert row["tls_id"] in stop_junctions


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
