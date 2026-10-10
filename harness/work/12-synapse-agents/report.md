# Row 12 Synapse agents gate report

## Result

Row 12 implements a deterministic, non-actuating Synapse slice over frozen Row 10f evidence. Exact-token local retrieval ingests only four hash-sealed sources into 260 stable paragraph chunks. S1 emits one bounded proposal with `awaiting-human-approval`; S2 fetches exactly one immutable event and answers with verified event facts plus allow-listed citations or explicitly abstains; S3 passes only fully resolved event/artifact claims and otherwise abstains.

The optional provider is a typed in-process drafting boundary with at most one retry. Provider prose is never released: only typed event/action/reason/citation fields are verified, and successful provider data is rendered through the closed deterministic local template. Regression coverage injects lives-saved, measured-air-quality, deployment/live-control, winner/model-performance, and uncited-policy claims and proves the released answer remains byte-equal to the safe template. Provider failure falls back to that same template.

## Tests

- `tests/contracts/test_synapse_retrieval.py`: 3 passed in 0.36s.
- `tests/acceptance/test_synapse_agents.py`: 6 passed in 1.67s.
- `tests/contracts/test_synapse_evidence.py`: 5 passed in 1.65s.
- `tests/contracts/test_synapse_non_actuation.py`: 6 passed in 3.35s.
- `tests/architecture/test_forbidden_imports.py`: 11 passed in 1.08s.

Both generator-calling contract suites now write only to pytest temporary directories. After one canonical generation, all five exact commands left all ten canonical artifact hashes byte-identical.

## Evidence

The exact ten-artifact pack is joined to source run `0db24e7b-133e-5b79-ba0c-171f1c0aaf34`, scenario `sha256:893fa5b0e52a4500881d78b8819bf893ebba1af4a81c563fca872fb927425d46`, and event `9fa9db22-b826-53cc-92eb-319b50688327`. It contains 47 joined stage traces spanning event fetch, retrieval, generation, verification, retry, fallback, and terminal outcomes.

All 7/7 golden cases pass. Citation validity is 15/15; event consistency is 3/3 answered cases; exact-source retrieval recall is 1.0 for the expected ADR source; one S2 retrieval miss and one S3 mismatch abstain visibly. The invalid provider used exactly two attempts, while the unavailable provider used one attempt before deterministic fallback. Estimated provider cost is USD 0.00.

Row 08 retains action hash `sha256:1b531200f19a934e64843dfae59332a0e4e8da2d7ce701884fbdbe12f3d1af3a` across four outage variants. The 76-event Row 12 replay retains action hash `sha256:8161d853f03b768975c4cdc6e79c7dd90b16716dc2c88722783e1adcb10510b5` across available, killed, retrieval-unavailable, and provider-unavailable variants. Every sealed Row 08 and Row 10f input hash still matches the contract.

## Limitations and Claim flags

- Retrieval is exact-token and local; semantic retrieval and embeddings are deliberately disabled.
- Golden event consistency covers one immutable graph-aware event and reason code `GRAPH_NEIGHBOUR_USED`; it is regression evidence, not broad language-model quality evidence.
- The observed p95 trace-stage latency, 67.0976 ms, is local Python `perf_counter` evidence and not hosted-provider latency.
- The source traffic matrix is deterministic fixture evidence; Row 10f's native Windows smoke remains blocked by application control.
- No lives saved, accident prevention, measured air quality, deployment, live control, winner, model performance, or unsupported policy claim is made.
