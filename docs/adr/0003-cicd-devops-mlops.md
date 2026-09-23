# ADR-0003: Later DevOps / MLOps CI/CD without live-signal CD

ADR-0001 stays accepted: CoFlow-5 is a reliable AI decision platform; only A1 writes signals; cooperative Max-Pressure is required; Synapse never reaches TraCI; DQN is optional.

ADR-0002 stays accepted: six named builders, three pairs, one sealed queue row, course success = rows 01–09.

This ADR freezes **how the software and evaluations are promoted later**. It does not authorize skipping row 01, putting SUMO in a hosted container, or treating simulation KPIs as field deployment evidence.

**Status:** Accepted  
**Date:** 22 September 2026

## Context

The 12-week course still needs a native Windows smoke test, an evidence bundle, and a professor-verifiable Control plane. The portfolio also needs a recognizable CI/CD and MLOps story.

Those are different consumers. Mixing them produces three false claims:

1. GitHub Actions or Docker replacing the native SUMO pin.
2. A hosted API that can change traffic lights.
3. MLflow (or any dashboard) inventing a second `run_id`.

Row 01 gated on 23 September 2026. The 22 September Code Integrity note is stale: TraCI, SUMO 1.27.1, and a 102-step libsumo smoke completed on the same Windows machine. pyarrow 21.0.0 may not match libsumo’s libarrow2300; that warning is not a failed gate. The hosted path below stays SUMO-free.

## Decision

### Three consumers

1. **Local runner** — native Windows Python 3.11 + one pinned SUMO release. TraCI for diagnosis. Measured libsumo for batches only after the same native install can import it. This remains the Control-plane path. Pair: Control (Aziz, Fares).
2. **Product API/UI** — FastAPI + React over **precomputed evidence bundles**. Synapse, when added, explains and never reaches TraCI. Hosted containers contain **no SUMO**. Pair: Product (Eya, Ranim).
3. **Offline analysis** — Parquet + DuckDB + versioned reports joined on `run_id` / `scenario_hash` / `event_id` / `message_id`. Pair: Data (Aymen, Oumayma).

Never: CD into a city signal cabinet, lives-saved claims, measured air quality, field-model drift on real Tunis loops, continuous cloud SUMO training, Kafka, Kubernetes, or Pinecone as the default.

### CI/CD ladder

| When | Workflow | What it may do | What it must not do |
|---|---|---|---|
| From this ADR | `.github/workflows/pr.yml` | Python 3.11; `tests/architecture` and read-only API tests; `compileall`; confirm contracts 01–09 exist | Install SUMO; run `test_native_windows_smoke.py`; require Docker for merge |
| After rows 08–09 gate, on a SUMO-capable runner | `.github/workflows/eval.yml` | `workflow_dispatch` or nightly when `SUMO_RUNNER=true`; named eval/fault tests | Pass if libsumo cannot load; headline a best episode; skip unfinished trips |
| After rows 11–13 exist as product | `deploy/docker-compose.yml` | Serve tagged evidence + API + UI | Ship `sumo`, `traci`, or `libsumo` in the hosted images; actuate anything |

Rollback for the hosted product is the previous **git tag** of the API image plus the previous **tagged evidence bundle**. Identity of a simulation run stays in `RunManifest`, not in the container tag.

### MLOps

The run manifest in [design.md](../../.kiro/specs/coflow5-reliable-agentic-platform/design.md) is the source of truth.

- MLflow is optional. It may **index** `run_id`, `scenario_hash`, git SHA, controller version, and artifact paths. It must not mint a second run identity.
- Row 09 is the evaluation gate even before any learned model exists.
- Row 10 A4 records `model_version` and fails CI on chronological leakage.
- Row 12 Synapse golden questions gate prompt/embedding/corpus changes. Template fallback is mandatory. This is LLMOps, not control.
- Row 15 DQN stays blocked until the cooperative core freezes. Checkpoints sit beside the manifest. They are not loaded by the hosted read-only API.

### Docker timing

Container packaging is allowed **only as a later product path**, and only after native row 01 has a passing `gate.json`. Until then:

- Docker is not a required smoke-test command.
- PR CI must stay SUMO-free.
- `deploy/` images must stay SUMO-free even after 01 gates.

## Consequences

### Positive

- A reviewer can see DevOps and MLOps without confusing them with live-city CD.
- Synapse or API failure cannot reach TraCI from the hosted path.
- Evaluation identity stays joinable when a UI is added.

### Negative

- GitHub-hosted runners will not gate row 01. A self-hosted Windows runner with an allowed `libsumo` is required for `eval.yml`.
- The hosted demo cannot run a live SUMO job. New scenarios still come from the local runner.

### Required safeguards

- Architecture tests fail if `api`, `ui`, or `synapse` import `traci` or `libsumo`.
- Architecture tests fail if `deploy/*.Dockerfile` or `deploy/docker-compose.yml` install Eclipse SUMO.
- Architecture tests fail if `pr.yml` runs the native Windows smoke test.
- Claim flags stay: simulation is not deployment evidence.

## Rejected alternatives

- **Docker as the row 01 requirement** — contradicts native Windows before containers.
- **SUMO inside the hosted API image** — puts actuation capability on the public path.
- **MLflow as source of truth** — splits `run_id`.
- **Kubernetes / Kafka / Pinecone** — scale and tenancy this corpus does not have.
- **Nightly green when SUMO is missing** — hides the ungated Control plane.

## References

- [ADR-0001](0001-reliable-ai-platform-boundary.md)
- [ADR-0002](0002-six-builders-one-queue-row.md)
- [`coflow5-synapse-portfolio-design.md`](../architecture/coflow5-synapse-portfolio-design.md)
- [`harness/queue.tsv`](../../harness/queue.tsv)
- [`.github/workflows/pr.yml`](../../.github/workflows/pr.yml)
- [`.github/workflows/eval.yml`](../../.github/workflows/eval.yml)
- [`deploy/README.md`](../../deploy/README.md)
