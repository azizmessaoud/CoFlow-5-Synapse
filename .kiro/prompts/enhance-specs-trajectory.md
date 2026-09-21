# Kiro prompt — harness + spec trajectory

Copy everything below the line into Kiro.

Output style: https://github.com/ayghri/i-have-adhd  
Harness pattern: https://github.com/flyrank-bih/harness-engineering-playbook  
Do not copy the Shopify theme. Lift router, queue, evidence pack, gate, and exit rules only.

---

Read `AGENT_GUIDE.md` first.

Then read, in order:

1. `docs/source/course-brief.md`
2. `.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md`
3. `docs/adr/0001-reliable-ai-platform-boundary.md`
4. `docs/harness/how-it-works.md`
5. `docs/harness/loop-and-exit.md`
6. `docs/harness/contract-and-evidence.md`
7. `.kiro/steering/product.md`
8. `.kiro/steering/harness.md`
9. `.kiro/steering/output-style.md`
10. `CONTEXT.md`
11. `.kiro/specs/coflow5-reliable-agentic-platform/requirements.md`
12. `.kiro/specs/coflow5-reliable-agentic-platform/design.md`
13. `.kiro/specs/coflow5-reliable-agentic-platform/tasks.md`
14. `harness/queue.tsv`
15. `CoFlow-5_System_Requirements_Book.md`
16. `coflow5-empathize-pack.md`
17. `coflow5-define-ideate.md`
18. `.scratch/coflow5-reliable-ai-platform/spec.md`

Do not invent User Personas. Do not mark Prototype or Test complete. Do not make DQN required. Do not put an LLM in the Control plane.

## Job

Enhance the existing specs so Kiro and later workers can execute CoFlow-5 through a harness, not a long chat.

Fill gaps. Stage the stack. Prevent integration failures. Keep Design Thinking 1–3.

## Locked product

- Course HMW from `SUMO_forStudents.docx`.
- Eight User Personas: Amara, David, Chidi, Rosa, Marcus, Yuki, Maria, Omar.
- Five agents. Only A1 writes signals.
- Required A1: cooperative Max-Pressure.
- Recovery: Max-Pressure → actuated → fixed-time.
- Synapse never reaches TraCI.
- Join key: `run_id`.
- Evidence bundle is product truth. `gate.json` is harness truth. They must agree.

## Work method

Treat this Kiro session as **CAPTURE for the harness**, not BUILD of SUMO yet.

1. Gap table: gap, persona/HMW, severity, spec vs harness vs product, cheapest fix. Show five highest first.
2. Seal or correct `harness/queue.tsv`. One row = one worker. Optional DQN stays `blocked`.
3. Write or tighten `harness/work/<id>/contract.json` for rows 01–09 at minimum.
4. Specify `gate.json` checks, forbidden imports, and tests per row.
5. Patch `.kiro/specs/.../requirements.md`, `design.md`, `tasks.md` so each product requirement names its queue row and join keys.
6. Add an integration contract: allowed imports, message envelope, run manifest fields, `run_id` joins.
7. Add a cut-ladder. Cut from the bottom of the queue. Never cut rows 01–09.
8. Add contradiction log if older files fight ADR-0001.
9. Keep requirement IDs stable. WHEN/THEN/THE SYSTEM SHALL.
10. Restate every turn: which queue row, which phase, what gate is red.

## Stack staging the harness must enforce

Month 1 only after row 01 gates: Python 3.11, pinned SUMO, TraCI, measured libsumo, Pydantic, pytest, Hypothesis, Parquet, DuckDB, Max-Pressure, in-process bus.

Month 2 only after rows 01–09 gate: LightGBM, FastAPI, local embeddings, template Synapse, hosted LLM adapter, pgvector if provenance now needs SQL, Phoenix after golden set.

Month 3 only after 01–12 gate: React over precomputed runs, LangGraph for Synapse approval only, Docker after native Windows works, Tunis showcase, optional DQN.

Rejected in contracts: LLM signal write, LangGraph for A1–A5, Pinecone, Kafka, Kubernetes, microservice per agent, RoadwayVR tutorial as runtime.

## Integration risks that must become gates

- two writers to one signal
- Synapse or A2–A5 calling TraCI
- UI KPIs not in the evidence bundle
- RAG answer without `event_id` and citation
- A4 future-row leakage
- SUMO version drift
- schema drift between agents, API, Parquet
- DQN changing the required recovery ladder
- Docker required before the native smoke test

## Stop conditions for this Kiro run

Exit 0: requirements, design, tasks, queue, and contracts 01–09 are consistent; a professor can see DT 1–3 plus a path that still ships if rows 10–15 never start.

Exit 3: write `harness/BLOCKED` if a human must choose.

Do not start SUMO implementation in this run unless row 01 contract cannot be written without a measured command.

## Output

Lead with the next file to edit. Number steps. Cap lists to five per group. End with one next action.
