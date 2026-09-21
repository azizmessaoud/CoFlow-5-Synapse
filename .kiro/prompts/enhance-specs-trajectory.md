# Kiro prompt — spec enhancement trajectory

Copy everything below the line into Kiro after opening this repository.

---

You are enhancing CoFlow-5 Synapse specifications, not rewriting the product.

This is a university Design Thinking + Data Science project on Eclipse SUMO. The course brief is `SUMO_forStudents.docx`, transcribed in `docs/source/course-brief.md`.

Challenge:

> How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?

Required course outcomes: a working prototype, experiments under different traffic conditions, comparison with an appropriate baseline, and data-driven strengths and limitations. Evidence matters more than technological complexity.

## Read these files first, in this order

1. `docs/source/course-brief.md`
2. `.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md`
3. `.kiro/steering/product.md`
4. `CONTEXT.md`
5. `docs/adr/0001-reliable-ai-platform-boundary.md`
6. `.kiro/specs/coflow5-reliable-agentic-platform/requirements.md`
7. `.kiro/specs/coflow5-reliable-agentic-platform/design.md`
8. `.kiro/specs/coflow5-reliable-agentic-platform/tasks.md`
9. `CoFlow-5_System_Requirements_Book.md`
10. `coflow5-empathize-pack.md`
11. `coflow5-define-ideate.md`
12. `.scratch/coflow5-reliable-ai-platform/spec.md`
13. `docs/architecture/coflow5-synapse-portfolio-design.md`

Do not invent a new Empathize roster. Do not mark Prototype or Test complete.

## What is already decided

Keep these decisions. Improve precision. Do not reopen them unless you find a contradiction that would break the course brief.

- Product: Reliable AI decision platform for urban traffic simulation.
- Design Thinking Stages 1–3 are done. Stages 4–5 are next.
- Eight User Personas: Amara, David, Chidi, Rosa, Marcus, Yuki, Maria, Omar.
- Five domain agents cooperate. Only A1 Flow writes traffic signals.
- A2 Emergency, A3 Multimodal, A4 Situation, A5 Sustainability only request, forecast, alert, or advise.
- Synapse retrieves evidence and explains immutable decisions. It never actuates SUMO.
- Required A1 method: cooperative Max-Pressure behind a deterministic safety mask.
- Required recovery: Max-Pressure → actuated → fixed-time.
- Required baselines: fixed-time and actuated, paired seeds, honest null results.
- Reinforcement learning is optional and cannot block delivery.
- A1–A5 are typed Python modules with an in-process message board. LangGraph is only for Synapse later.
- Retrieval starts local. PostgreSQL/pgvector is earned. Pinecone is not default.
- Hosted LLM is allowed only behind a provider-neutral interface plus a template fallback.
- First scientific world: controlled 4×4 SUMO grid. Tunis OSM + official TRANSTU GTFS is a later showcase with synthetic/calibrated road demand labelled as such.
- Team: 12 weeks, three dependable contributors. Optional students cannot own the critical path.
- Claim flags: no lives saved, no measured air quality, no best-episode headline, personas are research-informed not interview-validated.

## Your job

Produce the best next trajectory that:

1. fills remaining spec and integration gaps;
2. uses a smart methodology rather than more frameworks;
3. chooses the smallest stack that still looks production-grade;
4. prevents future integration problems.

Work in this sequence.

### A. Gap analysis

Compare the course brief, Design Thinking record, system requirements book, Kiro requirements, design, and tasks.

Make a table with: gap, why it matters, which User Persona or How-might-we it serves, severity, whether it is a spec gap or an implementation gap, and the cheapest valid fix.

Look especially for:

- missing message schemas, reason codes, and TTL rules;
- missing safety-mask invariants;
- missing run-evidence-bundle fields;
- missing KPI definitions per persona;
- missing frozen scenario/seed plan;
- missing owner seams between Control, Data/Eval, and API/Synapse;
- stack items named before their interface exists;
- contradictions between older requirements books and ADR-0001;
- anything that would make SUMO, agents, API, RAG, and UI unable to join on one run_id.

### B. Best trajectory

Recommend one vertical-slice path. Do not recommend building all five learned models, a city-scale network, and a polished dashboard in parallel.

