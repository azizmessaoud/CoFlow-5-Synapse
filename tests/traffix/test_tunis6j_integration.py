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
    served = {s.find("param").get("value") for s in stops.findall("busStop") if s.get("lines")}
    assert served == set(J)


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
