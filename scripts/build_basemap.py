"""
Street-map background for a SUMO network, already warped into the network's own x/y metres.

  py -3.11 scripts\\build_basemap.py                       current traffix network (tunis6j)
  py -3.11 scripts\\build_basemap.py --net scenarios\\tunis-centre-6j\\tunis6j.net.xml

Writes next to the net file:
  <name>.basemap.jpg    street map: sumo-gui decal (<name>.settings.xml), web app offline fallback
  <name>.basemap.json   the x/y box the image covers, the attribution, and the exact
                        net x/y <-> web-map transform the web app uses to place live tiles
                        (sharp at every zoom, streets or satellite)

Tiles come from Esri's ArcGIS Online services (as in SUMO's tileGet.py) and are cached in
data/generated/tiles. The web app darkens the street map itself for its dark theme.
SUMO's tileGet.py places tiles axis-aligned; this network is UTM, about 0.7 degrees
rotated from web-map tiles, so each tile is resampled here instead.
"""
import argparse
import json
import math
import os
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image

import _path  # noqa: F401
from traffix.core import config

SERVICES = {  # style -> ArcGIS Online tile service; only "streets" is also baked into an image
    "streets": "World_Street_Map",
    "satellite": "World_Imagery",
}
TILE_URL = "https://server.arcgisonline.com/ArcGIS/rest/services/{service}/MapServer/tile/{{z}}/{{y}}/{{x}}"
MAX_ZOOM = 19             # deepest zoom both services cover in Tunis
ATTRIBUTION = "Tiles © Esri — Esri, HERE, Garmin, OpenStreetMap contributors, Maxar, Earthstar Geographics"
TILE = 256


def utm(lon, lat, zone):
    """WGS84 lon/lat -> UTM easting/northing (Krüger series, centimetre accurate)."""
    a, f, k0 = 6378137.0, 1 / 298.257223563, 0.9996
    n = f / (2 - f)
    big_a = a / (1 + n) * (1 + n ** 2 / 4 + n ** 4 / 64)
    alpha = (n / 2 - 2 * n ** 2 / 3 + 5 * n ** 3 / 16, 13 * n ** 2 / 48 - 3 * n ** 3 / 5, 61 * n ** 3 / 240)
    phi, lam = math.radians(lat), math.radians(lon - (zone * 6 - 183))
    c = 2 * math.sqrt(n) / (1 + n)
    t = math.sinh(math.atanh(math.sin(phi)) - c * math.atanh(c * math.sin(phi)))
    xi, eta = math.atan2(t, math.cos(lam)), math.atanh(math.sin(lam) / math.sqrt(1 + t * t))
    east = 500000 + k0 * big_a * (eta + sum(alpha[j] * math.cos(2 * (j + 1) * xi) * math.sinh(2 * (j + 1) * eta)
                                            for j in range(3)))
    north = k0 * big_a * (xi + sum(alpha[j] * math.sin(2 * (j + 1) * xi) * math.cosh(2 * (j + 1) * eta)
                                   for j in range(3)))
    return east, north + (0 if lat >= 0 else 10000000)


def read_location(net_file):
    with open(net_file, encoding="utf-8") as f:
        head = f.read(20000)
    loc = re.search(r"<location ([^>]*)/>", head).group(1)
    attr = dict(re.findall(r'(\w+)="([^"]*)"', loc))
    zone = re.search(r"\+zone=(\d+)", attr["projParameter"])
    if not zone or "+proj=utm" not in attr["projParameter"]:
        raise SystemExit(f"only UTM networks are supported, got {attr['projParameter']}")
    off = [float(v) for v in attr["netOffset"].split(",")]
    conv = [float(v) for v in attr["convBoundary"].split(",")]
    orig = [float(v) for v in attr["origBoundary"].split(",")]
    return int(zone.group(1)), off, conv, orig


def world_pixel(lon, lat, zoom):
    """Web-Mercator pixel of lon/lat at this zoom (tiles are 256 px)."""
    s = TILE * 2 ** zoom
    y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    return (lon + 180) / 360 * s, (1 - y / math.pi) / 2 * s


def fetch(style, zoom, x, y, cache):
    path = os.path.join(cache, style, str(zoom), f"{x}_{y}.jpg")
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        url = f"https://server.arcgisonline.com/ArcGIS/rest/services/{style}/MapServer/tile/{zoom}/{y}/{x}"
        req = urllib.request.Request(url, headers={"user-agent": "coflow5-basemap/1.0"})
        for attempt in range(4):
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    data = r.read()
                break
            except OSError:
                if attempt == 3:
                    raise
        with open(path, "wb") as out:
            out.write(data)
    return path


