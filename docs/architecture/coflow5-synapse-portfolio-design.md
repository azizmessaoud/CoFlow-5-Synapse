# CoFlow-5 Synapse — AI Engineering Portfolio Design

**Status:** Accepted direction; implementation results are not yet available  
**Decision date:** 20 September 2026  
**Delivery envelope:** 12 weeks, five students nominally, three dependable core contributors  
**Evidence:** [`ai-engineering-stack-and-jd-fit.md`](../../.scratch/coflow5-feasibility/research/ai-engineering-stack-and-jd-fit.md)

## Project definition

**Name:** CoFlow-5 Synapse  
**Positioning:** a reliable AI decision platform for urban traffic simulation  
**One-line pitch:** CoFlow-5 combines safety-constrained traffic control in SUMO with fault-tested domain agents and a retrieval-grounded operator copilot whose explanations are evaluated, traced, and structurally unable to change a traffic light.

It addresses a practical gap in traffic-AI demonstrations: learned control, specialist requests, explanations, and operational failure handling are usually evaluated separately. CoFlow-5 makes them one auditable evidence chain:

`answer → cited policy → immutable decision event → controller/configuration → scenario/seed`

The project is not a live-city deployment and must not claim measured air quality, lives saved, or real Tunis traffic. SUMO and HBEFA provide simulation evidence and emission proxies.

## What ships in 12 weeks

### Required reliability slice

- A controlled 4×4 SUMO benchmark with fixed-time, actuated, and Max-Pressure baselines.
- A1 as the sole signal actuator, using cooperative Max-Pressure behind deterministic action masks and a recovery ladder.
- A2 emergency and A3 pedestrian/transit requests as transparent rules with accept/reject reason codes.
- A4 using a LightGBM forecast benchmark plus EWMA/CUSUM residual incident detection.
- A5 as a deterministic sustainability adviser; a learned emissions surrogate is optional.
- Typed in-process messages with timestamps, TTLs, confidence, correlation IDs, schema versions, and stale-message handling.
- Immutable event logs, scenario/configuration hashes, paired seeds, failure injection, and DuckDB analyses over Parquet.
- A bounded Synapse flow: classify question, fetch event, retrieve policy, draft cited explanation, verify facts, answer or abstain.
- FastAPI plus a focused React/Vite interface for scenario comparison, agent requests, fallbacks, citations, and traces.
- A Tunis showcase built from OSM and the official TRANSTU GTFS/CKAN source, using honestly labelled calibrated synthetic road demand.

### Explicit stretch work

- A shared DQN, MAPPO, LSTM/PatchTST, graph neural networks, a learned A5 surrogate, Redis, a local generator, and a full realistic-city training sweep.
- Civic planning comparisons such as bus lanes, bike lanes, and traffic calming.
- These may be attempted only after the reliability slice and evaluation gates are frozen.

## Hugging Face task mapping

The three required Hugging Face-aligned task families are:

1. **Time-series forecasting:** A4 link-flow/arrival prediction, benchmarked against persistence and tree-based baselines. This is a supported model family, but not necessarily a top-level hosted HF pipeline.
2. **Feature extraction / embeddings:** policy and SUMO-document retrieval using a small sentence-transformer, with model, pooling, normalization, and vector dimension recorded.
3. **Text generation and summarization:** cited event explanations and end-of-shift reports. “Summarization” applies only when a longer trace is actually condensed.

**Reinforcement Learning** is an optional A1 experiment after the cooperative core is frozen. If attempted, use PyTorch or established traffic-RL tooling; Hugging Face TRL is not the correct library for traffic-control DQN. RAG is an application architecture, not one Hugging Face task. Graph ML and tabular regression remain earned extensions, not headline claims.

## Recommended stack

### Control and evaluation plane

- Python 3.11 with pinned dependencies.
- One pinned SUMO release; TraCI for visual debugging and benchmarked libsumo for headless batches.
- Typed Python modules plus Pydantic/dataclass contracts.
- Cooperative Max-Pressure for required A1 control; LightGBM for A4; PyTorch CPU only for optional DQN.
- In-process event board/queues; no Redis on the critical path.
- Parquet, DuckDB, and a JSON/SQLite run manifest.
- pytest invariant, seeded integration, and fault-injection tests.
- Optional local MLflow with SQLite only after the run manifest is stable.

