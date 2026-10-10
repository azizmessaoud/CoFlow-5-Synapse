# CoFlow-5 Synapse: Project Context and Build Summary

## Purpose

This document records how the CoFlow-5 Synapse project was shaped, what is
implemented, how the Tunis showcase was built, how to run it, and what remains
before the six selected Tunis junctions become a live multi-junction control
experiment.

The repository is a reliable AI decision platform for urban traffic
simulation. It is not an LLM traffic controller. The safety-critical control
loop is deterministic and constrained; Synapse is a non-actuating explanation
and audit layer.

## Executive summary

The project currently contains three related demonstrations:

1. **Controlled J0 benchmark**
   - Synthetic, reproducible SUMO scenarios.
   - Fixed-time, actuated, and cooperative Max-Pressure control.
   - Matched seeds, ablations, and failure-injection evidence.
   - A1 is the only signal writer.

2. **Tunis OSM showcase**
   - Real Tunisia OSM PBF topology.
   - Wider Tunis display bounding box:

     ```text
     left   = 10.127879
     bottom = 36.787714
     right  = 10.233358
     top    = 36.820741
     ```

   - Six selected OSM junctions are marked in SUMO-GUI.
   - Deterministic synthetic vehicle demand.
   - The full imported road network contains many ordinary junctions; the
     six selected junctions are the showcase/control scope, not the total
     number of graph nodes.

3. **Read-only Synapse dashboard**
   - FastAPI serves frozen evidence.
   - React displays runs, provenance, explanations, citations, and metrics.
   - The dashboard cannot reach TraCI, SUMO, or signal execution.

The Tunis visual showcase is runnable. The remaining major product gap is that
the live A1 TraCI runner is still J0-specific. The next substantial step is an
explicit six-junction registry, per-junction lane mappings, and a
multi-junction TraCI runner.

## Non-negotiable architecture

```text
                    CONTROL PLANE

 SUMO observations
        |
        v
 A1 Flow / cooperative Max-Pressure
        |
        v
 deterministic safety mask
        |
        v
 sole signal executor
        |
        v
 SUMO traffic light

                    SYNAPSE PLANE

 completed run artifacts
        |
        v
 event summaries and evidence
        |
        v
 Synapse explanation/audit service
        |
        v
 FastAPI
        |
        v
 React dashboard
```

The central boundary is:

> Synapse explains logged decisions; it never actuates signals.

The domain agents are:

| Agent | Responsibility | Permission |
|---|---|---|
| A1 Flow | Selects legal signal actions using local pressure | The only signal writer |
| A2 Emergency | Publishes bounded emergency-priority requests | Advisory only |
| A3 Multimodal | Publishes pedestrian and transit evidence | Advisory only |
| A4 Situation | Forecasting and incident/residual detection | Advisory only |
| A5 Sustainability | SUMO/HBEFA emission-proxy advice | Advisory only |
| Synapse | Retrieval, explanations, audits, what-if support | Read-only; never actuates |

The recovery ladder is:

```text
cooperative Max-Pressure -> actuated -> fixed-time
```

Reinforcement learning/DQN is optional and remains outside the required core.

## Evidence contract and claim boundaries

The frozen J0 evidence contract requires:

- matched-seed evidence for cooperative A1, actuated, and fixed-time control;
- at least five matched seeds for the completed J0 benchmark;
- A2, A3, A4, and A5 ablations;
- failure-injection cases covering the recovery ladder;
- provenance on every response and decision;
- explicit abstention and fallback behavior.

The seven provenance fields are:

```text
run_id
scenario_hash
event_id
message_id
bundle_digest
corpus_hash
query_hash
```

Synapse fallback states are:

```text
verified
template
abstain
```

The distinction between incomplete support states is deliberate:

- no event or evidence: `abstain`;
- missing policy chunk: `template` with a policy-support marker.

The Tunis showcase manifest is explicitly:

```text
status: showcase_only
road_demand: synthetic_or_calibrated_unless_observed_source_is_attached
scheduled_transit_is_not_road_outcome_evidence: true
```

It must not be presented as:

- matched-seed inference;
- deployment validation;
- measured air quality;
- lives saved;
- measured real-world Tunis traffic performance.

