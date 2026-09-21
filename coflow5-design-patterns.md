# CoFlow-5 — Multi-Agent Design Patterns: Limitations & Trade-offs

Micro (one junction, one decision cycle) and macro (whole network, whole system) points of view, grounded in the verified evidence trail. This folds into the Design Thinking "Ideate → Prototype" stages: the micro table is your fidelity-ladder test checklist, the macro table is your decision-matrix justification.

---

## 1. The pattern inventory — what CoFlow-5 actually uses

| # | Pattern | What it is | Where in CoFlow-5 |
|---|---|---|---|
| P-1 | **Single actuation authority** (centralized executor) | One agent per junction holds the only write-access to the signals | A1 only — Rule 2, "Boss is boss" |
| P-2 | **Deterministic safety layer / action masking** | Hard interlocks (no conflicting greens, min green, clearance) filter every action before execution | Safety layer between A1 and SUMO |
| P-3 | **Blackboard / pub-sub messaging** | Agents post state and alerts to shared topics; consumers read asynchronously | Message bus: `state/`, `forecast/`, `alerts/`, `eco/` |
| P-4 | **Contract-net request/reply** | Request → propose → accept/reject with reason codes, bounded by a decision epoch | A2/A3 priority requests to A1 |
| P-5 | **Bid-based arbitration (auction)** | Requests valued by net benefit = benefit − externality; best feasible bid wins within a priority tier | A1's arbitration layer (§8 of design doc) |
| P-6 | **Shared-policy parameter sharing (MARL)** | One policy network, N per-junction executors; spatially discounted neighbor rewards | A1's per-junction DQN/MAPPO |
| P-7 | **Hierarchical temporal decomposition** | Fast local control (seconds) under slow advisory control (minutes) | A1 vs A2–A5 timescale split |
| P-8 | **Watchdog fallback ladder** | On invalid inputs/timeout, revert deterministically: policy → Max-Pressure → actuated → fixed-time | A1's Layer 4; Rule 3, "Backup plans" |
| P-9 | **Blackboard status + heartbeat (health supervision)** | Liveness TTLs, staleness discounts, degraded-mode flags | Channel emulator + degradation alerts |
| P-10 | **LLM as explainer (not controller)** | LLM reads decision logs and produces natural-language accounts; never acts | Optional explain panel [ADV] |

---

## 2. MICRO point of view — one junction, one 5–10 s decision cycle

### The micro problem
At a single junction in a single epoch, A1 must: observe noisy local state, receive 0–K pending requests, mask unsafe actions, weigh competing bids whose *externalities* it can only estimate, commit to a phase that cannot be revoked mid-clearance, and remain correct even when every advisory message is stale or absent. Micro is where correctness lives; everything above is advice.

### Pattern-by-pattern at micro scale

**P-1 single actuation authority.**
- *Strength:* eliminates contradictory orders by construction — A2 and A3 cannot deadlock each other because neither can act. Makes accountability trivial (one decision log).
- **Limitation:** A1 is a single point of failure *per junction*; a policy bug propagates everywhere at once because all executors share weights.
- **Trade-off:** safety/simplicity vs flexibility — an advisory agent can never fix a junction A1 has decided to serve badly; it can only ask.
- **Mitigation:** watchdog ladder (P-8) plus validation-based checkpoint selection.

