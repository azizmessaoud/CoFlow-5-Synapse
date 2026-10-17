# PR context: traffix3 hierarchy + CoFlow Synapse on Tunis J1–J6

Branch: `claude/elegant-johnson-vg5flu` · base: `main` at `516133d` · 6 commits · 552 files changed (+211,028 / −67,189; most of the deletions are removed harness and agent files).

| Commit | Content |
|---|---|
| `6769f35` | Six-junction Tunis centre-ville OSM network |
| `3d1bc84` | traffix3 hierarchy with CoFlow Synapse on Tunis J1..J6 |
| `9649cde` | Models retrained on the Tunis six-junction map |
| `f4f5264` | Live Tunis map in the web app, real TRANSTU lines, trip and lane fixes, docs merged into one README, harness and AI-agent files removed |
| `129c27c` | Lane evidence file for the 21 junction roads, 50 km/h urban speed, strict lane check, field-survey sheet |
| this commit | This document |

## 1. Summary

This PR adopts the multi-agent architecture of [traffix3](https://github.com/aymenhamzik/traffix3).
It adds the Synapse layer and a bridge to CoFlow `SynapseService`.
The simulation runs on the real OpenStreetMap streets of Tunis centre-ville.
Six real junctions (J1–J6) have traffic lights that the agents control.

## 2. Problem and objectives

Problem: each light in a fixed or actuated plan sees only its own queue.
Ambulances stop at red. Late buses bunch. Green can start while a pedestrian still crosses.
No one can say why a light changed.

Main objective: cut waiting time at J1–J6 with cooperating agents, and keep safety, fairness and explanations.

| # | Specific objective | Measure · target |
|---|---|---|
| O1 | Reduce car waiting time | mean wait vs SUMO actuated · lower |
| O2 | Green ahead for emergency vehicles | emergency trip time · lower |
| O3 | Protect pedestrians | green during a crossing · 0 |
| O4 | Help late buses only | bus lateness · lower, cars not hurt |
| O5 | Explain every decision | decisions with a reason code · 100% |
| O6 | Use a model only if it helps | model error vs its rule · lower |
| O7 | One safe writer per light | architecture check · passes in CI |

Target users (7 personas, one frontend page each): pedestrian, car driver, bus passenger, bus driver, ambulance crew, operator, analyst.

## 3. The six junctions

Built by `scripts/build_tunis_centre_6j.py` into `scenarios/tunis-centre-6j/`.

| Id | OSM node | Streets |
|---|---|---|
| J1 | 5294059357 | Av. Habib Bourguiba × Place du 14 Janvier 2011 × Av. Mohamed V (roundabout) |
| J2 | 287386655 | Av. Habib Bourguiba × Av. de France × Rue Jamel Abdel Nasser × Rue de Rome |
| J3 | 287837812 | Rue Saad Zagloul × Av. Moncef Bey |
| J4 | 287863982 | Av. Habib Thameur × Rue de Rome × Rue Mokhtar Attia |
| J5 | 387151856 | Av. Habib Thameur × Rue de Sparte × Rue Salonique × Rue d'Athènes |
| J6 | 517939913 | Av. Habib Bourguiba × Rue d'Alger |

The six junctions were chosen by a fixed rule from the OSM graph (`selection.json`): degree ≥ 3, then signals > roundabout > stop/give-way > named > degree > major road > node id.

Build steps:
1. Clip `scenarios/tunis-showcase/tunis.osm.xml` to bbox (10.1755, 36.7925, 10.1910, 36.8055), about 1.4 × 1.4 km. Cut ways at the box edge.
2. Apply verified lane values from `lane_overrides.json` to a copy of the clip. Junction roads without an OSM `maxspeed` get Tunisia's 50 km/h urban limit.
3. Remove OSM signal tags. Run `netconvert` with `--tls.guess false`, `--tls.set` on the 6 nodes, and `--junctions.join-exclude`. Ramp lane guessing is off, so lane counts follow OSM.
4. Plain-XML round trip: rename nodes and lights to J1..J6. Add a `name` param with the street names.
5. Build an actuated variant (`--tls.rebuild --tls.default-type actuated`) for the baseline.
6. Import TRANSTU bus lines and stops (`scripts/import_transtu_lines.py`) and the Esri basemap decal (`scripts/build_basemap.py`). Write randomTrips demand (seed 20261016; pedestrians 20261017), POIs, settings, two `.sumocfg` files.
7. Write `junctions.json`: OSM id, TLS id, name, phases, downstream neighbours (Dijkstra ≤ 800 m), bus stops, source hashes (including the SHA-256 of `lane_overrides.json`).

Result: 1,335 edges, 6 signalised junctions, 16 bus stops. OSM data as of 2026-10-15 20:21 UTC.

Lane evidence: only 3 of the 21 ways that touch J1–J6 have OSM lane tags. The other 18 are `unverified` and keep SUMO defaults. No dated imagery (Panoramax, KartaView, Commons, Mapillary) showed the stop-line markings. `scripts/lane_overrides.py --strict` fails until all 21 have evidence. `field-survey-sheet.html` is the printable sheet for a site visit.

## 4. Architecture

```
Frontend (React, 7 persona pages)
   │ REST only
FastAPI  ── /api/state, /api/ask, /api/synapse/{explain,audit,metrics}
   │ read only
Synapse layer (explainer, copilot, alert writer, CoFlow bridge) ── reads the decision log
───────────────────────────────────────────────────────────────
Supermaster ── 8 network agents ── directives down, status up
   │
Master J1 … Master J6 ── 5 junction agents each
   │ request()
Executor + safety rules ── the only light writer
   │
SUMO (TraCI / libsumo)
```

Rules:
- One master per junction is the only decider for its light.
- The executor is the only code that writes a light. It applies safety rules first: minimum green, yellow, pedestrian clearance.
- Priority order in every master: safety > emergency > supermaster directive > late bus > pedestrian > normal. It is code. It is never learned.
- Fallback modes: max_pressure → actuated → fixed.
- A message bus carries 6 kinds: request, proposal, directive, status, publication, notification. Messages expire.
- The decision log records every decision with a reason code (~50 codes).
- `scripts/check_architecture.py` enforces the rules. It runs in CI (`.github/workflows/pr.yml`).

### 4.1 Junction agents (one set per junction)

| Agent | Objective | Model (fallback) | Tools / output |
|---|---|---|---|
| Master | one decider per light | none: fixed priority + safety | arbitrate, `executor.request()`, `log()` |
| Traffic light | move the longest queue if the next road has room | max-pressure (default), predictive MPC, or RL (Fitted Q-Iteration) | proposal of a phase |
| Pedestrian | no long waits; no green during a crossing | pedestrian classifier | request walk |
| Transit priority | help late buses only | bus ETA regressor | request priority |
| Emergency priority | green before the ambulance arrives | ambulance ETA regressor (rule: distance ÷ speed) | request green |
| Sensor health | bad data must not drive a light | rule only (the model lost to the rule) | publish DATA_STALE |

### 4.2 Network agents (supermaster)

Cadence: every 5 s; incident detection, transit monitor and emergency route every 1 s.

| Agent | Objective | Model | Output |
|---|---|---|---|
| Demand forecast | traffic level for the next hour | 2 gradient-boosting regressors | forecast |
| Incident detection | blocked lanes, congestion | gradient-boosting classifier | publish INCIDENT |
| Rerouting | Route B, trip planner | travel-time regressor + shortest path | advice only |
| Emergency route | warn junctions ahead | arrival-time regressor | directive PREPARE |
| Corridor | green waves between neighbours | tuned platoon weight | directive BIAS |
| Transit monitor | find late buses | lateness regressor | publish LATE |
| Weather | longer timings in rain; floods | rain-effect regressor | directive + FLOOD |
| Notification | alerts for the 7 pages | decision tree (our rules) | notifications |

### 4.3 Synapse agents (read only)

| Agent | Objective | Model and why | Tools |
|---|---|---|---|
| Explainer | answer "why?" with proof | LLM: Claude Sonnet or Groq `openai/gpt-oss-120b`; language is needed for free questions | `search_log(query)`, `get_live_state()`, `get_results(measure)`; max 5 rounds; citation check, else ABSTAIN |
| Operator copilot | summary and suggested actions | LLM: Claude Sonnet or Groq `openai/gpt-oss-120b` | live snapshot, notifications, log; `approve()` only records |
| Alert writer | alerts in EN, FR, AR | LLM: Claude Haiku or Groq `openai/gpt-oss-20b`; short frequent text | templates; a rewrite that changes a number is rejected |
| CoFlow Synapse bridge | verify a decision or a claim | no LLM: deterministic | reason-code table, log, `SynapseService` → verified / template / abstain + 7 provenance fields |

Without an API key, or when the API fails, all LLM agents use templates. The control loop never waits for an LLM.
Models and the provider (`auto | anthropic | groq`) are set in `config/agents.yaml`. The key goes in a local, gitignored `.env` file.

## 5. What changed, by area

### Network and scenario
- `scripts/build_tunis_centre_6j.py` (new) and `scenarios/tunis-centre-6j/*` (new): see section 3.
- `config/networks/tunis6j.yaml` (new): network dir, 25 TRANSTU line directions (lines 104, 11, 19E, 36, 38B, 38C, 43B, 5, 51A, 5C, 5D, 6P, 74), demand override (2,400 veh/h, bus headway 900 s assumed), named places.
  - Bus-line geometry is TRANSTU-attributed data from a community visualization (`tunis6j.transtu.csv`, `tunis6j.lines.json`). It is not an official feed. Headways are assumptions.
- `scripts/lane_overrides.py`, `scenarios/tunis-centre-6j/lane_overrides.json`, `field-survey-sheet.html` (new): lane evidence per junction road.
- `scripts/import_transtu_lines.py`, `scripts/build_basemap.py` (new): bus lines and the aligned Esri basemap.
- `.gitattributes`: hashed sources stay LF.
  - Places: `incident_edge 577010716#1`, `incident_edge_b 10641416#1`, `incident_edge_c 577010716#0`, `training_incident_edge 10641416#2`, `sensor_fault_tls J1`, `sensor_fault_tls_b J4`, `flood_edge 26280306#2`, `surge_towards J1`.
- `config/networks/tunis_centre.yaml`: the same places for the schematic network.

### Ported from traffix3
- `traffix/` package (core, agents, control, evaluation, synapse, api), `config/`, `models/`, `frontend/` (with `dist/`), `data/networks/` (schematic).
- Scripts: `run_live`, `setup`, `train`, `build_demand`, `run_experiments`, `analyze`, `ask`, `check_architecture`, `build_network`, `import_osm`, `_path`.
- `tests/traffix/test_core.py`, `requirements-traffix.txt`.

### Adaptations for the Tunis map
- `traffix/core/config.py`: `network_name()`, `network()`, `network_files()`, `demand()` (merges overrides), `bus_lines()`, `resolve()` for `@place` placeholders. `scenarios()` returns resolved values.
- `config/simulation.yaml`: `network: tunis6j`. `config/scenarios.yaml` uses `@place` placeholders.
- Generator, live runner and `build_network.py` use `config.bus_lines()`. `build_network.py` forces `TRAFFIX_NETWORK=tunis_centre`.
- `setup.py` runs `build_tunis_centre_6j.py` for tunis6j.
- Training scenarios use placeholders through `config.resolve()`.
- Explainer regex accepts J ids (`[bfj]\d`).
- Monitor and transit agents use `config.demand()`.

### Bug fixes and live app
- `traffix/evaluation/monitor.py`: remove arrived buses before `getRoadID`. Before the fix, a teleported bus crashed the run ("Vehicle 'bus_L3_south_6' is not known").
- Live web app: basemap aligned to the network, real bus lines and stops, real-size vehicles, restart and error handling for live runs (`traffix/api/live.py`, `NetworkMap.jsx`).
- Trip planner: edge ids with `#` are encoded; 422 details are shown; places are labelled by street name.
- Traffic files record the network and its digest. `run_experiments.py` rebuilds stale traffic. Building traffic is about 40× faster.

### Synapse bridge (new)
- `traffix/synapse/coflow_bridge.py`: class `TraffixSynapse(entries, run_id, scenario, tally)`.
  - Each log entry becomes an `EvidenceEvent`.
  - Facts are limited to `simulation_time`, `selected_action`, `reason_code`, `agent`. A bare junction id cannot pass the audit.
  - Policies = `REASON_CODES`. `CORPUS_HASH` = digest of `REASON_CODES`.
  - Methods: `explain(question, decision_id)`, `audit(claim, decision_id)`, `metrics()`, `refreshed(entries)`, `from_log_file(path, events_file)`.
- `traffix/api/server.py`: `POST /api/synapse/explain`, `POST /api/synapse/audit`, `GET /api/synapse/metrics`. The bridge is cached and refreshed when the log grows.
- `frontend/src/pages/Analyst.jsx`: "Verify with CoFlow Synapse" button under each decision (fallback pill, explanation, citation, run, bundle and corpus hash). Examples use J ids. `dist/` rebuilt.

### Docs and repository cleanup
- All root and `docs/` markdown is merged into one `README.md` (quick start, live system, J0 platform, SUMO, architecture rules, design thinking, requirements, ADR-0001..0004, team plan, data sources, limits, glossary).
- Removed: `AGENT_GUIDE.md`, `AGENTS.md`, `.agents/`, `.kiro/`, `.scratch/`, `harness/`, `LEARNINGS.md`, and the evidence code that only worked with `harness/`. Evidence now goes to `results/evidence/`.
- `.github/workflows/pr.yml`: byte-compile, `scripts/check_architecture.py`, then `pytest tests/architecture tests/api`.
- `.gitignore`: keep `frontend/dist/`; ignore `data/generated/`, `data/training/`, `results/`.

## 6. Data

| Data | Source | Size | Use |
|---|---|---|---|
| Road network | OpenStreetMap, Tunis centre-ville, as of 2026-10-15 | 1,335 edges, 6 lights | SUMO network |
| Traffic demand | synthetic, randomTrips, fixed seeds | 2,400 veh/h base + pedestrians | every run |
| Bus lines | TRANSTU-attributed community data | 13 lines, 25 directions, 16 stops | transit agents |
| Lane evidence | OSM tags + desk imagery search | 21 junction roads, 3 tagged | network build |
| Basemap | Esri tiles aligned to the network | 1 image | web app background |
| Calendar | hijridate + sunset formula | Ramadan, Eid, iftar, peaks | demand pattern; hidden from agents |
| Scenarios | `config/scenarios.yaml` | 12 | train on 2025 dates, test on 2026 |
| Training rows | simulation recorder (what an agent saw + what happened later) | ~360,000 rows | 75/25 split |

A seed fixes the random demand. The same seed gives the same traffic, so runs can be repeated.
"Actuated" = SUMO detector-based plans (gap-out / max-out). It is the baseline and a fallback mode.

## 7. Models

All are scikit-learn `HistGradientBoosting` models, except notification (one decision tree).
Each model is compared with the rule it replaces on the same test data.
Retrained in the cloud with `scripts/train.py --skip-tune --skip-rl`, before the lane, speed and bus-line changes. Retrain on the current network. Light parameters and the RL Q-function are still from the schematic network.

| Model | Predicts | Model vs rule | Status |
|---|---|---|---|
| demand forecast | traffic level per half hour | 0.023 vs 0.044 (Ramadan 0.026 vs 0.103) | used |
| pedestrian | a person will wait too long | F1 0.72 vs 0.00 | used |
| ambulance ETA | seconds to the light | 87 s vs 118 s | used, few data |
| bus ETA | seconds to the light | 138 s vs 216 s | used |
| bus lateness | gap to the bus before | 119 s vs 165 s | used |
| rain speed | slowdown in rain | 0.21 vs 0.43 | used |
| arrivals | cars in the next 30 s | 0.75 vs 0.79 | used, small gain |
| travel time | road travel time | 23.2 s vs 23.0 s | no gain |
| sensor health | frozen detector | F1 0.62 vs 0.98 | removed; rule used |
| incident | blocked lane | too few examples | old schematic model |
| notification | message relevance | copies our rules | used |

A local full run (with tuning and RL) on Windows gave different numbers; it was still in progress. Commit those models only after `sensor_health.joblib` is deleted again.

RL: Fitted Q-Iteration, gamma 0.9, 12 refits, 3 rounds, reward = own wait + 0.5 × neighbours' mean queue, 60 s starvation guard, switch margin.

## 8. Validation

Tests (run on this branch head):
- `pytest tests/traffix tests/scripts tests/api tests/architecture tests/properties`: 108 pass, 1 fails. The failure is a pinned Hypothesis version check in the cloud environment, not a logic error.
- New test files: `test_lane_overrides.py`, `test_transtu_lines.py`, `test_basemap.py`.
- `tests/traffix/test_tunis6j_integration.py`: default network, six named lights, places and bus lines exist, 6 masters, the bridge verifies and abstains, a real SUMO run of a 300 s scenario.
- `scripts/check_architecture.py`: passes.
- Some older J0 acceptance tests need native Windows Python 3.11 and do not run in the Linux cloud.

Controller comparison, Tunis map, seed 1, `run_experiments --workers 1`:

| Scenario | Measure | Actuated | traffix rules | traffix models |
|---|---|---|---|---|
| morning peak | mean car wait | 103.1 s | 72.9 s | 61.2 s (−41%) |
| emergency | mean car wait | 131.7 s | 70.0 s | 52.6 s (−60%) |
| emergency | emergency trip | 486.9 s | 303.3 s | 240.7 s |
| both | pedestrians cut off (green during crossing) | 23 / 28 | 1 / 0 | 0 / 0 |

Objectives: O1, O2, O3, O5, O7 met (O1, O2 with 1 seed). O4 and O6 partial.

Live demo verified: 6 masters active, ambulance preemption at J1 (`#336 EMERGENCY_PREPARE → #337 EMERGENCY_GRANTED_HOLD → #341 RECOVERY_STARTED`), Synapse endpoints return verified and abstain.

## 9. Difficulties solved

- The 6 OSM junctions had no signals → signals set with `--tls.set`; OSM signal tags removed.
- Clipping by "any node inside" gave a 1.8 × 3.4 km net → ways cut at the box edge.
- J1 roundabout approaches are short (< 40 m) → stop threshold 20 m.
- traffix assumes TLS id = node id → both renamed by a plain-XML round trip.
- The grid jammed at 4,000 veh/h → tunis6j override of 2,400.
- A teleported bus crashed the monitor → fixed.
- The audit accepted a false claim because facts held the TLS id → facts restricted.
- Parallel `run_experiments` hung twice → use `--workers 1`.
- Motorway ramp guessing added false lanes → `--ramps.guess` removed.
- SUMO gave untagged city roads 80–100 km/h → 50 km/h legal urban limit.
- An earlier claim that lanes matched satellite imagery had no evidence → removed; lanes tracked in `lane_overrides.json`.

## 10. How to run

Windows, Python 3.11, SUMO 1.27.1:

```powershell
py -3.11 -m pip install -r requirements-traffix.txt
py -3.11 scripts\setup.py                       # network if missing, traffic, models if unusable
py -3.11 scripts\run_live.py --gui              # http://localhost:8000; --gui opens sumo-gui
py -3.11 scripts\build_tunis_centre_6j.py       # rebuild the network
py -3.11 scripts\train.py                       # full retrain: 30–60 min
py -3.11 scripts\run_experiments.py --scenario morning_peak --seeds 1
py -3.11 scripts\run_experiments.py             # 7 controllers x 12 scenarios x 3 seeds
py -3.11 scripts\analyze.py
py -3.11 scripts\check_architecture.py
py -3.11 scripts\lane_overrides.py --strict     # fails until all 21 junction roads have evidence
py -3.11 -m pytest -q
```

Optional: put `ANTHROPIC_API_KEY` or `GROQ_API_KEY` in a local `.env` for the LLM agents.

Demo: start the emergency scenario → operator page (map) → wait for an ambulance → analyst page → "Verify with CoFlow Synapse" on an `EMERGENCY_GRANTED` decision.

## 11. Limits

- Synthetic demand: results are simulation results, not Tunis measurements.
- 18 of 21 junction roads have unverified lane counts (SUMO defaults).
- Bus lines are community data, not an official feed; headways are assumed.
- The controller results in section 8 were measured before the lane, speed and bus-line changes. Run them again on the current network.
- One seed so far; no significance test yet.
- Calendar factors are our assumptions, not observed data.
- Weak models: travel time equals its rule; ambulance ETA has few rows; incident not retrained.
- Light parameters and RL come from the schematic network.

## 12. Next steps (priority order)

| P | Task | Closes |
|---|---|---|
| 1 | Re-run results on the current network; then 12 scenarios × 3 seeds + paired t-tests | O1, O2 significance |
| 1 | Retune lights and RL on the Tunis map (full `train.py`) | O1, O6 |
| 2 | Bus KPIs per line; check cars are not hurt | O4 |
| 2 | More incident runs; retrain the incident model | O6 |
| 2 | Field survey of the 18 unverified junction roads | realism of lanes |
| 3 | Real data: official timetables, weather API, traffic counts | realism |
| 3 | Accident-history risk model + read-only `get_accidents()` tool | new value |

## 13. Related material

- Presentation deck (private until shared): https://claude.ai/artifact/RW64woQcFu968Ur4rVzAhe
- Main guide, ADRs and limits: `README.md` (ADR-0004 is in section 10)
- Network details and sources: `scenarios/tunis-centre-6j/README.md`
