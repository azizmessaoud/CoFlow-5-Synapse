# CoFlow-5 × SUMO-Synapse — Project Context

**One-line pitch:** CoFlow-5 is a five-agent cooperative traffic management system built on Eclipse SUMO, with a LLM "Synapse layer" on top that grounds agent decisions in domain knowledge (RAG), explains every decision from an audit log, and runs under production LLMOps — an evidence-based answer to *«How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?»*

This file is the project's front door: what we're building, why, how it's organized, and how the research and portfolio framing fit together. Detailed companions: the **verified design document** (architecture, hypotheses, experiment matrix), **personas & journeys v2** (Empathize deliverables with the evidence trail), and the **design-patterns analysis** (micro/macro trade-offs).

---

## 1. The problem

Urban traffic congestion changes continuously with time, place, demand and unexpected events. Signal control today optimizes vehicle throughput, while everything else — emergency vehicles, pedestrians, transit reliability, air quality, incident response — is handled by separate, sometimes conflicting mechanisms. The literature is blunt about the state of the art:

- RESCO (NeurIPS 2021) found claimed-SOTA RL signal controllers **struggle on realistic networks** and are often beaten by a plain decentralized DQN; results tables report best episodes, overstating converged performance.
- T-REX (2025) quantified that independent RL controllers degrade sharply under incidents; hierarchical coordination is steadier but ~14× more expensive to train.
- A DQN study on full Luxembourg (203 signals) found **no significant difference** vs rule-based control — a rare published null result.
- Communication reliability is almost never tested: essentially one direct quantification exists (Finkelberg, IEEE T-ITS 2022).
- Prior work covers two or three objectives at a time; **no found work co-arbitrates five objectives (EV, pedestrian, transit, emissions, incidents) in one controller.** That is our gap claim — stated narrowly and defensibly.

CoFlow-5 targets that gap with a system that must *earn every feature by ablation* and degrade gracefully when communication, sensors or agents fail.

## 2. What we are building

A role-decomposed multi-agent system with **one actuation authority** and **four advisory specialists**, over SUMO (libsumo/TraCI, 1 s steps):

| Agent | Role | Method | Sole authority? |
|---|---|---|---|
| **A1 Flow** | Per-junction signal control + arbitration of all requests | Cooperative Max-Pressure with deterministic masking; optional DQN experiment | **Yes — only A1 writes to signals** |
| **A2 Emergency** | EV routing + corridor preemption with queue pre-clearance | Time-dependent shortest path + priority requests; logged civilian-delay budget | No — requests |
| **A3 Multimodal** | Pedestrian guarantees + bus headway regularity | Wait-aware escalation + conditional, lateness-gated TSP bids | No — bids |
| **A4 Situation** | Forecasting (30–120 s arrivals; 5–30 min links) + incident detection | LightGBM→LSTM ladder; EWMA/CUSUM residual detection | No — alerts with confidence |
| **A5 Sustainability** | Emission hot-spot care without wrecking mobility | λ_eco dual update; proxy rewards; HBEFA KPIs | No — weights |

**The three rules (kid-friendly, technically literal):** ① Safety first — never conflicting greens, clearance never truncated; ② the boss is boss — only A1 acts, everyone else asks; ③ backup plans — if messaging or an adviser fails, A1 continues with Max-Pressure; if the primary controller fails, recovery continues to actuated → fixed-time.

**The Synapse layer (LLM cognitive layer, never in the control loop).** On top of the five agents sits an LLM-powered layer with three jobs: (a) **RAG grounding** — a retrieval pipeline over SUMO docs, traffic-engineering guidance and the persona playbook, so explanations cite real rules; (b) **explanation** — it turns the reason-coded decision log into human-readable accounts for the control-room personas; (c) **orchestration of the *advisory* loop only** — it can query state, run what-if scenario analyses (AgentSUMO-style) and draft recommendations for human review. It **never** sets a signal. This is a deliberate correction of the naive "LLM orchestrates the traffic" framing: LLM latency and reliability are wrong for second-scale control (the evidence trail: CoLLMLight needs async caching to stay real-time; AgentSUMO is scenario tooling with no control loop, no seeds, no CIs; production systems like SCATS ship deterministic override). The LLM dies → nothing in the control path notices. That is the design.

## 3. HuggingFace tasks this project exercises

