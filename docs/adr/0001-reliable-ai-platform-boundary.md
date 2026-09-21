# ADR-0001: Position CoFlow-5 as a reliable AI decision platform

**Status:** Accepted  
**Date:** 20 September 2026

## Context

CoFlow-5 must satisfy three different goals without confusing them:

- a professor-verifiable SUMO and multi-agent project;
- a feasible 12-week build for three dependable contributors;
- a 2026 AI-engineering portfolio demonstrating RAG, workflows, evaluation, LLMOps, and production software.

Putting an LLM in the second-scale traffic-control loop would weaken safety, reproducibility, latency, and failure isolation. Building every specialist as a learned model would also exceed the current local-compute and schedule evidence.

## Decision

CoFlow-5 will be presented as a **reliable AI decision platform for urban traffic simulation**.

1. A deterministic safety-constrained control plane owns SUMO actuation.
2. A1 is the sole authority for signal changes and uses cooperative Max-Pressure in the required slice.
3. A2, A3, and A5 are transparent advisory domain agents in the required slice.
4. A4 uses bounded forecasting and residual incident detection.
5. Synapse is a non-actuating retrieval, explanation, evaluation, and human-reviewed what-if layer.
6. A1–A5 use typed Python modules and in-process contracts.
7. LangGraph is limited to Synapse and added only for persisted approval/resume or bounded verify/retry branching.
8. Retrieval starts with exact local search; PostgreSQL/pgvector is added for SQL-backed provenance and the hosted read-only product. Pinecone is not the default.
9. Cooperation, authority, evaluation, and failure recovery are the core. A shared DQN is an optional experiment after that core is frozen.
10. The evaluation spine—baselines, paired seeds, invariant tests, failure injection, citations, abstention, latency, and cost—has priority over feature count.
11. The scenario ladder uses a controlled 4×4 benchmark plus a Tunis OSM/TRANSTU GTFS showcase with explicitly synthetic/calibrated road demand.

## Consequences

### Positive

- LLM failure cannot alter traffic actions.
- The project demonstrates both classical ML and production AI engineering.
- The required platform remains complete without RL; an optional null DQN result remains publishable because the harness and recovery behavior are independently valuable.
- Framework use is justified by observable requirements rather than résumé logos.
- Three core contributors can own control, data/evaluation, and API/Synapse/evals in parallel.

### Negative

- The first version has fewer learned specialists than the conceptual five-agent design.
- A hosted LLM introduces network, cost, privacy, and provider-version dependencies.
- pgvector and LangGraph add Month-2 integration work.
- Tunis road demand is not live observed traffic and cannot validate deployment claims.

### Required safeguards

- Capability boundaries—not prompts—must prevent Synapse from reaching TraCI.
- A deterministic template/event-view fallback is mandatory.
- Resume and portfolio claims use measured values only.
- A one-day toolchain and throughput smoke test must replace compute estimates before training-volume commitments.

## Rejected alternatives

- **Five LLM traffic agents:** wrong authority and latency model for safety-critical actuation.
- **LangGraph for A1–A5:** obscures deterministic control semantics and adds framework failure modes.
- **Pinecone by default:** solves scale and tenancy not present in the initial corpus.
- **RL as a core dependency:** it would put training risk ahead of cooperation, authority, evaluation, and failure recovery.
- **All five agents learned:** too much training and evaluation breadth for the delivery envelope.
- **Tunis-only experiments:** locally relevant but insufficiently controlled for clean baseline comparisons.
- **Synthetic grid only:** reproducible but misses the real-data ingestion and local public-transport story.

## References

- [`coflow5-synapse-portfolio-design.md`](../architecture/coflow5-synapse-portfolio-design.md)
- [`ai-engineering-stack-and-jd-fit.md`](../../.scratch/coflow5-feasibility/research/ai-engineering-stack-and-jd-fit.md)
- [`local-toolchain-and-compute-feasibility.md`](../../.scratch/coflow5-feasibility/research/local-toolchain-and-compute-feasibility.md)
