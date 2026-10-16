# Tunis centre-ville, six junctions

OpenStreetMap road geometry for central Tunis, rebuilt from the Geofabrik
Tunisia snapshot containing data through 2026-10-15 20:21 UTC. The PBF and
clipped OSM XML hashes are in `junctions.json`. Only the six selected junctions
carry traffic lights. Road demand is synthetic; this is a showcase, not a
field-survey-verified model.

## Run

```powershell
py -3.11 scripts\watch_sumo.py tunis6j          # GUI, fixed-time plans
sumo-gui -c scenarios\tunis-centre-6j\tunis6j_actuated.sumocfg
```

Rebuild from the committed OSM (needs `SUMO_HOME` or `pip install eclipse-sumo==1.27.1`):

```powershell
py -3.11 scripts\build_tunis_centre_6j.py
py -3.11 -m pytest tests\scripts\test_tunis_centre_6j.py tests\scripts\test_lane_overrides.py -q
py -3.11 scripts\lane_overrides.py --strict     # release check: fails while any J1..J6 road is not lane-verified
```

`--require-verified-lanes` on the build refuses to build until every junction road has evidence.

## Junctions

| ID (node + light) | OSM node | Streets | Lat, lon | Phases | Downstream lights (≤ 800 m) |
|---|---|---|---|---|---|
| J1 | 5294059357 | Av. Habib Bourguiba / Place du 14 Janvier 2011 / Av. Mohamed V | 36.80035, 10.18588 | 6 | J3, J4, J5, J6 |
| J2 | 287386655 | Av. Habib Bourguiba / Av. de France / Rue Jamel Abdel Nasser / Rue de Rome | 36.79945, 10.17852 | 9 | J1, J4, J5, J6 |
| J3 | 287837812 | Rue Saad Zagloul / Av. Moncef Bey | 36.79474, 10.18799 | 6 | J1 |
| J4 | 287863982 | Av. Habib Thameur / Rue de Rome / Rue Mokhtar Attia | 36.80099, 10.17848 | 6 | J2, J5, J6 |
| J5 | 387151856 | Av. Habib Thameur / Rue de Sparte / Rue Salonique / Rue d'Athènes | 36.80319, 10.17933 | 9 | J2, J4, J6 |
| J6 | 517939913 | Av. Habib Bourguiba / Rue d'Alger | 36.79972, 10.17948 | 6 | J1, J2, J4 |

`junctions.json` maps each J id to its OSM node and has the incoming lanes,
signal plans, bus stops and source hashes for each junction.

## Files