The TRANSTU GTFS archive is official scheduled transit data. It is not
measured road-outcome evidence.

## How the project was built

### 1. Architecture and contract phase

The project first established the safe system boundary:

- deterministic control instead of an LLM in the second-scale signal loop;
- A1 as the sole signal writer;
- A2-A5 as typed advisory agents;
- Synapse as a non-actuating explanation layer;
- evidence and claim boundaries treated as first-class outputs.

The project queue, contracts, gates, and evidence packs follow the repository
harness rules. A queue row is only complete when its contract and `gate.json`
agree and the machine checks pass.

### 2. Controlled J0 implementation

The controlled prototype implemented:

- safety-constrained signal execution;
- cooperative Max-Pressure;
- fixed-time and actuated baselines;
- message transport and advisory arbitration;
- A2-A5 typed payloads;
- failure injection and recovery;
- matched-seed evidence;
- deterministic evidence artifacts.

The native J0 runner reads queue and downstream state through TraCI, computes
pressure, and gives A1 a safe signal-submission capability. The raw TraCI
connection is not passed to Synapse or advisory agents.

The native runner currently contains J0-specific assumptions:

```python
signal_id="J0"
incoming_lanes = {
    "north": "N_in_0",
    "east": "E_in_0",
    "south": "S_in_0",
    "west": "W_in_0",
}
```

That is why the live A1 demonstration is currently a J0 demonstration, not a
six-junction Tunis controller.

### 3. Synapse/API/dashboard phase

The Synapse service was added with:

- seven-field provenance;
- corpus pinning;
- deterministic cache key behavior;
- verified/template/abstain fallback states;
- explanation and audit operations;
- abstention, fallback, latency, and cost metrics;
- bounded event and comparison access.

The FastAPI layer added:

- `/health`;
- `/runs`;
- `/runs/{run_id}`;
- `/runs/{run_id}/artifacts/{name}`;
- `/events`;
- `/comparisons`;
- `/metrics`;
- `/explanations`;
- `/audits`;
- LOCAL_RUNNER-only proposal and approval endpoints.

The React dashboard is intentionally read-only and reports:

```text
actuates: false
sumo: false
```

It is an evidence viewer, not a live SUMO control console.

### 4. Tunis input phase

The supplied PBF was:

```text
C:\Users\dell\Downloads\ai agent prototype\tunisia-261009.osm.pbf
```

Its verified hash is:

```text
sha256:8bea4a9f2a86cce8ca198d9bad50dd1103239bbcb55669058fa50042c767f51
```

The official TRANSTU GTFS was downloaded from the Tunisian transport CKAN
portal and stored at:

```text
harness\work\14-tunis-showcase\inputs\transtu-gtfs.zip
```

Its verified hash is:

```text
sha256:293718f3cd96e5c5bcd7c980b4752a1f17d31106ee4465c39064c9bdc5d7dded
```

The archive contains the required GTFS files:

```text
agency.txt
calendar.txt
calendar_dates.txt
feed_info.txt
routes.txt
stops.txt
trips.txt
stop_times.txt
```

The six selected OSM junction IDs are:

```text
5294059357
287386655
287837812
287863982
387151856
517939913
```

The selection artifact is:

[harness/work/14-tunis-showcase/junctions.json](harness/work/14-tunis-showcase/junctions.json)

The selection rule is:

```text
degree >= 3
then traffic_signals > roundabout > stop/give_way > named
> degree > major_road > node_id
```

### 5. Why WSL is used

Windows `pyosmium` native DLL loading was blocked by the local Windows
application-control policy. WSL Ubuntu has a working `pyosmium` installation,
so clipping is performed in WSL.

The SUMO conversion and simulation still run natively on Windows using SUMO
1.27.1.

### 6. Runnable Tunis SUMO scenario

The build pipeline is:

```text
original Tunisia PBF
        |
        v
clip_tunis_osm.py in WSL
        |
        v
tunis.osm.xml
        |
        v
native SUMO netconvert
        |
        v
tunis.net.xml
        |
        v
SUMO randomTrips.py
        |
        v
tunis.rou.xml
        |
        v
six-junction marker overlay + GUI settings
        |
        v
tunis.sumocfg
```

The implementation files are:

