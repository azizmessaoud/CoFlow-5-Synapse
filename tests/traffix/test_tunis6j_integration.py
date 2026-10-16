"""traffix3 hierarchy + CoFlow Synapse on the six-junction Tunis map.

  python -m pytest tests/traffix -q

The SUMO run skips when libsumo/traci or the eclipse-sumo wheel is missing.
"""
import os
import sys
import xml.etree.ElementTree as ET

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
pytest.importorskip("yaml")

from traffix.core import config  # noqa: E402
from traffix.core.decision_log import DecisionLog  # noqa: E402

J = ["J1", "J2", "J3", "J4", "J5", "J6"]


@pytest.fixture(autouse=True)
def tunis6j(monkeypatch):
    monkeypatch.setenv("TRAFFIX_NETWORK", "tunis6j")


def net_root():
    return ET.parse(config.network_files()[0]).getroot()


def test_default_network_is_the_tunis_map():
    assert config.simulation()["network"] == "tunis6j"
    static, actuated = config.network_files()
    assert static.endswith(os.path.join("scenarios", "tunis-centre-6j", "tunis6j.net.xml"))
    assert os.path.exists(static) and os.path.exists(actuated)


def test_one_light_per_selected_junction():
    root = net_root()
    assert sorted(t.get("id") for t in root.findall("tlLogic")) == J
    named = {j.get("id"): {p.get("key"): p.get("value") for p in j.findall("param")}.get("name")
             for j in root.findall("junction") if j.get("type") == "traffic_light"}
    assert sorted(named) == J and all(named.values())


def test_scenario_places_and_bus_lines_exist_on_the_map():
    root = net_root()
    edges = {e.get("id"): e for e in root.findall("edge") if not e.get("function")}
    for name, scen in config.scenarios().items():
        events = scen.get("events") or {}
        if "incident" in events:
            edge = edges[events["incident"]["edge"]]
            assert len(edge.findall("lane")) > events["incident"]["lane"], name
        if "sensor_fault" in events:
            assert events["sensor_fault"]["tls"] in J
        if "surge" in events:
            assert events["surge"]["towards"] in J
        if "flood_edge" in events.get("rain", {}):
            assert events["rain"]["flood_edge"] in edges
    for _line, first, last in config.bus_lines():
        assert first in edges and last in edges
    stops = ET.parse(config.network_files()[0].replace(".net.xml", ".stops.xml")).getroot()
    before = {s.find("param").get("value") for s in stops.findall("busStop") if s.get("lines")}
    assert before <= set(J) | {""}          # real TRANSTU stops: some sit before a light, most do not
    assert before & set(J), "no stop before any light: transit priority has nothing to work with"
    # a stop tied to a light must be served by a line that then drives through that light
    import sumolib
    net = sumolib.net.readNet(config.network_files()[0])
    routes = config.line_routes(net)
    for s in stops.findall("busStop"):
        j = s.find("param").get("value")
        if j:
            crossed = {net.getEdge(e).getToNode().getID() for ln in s.get("lines").split()
                       for e in routes.get(ln, {}).get("edges", [])}
            assert j in crossed, f"{s.get('id')} is tied to {j} but none of its lines cross {j}"


def static_live_run():
    """The trip planner part of a live run, without starting SUMO."""
    from traffix.api.live import LiveRun
    lr = LiveRun.__new__(LiveRun)
    lr.geometry = {}
    lr._static(config.network_files()[0])
    lr.state = lambda: {}
    return lr


def test_trip_planner_places_are_named_streets():
    places = static_live_run().places
    for side in ("from", "to"):
        names = [p["name"] for p in places[side]]
        assert not [n for n in names if n.isdigit()], f"{side}: bare OSM ids shown to the driver"
        assert len(set(names)) == len(names), f"{side}: two places share one label"


def test_trip_api_accepts_edge_ids_with_hash():
    # the user's failing pair: From 11414303232 (-1230791925) to 6640940830 (9516351301#3)
    from fastapi.testclient import TestClient
    from traffix.api import server
    server.RUN["live"] = static_live_run()
    try:
        r = TestClient(server.app).get("/api/trip", params={"origin": "-1230791925",
                                                             "destination": "9516351301#3"})
    finally:
        server.RUN["live"] = None
    assert r.status_code == 200 and "error" not in r.json()
    assert r.json()["edges"][-1] == "9516351301#3"


def test_experiments_refuse_traffic_built_for_another_map(tmp_path):
    import json
    from traffix.evaluation import runner
    (tmp_path / "offpeak_seed1.events.json").write_text(json.dumps(
        {"scenario": "offpeak", "seed": 1, "start": "2026-10-14 11:00", "duration": 60,
         "events": {}, "vehicles": 0, "network": "tunis_centre"}))
    (tmp_path / "offpeak_seed1.rou.xml").write_text("<routes/>")
    with pytest.raises(RuntimeError, match="build_demand"):
        runner.run_one("fixed", "offpeak", 1, route_dir=str(tmp_path))
    assert runner.demand_is_current(str(tmp_path / "offpeak_seed1")) is False


