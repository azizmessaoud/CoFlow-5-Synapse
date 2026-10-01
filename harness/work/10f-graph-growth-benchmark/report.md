# Row 10f graph-growth benchmark gate report

## Result

Row 10f implements a deterministic four-signal 2x2 benchmark, immutable graph parser and hash, one-hop bounded graph scoring, explicit stale/missing/hash-mismatch local fallback, one A1 executor per signal in the native runner, deterministic paired growth fixtures, and read-only five-second graph frames.

The clean matrix contains exactly 80 deterministic fixture cells: four demand scales (`0.75`, `1.00`, `1.25`, `1.50`) × five paired seeds (`11`, `23`, `37`, `53`, `71`) × four controllers. It contains 2,880 planned-trip rows, 80 KPI rows, 6,080 decision rows, 6,080 junction-state rows, and 1,520 graph-frame rows. Every row joins to one declared run, scenario hash, and graph hash.

## Tests

- `tests/contracts/test_junction_graph.py`: 4 passed.
- `tests/acceptance/test_graph_growth_runner.py`: 4 passed.
- `tests/contracts/test_graph_growth_evidence.py`: 5 passed.
- `tests/architecture/test_forbidden_imports.py`: 10 passed.
- `tests/scripts/test_watch_sumo.py`: 5 passed.

## Evidence and authority

The parsed graph has exactly `J0`, `J1`, `J2`, and `J3`, eight directed internal graph edges, known lane identities, immutable adjacency, and graph hash `sha256:318efc52365362aa48e6eacb8273a2b16c4c6bd4ebb75ffb7b62497f3e5b0b5c`. Bounded one-hop, service-age, and switch terms cannot override a blocked downstream action. Stale, missing, and mismatched graph probes choose the same local action with explicit reason codes.

Only `SignalExecutorRegistry` can issue signal capabilities. The graph parser, scorer, evidence generator, frames, and optional watcher have no write capability. Architecture tests retain exactly one raw traffic-light write site in `signal_executor.py` and forbid NetworkX, learned-control, hosted-agent, and UI dependencies from Row 10f.

## Honest native status

The 80-cell matrix is deterministic fixture evidence, not 80 native SUMO runs. The attempted Windows Python 3.11 TraCI smoke is retained as `failed`: Windows application control raised `WinError 4551` while starting `sumo.exe`. No native traffic result was fabricated. `netconvert` 1.27.1 successfully compiled the four-signal network before the smoke attempt.

## Observed fixture outcome and limits

Graph-aware completed more trips than local Max-Pressure in 8 of 20 paired fixture groups and fewer in 4. The remaining groups tied. This is a mixed deterministic contract result: no winner, significance, deployment, live Tunis, lives-saved, accident-prevention, measured-air-quality, or best-episode claim is made.

Frozen Rows 05 and 10b retained their captured hashes. Pre-existing deleted presentation, modified watch XML, and untracked calendar/presentation/Tunisia materials were not changed by Row 10f.