**P-2 safety masking.**
- *Strength:* removes the entire unsafe action subspace; masking is the empirically-supported route for constrained control (transit TSP with invalid-action masking beat fixed-time and active TSP).
- **Limitation:** a mask is only as good as its model of the junction. Heterogeneous geometry (RESCO's divergence trigger) means masks must be generated per junction from the conflict matrix, not hand-coded.
- **Trade-off:** restrictiveness vs exploration — over-masking slows learning; under-masking risks the unsafe transitions RL will happily find.
- **Mitigation:** masks derived from SUMO's TLS logic programmatically; mask-on/mask-off ablation to prove the layer matters.

**P-4 contract-net requests.**
- *Strength:* every priority claim becomes auditable (accept/reject + reason code — Rosa's requirement); requests carry expiry, so stale claims self-cancel.
- **Limitation:** request *values* are lies in the general case — A3's "60 passengers" is an estimate, A2's ETA is a forecast. The arbiter optimizes garbage if the garbage isn't flagged.
- **Trade-off:** explicit negotiation vs decision latency — a full negotiation round within a 5–10 s epoch bounds how many requests can be considered; this is why the design caps arbitration at one round (not iterative bargaining).
- **Mitigation:** confidence fields on every request; A1 discounts by confidence and age (staleness discount); tie-break to the older request.

**P-5 bid-based arbitration.**
- *Strength:* the only pattern here that makes cross-objective trade-offs *explicit and loggable* — it is what lets Maria's emission bid compete against Marcus's corridor request on a recorded basis.
- **Limitation:** the externality term is a queueing approximation; it will be wrong at spillback (where MP's own theory already breaks) and for multi-step consequences. Bids can be gamed by a miscalibrated agent (reward hacking shows up as bid inflation).
- **Trade-off:** explainability vs optimality — an auction is almost never the global optimum; it buys auditability and bounded reasoning, and pays in marginal quality.
- **Mitigation:** priority tiers above the auction (EV > incident > pedestrian deadline > transit > flow > eco) so the auction only ever decides *within* a tier; auction-vs-greedy ablation.

**P-6 shared policy at one junction.**
- *Limitation (micro):* heterogeneity. RESCO's central finding — MPLight diverged on irregular realistic junctions (delay >200 s after divergence vs 78 s at its best episode) — is a per-junction pathology of one-size-fits-all policies.
- **Trade-off:** sample efficiency vs per-junction fit.
- **Mitigation:** movement-based state encoding, per-junction-type heads, and the pre-registered H1 test on non-stationary demand.

**P-8 watchdog fallback (micro).**
- *Limitation:* fallback triggers on *symptoms* (invalid input, timeout), not on *bad-but-well-formed decisions* — a policy can degrade gradually and stay inside the watchdog's blind spot. Also: the ladder is static; Max-Pressure itself failed on Ingolstadt-Regional (551 s vs 295 s fixed-time), so the fallback is not universally safe.
- **Trade-off:** responsiveness vs false fallbacks — too eager a watchdog thrashes between modes; too lax one misses degradation.
- **Mitigation:** fallback activations as a reported KPI; degradation alerts to Yuki/Omar.

### Micro failure modes to test explicitly (become scenario checks)
1. Two high-value requests arrive with contradictory windows (EV vs pedestrian deadline) → tier order must decide, and the log must show why.
2. Stale forecast drives a premature green extension → TTL/staleness discount must catch it.
3. Sensor dropout mid-epoch → obs imputation + confidence collapse, not silent zeros.
4. Spillback: receiving-lane full → green is useless; requires the receiving-occupancy feature to exist in the state.
5. Message flood (many simultaneous requests) → per-epoch arbitration budget must be enforced, not best-effort.

---

## 3. MACRO point of view — the network and the five-agent society

### The four macro architecture patterns, and why the middle two won

| Architecture | Optimality ceiling | Scalability | Resilience | Verdict |
|---|---|---|---|---|
| Fully centralized brain | Highest in principle | Worst — joint action space explodes exponentially | Zero (single point of failure) | Rejected; upper-bound comparator only, ≤4 junctions |
| Fully independent (B3) | Low — no network effects, non-stationarity from the neighbours' drift | Best | Best (nothing to lose) | Baseline, RESCO shows it's embarrassingly competitive |
| **Shared-policy CTDE (chosen for A1)** | Moderate | Linear-ish in junctions | Medium — shared-weight failure is correlated | **Core** |
| Hierarchical regional (T-REX's FMA2C) | Moderate-high | Medium | Highest under incidents | [ADV] — T-REX found it steadiest under incident shift but needed ~1,400 episodes vs ~100 |

**The central macro trade-off: coordination benefit vs coordination cost.** Communication is the cheapest thing to add and the hardest thing to trust. CoLight-style communication helped at large scale but was *less stable on small networks*; RESCO showed extended sensing (MPLight*) was *not* beneficial in most cases; Finkelberg (IEEE T-ITS 2022) showed state-of-the-art controllers are highly sensitive to delay and packet loss. So every message your bus carries is a hypothesis that must pay its own way in the ablations (none / neighbor-only / +priority / +forecast).

### Macro pattern-by-pattern

**P-3 blackboard/pub-sub (macro).**
- *Strength:* decouples producers from consumers; A4 can broadcast to everyone; new agents (the LLM explainer) subscribe without touching A1.
- **Limitation:** blackboards hide *feedback loops*. A4's forecast influences A1's actions, which change the traffic A4 observes — a self-referential loop that can entrench its own predictions (the policy makes the forecast come true, then trusts it). Classic forecast-feedback pathology.
- **Trade-off:** loose coupling vs causal accountability — pub-sub makes it hard to answer "who acted on this message?" after the fact.
- **Mitigation:** reason codes record which messages influenced each decision (message IDs in the log); forecast-quality ablation (oracle/learned/noisy/none) is exactly the H4 test of whether the loop helps or harms.

**P-4/P-5 request economy (macro).**
- *Limitation:* network-level priority is a *zero-sum resource* — every green window granted to Marcus is billed to David, Amara or Chidi. Without a per-mission civilian-delay budget, macro-level "success" of A2 is invisible displacement, the same trap as Maria's emission displacement.
- **Trade-off:** local fairness vs network efficiency; per-junction autonomy vs corridor coherence. Preemption is precisely the case where per-junction optimality is wrong: isolated preemption just moves the bottleneck downstream (+20–30 s arterial cost with closely spaced calls — Nelson & Bullock 2000), which is why corridor coordination exists.
- **Mitigation:** per-mission logged budgets (EV benefit per civilian delay KPI); mandatory recovery phase after preemption.

**P-7 hierarchical timescales (macro).**
- *Strength:* it is the only pattern here that reconciles 1-second physics with 5-minute forecasting. It also mirrors the evidence: forecasts matter more for routing and incident response than for second-by-second phase choice.
- **Limitation:** the timescale boundary is where information dies. A 60-second-old incident alert crossing into A1's epoch arrives as a "confidence-tagged opinion" — the layering *creates* the staleness problem the channel emulator then studies (H6).
- **Trade-off:** reactivity (A1 acts on what it sees) vs anticipation (A2–A5 act on what will be). The system is honest only if it can *show* when anticipation was wrong — hence alert confidence, detection delay and false-alarm rate as first-class KPIs, not decoration.

**P-6 shared policy at network scale.**
- *Strength:* the parameter count stays constant as the city grows — this is why MPLight reached 2,510 signals.
- **Limitation:** correlated failure (one bug, city-wide) and the non-stationarity problem — each junction's environment includes other learning executors, so the MDP itself is non-stationary; convergence guarantees from single-agent theory do not transfer.
- **Trade-off:** scale vs specialization. GPLight's clustering and per-type heads buy specialization back at the cost of more parameters per cluster and a harder training problem.
- **Mitigation:** transfer test H7 (4×4 → larger network, zero-shot) makes the scale claim falsifiable instead of asserted.

**P-8/P-9 at macro scale.**
- *Limitation:* the fallback ladder is per-junction, but macro failure is *correlated* (a comms partition fails many junctions at once) — the ladder can fire everywhere simultaneously and produce a synchronized, network-wide mode switch that is itself a disturbance (all junctions re-tuning at once). 
- **Trade-off:** graceful degradation vs graceful *coordination* of degradation.
- **Mitigation:** staggered/jittered fallback transitions; degradation alerting (Omar's requirement) treats mode switches as events on the dashboard.

**P-10 LLM explainer (macro).**
- *Strength:* the only component that speaks human — Rosa/Omar/Yuki need accounts, not tensors.
- **Limitation:** an LLM can hallucinate reasons that weren't the decision's reasons. Its output must be grounded strictly in the decision log (reason codes + features), and evaluated for faithfulness (does the explanation cite the actual accept/reject cause?), not fluency.
- **Trade-off:** interpretability vs trustworthiness — a fluent wrong explanation is worse than a terse correct one.

---

## 4. The trade-off map (one page for the report)

| Trade-off axis | Chosen point | What we gave up | Evidence anchor |
|---|---|---|---|
| Centralized vs decentralized | Decentralized execution, centralized training | Global optimality | RESCO: IDQN (decentralized) beat claimed-SOTA on realistic tasks |
| Learned vs rule-based | Rules own safety; learning owns efficiency | A fully-learned controller's theoretical ceiling | Masked-action TSP results; MP's provability |
| Explicit arbitration vs learned arbitration | Explicit auction with tiers | Optimality, adaptivity of the bidding itself | Explainability is a stakeholder requirement (Rosa, Yuki) |
| Rich messaging vs minimal messaging | Pub-sub + request/reply, TTL'd | Bandwidth, simplicity; more surface for H6 failure | Finkelberg 2022; RESCO sensing fragility |
| Hierarchical vs flat | Flat with timescale separation (hierarchy is [ADV]) | Incident-steadiness of full hierarchy | T-REX: FMA2C steadier but ~14× more episodes |
| Forecast-in-the-loop vs reactive | Advisory, confidence-gated | Nothing structural — forecasts can be switched off | PBOT field evidence supports in-loop prediction; timescale mismatch argues advisory-only |
| Single policy vs per-junction policies | Shared with type heads | Per-junction specialization | MPLight divergence on irregular junctions |
| Deterministic fallback vs always-learned | Watchdog ladder | Max adaptive performance under degradation | Surtrac's own executor falls back on failure |

**The system-level statement this table supports:** CoFlow-5 trades *optimality* for *auditability, safety and graceful degradation* at every layer — deliberately, because the evidence (RESCO, T-REX, Finkelberg, the SCATS/Surtrac operating practice) says unverifiable optimality loses to auditable competence in systems people must run.

---

## 5. Tech stack for the agent society (where each pattern lives)

| Pattern | Implementation | Stack note |
|---|---|---|
| P-1/P-2/P-8 | A1 executors + safety layer + watchdog | Python, PyTorch; deterministic layer is plain code — no framework |
| P-3 | Message bus | In-process asyncio pub/sub; Redis Streams only if a distribution demo is required; Kafka explicitly overkill |
| P-4/P-5 | Request/reply + auction | Plain dataclasses with reason-code enums; JSON envelopes as specced in §8 |
| P-6 | Shared-policy training | Parameter-shared Double/Dueling DQN with masking (RESCO-informed default); MAPPO as declared comparator |
| P-9 | Health/degradation | Heartbeat TTLs + channel emulator (latency 0–1,000 ms, loss 0–30%) |
| P-10 | Explainer | Optional LangGraph-style orchestration *outside* the control loop; grounded strictly on the decision log; pgvector/RAG over the ops playbook if the portfolio angle is wanted |
| Tooling | Scenario & analysis pipeline | `agentsumo-mcp` (MIT, SUMO ≥ 1.24) usable LLM-free for OSM→net→routes→run→SQLite; emission KPIs via `attributeStats.py` |

**LLM-layer caution (consistent with the design):** the LLM never touches the bus's control topics. It subscribes to the audit log and publishes only to `explain/*` topics. If it dies, nothing in the control path notices — which is the point.

---

## 6. What this analysis changes in the plan (concrete deltas)

1. **Add auction-vs-greedy and mask-on/mask-off to the ablation list** (§11) — the micro analysis shows these two patterns are load-bearing claims, so they need their own ablations, not just leave-one-agent-out.
2. **Add "synchronized fallback" to the S7 robustness scenario** — staggered transition timing as a treatment variable.
3. **Add forecast-feedback loop check to A4's edge cases** — log whether policies trained with forecast input make forecasts self-fulfilling (H4's noisy-forecast arm partially covers this; make it explicit).
4. **Justify the arbitration budget** — per-epoch arbitration cost is bounded; document the cap and its effect on request starvation (ties to the anti-thrash cooldowns).
5. **Cite the macro table in the report's architecture-justification section** — it is the decision matrix the Design Thinking "Ideate" stage asks for, with evidence attached to every row.
</arg_value></tool_call>Everything is done and saved. Here's where things stand:

**Design document updated (3 AgentSUMO edits applied to the saved artifact):**
- Tech-stack table: Simulation row now lists `agentsumo-mcp` (MIT) as scenario/analysis tooling with the SUMO ≥ 1.24 pin.
- Related work: the LLM-agents bullet now cites AgentSUMO as *tooling, not a controller* — no RL inside, no seeds/CIs in its case studies — reinforcing the "LLM never in the control loop" decision.
- References: full entry added (arXiv:2511.06804, ACM DOI 10.1145/3764921.3770151, repo link) with the citation-context warning.

**New saved artifact: "CoFlow-5: Multi-Agent Design Patterns — Limitations & Trade-offs"** — the analysis you asked for, structured as:

- **Pattern inventory** — the nine patterns the system actually uses (single actuation authority, safety masking, blackboard/pub-sub, contract-net requests, bid arbitration, shared-policy CTDE, hierarchical timescales, watchdog ladder, LLM explainer), each mapped to your A1–A5 and the "three big rules."
- **Micro POV** (one junction, one 5–10 s cycle) — pattern-by-pattern strengths, limitations and trade-offs, plus five concrete micro failure modes that become scenario checks (contradictory request windows, stale forecasts, sensor dropout, spillback, message flood).
- **Macro POV** (network + agent society) — the four architecture options compared, and the system-level trade-offs: coordination benefit vs coordination cost, forecast-feedback loops, correlated failure of shared policies, synchronized fallback as its own disturbance.
- **A one-page trade-off map** — nine axes, what CoFlow-5 chose, what it gave up, and the evidence anchor for each (RESCO, T-REX, Finkelberg, SCATS/Surtrac practice). The report-ready thesis it supports: *CoFlow-5 deliberately trades optimality for auditability, safety and graceful degradation.*
- **Tech-stack table** — which stack component implements which pattern, including the optional LangGraph/RAG explainer layer that never touches control topics.
- **Five concrete plan deltas** — new ablations (auction-vs-greedy, mask-on/off), the synchronized-fallback test in S7, the A4 forecast-feedback check, the arbitration budget cap, and using the macro table as the Ideate-stage decision matrix.

All three Empathize/design artifacts now form a complete, citation-defensible set. The next step on the roadmap is still week 1's build — pin SUMO, get Max-Pressure and fixed-time on a 4×4 grid, measure simulation speed — which needs a compute budget before anything can run.