| HF task (from the HF task index) | Where it lives |
|---|---|
| **Time Series Forecasting** | A4: link-flow forecasting (LightGBM → LSTM → GNN ladder); incident detection via EWMA/CUSUM on forecast residuals |
| **Reinforcement Learning (optional)** | A1: shared DQN experiment after the cooperative core is frozen |
| **Graph Machine Learning** | A1/A4: movement-graph encodings; [ADV] CoLight-style graph attention |
| **Tabular Regression** | A5: emission surrogate regressed on SUMO/HBEFA ground truth; fleet-mix sweeps |
| **Question Answering / RAG (Feature Extraction, `all-MiniLM-L6-v2`-class embedders)** | Synapse layer: grounded Q&A over SUMO docs + ops playbooks (pgvector) |
| **Text Generation / Summarization** | Synapse: decision-log explanations; end-of-shift incident summaries for Rosa/Omar |

## 4. Tech stack (merged and justified)

| Layer | Choice | Why |
|---|---|---|
| Simulation | **SUMO ≥ 1.24** + libsumo/TraCI | Documents transit, EVs, emissions, SSM safety measures; `agentsumo-mcp` (MIT) provides a reusable scenario pipeline (OSM→net→routes→run→SQLite) usable without the LLM |
| Control | Cooperative Max-Pressure required; optional PyTorch DQN experiment | Cooperation, authority, evaluation and recovery are core; RL cannot block delivery |
| Agent orchestration (advisory/explain layer only) | **LangGraph** | Stateful, cyclical workflows for the Synapse layer's reason→retrieve→explain loop; explicitly *not* in the control path |
| RAG | **LlamaIndex connectors + pgvector on PostgreSQL** | Production-pattern RAG over docs/playbooks; enterprise-realistic |
| Core LLM | Open-weights via HF (Llama/Mistral-class) | Ecosystem proficiency; explainer role only |
| Messaging | In-process asyncio pub/sub (Redis Streams if a distribution demo is needed) | TTL, staleness discounts, heartbeats; Kafka overkill |
| Data | Parquet event logs + DuckDB feature store; `simulations.db` SQL comparison | Cross-scenario deltas; A4 training datasets with chronological splits |
| Serving | FastAPI (REST + WebSocket) | Control/query endpoints; LLMOps-ready |
| Observability | LangSmith or Arize Phoenix for the LLM layer; **trackio** dashboards for training runs | Debugging agentic systems is a JD requirement |
| Evaluation | Custom harness: baselines (fixed-time, actuated, Max-Pressure), common random numbers, paired stats, rliable-style intervals; MLflow regression gates | The project's spine — honest comparison, pre-registered hypotheses H1–H8 |
| Deployment | Docker Compose (SUMO, API, agents, DB) | Reproducibility; pinned SUMO + Python; git hash in every log |

## 5. Milestones (tiered, feature-freeze discipline)

- **Tier 0 / MVP (week 6):** SUMO grid; A1 vs fixed-time/actuated/Max-Pressure; KPIs + statistics. *Satisfies the brief alone.*
- **Tier 1 (week 10):** A2, A3, A5 + message bus + arbitration; ablations. Gate G3 = feature freeze.
- **Tier 2 (week 12):** learned A4, incident detection, communication-failure sweeps, realistic network, scale.
- **Synapse layer (parallel, portfolio-facing):** RAG + explain panel + eval harness + observability land incrementally from week 6 onward.

If a tier slips, cut features, not rigor. A well-evidenced negative result beats an untested feature list.

## 6. Evaluation & honesty commitments

- Baselines get equal tuning effort; common random numbers make comparisons paired; pre-registered hypotheses (H1–H8) with Holm correction; never report best episodes.
- All numeric targets are **proposed acceptance criteria tested against baselines** — not achieved results, not literature-established thresholds.
- Simulation ≠ deployment evidence; HBEFA outputs are emission estimates (proxies), not air-quality measurements; simulated EV time savings are never translated into predicted lives saved.
- Teleports/standstills counted as failures; unfinished trips counted in P95; displacement checks (emissions *and* delay) reported, not buried.

## 7. Portfolio / JD mapping

