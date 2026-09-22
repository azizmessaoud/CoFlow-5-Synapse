# How to run SUMO in this repo

Queue truth: [harness/queue.tsv](../harness/queue.tsv).

- Row **01** is `blocked` (libsumo / Windows application control). TraCI still works.
- Rows **02–09** are `gated` on native TraCI. That is the course Control-plane prototype.
- Rows **10–14** are `todo`. Row **15** stays `blocked`.

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

Same thing by hand:

```powershell
sumo-gui -c scenarios\smoke\smoke.sumocfg
sumo-gui -c scenarios\safety-mask\safety.sumocfg
sumo-gui -c scenarios\baselines\baselines.sumocfg
sumo-gui -c scenarios\max-pressure\max-pressure.sumocfg
```

Press Play.

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