- [scripts/clip_tunis_osm.py](scripts/clip_tunis_osm.py)
- [scripts/build_tunis_sumo.py](scripts/build_tunis_sumo.py)
- [scripts/watch_sumo.py](scripts/watch_sumo.py)

The generated scenario files are:

- [scenarios/tunis-showcase/tunis.osm.xml](scenarios/tunis-showcase/tunis.osm.xml)
- [scenarios/tunis-showcase/tunis.net.xml](scenarios/tunis-showcase/tunis.net.xml)
- [scenarios/tunis-showcase/tunis.rou.xml](scenarios/tunis-showcase/tunis.rou.xml)
- [scenarios/tunis-showcase/tunis.sumocfg](scenarios/tunis-showcase/tunis.sumocfg)
- [scenarios/tunis-showcase/tunis-junctions.add.xml](scenarios/tunis-showcase/tunis-junctions.add.xml)
- [scenarios/tunis-showcase/tunis.settings.xml](scenarios/tunis-showcase/tunis.settings.xml)

The wider display build currently imports approximately:

```text
2,698 OSM ways
15,385 OSM nodes
200 deterministic synthetic vehicles
```

The exact number of SUMO junction objects is larger than six because the
network contains the full road graph. The six selected OSM junctions are
preserved and marked, but ordinary intermediate junctions remain part of the
road topology.

## Run commands

### Build the full Tunis visual scenario

```powershell
cd C:\Users\dell\Downloads\sumo

$env:SUMO_HOME = "C:\Program Files (x86)\Eclipse\Sumo"
$env:Path = "$env:SUMO_HOME\bin;" + $env:Path

py -3.11 scripts\build_tunis_sumo.py --force
```

### Open Tunis in SUMO-GUI

```powershell
py -3.11 scripts\watch_sumo.py tunis
```

Then press the green **Play** button.

The GUI shows:

- the imported Tunis road network;
- deterministic synthetic routes;
- the six selected junction markers;
- the full display bounding box.

### Run Tunis headlessly

```powershell
& "$env:SUMO_HOME\bin\sumo.exe" `
  -c scenarios\tunis-showcase\tunis.sumocfg `
  --duration-log.statistics `
  --no-step-log true
```

### Run the live J0 A1 demonstration

```powershell
py -3.11 scripts\watch_sumo.py a1
```

This starts SUMO-GUI and attaches the current native A1 Max-Pressure runner to
the controlled J0 scenario. It does not attach A1 to the Tunis network yet.

### Start the API

```powershell
cd C:\Users\dell\Downloads\sumo
$env:EVIDENCE_ROOT = (Resolve-Path "deploy\evidence").Path
py -3.11 -m uvicorn coflow5.api.app:app `
  --app-dir src `
  --host 127.0.0.1 `
  --port 8000
```

### Start the React dashboard

```powershell
cd C:\Users\dell\Downloads\sumo\web
npm.cmd run dev -- --host 127.0.0.1
```

Open:

```text
http://127.0.0.1:5173/
```

The dashboard and SUMO-GUI are separate:

```text
SUMO-GUI       = live visual traffic simulation
FastAPI        = read-only evidence API
React          = read-only explanations and audit UI
```

## Codebase map

```text
src/coflow5/
├── a2/
│   └── emergency.py              # A2 emergency advisory payloads
├── a3/
│   ├── multimodal.py             # pedestrian/transit advisory payloads
│   └── pedestrian_demand.py
├── a4/
│   └── situation.py              # forecasting and incident evidence
├── a5/
│   └── sustainability.py         # emission-proxy advice
├── api/
│   ├── app.py                    # read-only FastAPI surface
│   └── store.py                  # evidence store
├── control/
│   ├── a1_controller.py          # sole safe submission capability
│   ├── max_pressure.py           # cooperative A1 policy
│   ├── recovery.py               # recovery ladder
│   ├── safety.py                 # safety constraints
│   └── request_arbitration.py    # advisory arbitration
├── evaluation/
│   ├── harness.py
│   ├── j0_completion.py
│   └── failure_artifacts.py
├── evidence/
│   ├── bundle.py
│   ├── schemas.py
│   ├── max_pressure_artifacts.py
│   └── professor_page.py
├── messaging/
│   ├── a1_advisories.py
│   └── a1_forecasts.py
├── sumo_adapter/
│   ├── max_pressure_runner.py    # current J0-specific TraCI runner
│   ├── signal_executor.py        # guarded signal writes
│   └── smoke_backends.py
└── synapse/
    ├── service.py                # explanations, audits, fallback
    └── observer.py

scripts/
├── build_tunis_sumo.py            # build full Tunis visual scenario
├── clip_tunis_osm.py              # WSL PBF clipping
├── find_tunis_junctions.py        # deterministic six-junction selection
├── prepare_tunis_showcase.py      # OSM/GTFS manifest
└── watch_sumo.py                 # SUMO-GUI launcher

web/
├── src/App.jsx                    # read-only evidence dashboard
└── src/index.css

harness/work/14-tunis-showcase/
├── contract.json                  # Tunis row contract
├── gate.json                      # sealed gate
├── junctions.json                 # six selected junctions
├── manifest.json                  # provenance and claim boundaries
├── pbf-source.json                # PBF provenance
└── inputs/transtu-gtfs.zip
```