| JD theme (2026 postings) | What this project evidences |
|---|---|
| Agentic AI architecture | Five specialized agents + deterministic safety + advisory LLM layer, with role separation justified by ablation — not "agents because agents" |
| Advanced RAG | Grounded retrieval over domain docs; faithfulness-evaluated explanations (does the account match the decision log?) |
| LLM evaluation & guardrails | LLM-as-judge faithfulness scoring; the LLM is structurally barred from actuation — guardrails by architecture, not prompt |
| LLMOps | Tracing (LangSmith/Phoenix), prompt versioning, CI-gated eval harness vs simulation baselines |
| Production AI APIs | FastAPI + Docker + SQL-backed scenario registry (AgentSUMO-style `simulations.db` pattern) |
| Classical ML depth | Forecasting benchmark ladder, RL training with statistics, emission-surrogate regression — differentiator vs API-wrapper portfolios |

## 8. Evidence base (anchors)

Verified against primary sources during the Empathize stage — see the personas/evidence artifact for the full 33-row trail. Key anchors: RESCO (arXiv:2108.09694), EMVLight (arXiv:2206.13441), T-REX (arXiv:2506.13836), CoLLMLight (arXiv:2503.11739), LuST DQN case study (arXiv:2402.14886), MOMA-DDPG (arXiv:2306.09662), Finkelberg IEEE T-ITS 2022 (V2I reliability), AgentSUMO (arXiv:2511.06804 — tooling), SURTRAC pilot (self-reported), DfT TAG A1.3 (reliability ratio 0.4), *PLOS One* 2022 (−7%/min ALS survival), Nelson & Bullock TRR 1727 (preemption externality).

**Do-not-claim list (kept from verification):** no "1.5× perceived wait" (measured: 2×); no "engineers distrust AI" statistic; no rider-abandonment percentages; no universal incident-detection-delay benchmark; no lives-saved claims from simulated EV times.
</arg_value></tool_call>Saved — that's the project context file (README-style) for CoFlow-5 × SUMO-Synapse.

One important thing about how I reconciled the SUMO-Synapse proposal with our verified design, so you can defend it in interviews: the proposal you pasted makes **A1 an LLM orchestrator** — that directly contradicts what the evidence says. CoLLMLight needs asynchronous caching just to stay real-time; AgentSUMO (the paper we just analyzed) is exactly this pattern and contains no control loop at all; and production systems (SCATS/Surtrac) keep deterministic override. So the document merges the two directions like this:

- **Control plane (CoFlow-5):** A1 uses cooperative Max-Pressure plus deterministic arbitration and safety. RL is optional research after the core is frozen.
- **Cognitive plane (the "Synapse layer"):** the LLM/LangGraph/RAG ideas from the proposal all live, but as the advisory + explanation layer — RAG grounding over SUMO docs and the persona playbook (pgvector), LangGraph orchestration for the explain/what-if loop only, LangSmith/Phoenix tracing, and the FastAPI/Docker/MLflow eval harness. The LLM is structurally barred from actuation; if it dies, control doesn't notice.
- **HF tasks** required by the design are Time Series Forecasting (A4), Question Answering/feature-extraction (RAG), and Text Generation + Summarization (Synapse layer). Reinforcement Learning (A1) and Tabular Regression (A5) are optional.
- The JD-mapping section keeps the resume language from the proposal but each claim is backed by something actually built in the plan.

Everything else (problem framing, five-agent table, milestones, honesty commitments, evidence anchors) comes straight from the verified design and personas artifacts, so this README is consistent with everything already saved. You can drop it in the repo root as `README.md` or `PROJECT.md` as-is.<artifact identifier="coflow5-project-context" type="markdown" title="CoFlow-5 × SUMO-Synapse — Project Context (README)">
# CoFlow-5 × SUMO-Synapse — Project Context (README)

**One-line pitch:** CoFlow-5 is a five-agent cooperative traffic management system built on Eclipse SUMO, with an LLM "Synapse layer" on top that grounds, explains and audits — never controls. It is an evidence-based answer to *«How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?»*, engineered to production-grade patterns (multi-agent orchestration, RAG, LLM evaluation, LLMOps) rather than an API wrapper.

This file is the project's front door. Companion documents: the **verified design document** (architecture, hypotheses H1–H8, experimental design), **personas, journeys & evidence v2** (Empathize deliverable, 33-row verified evidence trail), and the **design-patterns analysis** (micro/macro trade-offs).

---

