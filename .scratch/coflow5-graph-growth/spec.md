# CoFlow-5 Graph-Aware Traffic Growth — Bounded Simulation Proposal

**Decision:** Build a controlled four-junction directed graph and graph-aware cooperative Max-Pressure before adding GNNs, DQN, city scale, or live data.

**HMW:** How might A1 keep legal, useful signal service as demand grows while A2–A5 and Synapse use network structure to advise and explain without gaining actuation authority?

**Authority:** A1 remains the only signal-writing agent. Each controlled signal has exactly one A1 executor. A2–A5 publish typed expiring advice. Synapse, API, React, and graph visualizations are read-only. Recovery remains `cooperative Max-Pressure -> actuated -> fixed-time`.

---

## 1. What the project can and cannot claim now

| Current fact | Evidence | Consequence |
|---|---|---|
| Measured A1 controls one signal | Native runners hard-code `signal_id="J0"` and four movement/lane pairs | There is no measured junction coordination graph yet |
| Current pressure is local | `MovementPressure` uses upstream queue, downstream queue, and downstream capacity | Good graph seed, but no neighbour identity, source age, or topology contract |
| Current observation has no graph freshness | `MaxPressureObservation` contains local movements, advisories, and pedestrian clearance | Stale neighbour information cannot yet be rejected explicitly |
| Current traffic evidence is one cell | 84 planned trips, seed 37, 120-second horizon | Demand-growth robustness is not established |
| Current matched result is mixed/negative | Fixed completed 71, actuated 84, Max-Pressure 70 | Do not claim Max-Pressure is best; investigate why it leaves 14 unfinished |
| Live A1 GUI exists | `py -3.11 scripts\watch_sumo.py a1` | Useful for diagnosis, but it has no graph overlay and is not evaluation evidence |
| No multi-junction scenario exists | Scenario inventory contains one-junction safety/baseline/Max-Pressure assets | The next control row must create a bounded graph benchmark first |

“Lights work correctly under growth” means: legal phases, one writer, no crossing truncation, no dead controller, explicit stale-data handling, bounded switching, and complete trip accounting. It does **not** mean one controller must win every KPI.

---

## 2. RoadwayVR tutorial — use and reject

The repository `RoadwayVR/SUMO-Traffic-Simulator-Tutorial` is MIT-licensed tutorial material. Use official SUMO documentation as API authority and keep RoadwayVR out of runtime dependencies.

| Tutorial pattern | Decision | CoFlow-5 use |
|---|---|---|
| `SUMO_HOME`, `traci.start`, labelled step loop, `simulationStep` | Reuse concept | Adapter-owned start/step/close lifecycle |
| Vehicle/lane telemetry and `vehicle.getNextTLS` | Reuse concept | Observation and A2 route evidence only |
| `sumo-gui`, delay, and GUI schema | Reuse concept | Human-paced diagnosis, never batch truth |
| Car-following and lane-changing parameters | Later | Separate scenario sensitivity, not agent intelligence |
| Hard-coded detector, edge, and TLS IDs | Reject | Build IDs from a versioned network graph contract |
| `trafficlight.setPhase` or `setPhaseDuration` from tutorial logic | Reject | Only `SignalExecutor` writes after the deterministic mask |
| Emergency shortening to `0.1` seconds | Reject | It can violate minimum green, yellow, all-red, and crossing clearance |
| Online Q-learning/DQL during the evaluated episode | Reject | Non-reproducible, unsafe critical path; optional DQN remains Row 15 |
| Queue-only reward and best plot | Reject | Use paired controllers, tails, unfinished trips, safety, spillback, and null results |
| TensorFlow/NumPy/Matplotlib copied into control | Reject | No dependency is earned by this row |

No RoadwayVR source file is copied. Its value is teaching TraCI calls and GUI pacing, not supplying the product architecture.

---

## 3. Graph theory model

### 3.1 Two graph views

1. **Movement graph:** a directed vertex is a legal incoming-to-outgoing movement. Directed edges connect movements that feed downstream movements. This is the control view used for pressure and receiving capacity.
2. **Junction graph:** a vertex is a controlled traffic-light junction. A directed edge `J_i -> J_j` exists when an outgoing lane from `J_i` feeds an incoming lane controlled by `J_j`. This is the coordination, route, anomaly, and operator view.

Graph theory helps by making topology explicit; it does not make an LLM or GNN necessary.

### 3.2 Typed immutable contracts