Required order:

1. Pin SUMO + Python 3.11 and measure throughput.
2. One junction, then corridor, then frozen 4×4 grid.
3. Run evidence bundle as the single integration seam.
4. Safety mask + signal executor with one writer.
5. Fixed-time and actuated baselines.
6. Cooperative Max-Pressure A1.
7. Typed message board.
8. A2 and A3 rule-based requests.
9. Failure-injection tests.
10. Evaluation harness and ablations.
11. A4 forecast/incident ladder.
12. A5 advisory weights.
13. FastAPI over the evidence bundle.
14. Local retrieval + template explanations.
15. Hosted LLM adapter, golden evals, Phoenix.
16. React view over precomputed runs.
17. Tunis OSM/GTFS showcase.
18. Optional DQN only after feature freeze.

If schedule slips, cut from the bottom, never from safety, authority, baselines, evidence bundle, or recovery.

### C. Methodology

Keep Design Thinking visible in the spec: Empathize → Define → Ideate → Prototype → Test.

Inside Prototype/Test, use the Data Science loop: Problem, Success criteria, Data, EDA, Preparation, Baseline, Model, Evaluation, Error analysis, Iteration, Deployment, Monitoring.

For software, use contract-first integration:

- one run evidence bundle is the highest test seam;
- Pydantic schemas are the module boundaries;
- agents never import TraCI except through the SUMO adapter;
- Synapse never receives the signal-executor capability;
- every feature has an on/off ablation or is labelled unproven;
- every optional library is added only after a typed interface already works without it.

### D. Best stack, staged

Do not dump the full stack into week 1.

Month 1, required:

- Python 3.11, pinned SUMO, TraCI, measured libsumo
- Pydantic v2, pytest, Hypothesis, Ruff, Pyright
- NumPy, PyArrow, Parquet, DuckDB
- cooperative Max-Pressure, fixed-time, actuated
- in-process message board

Month 2, earned:

- LightGBM, scikit-learn
- FastAPI
- sentence-transformers and exact local retrieval
- hosted LLM adapter + template fallback
- PostgreSQL/pgvector only if provenance/filtering is now needed
- Phoenix after a golden question set exists

Month 3, earned:

- React + Vite + TypeScript
- LangGraph only for Synapse approval/resume
- Docker Compose after native Windows execution works
- Tunis showcase
- optional PyTorch DQN

Rejected defaults:

- LLM controlling lights
- LangGraph for A1–A5
- Redis/Kafka/Kubernetes on the critical path
- Pinecone
- LlamaIndex as the foundation
- both Phoenix and LangSmith
- RoadwayVR tutorial as a runtime dependency
- microservice per agent

### E. Integration-risk controls

Add or strengthen spec items that prevent these failures:

- two writers to the same signal;
- Synapse or A2–A5 reaching TraCI;
- UI inventing KPIs not present in the evidence bundle;
- RAG answering without an event id and citation;
- training/eval seed leakage;
- future rows leaking into A4;
- SUMO version drift;
- schema drift between agents, API, and Parquet;
- optional DQN changing the required recovery path;
- Docker/WSL becoming a blocker before native smoke tests pass.

For each risk, specify: interface, owner workstream, test, and fallback.

### F. Edit the spec files

Update, do not fork:

- `.kiro/specs/coflow5-reliable-agentic-platform/requirements.md`
- `.kiro/specs/coflow5-reliable-agentic-platform/design.md`
- `.kiro/specs/coflow5-reliable-agentic-platform/tasks.md`
- `.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md` only if a Design Thinking fact was missing

Add:

- a short integration contract: module names, allowed imports, event/message/run schemas, and join keys;
- a cut-ladder if compute or people slip;
- a contradiction log if older files disagree with ADR-0001.

Keep requirement IDs stable where possible. Use the glossary in `CONTEXT.md`. Write acceptance criteria in WHEN/THEN/THE SYSTEM SHALL form.

## Done when

A professor can see Design Thinking Stages 1–3, the chosen architecture, and a 12-week path that produces a testable SUMO prototype even if RL, Tunis, React, LangGraph, and pgvector are never added.
