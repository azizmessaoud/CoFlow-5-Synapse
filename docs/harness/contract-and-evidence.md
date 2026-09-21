# Contract and evidence pack

Externalize agent memory into files a machine can validate.

Work unit: one row in `harness/queue.tsv`.  
Pack: `harness/work/<id>/`.

```text
harness/work/<id>/
  contract.json      # target spec, TRACKED
  deltas.md          # generated mismatches, TRACKED
  gate.json          # machine verdict, TRACKED
  report.md          # human summary after gate, TRACKED
  artifacts/         # run manifests, logs, plots as named by contract
```

Join key across SUMO, agents, API, RAG, and UI: `run_id`.

Also join: `scenario_hash`, `configuration_hash`, `seed`, `event_id`, `message_id`.

## contract.json shape

```json
{
  "id": "03-safety-mask",
  "kind": "control",
  "persona_or_hmw": "P1 Amara; P6 Yuki",
  "stage": "prototype",
  "must_pass": [
    "illegal action never executed",
    "clearance never truncated",
    "reason code recorded"
  ],
  "tests": [
    "pytest -k safety_mask"
  ],
  "artifacts": [
    "run_manifest.json",
    "decision_events.parquet"
  ],
  "imports_forbidden": [
    "synapse -> traci",
    "a2 -> trafficlight.setPhase"
  ]
}
```

## gate.json shape

```json
{
  "id": "03-safety-mask",
  "pass": false,
  "openDeltas": 2,
  "contractHash": "sha256:...",
  "testsRun": [],
  "artifactsPresent": [],
  "decidedBy": "tests-and-files"
}
```

`decidedBy` must never be `agent-self-assessment`.

The CoFlow-5 run evidence bundle is the product-level pack for a simulation. This folder is the harness-level pack for one queue row. They must not invent separate truths. A control-row gate reads the evidence bundle; it does not replace it.

Adapted from [contract-and-evidence.md](https://github.com/flyrank-bih/harness-engineering-playbook/blob/main/docs/contract-and-evidence.md).