```text
JunctionNode
  signal_id
  incoming_lane_ids
  outgoing_lane_ids
  legal_phase_ids
  executor_owner = A1

GraphEdge
  edge_id
  from_signal_id
  to_signal_id
  connecting_lane_ids
  storage_capacity_vehicles
  free_flow_seconds

NeighbourObservation
  from_signal_id
  to_signal_id
  observed_at
  expires_at
  queue_vehicles
  occupancy_ratio
  predicted_discharge_vehicles
  source = observation_adapter

JunctionGraphObservation
  run_id
  scenario_hash
  graph_hash
  simulation_time
  local_signal_id
  local_movements
  one_hop_neighbours
  stale_neighbour_ids
  unavailable_neighbour_ids

GraphFrame
  run_id
  scenario_hash
  graph_hash
  simulation_time
  nodes[]
  edges[]
  messages[]
  faults[]
  mode
  limitations[]
```

Every graph object is derived from a hashed SUMO network file. Unknown lane or signal references fail validation. Neighbour data is advisory observation state, not a write capability.

### 3.3 Graph features that are useful now

| Feature | Graph use | Owner | Now/Later |
|---|---|---|---|
| Immediate downstream receiving capacity | Hard-mask a transition into a full exit | A1 | Now |
| One-hop predicted discharge | Bounded cooperative pressure term | A1 | Now |
| Queue age and persistent-demand age | Detect starvation and support bounded service-age term | A1 | Now |
| Edge occupancy gradient | Show queue propagation direction | A4 | Now evidence |
| Shortest legal emergency corridor | Select A2 request path, not phases | A2 | Later after 10f |
| Transit route subgraph | Limit A3 coordination to relevant junctions | A3 | Later after 10f |
| Strongly connected congested component | Identify spillback loops | A4 | Later after graph frames exist |
| Betweenness/articulation criticality | Prioritize monitoring and failure injection | A4/Yuki | Later; static planning only |
| Link stop/emission proxy burden | Optional A5 graph layer | A5 | Later and proxy-labelled |
| Graph neural network embedding | Learned forecast/control feature | A4 or optional A1 experiment | Reject for 10f; earned only after deterministic graph baseline |

Do not add NetworkX initially. Use immutable adjacency maps and deterministic traversal; add a library only if a tested centrality requirement cannot be met simply.

---

## 4. Recommended A1 control improvement

### 4.1 Keep Max-Pressure as the core

For legal candidate phase `p` at junction `j`:

```text
local_pressure(p)
  = sum over served movements of
    (upstream_queue - immediate_downstream_queue)
    * receiving_capacity_ratio

graph_score(p)
  = local_pressure(p)
    + bounded_one_hop_discharge_bonus(p)
    + bounded_service_age_bonus(p)
    - bounded_switch_penalty(p)
```

All added terms are bounded and individually logged. A full downstream lane remains a hard mask. The safety mask runs before execution and remains authoritative.

### 4.2 Freshness and failure behavior

| Input state | A1 behavior | Evidence reason |
|---|---|---|
| Fresh valid neighbour state | Use bounded one-hop term | `GRAPH_NEIGHBOUR_USED` |
| Stale or expired neighbour state | Drop that term; use local pressure | `GRAPH_NEIGHBOUR_STALE_LOCAL_ONLY` |
| Missing neighbour state | Use local pressure | `GRAPH_NEIGHBOUR_UNAVAILABLE_LOCAL_ONLY` |
| Invalid graph identity/hash | Reject graph observation; use local pressure | `GRAPH_IDENTITY_MISMATCH_LOCAL_ONLY` |
| Local observation corrupt | Recovery supervisor evaluates controller failure | Existing recovery reason |
| Exit full | Candidate cannot be promoted by graph or agent advice | `DOWNSTREAM_BLOCKED` |

No stale graph input can stop A1 or authorize an action.

### 4.3 Anti-oscillation and anti-starvation

- Preserve minimum green, yellow, all-red, pedestrian clearance, and legal transition graph.
- Add a bounded switch penalty or hysteresis so one-vehicle noise does not flip phases repeatedly.
- Track persistent-demand age; add only a bounded service-age term. Pedestrian deadlines and active crossings keep their existing higher authority.
- Record maximum red/service age by movement. Treat an observed starvation breach as a failed growth cell, not something hidden by network averages.
- Pre-register term bounds and run each term as an ablation. If graph terms do not help, keep local Max-Pressure.

---

## 5. Traffic-growth benchmark

### 5.1 Scenario

Create a synthetic **2x2 grid with four controlled junctions**, bidirectional links, enough internal storage to observe spillback, and deterministic OD route generation. Four junctions are the smallest useful cycle for propagation and alternative paths; the current one-junction scenario cannot test graph coordination. A 4x4 network is a later scale rung, not the first fix.

