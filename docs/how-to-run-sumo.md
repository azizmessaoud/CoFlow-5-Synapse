# How to run SUMO in this repo

Queue truth: [harness/queue.tsv](../harness/queue.tsv).

- Row **01** is `blocked` (libsumo / Windows application control). TraCI still works.
- Rows **02–09** are `gated` on native TraCI. That is the course Control-plane prototype.
- Remaining order: **10 -> 10b Max-Pressure trip KPIs -> 10c deterministic evidence page -> 12 Synapse agents -> 11 API -> 13 React -> 14 Tunis**. Row **15** stays `blocked`.

Two different run actions:

1. **Watch the map** — `sumo-gui` and the green Play button. Default lights. A1 is not attached.
2. **Run this project’s agents** — Python starts headless `sumo.exe` through TraCI. Evidence files appear under `harness/work/`.

```text
sumo-gui Play  ->  watch cars
py -3.11 scripts  ->  A1 / baselines / tests
```

## Once per PowerShell window

```powershell
$env:SUMO_HOME = "C:\Program Files (x86)\Eclipse\Sumo"
$env:Path = "$env:SUMO_HOME\bin;" + $env:Path
cd C:\Users\dell\Downloads\sumo
```

Or let the helper set `SUMO_HOME` if it is empty:

```powershell
py -3.11 scripts\watch_sumo.py smoke
```

## A. Watch the window

| Command | What you see |
|---|---|
| `py -3.11 scripts\watch_sumo.py smoke` | Tiny smoke grid (~180 s) |
| `py -3.11 scripts\watch_sumo.py safety` | 4-way used by later rows |
| `py -3.11 scripts\watch_sumo.py baselines` | Baseline TLS file |
| `py -3.11 scripts\watch_sumo.py max-pressure` | Max-Pressure TLS file, **not** live A1 |
| `py -3.11 scripts\watch_sumo.py tunis` | Imported Tunis OSM showcase with fixed synthetic routes |
| `py -3.11 scripts\watch_sumo.py tunis6j` | Tunis centre-ville, only the six selected junctions signalised (J1..J6) |

Same thing by hand:

```powershell
sumo-gui -c scenarios\smoke\smoke.sumocfg
sumo-gui -c scenarios\safety-mask\safety.sumocfg
sumo-gui -c scenarios\baselines\baselines.sumocfg
sumo-gui -c scenarios\max-pressure\max-pressure.sumocfg
sumo-gui -c scenarios\tunis-showcase\tunis.sumocfg
sumo-gui -c scenarios\tunis-centre-6j\tunis6j.sumocfg
```

### Tunis OSM showcase

Build the runnable Tunis scenario once. The PBF is clipped in WSL because
Windows pyosmium is blocked by local application-control policy; SUMO itself
then runs natively on Windows:

```powershell
$env:SUMO_HOME = "C:\Program Files (x86)\Eclipse\Sumo"
py -3.11 scripts\build_tunis_sumo.py
py -3.11 scripts\watch_sumo.py tunis
```

The builder uses the frozen AOI (`10.170,36.790,10.190,36.805`), converts the
OSM topology with `netconvert`, and creates deterministic synthetic vehicle
routes with seed `20261010`. The routes are not observed Tunis traffic and
the TRANSTU schedule is not used as road-outcome evidence.

Press Play.

### Tunis centre-ville, six junctions

`scenarios/tunis-centre-6j/` is the control network: a 1.4 km box of the
committed OSM around the six row-14 junctions, where only J1..J6 carry
traffic lights. It needs no PBF or WSL, only SUMO:

```powershell
py -3.11 scripts\build_tunis_centre_6j.py
py -3.11 scripts\watch_sumo.py tunis6j
```

See `scenarios/tunis-centre-6j/README.md` for the junction table and the
traffix hierarchy (`python scripts/run_live.py`, see `docs/traffix/README.md`).

## B. Run the gated agents (headless)

```powershell
py -3.11 scripts\generate_safety_artifacts.py
py -3.11 scripts\generate_baseline_artifacts.py
py -3.11 scripts\generate_max_pressure_artifacts.py
```

A1 files: `harness\work\05-max-pressure\artifacts\`.

Spot-check (no libsumo):

```powershell
py -3.11 -m pytest tests/acceptance/test_max_pressure.py tests/architecture/test_forbidden_imports.py -q
```

## C. Watch live A1 (optional)

This starts `sumo-gui` **and** TraCI Max-Pressure. Press Play in the GUI if SUMO waits.

```powershell
py -3.11 scripts\watch_sumo.py a1
```

It does **not** rewrite the gated row-05 artifacts.

## Do not

- Do not use `scripts\run_native_smoke.py` as the daily demo until an admin allows `libsumo`. It rewrites `harness/BLOCKED`.
- Do not start a second Kiro chat while one is writing this repo.
- After Cursor: paste `.kiro/prompts/student-kiro-continue.md` and start at **row 10**.