### Synapse and product plane

- FastAPI, Pydantic, idempotency keys, bounded jobs, cancellation, and structured errors.
- React/Vite with server-sent events or WebSockets only where progress streaming is useful.
- Custom deterministic ingestion first: source manifests, content hashes, stable chunk IDs, and provenance metadata.
- A small sentence-transformer and exact local cosine search as the development fallback.
- PostgreSQL plus pgvector in Month 2 for SQL-backed provenance, filters, and the hosted read-only experience.
- A provider-neutral hosted-LLM adapter plus a mandatory deterministic template fallback.
- LangGraph in Month 2 only for persisted human approval/resume and bounded verify/retry branching. A1–A5 remain typed Python, never LangGraph nodes.
- OpenTelemetry/OpenInference semantics and Phoenix after the golden evaluation set exists.
- Dockerized local reproduction plus a hosted API/dashboard over precomputed runs. Continuous cloud SUMO training is not promised.

### Deliberately excluded from the default

- Pinecone: it solves scale and tenancy that the initial corpus does not have.
- LlamaIndex as a foundation: add one connector only if a difficult changing source earns it.
- LangSmith alongside Phoenix: choose one observability system.
- Kafka, Kubernetes, five conversational LLM agents, LLM fine-tuning, or LLM signal actuation.

## Why this stack is staged

The selected portfolio architecture includes LangGraph and pgvector, but neither belongs in the first vertical slice.

- **Month 1:** typed workflows, exact local retrieval, deterministic templates, SUMO baselines, event contracts, and evaluation manifests.
- **Month 2:** cooperation and failure-recovery evaluation, one or two specialist request paths, hosted explanations, golden RAG/evaluation data, FastAPI, pgvector, and Phoenix.
- **Month 3:** LangGraph approval/resume, A4 forecasting/incident detection, Tunis showcase, React polish, model/message outage sweeps, and case-study packaging.

This sequence prevents framework setup from masquerading as progress while still demonstrating recognizable production tools.

## Scenario trade-offs and gaps

### Controlled 4×4 benchmark

Best for paired comparisons, fault injection, ablation, and reproducibility. Its gap is external realism; results must not be generalized to Tunis.

### Tunis OSM + TRANSTU GTFS showcase

Best for local relevance, real data ingestion, transit personas, and a memorable portfolio story. The official feed is scheduled GTFS, not confirmed live road traffic. Road demand therefore remains synthetic/calibrated and must be labelled as such.

### LuST/Luxembourg fallback

Useful if a reusable city-scale SUMO scenario is required, but its original validated mobility was produced for old SUMO versions. Running it on a modern SUMO release does not preserve the original validation claim.

### Optional learned control

The required platform uses cooperative Max-Pressure. DQN can demonstrate additional RL depth, but it can consume time without improving control. Attempt it only after the core is frozen. Max-Pressure may equal or beat it; that result is acceptable when reported with paired confidence intervals and failure analysis.

### Multi-agent design

A1–A5 are domain agents with state, contracts, and failure semantics—not five chatbots. Rules for A2/A3/A5 improve auditability and delivery odds; the gap is less learned-model breadth.

### RAG and explanations

The small corpus does not require a managed vector service. The hard problem is evidence fidelity, not vector scale. The evaluation must separate retrieval misses, unsupported citations, event inconsistency, abstention, latency, and cost.

### Hosted LLM

It improves demo quality on CPU-only machines but adds cost, network, privacy, rate-limit, and model-version risks. The template fallback and provider-neutral interface are required.

## Evaluation contract

### Control and simulation

- Zero conflicting-green or clearance-truncation violations.
- A1 remains operational when advisory messages are missing, duplicated, stale, delayed, or malformed.
- Learned-policy failure activates Max-Pressure, then actuated, then fixed-time fallbacks as specified.
- Compare fixed-time, actuated, and cooperative Max-Pressure with common random numbers and paired intervals. Apply the same contract to optional DQN.
- Report unfinished trips, teleports, tail delay, emergency delay, pedestrian waits, transit regularity, and emissions proxies.
- Publish null and negative results; never headline a best episode.