### 5.2 Paired experiment matrix

| Dimension | Contracted values |
|---|---|
| Network | One hashed 2x2 graph |
| Demand scale | `low=0.75`, `base=1.00`, `growth=1.25`, `surge=1.50` |
| Seed | Five fixed paired seeds declared in the contract |
| Controller | Fixed-time; actuated; local cooperative Max-Pressure; graph-aware cooperative Max-Pressure |
| Graph state | Fresh; one-hop stale; one-hop missing |
| Incident | None in the first gate; one deterministic blocked-edge cell only after the clean matrix passes |
| Horizon | Long enough for demand insertion plus a fixed clearance tail; unfinished trips retained |

The first clean matrix is 4 demand levels x 5 seeds x 4 controllers = 80 paired runs. Stale/missing graph cells are robustness probes, not multiplied across every controller.

### 5.3 Correctness and evidence metrics

| Family | Required measures |
|---|---|
| Safety | Conflicting commands; clearance truncations; illegal transitions; one writer per signal |
| Liveness | Decisions produced; fallback transitions; controller deadline misses; movement service age |
| Demand growth | Planned, departed, completed, unfinished, teleports, clearance-tail residue |
| Journey | Mean, median, P90/P95 travel time and wait; time loss; stops; standstill seconds |
| Junction | Queue by movement; max queue/storage ratio; green occupancy; switch count; split failure proxy |
| Graph | Edge occupancy; blocked-edge events; spillback propagation; congested component size; stale/missing neighbour use |
| Agents | Messages considered, expired, rejected, reason codes, externality fields |
| Runtime | Simulation steps per wall second; artifact bytes; peak memory if available |

### 5.4 Pass/fail meaning

A growth cell passes **correctness** only when safety is zero-violation, each signal has one writer, graph identity joins resolve, stale data falls local, and all planned trips are accounted for. Performance is reported, not gated to “graph-aware wins.” A null or negative graph result is acceptable and decides whether the graph term is retained.

---

## 6. Proposed agentic-AI solutions

| Agent | Graph-aware solution | Typed output | Cannot do | Persona value |
|---|---|---|---|---|
| A1 Flow | One-hop graph-aware cooperative Max-Pressure, blocked-exit mask, freshness fallback, service-age evidence | Signal proposal through existing safety/executor path | Bypass mask or use Synapse | David reliability; Yuki control |
| A2 Emergency | Shortest feasible corridor plus downstream-space check and expiring pre-clear requests | `priority_request` with path, ETA, TTL, benefit, externality | Set phases or reserve an unsafe crossing | Marcus passage and recovery |
| A3 Multimodal | Transit route subgraph and conditional headway-gap coordination; crossing state remains local safety input | Pedestrian state and conditional TSP request | Treat scheduled GTFS as live position | Amara completion; Chidi regularity; Rosa reasons |
| A4 Situation | Graph residuals and spatial consistency to distinguish local sensor failure, demand wave, spillback, and likely incident | Forecast or alert with topology, confidence, age, alternatives | Declare cause or actuate | Omar trustworthy awareness |
| A5 Sustainability | Optional link stop/emission-proxy and displacement layer | Proxy-labelled eco advice | Claim air quality or override spillback | System KPI only; no persona invented |
| Synapse | Graph evidence explainer, data-quality checker, and human-reviewed what-if planner over frozen runs | Cited explanation, abstention, or proposed new run | Read/write TraCI, alter live graph, mint facts | Rosa/Yuki/Omar auditability |

### 6.1 Why this is agentic AI

The system has specialized agents with distinct observations, goals, permissions, expiring messages, conflict arbitration, failure semantics, and an evidence feedback loop. The agentic property is **cooperation under explicit authority**, not five chatbots. Graph theory supplies shared structure; it does not replace safety or make a language model the controller.

### 6.2 Deferred learned features

- **A4 graph forecasting:** a graph-temporal model may be compared only after persistence/tree and deterministic spatial residual baselines exist.
- **Optional A1 DQN/GNN:** remains Row 15 and must use the same action mask, evidence, recovery, paired seeds, and one-writer interface.
- **Graph embeddings for retrieval:** unnecessary for the small evidence corpus; exact IDs and topology filters come first.

---

## 7. Graphical interface

### 7.1 Live SUMO GUI diagnosis

Reuse tutorial concepts only for pacing and read telemetry:

```powershell
py -3.11 scripts\watch_sumo.py graph-growth
```

The optional watcher may start `sumo-gui` through the same A1 runner, set a documented GUI schema, and emit read-only graph frames every five simulation seconds. It must not call traffic-light setters outside `SignalExecutor`, and its results do not become the paired evaluation merely because they are visible.