## What is complete

```text
✅ architecture boundary
✅ J0 evidence contract
✅ matched seed evidence
✅ A2-A5 ablations
✅ failure-injection evidence
✅ deterministic safety mask
✅ A1-only signal writing
✅ recovery ladder
✅ Synapse explanation/audit service
✅ seven-field provenance
✅ fallback and abstention metrics
✅ bounded FastAPI API
✅ read-only React dashboard
✅ OSM PBF provenance
✅ official TRANSTU GTFS provenance
✅ deterministic six-junction artifact
✅ Tunis SUMO network conversion
✅ deterministic Tunis synthetic routes
✅ full Tunis visual SUMO-GUI map
✅ six-junction SUMO markers
✅ full-map viewport alignment
```

## What remains

```text
⚠️ current Tunis A1 runner is not multi-junction
⚠️ current native runner is J0 lane/signal specific
⚠️ selected OSM junctions need an explicit OSM-to-SUMO control registry
⚠️ not every selected OSM junction is necessarily signalized
⚠️ six live signal programs need to be designed or imported
⚠️ A2-A5 are not yet driving a live six-junction Tunis run
⚠️ the dashboard remains read-only by design
⚠️ Tunis demand remains synthetic
```

## Recommended next implementation slice

Do not reduce the full visual map to six graph nodes. Instead:

1. Add a `tunis_control_registry.json` containing:
   - `control_id` (`J1` through `J6`);
   - OSM node ID;
   - SUMO junction ID;
   - SUMO traffic-light ID, if present;
   - incoming lanes;
   - outgoing lanes;
   - legal phase mapping;
   - signalization status.

2. Inspect the generated network and classify the six selected junctions:
   - traffic-light controlled;
   - priority;
   - roundabout;
   - unsuitable for signal control.

3. Decide whether the showcase is:
   - a mixed six-junction observation corridor; or
   - six explicitly signalized SUMO control points.

4. Generalize the J0 runner:
   - one A1 controller per controlled junction;
   - per-junction lane mappings;
   - independent safety masks;
   - shared advisory transport;
   - junction-specific provenance.

5. Route synthetic demand through the selected corridor.

6. Add six-junction evidence artifacts and a dashboard view that groups
   decisions by `control_id`.

The resulting target flow is:

```text
Tunis SUMO
    |
    v
TraCI observations for J1-J6
    |
    +--> A2 emergency advisories
    +--> A3 pedestrian/transit advisories
    +--> A4 forecasts/incidents
    +--> A5 sustainability proxies
    |
    v
six independent A1 Max-Pressure controllers
    |
    v
six deterministic safety masks
    |
    v
SUMO signal writes
    |
    v
event/evidence artifacts
    |
    v
Synapse explanations and dashboard
```

## Final interpretation

The system currently is:

```text
real Tunis road topology
+ six selected junctions
+ deterministic synthetic traffic
+ SUMO-GUI visual simulation
+ controlled J0 A1 evidence runner
+ advisory A2-A5 modules
+ read-only Synapse/API/dashboard
```

It is not yet:

```text
six live A1 controllers operating six Tunis signals
```

That distinction is intentional and preserves the project's evidence and
safety boundaries.
