import json
import xml.etree.ElementTree as ET
from pathlib import Path

import sumolib

from traffix.core import config

ROOT = Path(__file__).resolve().parents[2]
SCENARIO = ROOT / "scenarios" / "tunis-centre-6j"


def lines() -> dict:
    return json.loads((SCENARIO / "tunis6j.lines.json").read_text(encoding="utf-8"))["lines"]


def test_config_lines_are_the_imported_transtu_lines() -> None:
    routes = lines()
    assert [line for line, _, _ in config.bus_lines()] == list(routes)
    for line, first, last in config.bus_lines():
        assert " " not in line and routes[line]["transtu"]
        assert (first, last) == (routes[line]["edges"][0], routes[line]["edges"][-1])


def test_routes_are_connected_bus_legal_and_loop_free_except_at_a_terminus() -> None:
    net = sumolib.net.readNet(str(SCENARIO / "tunis6j.net.xml"))
    for line, route in lines().items():
        edges = [net.getEdge(e) for e in route["edges"]]
        assert all(e.allows("bus") for e in edges), line
        for a, b in zip(edges, edges[1:]):
            assert b in a.getOutgoing(), (line, a.getID(), b.getID())
        assert route["length_m"] < 2 * 1500, line       # no tour of the 1.4 km box


def test_each_line_stops_on_its_own_route_in_order() -> None:
    stops = {s.get("id"): s for s in ET.parse(SCENARIO / "tunis6j.stops.xml").getroot().findall("busStop")}
    for line, route in lines().items():
        assert route["stops"], line
        k = 0
        for sid in route["stops"]:
            stop = stops[sid]
            assert line in stop.get("lines").split()
            edge = stop.get("lane").rsplit("_", 1)[0]
            k = route["edges"].index(edge, k)            # raises if the stop is off the route or out of order
    served = {line for s in stops.values() for line in s.get("lines").split()}
    assert served == set(lines())
