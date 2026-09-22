from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from scripts import watch_sumo

ROOT = Path(__file__).resolve().parents[2]
WATCH = ROOT / "scenarios" / "watch"


def test_watch_scenario_is_long_readable_paced_and_detached(monkeypatch) -> None:
    required = {
        "watch.nod.xml", "watch.edg.xml", "watch.con.xml", "watch.net.xml",
        "watch.tls.xml", "watch.rou.xml", "watch.settings.xml", "watch.sumocfg",
    }
    assert required <= {path.name for path in WATCH.iterdir()}

    nodes = ET.parse(WATCH / "watch.nod.xml").getroot()
    positions = {node.get("id"): (float(node.get("x")), float(node.get("y"))) for node in nodes}
    assert positions == {"J0": (0, 0), "N": (0, 300), "S": (0, -300), "E": (300, 0), "W": (-300, 0)}

    edges = ET.parse(WATCH / "watch.edg.xml").getroot().findall("edge")
    for edge in edges:
        lanes = edge.findall("lane")
        vehicle_lanes = [lane for lane in lanes if "passenger" in (lane.get("allow") or "")]
        sidewalks = [lane for lane in lanes if lane.get("allow") == "pedestrian"]
        assert len(vehicle_lanes) == (2 if edge.get("id", "").endswith("_in") else 1)
        assert len(sidewalks) == 1

    connections = ET.parse(WATCH / "watch.con.xml").getroot().findall("connection")
    assert len(connections) == 8
    assert not any(connection.get("from", "").replace("_in", "") == connection.get("to", "").replace("_out", "") for connection in connections)

    tls = ET.parse(WATCH / "watch.tls.xml").getroot().find("tlLogic")
    assert tls is not None and tls.get("type") == "static"
    phases = tls.findall("phase")
    assert sum(int(phase.get("duration")) for phase in phases) == 72
    assert {phase.get("name") for phase in phases} >= {"North-South green", "North-South yellow", "East-West green", "East-West yellow", "All red"}
    assert all(len(phase.get("state", "")) == 8 for phase in phases)

    settings = ET.parse(WATCH / "watch.settings.xml").getroot()
    assert settings.find("scheme").get("name") == "real world"
    assert settings.find("delay").get("value") == "1000"
    assert settings.find("tracker").get("tl") == "J0"

    config = ET.parse(WATCH / "watch.sumocfg").getroot()
    assert config.find(".//begin").get("value") == "0"
    assert config.find(".//end").get("value") == "120"
    assert config.find(".//step-length").get("value") == "1"
    assert config.find(".//seed").get("value") == "53"
    assert "harness/work" not in (config.find(".//tripinfo-output").get("value") or "")

    routes = ET.parse(WATCH / "watch.rou.xml").getroot()
    buses = [flow for flow in routes.findall("flow") if flow.get("type") == "bus"]
    assert {bus.get("line") for bus in buses} == {"B1", "B2"}
    assert watch_sumo.planned_trips(WATCH / "watch.rou.xml") == 126

    monkeypatch.setattr(watch_sumo, "require_gui", lambda: "sumo-gui.exe")
    command = watch_sumo.demo_command(Path("temporary-tripinfo.xml"))
    assert command[:3] == ["sumo-gui.exe", "-c", str(WATCH / "watch.sumocfg")]
    assert command[command.index("--start") + 1] == "true"
    assert command[command.index("--delay") + 1] == "1000"
    assert "--tripinfo-output" in command and "--quit-on-end" in command

    source = (ROOT / "scripts/watch_sumo.py").read_text(encoding="utf-8").lower()
    assert "qwen" not in source and "langgraph" not in source
    assert 'sumo_extra_args=("--delay", "1000")' in source


def test_terminal_page_uses_tripinfo_and_gated_evidence(tmp_path: Path) -> None:
    tripinfo = tmp_path / "tripinfo.xml"
    tripinfo.write_text(
        """<?xml version="1.0"?><tripinfos>
        <tripinfo id="done-1" arrival="10" waitingTime="1"/>
        <tripinfo id="unfinished" arrival="-1" waitingTime="5"/>
        <tripinfo id="done-2" arrival="20" waitingTime="3"/>
        </tripinfos>""",
        encoding="utf-8",
    )
    page = watch_sumo.build_watch_report(
        config=WATCH / "watch.sumocfg", route_file=WATCH / "watch.rou.xml",
        tripinfo=tripinfo,
    )
    assert "Controller: fixed-time watch scene" in page
    assert "Seed: 53" in page
    assert "Simulation time: 0 to 120 seconds" in page
    assert "Trips completed / planned: 2 / 126" in page
    assert "Mean waiting seconds: 3.00" in page
    assert "Max waiting seconds: 5.00" in page
    assert "Safety violations: none recorded in this watch scene" in page
    assert "actuated completed 84/84 trips versus fixed-time 71/84" in page
    assert "Row 10b later measured cooperative Max-Pressure: 70/84 trips completed" in page
    assert "mean wait 14.21 s, and P95 wait 25.00 s" in page
    assert "so no winner is established" in page
    assert "Max-Pressure trip KPIs are still missing" not in page
    _, historical_fallback = watch_sumo.evaluation_sentences(
        followup_gate_path=tmp_path / "missing-gate.json",
        followup_comparison_path=tmp_path / "missing-comparison.json",
    )
    assert historical_fallback == "Max-Pressure trip KPIs are still missing."
    assert "No lives saved. No measured air quality. No winner announced." in page


def test_missing_watch_numbers_are_never_estimated(tmp_path: Path) -> None:
    page = watch_sumo.build_watch_report(
        config=WATCH / "watch.sumocfg", route_file=tmp_path / "missing.rou.xml",
        tripinfo=tmp_path / "missing-tripinfo.xml", evaluation_report=tmp_path / "missing-report.json",
    )
    assert "Trips completed / planned: not in this watch run / not in this watch run" in page
    assert page.count("not in this watch run") >= 5



def test_tripinfo_arrival_zero_is_completed(tmp_path: Path) -> None:
    tripinfo = tmp_path / "arrival-zero.xml"
    tripinfo.write_text(
        '<?xml version="1.0"?><tripinfos>'
        '<tripinfo id="zero" arrival="0" waitingTime="0"/>'
        '<tripinfo id="unfinished" arrival="-1" waitingTime="2"/>'
        '</tripinfos>',
        encoding="utf-8",
    )
    summary = watch_sumo.tripinfo_summary(tripinfo)
    assert summary["completed"] == 1
    assert summary["mean_waiting"] == 1.0
