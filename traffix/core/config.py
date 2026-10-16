"""Loads the YAML files in config/. Every assumption lives there, not in code."""
import json
import os
from functools import lru_cache

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def path(*parts):
    return os.path.join(ROOT, *parts)


@lru_cache(maxsize=None)
def load(name):
    with open(path("config", f"{name}.yaml"), encoding="utf-8") as f:
        return yaml.safe_load(f)


def simulation():
    return load("simulation")


def agents():
    return load("agents")


def scenarios():
    return resolve(load("scenarios"))


def calendar():
    return load("calendar")


def network_name():
    return os.environ.get("TRAFFIX_NETWORK", simulation()["network"])


def network():
    """Per-network settings: folder, bus lines and scenario event places."""
    return load(f"networks/{network_name()}")


def network_files():
    name = network_name()
    folder = path(*network()["dir"].split("/"))
    return (os.path.join(folder, f"{name}.net.xml"),
            os.path.join(folder, f"{name}_actuated.net.xml"))


def demand():
    """Demand settings from simulation.yaml, with the current network's overrides."""
    return {**simulation()["demand"], **network().get("demand", {})}


def bus_lines():
    return [tuple(line) for line in network().get("bus_lines", [])]


def line_routes(net=None):
    """Full route (edges) and stop ids per bus line from <network>.lines.json, or {} if the network
    has none (then a line follows the shortest bus path from its entry to its exit edge).
    With a sumolib net, lines whose edges are not all in it (stale lines.json) are left out."""
    f = network_files()[0].replace(".net.xml", ".lines.json")
    if not os.path.exists(f):
        return {}
    with open(f, encoding="utf-8") as fh:
        lines = json.load(fh)["lines"]
    if net is not None:
        stale = [lid for lid, r in lines.items() if not all(net.hasEdge(e) for e in r["edges"])]
        if stale:
            print(f"lines.json does not match the network, leaving out lines {stale}; "
                  "rerun scripts/import_transtu_lines.py")
        lines = {lid: r for lid, r in lines.items() if lid not in stale}
    return lines


def resolve(value):
    """Replace "@place" strings with the current network's place (deep copy)."""
    if isinstance(value, dict):
        return {k: resolve(v) for k, v in value.items()}
    if isinstance(value, list):
        return [resolve(v) for v in value]
    if isinstance(value, str) and value.startswith("@"):
        places = network().get("places", {})
        if value[1:] not in places:
            raise KeyError(f"network {network_name()!r} has no place {value[1:]!r}")
        return places[value[1:]]
    return value
