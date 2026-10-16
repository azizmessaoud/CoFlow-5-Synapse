"""
Community-published TRANSTU-attributed bus line geometry on a SUMO network: stops,
routes and the traffix bus_lines config. This is not an official timetable or GTFS feed.

  py -3.11 scripts\\import_transtu_lines.py            use the committed clipped stop list
  py -3.11 scripts\\import_transtu_lines.py --fetch    refresh it from the TRANSTU visualisation

Source: the stop list behind https://hobbes-286.github.io/transtu-visualisation/
(busdata.js: line, stop order, stop name, lon, lat). Every line variant ("74", "74 Retour")
with at least two stops inside the network becomes one SUMO line.

For each line the stops are snapped to bus lanes. Lane and direction are chosen together
(cheapest route through all stops), so outbound and return stops land on the right side
of two-way streets. The bus enters at the border road nearest to where the real line
crosses into the box and leaves the same way.

Writes next to the net file:
  <name>.stops.xml      busStops with the TRANSTU names and the lines serving them
  <name>.lines.json     per line: full edge list, stops, headway, provenance
  <name>.transtu.csv    the clipped source rows (only lines that reach the network)
and replaces the bus_lines block of config/networks/<name>.yaml.
"""
import argparse
import csv
import hashlib
import json
import math
import os
import re
import urllib.request
from xml.sax.saxutils import escape

import sumolib

import _path  # noqa: F401
from build_basemap import read_location, utm
from traffix.core import config

SOURCE = "https://hobbes-286.github.io/transtu-visualisation/busdata.js"
HEADWAY = 900          # s: a TRANSTU bus every 15 minutes per line and direction
SNAP = 45              # m: farthest a stop may be from a bus lane
STOP_LENGTH = 15       # m
SKIPS = (150, 300, 600, math.inf)   # m of extra driving a skipped stop is worth, tried in turn
ON_ROUTE = 80          # m: farthest a skipped stop may be placed from its TRANSTU position


def line_id(name):
    """'74 Retour' -> '74_R', '43 B (Retour)' -> '43B_R': safe for SUMO's space-separated lines."""
    back = re.search(r"retour", name, re.I) is not None
    base = re.sub(r"\(?\s*retour\s*\)?", "", name, flags=re.I).strip()
    base = re.sub(r"[^0-9A-Za-z]", "", base)
    return base + ("_R" if back else "")


def stop_name(name):
    return re.sub(r"[\s-]+(ALLER|RETOUR)\s*$", "", name, flags=re.I).strip().title()


def read_source(fetch, cache_csv):
    if fetch:
        req = urllib.request.Request(SOURCE, headers={"user-agent": "coflow5-transtu/1.0"})
        text = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
        rows = re.findall(r"\['([^']*)','(\d+)',\"([^\"]*)\",'([-\d.]+)','([-\d.]+)'\]", text)
        return [(r[0], int(r[1]), r[2], float(r[3]), float(r[4])) for r in rows], \
            hashlib.sha256(text.encode("utf-8")).hexdigest()
    with open(cache_csv, encoding="utf-8", newline="") as f:
        rows = [(r["line"], int(r["order"]), r["name"], float(r["lon"]), float(r["lat"])) for r in csv.DictReader(f)]
    with open(cache_csv.replace(".transtu.csv", ".lines.json"), encoding="utf-8") as f:
        return rows, json.load(f)["source_sha256"]


def clip(p, q, box):
    """Point where segment p->q first crosses into box (Liang-Barsky), or None."""
    (x0, y0), (dx, dy) = p, (q[0] - p[0], q[1] - p[1])
    t0, t1 = 0.0, 1.0
    for d, lo, hi, s in ((dx, box[0], box[2], x0), (dy, box[1], box[3], y0)):
        if abs(d) < 1e-9:
            if not lo <= s <= hi:
                return None
            continue
        a, b = (lo - s) / d, (hi - s) / d
        t0, t1 = max(t0, min(a, b)), min(t1, max(a, b))
    return (x0 + t0 * dx, y0 + t0 * dy) if t0 <= t1 else None


class Router:
    def __init__(self, net):
        self.net, self.cache = net, {}

    def path(self, a, b):
        key = (a.getID(), b.getID())
        if key not in self.cache:
            p, cost = self.net.getShortestPath(a, b, vClass="bus")
            self.cache[key] = (p, cost if p else math.inf)
        return self.cache[key]

    def between(self, a, pos_a, b, pos_b):
        """Driving distance from pos_a on edge a to pos_b on edge b."""
        if a is b:
            return pos_b - pos_a if pos_b >= pos_a - 1 else math.inf
        p, cost = self.path(a, b)
        return cost - pos_a - (b.getLength() - pos_b) if p else math.inf