## 1. The problem, and what the evidence says

Urban congestion changes continuously with time, place, demand and unexpected events. Signal control optimizes vehicle throughput; emergency vehicles, pedestrians, transit, air quality and incidents are handled by separate, sometimes conflicting mechanisms. Four research findings shaped this project:

- **RESCO** (NeurIPS 2021, arXiv:2108.09694): claimed-SOTA RL signal controllers struggle on realistic networks and are often beaten by a plain decentralized DQN; best-episode reporting overstates performance.
- **T-REX** (2025, arXiv:2506.13836): independent RL controllers degrade sharply under incidents; hierarchical coordination is steadier but ~14× more expensive to train.
- **LuST DQN case study** (arXiv:2402.14886): on full Luxembourg (203 signals), DQN showed no significant difference vs rule-based control — a rare published null result.
- **Communication robustness** has essentially one direct quantification (Finkelberg, IEEE T-ITS 2022) — the strongest surviving methodological gap, and our H6.
- Prior work covers two or three objectives at a time; **no found work co-arbitrates five objectives (EV, pedestrians, transit, emissions, incidents) in one controller.** Our gap claim, stated narrowly and defensibly.

## 2. What we are building

A role-decomposed multi-agent system with **one actuation authority** and **four advisory specialists**, on SUMO (libsumo/TraCI, 1 s steps):

| Agent | Role | Method | Authority |
|---|---|---|---|
| **A1 Flow** | Per-junction signal control; arbiter of all requests | Cooperative Max-Pressure with deterministic masking; optional DQN experiment | **Only A1 writes to signals** |
| **A2 Emergency** | EV routing + corridor preemption with queue pre-clearance | Time-dependent shortest path + priority requests; logged civilian-delay budget | Requests |
| **A3 Multimodal** | Pedestrian guarantees + bus headway regularity | Wait-aware escalation; conditional, lateness-gated TSP bids | Bids |
| **A4 Situation** | Forecasts (30–120 s arrivals; 5–30 min links) + incident detection | LightGBM→LSTM ladder; EWMA/CUSUM residual detection | Alerts with confidence |
| **A5 Sustainability** | Emission hot-spot care without wrecking mobility | λ_eco dual update; proxy rewards; HBEFA KPIs | Weights |

**The three rules:** ① Safety first — never conflicting greens; clearance never truncated. ② The boss is boss — only A1 acts; everyone else asks. ③ Backup plans — messaging or an adviser fails → A1 continues with Max-Pressure; primary control fails → actuated → fixed-time.

**The Synapse layer (LLM cognitive layer — never in the control loop).** Three jobs: (a) **RAG grounding** over SUMO docs, traffic-engineering guidance and the persona playbook (pgvector), so explanations cite real rules; (b) **explanation** — reason-coded decision logs become human-readable accounts for the control-room personas; (c) **orchestration of the advisory loop only** — state queries, AgentSUMO-style what-if scenario analyses, recommendations for human review. It **never** sets a signal. This corrects the naive "LLM orchestrates traffic" framing: CoLLMLight needs async caching merely to stay real-time; AgentSUMO (arXiv:2511.06804) is exactly this pattern and contains no control loop, no seeds, no CIs; production systems (SCATS, Surtrac) ship deterministic override and audit trails. The LLM dying must not be noticeable in the control path — that is the design.

## 3. HuggingFace tasks exercised

| HF task (from the task index) | Where |
|---|---|
| Time Series Forecasting | A4 link-flow forecasting; EWMA/CUSUM incident detection on forecast residuals |
| Reinforcement Learning (optional) | A1 shared DQN experiment after the cooperative core is frozen |
| Graph Machine Learning | Movement-graph encodings; [ADV] CoLight-style graph attention |
| Tabular Regression | A5 emission surrogate on SUMO/HBEFA ground truth |
| Question Answering / Feature Extraction (RAG) | Synapse layer grounded Q&A (all-MiniLM-L6-v2-class embedders, pgvector) |
| Text Generation / Summarization | Decision-log explanations; end-of-shift summaries for Rosa/Omar |

## 4. Tech stack (merged and justified)