Suggested layers:

- Node fill: current phase and controller mode.
- Node border: healthy, stale, degraded, fallback.
- Edge width: flow; edge colour: occupancy/spillback ratio.
- Badges: A2/A3 request pending, accepted, rejected, or expired.
- Timeline: A1 action, reason, safety result, graph freshness, fallback.

### 7.2 Read-only React operator view

React remains Row 13 after Synapse and API. It reads precomputed `GraphFrame` artifacts through a read-only API.

| Panel | Answers | Required honesty |
|---|---|---|
| Network graph | Where are queues and blocked receiving links? | Frame time, scenario hash, graph hash |
| Demand slider/comparison | How do controllers behave at 0.75–1.50 demand? | Selects frozen runs; does not change a live signal |
| Agent messages | Which advice did A1 consider and why? | TTL, confidence, disposition, source agent |
| Health/freshness | Can the system see each neighbour? | Stale and unavailable are not normal |
| KPI comparison | What changed in tails, completion, stops, and spillback? | Paired seed and unfinished counts visible |
| Explanation drawer | Why did this signal act? | Exact event and policy citation, or abstain |

No “manual phase” button is exposed in the read-only product. A future authorized override selects a bounded controller mode through the control plane and safety mask; it is not a React-to-TraCI shortcut.

---

## 8. Options considered

| Option | Value | Risk | Decision |
|---|---|---|---|
| A. Four-junction deterministic graph baseline | Tests growth, propagation, freshness, and UI evidence with current stack | More scenario/evidence work | **Now** |
| B. Central network supervisor that advises A1s | Can add perimeter gating and corridor plans | Central bad advice and timing complexity | Later after Option A evidence |
| C. GNN/DQN controller from RoadwayVR-style RL | Portfolio novelty | Online training, weak safety/evidence, compute, no baseline proof | Reject for required path; optional Row 15 only |
| D. City-scale OSM first | Visually impressive | Confounds geometry, demand, calibration, and control | Later Row 14 after controlled graph gate |

---

## 9. Next executable row — 10f graph-growth benchmark

### Entry

- Row 10e gate is green.
- Rows 05 and 10b remain immutable reference evidence.
- Exact Python/SUMO path is recorded; TraCI is allowed even while Row 01 libsumo remains blocked.
- Contract freezes the 2x2 network, OD generator, four demand scales, five seeds, horizons, controller interfaces, and artifact schemas.

### Build order

1. Add deterministic graph schema/parser and tests; no graph library.
2. Add 2x2 network and route generator with source hashes and planned-trip accounting.
3. Generalize the A1 runner from hard-coded `J0` to one executor/controller per declared signal.
4. Add graph-aware bounded terms, freshness fallback, reason codes, and local-Max-Pressure ablations.
5. Generate paired growth evidence and five-second `GraphFrame` artifacts; add optional `watch_sumo.py graph-growth` diagnosis.

### Required tests

```text
tests/contracts/test_junction_graph.py
tests/acceptance/test_graph_growth_runner.py
tests/contracts/test_graph_growth_evidence.py
tests/architecture/test_forbidden_imports.py
tests/scripts/test_watch_sumo.py
```

### Required artifacts

```text
run_manifest.json
graph.json
demand_cells.json
junction_states.parquet
graph_frames.parquet
decision_events.parquet
trips.parquet
run_kpis.parquet
matched_growth_comparison.json
growth_report.md
```

### Stop conditions

- Stop and fail closed on graph hash or lane/signal identity mismatch.
- Keep stale/missing neighbour cells as evidence; do not silently rerun them as healthy.
- Do not tune against the five evaluation seeds after viewing results.
- Do not add NetworkX, TensorFlow, PyTorch, GNN, DQN, WebSocket, or React to 10f.
- Do not claim a winner from an incomplete matrix; retain gridlock, unfinished runs, and negative graph results.

### Exit

Row 10f gates only when all four demand levels and five paired seeds are accounted for, all safety/identity checks pass, graph fallback probes remain locally live, artifacts join on run/scenario/graph identities, and the report states strengths and limitations without requiring graph-aware superiority.

---

## 10. Final recommendation

The best next simulation is not “more AI.” It is a small network where topology, demand growth, stale information, and signal authority are observable and testable. Use RoadwayVR to learn TraCI and GUI mechanics, but retain CoFlow-5’s executor, safety, evidence, recovery, and claim boundaries. If deterministic one-hop graph coordination does not improve the paired growth cells, keep local cooperative Max-Pressure and publish the negative result; that is stronger evidence than an untested GNN animation.