def candidates(net, x, y):
    out = {}
    for lane, dist in net.getNeighboringLanes(x, y, SNAP, includeJunctions=False):
        edge = lane.getEdge()
        if not lane.allows("bus") or edge.getFunction():
            continue
        pos, d = lane.getClosestLanePosAndDist((x, y))
        if edge.getID() not in out or d < out[edge.getID()][2]:
            out[edge.getID()] = (edge, lane, d, pos)
    return sorted(out.values(), key=lambda c: c[2])[:8]


def border_edges(net, entering):
    """Bus edges that start (entering) or end (leaving) at the edge of the clipped network."""
    out = []
    for e in net.getEdges():
        if e.getFunction() or not e.allows("bus"):
            continue
        node = e.getFromNode() if entering else e.getToNode()
        other = e.getToNode() if entering else e.getFromNode()
        links = node.getIncoming() if entering else node.getOutgoing()
        if all(x.getFunction() or (x.getFromNode() if entering else x.getToNode()) is other for x in links):
            out.append(e)
    return out


def snap_line(stops, router, skip=math.inf):
    """Viterbi over stop candidates: the lane choice that gives the cheapest consistent route.
    A stop may be skipped for `skip` metres when serving it would force a loop (one-way streets,
    or a stop coordinate on the wrong street). Returns one candidate per layer, None = skipped."""
    # state: (candidate the bus is on, cost, back index, skipped this layer)
    layers = [[(c, 2.0 * c[2], None, False) for c in stops[0]["cands"]]]
    for s in stops[1:]:
        prev, layer = layers[-1], []
        for c in s["cands"]:
            best = (math.inf, None)
            for i, (pc, cost, _, _) in enumerate(prev):
                step = router.between(pc[0], pc[3], c[0], c[3])
                best = min(best, (cost + step + 2.0 * c[2], i), key=lambda t: t[0])
            layer.append((c, best[0], best[1], False))
        if s.get("skippable") and skip < math.inf:
            layer += [(pc, cost + skip, i, True) for i, (pc, cost, _, _) in enumerate(prev)]
        layers.append(layer)
    end = min(range(len(layers[-1])), key=lambda i: layers[-1][i][1])
    if layers[-1][end][1] == math.inf:
        return None
    chosen, i = [], end
    for layer in reversed(layers):
        chosen.append(None if layer[i][3] else layer[i][0])
        i = layer[i][2]
    return chosen[::-1]


def on_route(net, route, start, end, xy):
    """Closest bus-lane point to xy on route[start:end], as a snap candidate, or None if too far."""
    best = None
    for edge in route[start:end]:
        for lane in edge.getLanes():
            if lane.allows("bus"):
                pos, d = lane.getClosestLanePosAndDist(xy)
                if d <= ON_ROUTE and (best is None or d < best[2]):
                    best = (edge, lane, d, pos)
                break
    return best


def border_cands(edges, point, entering):
    """Border roads nearest to where the real line crosses the box, as snap candidates.
    The distance is halved because snap_line weighs it twice."""
    end = 0 if entering else -1
    near = sorted(edges, key=lambda e: _dist(e.getShape()[end], point))[:8]
    return [(e, None, _dist(e.getShape()[end], point) / 2, 0.0 if entering else e.getLength()) for e in near]


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def join(router, edges):
    route = [edges[0]]
    for e in edges[1:]:
        if e is route[-1]:
            continue
        p, _ = router.path(route[-1], e)
        route += list(p[1:])
    return route


