# Tunis centre-ville, six junctions

Real OSM streets of central Tunis. Only the six row-14 junctions carry traffic
lights, so each light has exactly one master (A1 here, a junction master in
the traffix3 layout). The road demand is synthetic. Showcase only.

## Run

```powershell
py -3.11 scripts\watch_sumo.py tunis6j          # GUI, fixed-time plans
sumo-gui -c scenarios\tunis-centre-6j\tunis6j_actuated.sumocfg
```

Rebuild from the committed OSM (needs `SUMO_HOME` or `pip install eclipse-sumo==1.27.1`):

```powershell
py -3.11 scripts\build_tunis_centre_6j.py
py -3.11 -m pytest tests\scripts\test_tunis_centre_6j.py -q
```

## Junctions

| ID (node + light) | OSM node | Streets | Lat, lon | Phases | Downstream lights (≤ 800 m) |
|---|---|---|---|---|---|
| J1 | 5294059357 | Av. Habib Bourguiba / Place du 14 Janvier 2011 / Av. Mohamed V | 36.80035, 10.18588 | 4 | J3, J4, J6 |
| J2 | 287386655 | Av. Habib Bourguiba / Av. de France / Rue Jamel Abdel Nasser / Rue de Rome | 36.79945, 10.17852 | 6 | J1, J4, J5, J6 |
| J3 | 287837812 | Rue Saad Zagloul / Av. Moncef Bey | 36.79474, 10.18799 | 6 | J1 |
| J4 | 287863982 | Av. Habib Thameur / Rue de Rome / Rue Mokhtar Attia | 36.80099, 10.17848 | 5 | J2, J5, J6 |
| J5 | 387151856 | Av. Habib Thameur / Rue de Sparte / Rue Salonique / Rue d'Athènes | 36.80319, 10.17933 | 9 | J2, J4, J6 |
| J6 | 517939913 | Av. Habib Bourguiba / Rue d'Alger | 36.79972, 10.17948 | 5 | J1, J2, J4 |

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
| `tunis6j.stops.xml` | bus stops before each light on the four illustrative bus lines |
| `tunis6j.poi.add.xml`, `tunis6j.settings.xml` | GUI labels J1..J6 and viewport |
| `junctions.json` | junction spec and provenance manifest |

## traffix hierarchy

This is the default network of the traffix hierarchy in this repo
(`config/networks/tunis6j.yaml`, `TRAFFIX_NETWORK=tunis6j`). File names follow
traffix3's `<network>.net.xml` / `_actuated.net.xml` / `.stops.xml` layout.
Light and node ids are J1..J6; each node carries its street names as a `name`
param. Run it with `python scripts/run_live.py`; see `docs/traffix/README.md`.

## Claim boundary

Demand is generated, not observed Tunis traffic. No deployment validation, no
measured air quality, no lives saved. Synapse may explain decisions on this
network; it never reaches TraCI.
