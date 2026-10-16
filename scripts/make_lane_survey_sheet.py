"""Printable field-survey sheet for the J1..J6 approaches, generated from lane_overrides.json.

    python scripts/make_lane_survey_sheet.py   ->  scenarios/tunis-centre-6j/field-survey-sheet.html

One page per junction. Each OSM way gets one row per direction that meets the
junction, labelled with the OSM node-order direction so the result can be
entered as lanes / lanes:forward / lanes:backward without guessing.
"""

from __future__ import annotations

import json
import sys
from html import escape
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lane_overrides  # noqa: E402

SCENARIO = lane_overrides.ROOT / "scenarios" / "tunis-centre-6j"
OUT = SCENARIO / "field-survey-sheet.html"

CSS = """
@page { size: A4 landscape; margin: 10mm; }
body { font: 10pt/1.3 system-ui, "Segoe UI", Arial, sans-serif; color: #111; background: #fff; margin: 0 16px; }
h1 { font-size: 14pt; margin: 8px 0 2px; } h2 { font-size: 12pt; margin: 0 0 4px; }
.page { page-break-after: always; padding-top: 6px; } .page:last-child { page-break-after: auto; }
.meta, .rules { font-size: 8.5pt; color: #333; margin: 2px 0 6px; }
.rules li { margin: 1px 0; }
table { border-collapse: collapse; width: 100%; table-layout: fixed; }
th, td { border: 1px solid #555; padding: 3px 4px; vertical-align: top; font-size: 8.5pt; }
th { background: #eee; text-align: left; }
td.blank { height: 30px; } .ids { font-family: Consolas, monospace; font-size: 8pt; }
.box { display: inline-block; width: 10px; height: 10px; border: 1px solid #333; margin: 0 2px -1px 6px; }
.status { font-size: 8pt; color: #a00; } .wrap { overflow-x: auto; }
"""


def rows_for(way: dict, junction: str) -> list[tuple[str, str]]:
    """(role, direction label) for each direction of ``way`` that meets ``junction``."""
    sense = way["node_order_at_junctions"][junction]
    if way["oneway"]:
        out = []
        if sense["approach"]:
            out.append(("APPROACH", "one-way, towards junction"))
        if sense["exit"]:
            out.append(("EXIT", "one-way, away from junction"))
        return out
    return [("APPROACH", f"two-way: travels {sense['approach_direction'].upper()} (OSM node order)"),
            ("EXIT", f"two-way: travels {sense['exit_direction'].upper()} (OSM node order)")]


def page(junction: dict, ways: list[dict]) -> str:
    jid = junction["id"]
    rows = []
    for way in ways:
        for role, direction in rows_for(way, jid):
            name = way.get("name_fr") or way.get("name") or "(unnamed)"
            approach = role == "APPROACH"
            rows.append(f"""<tr>
<td class="ids"><b>{escape(way['osm_way_id'])}</b><br>{escape(way['highway'])}<br><span class="status">{escape(way['status'])}</span></td>
<td>{escape(name)}<br><b>{role}</b><br>{escape(direction)}</td>
<td class="blank">{'general lanes at stop line: ____<br>arrows L&rarr;R: ______________' if approach else 'general lanes: ____'}</td>
<td class="blank">bus-only: ____<br>other restricted: ____<br>parking lane<span class="box"></span></td>
<td class="blank">posted: ____ km/h<br>no sign<span class="box"></span></td>
<td class="blank">{'length ____ m<br>width ____ m<br>refuge<span class="box"></span>' if approach else ''}</td>
<td class="blank">{'ped signal<span class="box"></span> green ___ s<br>flash ___ s button<span class="box"></span>' if approach else ''}</td>
<td class="blank">count changes along way?<span class="box"></span><br>where: ________</td>
<td class="blank">photo ID: ______<br>date/time: ______<br>GPS: ______ heading: ___&deg;</td>
<td class="blank">reviewer: ______<br>confidence H / M / L</td>
</tr>""")
    return f"""<section class="page">
<h2>{jid} &middot; {escape(junction['name'])}</h2>
<p class="meta">OSM node <span class="ids">{junction['osm_node_id']}</span> &middot; {junction['lat']:.6f}, {junction['lon']:.6f}
&middot; Junction control observed: vehicle signals on every entry<span class="box"></span> some entries<span class="box"></span> none (priority/roundabout)<span class="box"></span>
&middot; signal heads photographed<span class="box"></span> &middot; date ______ time ______</p>
<div class="wrap"><table>
<colgroup><col style="width:9%"><col style="width:15%"><col style="width:13%"><col style="width:10%"><col style="width:8%">
<col style="width:8%"><col style="width:10%"><col style="width:9%"><col style="width:11%"><col style="width:7%"></colgroup>
<tr><th>OSM way / class / status</th><th>Street, role, direction</th><th>Vehicle lanes &amp; turn arrows</th><th>Restricted lanes</th>
<th>Speed sign</th><th>Crossing on this leg</th><th>Pedestrian signal</th><th>Uniform?</th><th>Photo evidence</th><th>Review</th></tr>
{''.join(rows)}
</table></div>
</section>"""


def main() -> int:
    data = lane_overrides.load()
    manifest = json.loads((SCENARIO / "junctions.json").read_text(encoding="utf-8"))
    pending = sorted((w["osm_way_id"] for w in data["ways"] if w["status"] == "unverified"), key=int)
    pages = []
    for junction in manifest["junctions"]:
        ways = [w for w in data["ways"] if junction["id"] in w["junctions"]]
        pages.append(page(junction, sorted(ways, key=lambda w: int(w["osm_way_id"]))))
    html = f"""<title>Tunis J1–J6 lane survey</title>
<style>{CSS}</style>
<h1>Tunis centre-ville J1–J6: lane and crossing field survey</h1>
<ul class="rules">
<li>Count vehicle lanes <b>at the stop line</b>, left to right as seen by an approaching driver. Do not count parking bays. Write each lane's arrows (e.g. <code>L|T|TR</code>); write <code>?</code> where unmarked.</li>
<li>Bus-only or other restricted lanes go in their own column, not in the general count. If the count changes before the junction, tick "count changes" and note where: the way must be split before the value can be applied.</li>
<li>"Forward/backward" follow the OSM way's node order, not compass direction. The direction is printed on each row.</li>
<li>Every row needs a dated, geotagged photo showing the markings, plus the camera heading. Undated imagery or road width alone does not verify a count.</li>
<li>Speeds: Tunisia's urban limit is 50 km/h unless a sign shows a 30 or 70 km/h decision. Record the sign actually posted.</li>
<li>Still unverified ({len(pending)}): <span class="ids">{', '.join(pending)}</span></li>
</ul>
{''.join(pages)}
"""
    OUT.write_text(html, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.relative_to(lane_overrides.ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