| Layer | Choice | Why |
|---|---|---|
| Simulation | SUMO ≥ 1.24 + libsumo/TraCI | Transit, EVs, emissions, SSM safety measures; `agentsumo-mcp` (MIT) gives a reusable scenario pipeline (OSM→net→routes→run→SQLite) usable without any LLM |
| Control | Cooperative Max-Pressure required; optional PyTorch DQN experiment | Cooperation, authority, evaluation and recovery are core; RL cannot block delivery |
| Agent orchestration | LangGraph — advisory/explain loop only, never the control path | Stateful, cyclical reasoning for retrieve→explain→recommend |
| RAG | LlamaIndex connectors + pgvector on PostgreSQL | Production-pattern RAG; enterprise-realistic |
| Core LLM | Open weights via HF (Llama/Mistral-class) | Explainer role only |
| Messaging | In-process asyncio pub/sub; Redis Streams only for a distribution demo | TTL, staleness discounts, heartbeats; Kafka overkill |
| Data | Parquet event logs + DuckDB; `simulations.db` SQL scenario registry | Cross-scenario deltas; chronological splits for A4 |
| Serving | FastAPI (REST + WebSocket) | Control/query endpoints; LLMOps-ready |
| Observability | LangSmith or Arize Phoenix (LLM layer); trackio dashboards (training) | The "Ops" in LLMOps |
| Evaluation | Custom harness: fixed-time/actuated/Max-Pressure baselines, common random numbers, paired stats, rliable-style intervals; MLflow regression gates | Honest comparison against pre-registered hypotheses |
| Deployment | Docker Compose (SUMO, API, agents, DB) | Pinned SUMO + Python; git hash in every log |

## 5. Milestones (tiered, feature-freeze discipline)

- **Tier 0 / MVP (week 6):** SUMO grid; A1 vs fixed-time/actuated/Max-Pressure; KPIs + statistics. Satisfies the brief alone.
- **Tier 1 (week 10):** A2, A3, A5 + message bus + arbitration + ablations. Gate G3 = feature freeze.
- **Tier 2 (week 12):** learned A4, incident detection, communication-failure sweeps, realistic network, scale.
- **Synapse layer (parallel):** RAG + explain panel + eval harness + observability, incrementally from week 6.

If a tier slips, cut features, not rigor. A well-evidenced negative result beats an untested feature list.

## 6. Evaluation & honesty commitments

- Baselines get equal tuning effort; common random numbers; pre-registered H1–H8 with Holm correction; never report best episodes.
- All numeric targets are **proposed acceptance criteria tested against baselines** — not achieved results, not literature-established thresholds.
- Simulation ≠ deployment evidence; HBEFA outputs are proxies, not air-quality measurements; simulated EV time savings are never converted into lives-saved claims.
- Teleports/standstills counted as failures; unfinished trips counted in P95; displacement checks reported, not buried.

## 7. Portfolio / JD mapping

| JD theme (2026 postings) | What this project evidences |
|---|---|
| Agentic AI architecture | Five specialized agents + deterministic safety + advisory LLM layer, role separation justified by ablation — not "agents because agents" |
| Advanced RAG | Grounded retrieval over domain docs; faithfulness-evaluated explanations |
| LLM evaluation & guardrails | LLM-as-judge faithfulness scoring; LLM structurally barred from actuation — guardrails by architecture |
| LLMOps | Tracing (LangSmith/Phoenix), prompt versioning, CI-gated eval harness vs simulation baselines |
| Production AI APIs | FastAPI + Docker + SQL-backed scenario registry |
| Classical ML depth | Forecasting with chronological evaluation; optional RL and emission-surrogate experiments after the core is frozen |

## 8. Evidence base and do-not-claim list

Key verified anchors: RESCO (arXiv:2108.09694), EMVLight (arXiv:2206.13441), T-REX (arXiv:2506.13836), CoLLMLight (arXiv:2503.11739), LuST DQN case study (arXiv:2402.14886), MOMA-DDPG (arXiv:2306.09662), Finkelberg IEEE T-ITS 2022, AgentSUMO (arXiv:2511.06804 — tooling), SURTRAC pilot (self-reported), DfT TAG A1.3 (reliability ratio 0.4), *PLOS One* 2022 (−7%/min ALS survival), Nelson & Bullock TRR 1727.

**Do not claim:** "1.5× perceived wait" (measured: 2×); "engineers distrust AI" statistics; rider-abandonment percentages; a universal incident-detection-delay benchmark; lives-saved figures from simulated EV times.