def build(net_file, zoom, res, margin, cache):
    zone, off, conv, orig = read_location(net_file)
    lon0, lat0, lon1, lat1 = orig
    pad = 2 * margin / 111000                          # degrees, generous
    lon0, lat0, lon1, lat1 = lon0 - pad, lat0 - pad, lon1 + pad, lat1 + pad
    px0, py0 = world_pixel(lon0, lat1, zoom)
    px1, py1 = world_pixel(lon1, lat0, zoom)
    tx0, ty0, tx1, ty1 = int(px0 // TILE), int(py0 // TILE), int(px1 // TILE), int(py1 // TILE)

    # net x/y -> mosaic pixel is affine to well under a pixel over a few km: fit it on a grid
    src, dst = [], []
    for lon in np.linspace(lon0, lon1, 12):
        for lat in np.linspace(lat0, lat1, 12):
            e, n = utm(lon, lat, zone)
            px, py = world_pixel(lon, lat, zoom)
            src.append((e + off[0], n + off[1], 1.0))
            dst.append((px - tx0 * TILE, py - ty0 * TILE))
    src, dst = np.array(src), np.array(dst)
    m, *_ = np.linalg.lstsq(src, dst, rcond=None)
    err = np.abs(src @ m - dst).max()
    # the same transform with zoom-free web-map coordinates (u, v in 0..1, v down) for the browser
    scale = TILE * 2 ** zoom
    to_merc = (m + np.array([[0, 0], [0, 0], [tx0 * TILE, ty0 * TILE]])) / scale
    full = np.array([[to_merc[0, 0], to_merc[1, 0], to_merc[2, 0]],
                     [to_merc[0, 1], to_merc[1, 1], to_merc[2, 1]], [0, 0, 1]])
    back = np.linalg.inv(full)

    x0, y0, x1, y1 = conv[0] - margin, conv[1] - margin, conv[2] + margin, conv[3] + margin
    w, h = round((x1 - x0) / res), round((y1 - y0) / res)
    # output pixel (i, j) -> net (x0 + i*res, y1 - j*res) -> mosaic pixel
    a, d = m[0] * res, -m[1] * res
    c = m[0] * x0 + m[1] * y1 + m[2]
    coeffs = (a[0], d[0], c[0], a[1], d[1], c[1])

    tiles = [(x, y) for x in range(tx0, tx1 + 1) for y in range(ty0, ty1 + 1)]
    files = {}
    for name, suffix, style in (("streets", "", SERVICES["streets"]),):
        with ThreadPoolExecutor(6) as pool:
            paths = list(pool.map(lambda t: fetch(style, zoom, *t, cache), tiles))
        mosaic = Image.new("RGB", ((tx1 - tx0 + 1) * TILE, (ty1 - ty0 + 1) * TILE))
        for (x, y), p in zip(tiles, paths):
            mosaic.paste(Image.open(p).convert("RGB"), ((x - tx0) * TILE, (y - ty0) * TILE))
        out = net_file.replace(".net.xml", f".basemap{suffix}.jpg")
        mosaic.transform((w, h), Image.AFFINE, coeffs, Image.BICUBIC).save(out, quality=85, optimize=True)
        files[name] = os.path.basename(out)
        print(f"wrote {out} ({w}x{h} px, {len(tiles)} tiles, {style})")

    meta = {"bounds": [round(v, 2) for v in (x0, y0, x1, y1)], "zoom": zoom, "metres_per_pixel": res,
            "attribution": ATTRIBUTION, "styles": files,
            "tiles": {name: TILE_URL.format(service=svc) for name, svc in SERVICES.items()}, "max_zoom": MAX_ZOOM,
            "net_to_merc": [float(v) for v in full[:2].ravel()], "merc_to_net": [float(v) for v in back[:2].ravel()],
            "fit_error_px": round(float(err), 4)}
    with open(net_file.replace(".net.xml", ".basemap.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
        f.write("\n")
    add_decal(net_file, meta)
    print(f"projection fit error {err:.4f} px")


def decal_line(meta):
    x0, y0, x1, y1 = meta["bounds"]
    return (f'  <decal file="{meta["styles"]["streets"]}" centerX="{(x0 + x1) / 2:.2f}" centerY="{(y0 + y1) / 2:.2f}" '
            f'width="{x1 - x0:.2f}" height="{y1 - y0:.2f}" rotation="0.00" layer="-10"/>')


def add_decal(net_file, meta):
    """Put the street map behind the network in <name>.settings.xml (replacing an older one)."""
    settings = net_file.replace(".net.xml", ".settings.xml")
    if not os.path.exists(settings):
        return
    with open(settings, encoding="utf-8") as f:
        lines = [ln for ln in f.read().splitlines() if "<decal " not in ln]
    end = lines.index("</viewsettings>")
    lines.insert(end, decal_line(meta))
    with open(settings, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"updated {settings}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--net", default=None, help="net.xml (default: the current traffix network)")
    p.add_argument("--zoom", type=int, default=19, help="tile zoom (19 is about 0.24 m per pixel here)")
    p.add_argument("--res", type=float, default=0.25, help="output metres per pixel")
    p.add_argument("--margin", type=float, default=40, help="metres of map around the network")
    a = p.parse_args()
    build(os.path.abspath(a.net or config.network_files()[0]), a.zoom, a.res, a.margin,
          config.path("data", "generated", "tiles"))