| File | What |
|---|---|
| `tunis6j.osm.xml` | OSM clipped to `10.1755,36.7925,10.1910,36.8055`; ways cut at the box edge; OSM signal tags removed |
| `tunis6j.net.xml` | static (fixed-time) plans on J1..J6 |
| `tunis6j_actuated.net.xml` | same network, actuated plans |
| `tunis6j.rou.xml` | 3000 synthetic vehicles over 3600 s (randomTrips seed 20261016) |
| `tunis6j.ped.rou.xml` | 900 synthetic pedestrians (seed 20261017) |
| `tunis6j.stops.xml` | TRANSTU-attributed stop names and line geometry from a community-maintained visualization, snapped to bus lanes |
| `tunis6j.lines.json` | 25 community-published line variants routed over the OSM network; not an independently verified official feed; assumed 15 min headway |
| `tunis6j.transtu.csv` | source rows from [transtu-visualisation](https://hobbes-286.github.io/transtu-visualisation/), with provenance hash in `tunis6j.lines.json` |
| `tunis6j.basemap.jpg`, `.basemap.json` | street map warped into SUMO x/y: sumo-gui background, web map fallback, web tile transform |

Rebuild the bus lines with `py -3.11 scripts\import_transtu_lines.py` (`--fetch` to refresh the
source) and the map with `py -3.11 scripts\build_basemap.py`. Where a TRANSTU stop can only be
reached by looping round a block (one-way streets), the bus serves it where its route passes within
80 m, or the stop is left out and the import says so. Headways are assumed, not timetabled.
| `tunis6j.poi.add.xml`, `tunis6j.settings.xml` | GUI labels J1..J6 and viewport |
| `junctions.json` | junction spec and provenance manifest |
| `lane_overrides.json` | every OSM way touching J1..J6: lane evidence status, verified values, speed basis, evidence log |
| `field-survey-sheet.html` | printable survey sheet, one page per junction (`py -3.11 scripts\make_lane_survey_sheet.py`) |

The fresh central clip contains 466 road ways. Only 43 have an explicit OSM
lane-count tag; the other 423 receive SUMO defaults (see "Lane evidence" below for
the 21 junction roads). This is reported under
`network.lane_tag_coverage` in `junctions.json`. Those defaults are modelling
assumptions, not verified lane counts. Verify missing lane counts against a
current local survey or sufficiently clear, current imagery before treating the
network as a geometrically exact lane model.

The six stored junction node IDs were checked against this source snapshot;
the maximum coordinate difference is below 0.01 m. More importantly for signal
operations, only 3 of the 21 unique OSM road ways directly incident to those
signals carry an explicit lane-count tag. The remaining 18 approach ways use
SUMO defaults. An Esri World Imagery cross-check at zoom 19 was used to review
the street layout, but its imagery date is not exposed and it was not used to
certify lane counts.

## Lane evidence and real-world accuracy

`lane_overrides.json` has one entry per OSM way touching J1..J6 (21 ways). The
builder validates it, writes verified lane counts, turn lanes and speeds onto a
temporary copy of the clip before `netconvert`, records the file's SHA-256 and
what was applied under `sources.lane_overrides` in `junctions.json`, and checks
that both generated networks carry those values. `tunis6j.osm.xml` itself stays
an unmodified OSM clip.

| Status | Ways | Meaning |
|---|---|---|
| `verified` | 0 | dated field survey, authoritative plan or dated geolocated street-level imagery; applied |
| `osm_tagged` | 3 (10641416, 10641456, 26280306) | OSM lane tag used as source data, not corroborated |
| `unverified` | 18 | no evidence; lane value left `null`, SUMO's importer default is used and is **not** a real lane count |

Evidence searched on 2026-10-16/17 (logged in the file): Panoramax has 4 images
from 2019, the nearest 270 m away; KartaView has none; Wikimedia Commons has
dated photos but none shows countable stop-line markings; Esri imagery has no
capture date. Mapillary has 2015/2018 (and some 2020) phone photos covering 19
of the 30 way-directions, but almost none of these streets show lane-divider
paint near the junctions. The one readable case, 2 marked lanes on Avenue
Habib Bourguiba west of J1 (way 10641416), agrees with its OSM tag but covers
30 m of a 316 m way. **No lane count could be verified from a desk.** Unmarked
streets need a judgement of how many queues actually form at the stop line, so
record that on site and say in the evidence that the lanes are unmarked. Fill in `field-survey-sheet.html` on
site, then enter each value in `lane_overrides.json` with its evidence.

What is legal fact, observed fact and model default:

- **Speed (legal fact).** Tunisia's Code de la route sets 50 km/h inside built-up
  areas; a commune may lower it to 30 km/h and the Minister of Equipment may raise
  it to 70 km/h on named roads (Imprimerie Officielle text published at
  transport.tn, quoted in `lane_overrides.json`). The 19 junction roads without an
  OSM `maxspeed` now use 50 km/h as `legal_default`; the 2 Avenue Moncef Bey ways
  already carry OSM `maxspeed=50`. Posted signs and road-specific decisions are
  not verified. All other roads keep SUMO's type defaults (80–100 km/h on
  primary/secondary roads), which are not Tunisian limits.
- **Sidewalks and crossings (model consequence).** netconvert only guesses
  sidewalks on roads up to 50 km/h, so the old 100 km/h defaults left the main
  avenues without sidewalks and J1 and J2 without crossings. With the legal
  speed, 45 junction edges gained sidewalks, J1 has 2 crossings and J2 3, and the
  signal plans gained pedestrian links. Crossing lengths follow SUMO's 3.2 m
  default lane width, so they are not measured crossing distances.
- **J1 control (partly observed).** OSM maps Place du 14 Janvier as a roundabout
  with signals 34 m and 67 m from J1 (removed by this build) and marked
  "uncontrolled" crossings. Commons photos taken 2025-10-02 (CC0, "Tour de
  l'Horloge du centre-ville de Tunis 01..06") show a signalised pedestrian crossing
  at the roundabout. Which vehicle entries are signal-controlled is not
  established; the single J1 light is a modelling simplification.
- **Bus lanes (unknown).** No OSM way in the box carries a bus-lane tag and the
  model has no bus-only lanes. No authoritative source on reserved bus lanes in
  this area was found; record them in the survey.

The trained models in `models/` were fitted before the speed change; retrain
them before quoting predicted travel times on this network.

## Line endings and checksums

`.gitattributes` keeps `scenarios/**/*.osm.xml`, `selection.json` and
`lane_overrides.json` LF on every platform, because their SHA-256 is recorded
in a manifest. A Windows `core.autocrlf=true` checkout otherwise rewrites them
with CRLF and the recorded hashes no longer match.

## traffix hierarchy

This is the default network of the traffix hierarchy in this repo
(`config/networks/tunis6j.yaml`, `TRAFFIX_NETWORK=tunis6j`). File names follow
traffix3's `<network>.net.xml` / `_actuated.net.xml` / `.stops.xml` layout.
Light and node ids are J1..J6; each node carries its street names as a `name`
param. Run it with `python scripts/run_live.py`; see the root `README.md`.

## Claim boundary

Demand is generated, not observed Tunis traffic. No deployment validation, no
measured air quality, no lives saved. Synapse may explain decisions on this
network; it never reaches TraCI.