def test_generated_traffic_records_its_map(tmp_path):
    import json
    from traffix.demand.generator import DemandGenerator
    from traffix.evaluation import runner
    scen = {"start": "2026-10-14 11:00", "duration": 60}
    _, meta = DemandGenerator(config.network_files()[0]).build("t6j", scen, 1, str(tmp_path))
    assert meta["network"] == "tunis6j"
    assert runner.demand_is_current(str(tmp_path / "t6j_seed1"))
    # same map name, but the network was rebuilt since (e.g. lanes or edges changed)
    meta["net_digest"] = "an older build"
    (tmp_path / "t6j_seed1.events.json").write_text(json.dumps(meta))
    assert runner.demand_is_current(str(tmp_path / "t6j_seed1")) is False


def test_trip_reachability_matches_sumolib_routing():
    """The generator's quick reachability check must agree with sumolib's own router."""
    import random
    from traffix.demand.generator import DemandGenerator
    g = DemandGenerator(config.network_files()[0])
    rng = random.Random(7)
    cases = [(rng.choice(g.entries + g.inner), rng.choice(g.exits + g.inner), "passenger") for _ in range(120)]
    cases += [(*rng.sample(g.walk_edges, 2), "pedestrian") for _ in range(120)]
    for a, b, vc in cases:
        if a == b or b.getToNode() == a.getFromNode():
            continue
        path, _ = g.net.getShortestPath(a, b, vClass=vc, ignoreDirection=(vc == "pedestrian"))
        assert g._ok(a, b, vc) == (path is not None), (a.getID(), b.getID(), vc)


def test_traffic_for_one_scenario_builds_quickly(tmp_path):
    # run_experiments rebuilds up to 35 scenario/seed pairs; 134 s each made that over an hour
    import time
    from traffix.demand.generator import DemandGenerator
    t = time.time()
    DemandGenerator(config.network_files()[0]).build("offpeak", config.scenarios()["offpeak"], 1, str(tmp_path))
    assert time.time() - t < 30


def test_network_model_gives_six_masters_with_street_names():
    from traffix.simulation.network_model import load_models
    models = load_models(config.network_files()[0])
    assert sorted(models) == J
    assert all(m.green_phases and m.name != m.id for m in models.values())


def synthetic_log():
    log = DecisionLog()
    log.log(10, "master@J1", "switch", "MAX_PRESSURE_SWITCH", tls="J1", pressure_new=4.0)
    log.log(12, "master@J2", "grant", "EMERGENCY_GRANTED_SWITCH", tls="J2", vehicle="ambulance0")
    return log.entries


def test_coflow_synapse_verifies_cites_and_abstains():
    from traffix.synapse.coflow_bridge import TraffixSynapse
    syn = TraffixSynapse(synthetic_log(), run_id="test_run", scenario={"scenario": "emergency"})
    answer = syn.explain("Why did J2 change?", 2)
    assert answer["fallback"] == "verified"
    assert answer["citations"] == ["EMERGENCY_GRANTED_SWITCH"]
    assert answer["provenance"]["event_id"] == "test_run#2"
    assert all(answer["provenance"][k] for k in ("run_id", "scenario_hash", "bundle_digest",
                                                 "corpus_hash", "query_hash"))
    assert syn.explain("Why?", 99)["fallback"] == "abstain"
    assert syn.audit("J2 turned green for a late bus", 2)["fallback"] == "abstain"
    assert syn.audit("EMERGENCY_GRANTED_SWITCH for the ambulance", 2)["fallback"] == "verified"
    metrics = syn.refreshed(synthetic_log()).metrics()
    assert metrics["request_count"] == 4 and metrics["abstain_count"] == 2


def test_hierarchy_runs_on_the_tunis_map(tmp_path):
    pytest.importorskip("sumo")
    pytest.importorskip("sumolib")
    try:
        import libsumo  # noqa: F401
    except ImportError:
        pytest.importorskip("traci")
    from traffix.demand.generator import DemandGenerator
    from traffix.evaluation import runner
    from traffix.synapse.coflow_bridge import TraffixSynapse

    scenario = {"start": "2026-10-14 11:00", "duration": 300,
                "events": {"ambulances": {"count": 2}}}
    DemandGenerator(config.network_files()[0]).build("t6j", scenario, 1, str(tmp_path))
    row = runner.run_one("traffix", "t6j", 1, route_dir=str(tmp_path))
    assert row["decisions_logged"] > 0
    log_file = os.path.join(runner.OUT, "logs", "decisions_traffix_t6j_1.jsonl")
    syn = TraffixSynapse.from_log_file(log_file)
    masters = {e["tls"] for e in syn.entries.values() if e["agent"].startswith("master@")}
    assert len(masters) >= 4 and masters <= set(J)
    first = min(syn.entries)
    assert syn.explain("Why?", first)["fallback"] == "verified"
