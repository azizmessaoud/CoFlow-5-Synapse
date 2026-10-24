"""traffix3 quick tests:  python -m pytest tests/traffix   (or python tests/traffix/test_core.py)"""
import os
import subprocess
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from traffix.core.decision_log import DecisionLog  # noqa: E402
from traffix.demand import hijri  # noqa: E402
from traffix.demand.calendar_model import CalendarModel  # noqa: E402


def test_ramadan_2026_dates():
    assert hijri.info(datetime(2026, 2, 18).date())["ramadan"]
    assert hijri.info(datetime(2026, 3, 20).date())["eid_al_fitr"]
    assert not hijri.info(datetime(2026, 4, 15).date())["ramadan"]


def test_calendar_layers():
    c = CalendarModel()
    sept, _, _ = c.level(datetime(2026, 9, 14, 8, 0))
    aug_sat, _, _ = c.level(datetime(2026, 8, 15, 8, 0))
    assert abs(sept - 1.15) < 1e-6
    assert aug_sat < 0.6 * sept
    _, morning_share, _ = c.level(datetime(2026, 10, 13, 8, 0))
    _, evening_share, _ = c.level(datetime(2026, 10, 13, 17, 0))
    assert morning_share > 0.6 > 0.4 > evening_share


def test_decisions_need_reason_codes():
    log = DecisionLog()
    log.log(1, "master@B1", "switch", "MAX_PRESSURE_SWITCH", tls="B1")
    try:
        log.log(2, "master@B1", "switch", "MADE_UP_REASON")
        assert False, "unknown reason code accepted"
    except ValueError:
        pass


def test_explainer_finds_entries_for_a_junction_question():
    from traffix.agents.network.explainer import select_entries
    log = DecisionLog()
    log.log(10, "master@J1", "switch", "MAX_PRESSURE_SWITCH", tls="J1")
    log.log(20, "master@J1", "switch", "MAX_PRESSURE_SWITCH", tls="J1")
    log.log(30, "master@J2", "switch", "MAX_PRESSURE_SWITCH", tls="J2")
    for q in ("Why did the lights at J1 switch?", "Why did J1 turn green?", "J1"):
        found, _ = select_entries(log.entries, q)
        assert found and all(e["tls"] == "J1" for e in found), q
    found, _ = select_entries(log.entries, "Why did the late buses get priority?")
    assert not found


def test_explainer_answers_the_demo_questions():
    from traffix.agents.network.explainer import explain, select_entries
    log = DecisionLog()
    log.log(5, "master@J3", "abstain", "BUS_NO_REFERENCE", tls="J3", vehicle="bus_74_R_0")
    log.log(10, "master@J3", "switch", "MAX_PRESSURE_SWITCH", tls="J3")
    log.log(20, "supermaster", "directive", "EMERGENCY_PREPARE", tls="J5", vehicle="ambulance1", eta_s=30)
    log.log(25, "master@J5", "grant", "EMERGENCY_GRANTED_SWITCH", tls="J5", vehicle="ambulance1")
    log.log(50, "master@J3", "switch", "MAX_PRESSURE_SWITCH", tls="J3")

    # a junction question lists its light changes, newest first in ranking, not a bus that merely passed
    found, _ = select_entries(log.entries, "Why did J3 switch?")
    assert [e["id"] for e in found] == [2, 5]
    # "denied" narrows the emergency topic instead of matching bus entries, and says nothing was denied
    out = explain(log.entries, "Was any emergency vehicle denied?", engine="template")
    assert out["answer"].startswith("Nothing on this topic was denied")
    assert set(out["citations"]) == {3, 4}
    # generic vehicle questions work without knowing the vehicle's number
    assert set(explain(log.entries, "Why did the ambulance get green?", engine="template")["citations"]) == {3, 4}
    log.log(55, "master@J6", "grant", "EMERGENCY_GRANTED_SWITCH", tls="J6", vehicle="police0")
    assert 6 not in explain(log.entries, "Why did the ambulance get green?", engine="template")["citations"]
    assert explain(log.entries, "Why did the fire truck get green?", engine="template")["abstained"]
    log.log(60, "master@J5", "deny", "EMERGENCY_DENIED_EXIT_FULL", tls="J5", vehicle="ambulance2",
            exit_lane="x_0", exit_occupancy=0.9)
    out = explain(log.entries, "Was any emergency vehicle denied?", engine="template")
    assert 7 in out["citations"] and not out["answer"].startswith("Nothing")


def test_incident_places_are_visible_to_the_incident_agent():
    import sumolib
    from traffix.core import config
    from traffix.simulation.network_model import load_models
    net_file = config.network_files()[0]
    net, models = sumolib.net.readNet(net_file), load_models(net_file)
    seen = {l.rsplit("_", 1)[0] for m in models.values() for l in m.incoming_lanes + m.outgoing_lanes}
    for name, edge in config.network()["places"].items():
        if "incident_edge" in name:            # the incident blocks lane 1 of a detector road
            assert edge in seen, f"{name} {edge} has no detector"
            assert net.getEdge(edge).getLaneNumber() >= 2, f"{name} {edge} has no lane 1"


def test_architecture():
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "check_architecture.py")])
    assert r.returncode == 0


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
