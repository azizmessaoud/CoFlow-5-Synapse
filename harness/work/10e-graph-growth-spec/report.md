# Row 10e report — graph-aware traffic growth

## Verdict

The current one-junction simulation is not evidence that signal control remains effective as traffic grows. The bounded next improvement is a four-junction 2x2 directed benchmark with graph-aware cooperative Max-Pressure, freshness fallback, paired demand-growth evidence, and read-only graph frames.

## Current evidence

- Native A1 runners hard-code `J0` and four local movement pairs.
- `MaxPressureObservation` has no junction graph, graph hash, neighbour source age, or stale-neighbour state.
- Row 10b is one 84-trip, one-seed cell: fixed-time completed 71, actuated 84, and Max-Pressure 70.
- No 2x2 or 4x4 controlled scenario exists in the current scenario inventory.
- Therefore growth robustness and controller superiority are not established.

## Chosen solution

- Build a hashed four-junction directed graph before city scale or learned graph control.
- Preserve local pressure and downstream hard blocking; add only bounded one-hop discharge, service-age, and switch terms.
- Drop stale, missing, or identity-mismatched neighbour state and continue with local Max-Pressure.
- Compare fixed-time, actuated, local Max-Pressure, and graph-aware Max-Pressure across 0.75, 1.00, 1.25, and 1.50 demand with five paired seeds.
- Gate correctness and evidence completeness, not a graph-aware win.

## Agentic-AI and interface

A1 is still the only signal writer. A2 uses a feasible corridor graph for expiring emergency requests; A3 uses route subgraphs for conditional transit requests; A4 uses graph residuals for anomaly/degradation evidence; A5 may publish proxy-labelled link burdens; Synapse explains frozen graph evidence or abstains. SUMO GUI is optional diagnosis. React later reads precomputed `GraphFrame` artifacts and never reaches TraCI.

## RoadwayVR boundary

Reuse TraCI lifecycle, telemetry, `getNextTLS`, GUI schema, and delay concepts. Do not copy hard-coded IDs, direct phase setters, 0.1-second shortening, online Q-learning/DQL, queue-only reward, or evidence-free plots. RoadwayVR is not a runtime dependency.

## Next row

`10f-graph-growth-benchmark` is queued as the next executable row. It creates the 2x2 scenario, typed graph parser, generalized per-signal A1 runner, growth matrix, graph frames, GUI diagnosis option, and hash-bound evidence without modifying Rows 05 or 10b.

## Validation

```text
py -3.11 -m pytest tests/acceptance/test_graph_growth_spec.py -q
.....                                                                    [100%]
5 passed in 0.37s
```