### Retrieval and generation

- Retrieval hit/recall at `k` on a versioned operator-question set.
- Citation validity and policy-source correctness.
- Exact consistency with immutable decision fields and required reason codes.
- Abstention on unsupported questions.
- End-to-end latency, token use, estimated cost, and provider/template fallback rate.
- LLM-as-judge may be secondary; deterministic checks and human-labelled cases remain the reference.

### Reliability demonstration

The portfolio demo must visibly prove:

- kill Synapse → the same control inputs produce the same traffic actions;
- drop agent messages → A1 continues locally;
- fail cooperative Max-Pressure → actuated and fixed-time recovery activates;
- remove retrieval support → Synapse abstains or returns structured event facts;
- change a model or prompt → the regression suite reports the effect.

## Mapping to AI-engineering roles

Representative 2026-oriented roles emphasize production workflows, evaluation, RAG/context engineering, observability, APIs/data systems, safe tool boundaries, latency, cost, and graceful failure. CoFlow-5 demonstrates:

- **Agent/workflow engineering:** bounded LangGraph advisory workflow, typed tools, approval, retries, and explicit authority.
- **RAG/context engineering:** provenance-aware ingestion, pgvector filtering, citations, retrieval evaluation, and abstention.
- **AI evaluation:** golden datasets, deterministic verifiers, paired simulation baselines, regression gates, and ablations.
- **LLMOps:** provider/prompt/embedding versions, traces, latency/cost, Phoenix experiments, and fallback monitoring.
- **ML engineering:** forecasting, chronological splits, reproducible manifests, honest negative results, and optional DQN evaluation after the core is frozen.
- **Production SWE:** FastAPI contracts, React integration, idempotency, cancellation, SQL, Docker, CI, and failure isolation.

No evidence supports claiming that every AI-engineering job requires LangGraph, RAG, or RL. The defensible claim is that the project shows measurable, production-shaped AI engineering across model and software boundaries.

## Team ownership

The schedule assumes three dependable workstreams:

1. **Control:** SUMO, A1, safety masks, baselines, and fallback tests.
2. **Data/evaluation:** scenarios, OSM/TRANSTU ingestion, A4, manifests, statistics, and reports.
3. **API/Synapse/evals:** FastAPI, React integration, LangGraph, retrieval, pgvector, Phoenix, golden datasets, and end-to-end reliability.

The requesting student owns Workstream 3. The other two students may contribute dashboard polish, documentation, or additional scenarios, but nothing assigned to them may block the reliability slice.

## Resume-ready metrics

Use only measured values. Replace brackets after evaluation:

- Built a safety-constrained AI traffic platform evaluated across **[N scenarios] × [N seeds]**, with **zero [tested safety violations]** and deterministic fallback under **[N fault modes]**.
- Implemented a provenance-aware RAG/evaluation pipeline over **[N documents/chunks]**, achieving **[retrieval recall@k]**, **[citation validity]**, and **[event-consistency rate]** at **[p95 latency]** and **[$ cost/query]**.
- Designed FastAPI/LangGraph workflows with human approval, pgvector retrieval, Phoenix traces, and provider outage fallback; regression-tested **[N golden cases]** in CI.
- Evaluated cooperative Max-Pressure against fixed-time and actuated control across **[N scenarios × N seeds]**, including **[N communication/controller/model fault modes]** and measured recovery behavior.
- Optional only: compared DQN with Max-Pressure using paired seeds and confidence intervals; improved **[specific KPI] by [measured value]** or documented the null result and retained Max-Pressure.
- Integrated OSM and official TRANSTU GTFS data into a reproducible Tunis SUMO showcase with versioned source, scenario, configuration, and model hashes.

## Portfolio package

- A 90-second reliability demo, not a generic chatbot video.
- Architecture and authority-boundary diagram.
- Reproduction command and pinned environment.
- Public scenario/evaluation manifests and selected run artifacts.
- Model/system cards and failure taxonomy.
- Golden retrieval/explanation dataset with CI results.
- A case study covering rejected alternatives, null results, trade-offs, and cut decisions.
- Separate “team result” and “my contribution” sections, with the API/Synapse/evaluation work demonstrated in code and traces.