def build(net_file, fetch):
    name = os.path.basename(net_file).replace(".net.xml", "")
    folder = os.path.dirname(net_file)
    cache_csv = os.path.join(folder, f"{name}.transtu.csv")
    rows, sha = read_source(fetch, cache_csv)
    zone, off, conv, _ = read_location(net_file)
    net = sumolib.net.readNet(net_file)
    router = Router(net)
    box = (conv[0] + 15, conv[1] + 15, conv[2] - 15, conv[3] - 15)
    inside = lambda p: box[0] <= p[0] <= box[2] and box[1] <= p[1] <= box[3]
    entries, exits = border_edges(net, True), border_edges(net, False)

    by_line = {}
    for line, order, stop, lon, lat in rows:
        e, n = utm(lon, lat, zone)
        by_line.setdefault(line, []).append({"order": order, "name": stop, "lon": lon, "lat": lat,
                                             "xy": (e + off[0], n + off[1])})
    lines, stops, kept_rows, report = {}, {}, [], []
    def inbox(seq):
        """(first, last) index of the longest run of stops inside the box, or None."""
        runs, start = [], None
        for k, f in enumerate([inside(x["xy"]) for x in seq] + [False]):
            if f and start is None:
                start = k
            if not f and start is not None:
                runs.append((start, k - 1))
                start = None
        return max(runs, key=lambda r: r[1] - r[0]) if runs else None

    ordered = {raw: sorted(by_line[raw], key=lambda x: x["order"]) for raw in by_line}
    in_names = {}
    for raw, seq in ordered.items():
        r = inbox(seq)
        in_names[raw] = [stop_name(x["name"]) for x in seq[r[0]:r[1] + 1]] if r else []
    for raw in sorted(by_line):
        seq, reversed_note = ordered[raw], None
        outbound = next((o for o in by_line if line_id(o) + "_R" == line_id(raw)), None)
        if outbound and in_names[raw] and in_names[outbound] == in_names[raw]:
            seq = seq[::-1]                  # source repeats the outbound stops here: run them backwards
            reversed_note = f"note {raw}: same stops in the same order as {outbound} in the source, reversed"
        r = inbox(seq)
        if not r or r[1] - r[0] < 1:
            continue
        i, j = r
        kept_rows += [(raw, x["order"], x["name"], x["lon"], x["lat"]) for x in seq]   # offline copy: every line here
        run = seq[i:j + 1]
        for s in run:
            s["cands"] = candidates(net, *s["xy"])
        run = [s for s in run if s["cands"]]
        if not run:
            report.append(f"skip {raw}: no stop within {SNAP} m of a bus lane")
            continue
        lid = line_id(raw)
        # entry and exit roads take part in the lane choice, so one-way streets do not force loops
        p_in = clip(seq[i - 1]["xy"], run[0]["xy"], box) if i > 0 else None
        p_out = clip(seq[j + 1]["xy"], run[-1]["xy"], box) if j + 1 < len(seq) else None
        for s in run:
            s["skippable"] = True
        if not p_out:
            run[-1]["skippable"] = False         # a terminus: skipping it would just cut the route short
        layers = ([{"cands": border_cands(entries, p_in, True)}] if p_in else []) + run + \
            ([{"cands": border_cands(exits, p_out, False)}] if p_out else [])
        # cheapest skip penalty giving a loop-free route that serves every stop; otherwise loop-free
        # with the most stops; a loop means driving round a block to reach a stop, which buses do not do
        best = None
        for skip in SKIPS if len(run) >= 2 else ():
            chosen = snap_line(layers, router, skip)
            if not chosen:
                continue
            route = join(router, [c[0] for c in chosen if c is not None])
            stops_only = chosen[1 if p_in else 0:len(chosen) - (1 if p_out else 0)]
            served, missing, k = [], [], 0
            for idx, (st, c) in enumerate(zip(run, stops_only)):
                if c is None:          # the return bus often uses a parallel one-way street
                    # only between the previous and the next served stop, so stop order is kept
                    nxt = next((x for x in stops_only[idx + 1:] if x is not None), None)
                    end = next((n for n in range(k, len(route)) if nxt and route[n] is nxt[0]), len(route))
                    c = on_route(net, route, k, end + 1, st["xy"])
                    if c is None:
                        missing.append(stop_name(st["name"]))
                        continue
                k = next((n for n in range(k, len(route)) if route[n] is c[0]), k)
                served.append((st, c))
            nodes = [e.getFromNode().getID() for e in route]
            rank = (len(served) > 0, len(set(nodes)) == len(nodes), len(served))
            if best is None or rank > best[3]:
                best = (route, served, missing, rank)
            if rank[1] and not missing:
                break
        if not best or not best[1]:
            report.append(f"skip {raw}: no stop reachable by bus")
            continue
        route, served, missing, rank = best
        if not rank[1]:
            report.append(f"note {raw}: route still loops")
        report += [f"note {raw}: stop {m} not on any bus route, left out" for m in missing]
        length = sum(e.getLength() for e in route)
        ids = []
        for s, (edge, lane, _, pos) in served:
            key = next((k for k, v in stops.items() if v["lane"] == lane.getID() and abs(v["pos"] - pos) < 25), None)
            if key is None:
                key = f"ts_{len(stops) + 1}"
                stops[key] = {"lane": lane.getID(), "pos": pos, "length": lane.getLength(), "name": stop_name(s["name"]),
                              "edge": edge.getID(), "lines": []}
            if lid not in stops[key]["lines"]:
                stops[key]["lines"].append(lid)
            ids.append(key)
        lines[lid] = {"name": f"Ligne {re.sub(r'_R$', '', lid)}", "transtu": raw,
                      "direction": "retour" if lid.endswith("_R") else "aller",
                      "from": stop_name(seq[0]["name"]), "to": stop_name(seq[-1]["name"]),
                      "edges": [e.getID() for e in route], "stops": ids, "headway": HEADWAY,
                      "length_m": round(length)}
        report += [reversed_note] if reversed_note else []
        report.append(f"line {lid:7s} {len(ids)} stops, {len(route)} edges, {length:.0f} m")

    # next traffic light downstream of each stop (for the junction param the transit agents read)
    for lid, line in lines.items():
        for sid in line["stops"]:
            st = stops[sid]
            if "junction" in st:
                continue
            k, ahead = line["edges"].index(st["edge"]), -st["pos"]
            for eid in line["edges"][k:]:
                ahead += net.getEdge(eid).getLength()
                node = net.getEdge(eid).getToNode()
                if node.getType() == "traffic_light":
                    st["junction"] = node.getID() if ahead < 250 else ""
                    break
    out = ["<additional>"]
    for sid, st in stops.items():
        start = max(0.0, min(st["pos"] - STOP_LENGTH / 2, st["length"] - STOP_LENGTH))
        end = min(st["length"], start + STOP_LENGTH)
        out.append(f'  <busStop id="{sid}" lane="{st["lane"]}" startPos="{start:.1f}" endPos="{end:.1f}" '
                   f'lines="{" ".join(st["lines"])}" name="{escape(st["name"], {chr(34): "&quot;"})}">'
                   f'<param key="junction" value="{st.get("junction", "")}"/></busStop>')
    out.append("</additional>")
    with open(os.path.join(folder, f"{name}.stops.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    with open(os.path.join(folder, f"{name}.lines.json"), "w", encoding="utf-8") as f:
        json.dump({"source": SOURCE, "source_sha256": sha,
                   "source_status": "community-published visualization; not independently verified as an official TRANSTU feed",
                   "note": "TRANSTU-attributed stop/line geometry; routes snapped to OSM roads. Headways are assumed, not timetabled.",
                   "lines": lines}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    with open(cache_csv, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["line", "order", "name", "lon", "lat"])
        w.writerows(sorted(kept_rows, key=lambda r: (r[0], r[1])))
    write_config(name, lines)
    spec_file = os.path.join(folder, "junctions.json")
    if os.path.exists(spec_file):                 # which stops sit before each light
        with open(spec_file, encoding="utf-8") as f:
            spec = json.load(f)
        for row in spec["junctions"]:
            row["bus_stops"] = sorted(k for k, v in stops.items() if v.get("junction") == row["tls_id"])
        with open(spec_file, "w", encoding="utf-8") as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
            f.write("\n")
    print("\n".join(report))
    print(f"{len(lines)} lines, {len(stops)} stops")
    return lines, stops


def write_config(name, lines):
    path = config.path("config", "networks", f"{name}.yaml")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    block = ["# Real TRANSTU lines (entry edge, exit edge), from scripts/import_transtu_lines.py.",
             f"# Full routes and stops: {name}.lines.json / {name}.stops.xml. Headways are assumed.",
             "bus_lines:"]
    block += [f'  - ["{lid}", "{line["edges"][0]}", "{line["edges"][-1]}"]    # {line["name"]} {line["direction"]}: '
              f'{line["from"]} -> {line["to"]}' for lid, line in lines.items()]
    pattern = r"(?ms)^# (Illustrative bus lines|Real TRANSTU lines).*?^bus_lines:\n(?:  - [^\n]*\n)+"
    new = re.sub(pattern, lambda m: "\n".join(block) + "\n", text)
    if not re.search(pattern, text):
        raise SystemExit(f"could not find the bus_lines block in {path}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--net", default=None, help="net.xml (default: the current traffix network)")
    p.add_argument("--fetch", action="store_true", help="download the stop list instead of the committed copy")
    a = p.parse_args()
    build(os.path.abspath(a.net or config.network_files()[0]), a.fetch)
