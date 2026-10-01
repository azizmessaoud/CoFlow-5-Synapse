# Row 01 — native smoke

Row 01 was ungated. Its stored 22 September Windows Code Integrity blocker is stale: current TraCI, SUMO 1.27.1, and a 102-step libsumo smoke execute successfully. This pack is the fresh comparable throughput, memory, and artifact-size evidence, with the named tests and a hash-bound gate. `harness/BLOCKED` is removed.

Same scenario and seed 20260922:

- TraCI: 102 steps, 9321 artifact bytes, peak memory 57905152 bytes, 119.46 steps/s.
- libsumo: 102 steps, 9268 artifact bytes, peak memory 55693312 bytes, 303.30 steps/s.

Warning, not a failure: pyarrow 21.0.0 may be incompatible with libsumo compiled against libarrow2300.

`harness/BLOCKED` is removed. Docker and WSL were not used.

## Gate inventory

Across the 20 physical queue entries: 13 valid gates, 5 stale gates, and 2 open rows.

Valid: 01, 02–09, 10d, 10e, 11, and 12.

Stale, not re-sealed:

- 10, 10b, 10c: `contract.json` bytes no longer match `gate.contractHash`.
- 10f: `scripts/watch_sumo.py`, `tests/architecture/test_forbidden_imports.py`, `tests/scripts/test_watch_sumo.py`, `scenarios/graph-growth/graph-growth.tls.xml`, and `scenarios/graph-growth/graph-growth.sumocfg` drifted. The recorded native smoke artifact can still say WinError 4551; the toolchain works now, so that smoke belongs in a re-gate, not a hash rewrite.
- 13: `web/src/App.jsx`, `web/src/evidence.js`, `web/src/index.css`, and `web/src/evidence.test.js` changed after the gate.
- 10d and 10e remain valid. Their contracts, specifications, reports, deltas, and recorded test hashes currently match their gates.

Open: Row 14 is not started. Row 15 is optional and blocked; it may be cut. It is not required. For the fifteen numbered rows, four are not currently verifiably complete: 10, 13, 14, and 15. Among the lettered follow-ups, 10b, 10c, and 10f need re-gating.
