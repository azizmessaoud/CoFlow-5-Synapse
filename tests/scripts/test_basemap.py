import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCENARIO = ROOT / "scenarios" / "tunis-centre-6j"
sys.path.insert(0, str(ROOT / "scripts"))

import build_basemap  # noqa: E402


def test_utm_puts_osm_junctions_on_their_sumo_coordinates() -> None:
    zone, off, _, _ = build_basemap.read_location(str(SCENARIO / "tunis6j.net.xml"))
    for row in json.loads((SCENARIO / "junctions.json").read_text(encoding="utf-8"))["junctions"]:
        east, north = build_basemap.utm(row["lon"], row["lat"], zone)
        assert abs(east + off[0] - row["x"]) < 0.05, row["id"]
        assert abs(north + off[1] - row["y"]) < 0.05, row["id"]


def test_basemap_covers_network_and_is_the_gui_decal() -> None:
    meta = json.loads((SCENARIO / "tunis6j.basemap.json").read_text(encoding="utf-8"))
    _, _, conv, _ = build_basemap.read_location(str(SCENARIO / "tunis6j.net.xml"))
    x0, y0, x1, y1 = meta["bounds"]
    assert x0 <= conv[0] and y0 <= conv[1] and x1 >= conv[2] and y1 >= conv[3]
    assert meta["fit_error_px"] < 1
    for name in meta["styles"].values():
        assert (SCENARIO / name).is_file()
    decal = ET.parse(SCENARIO / "tunis6j.settings.xml").getroot().find("decal")
    assert decal.get("file") == meta["styles"]["streets"]
    assert float(decal.get("centerX")) == round((x0 + x1) / 2, 2)
    assert float(decal.get("width")) == round(x1 - x0, 2)
