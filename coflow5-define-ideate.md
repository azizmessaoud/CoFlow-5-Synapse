# CoFlow-5 — Design Thinking Stage 2: Define & Stage 3: Ideate

Framework: Interaction Design Foundation (Empathize → Define → Ideate). Stage 1 (Empathize) is complete — see *CoFlow-5: User Personas, User Journeys & Possible Solutions (v2)* with its 33-row verified evidence trail. This document synthesizes those findings into a human-centered problem definition, then runs the ideation techniques the framework names (Brainstorm/Brainwrite, Worst Possible Idea, SCAMPER, morphological chart, weighted decision matrix) and converges on the chosen architecture.

> [!IMPORTANT]
> **Historical/superseded architecture note (ADR-0001):** This document preserves the Stage 2–3 evidence of ideas considered; it is not the current implementation boundary. References below to “F1→A1 core,” “Rules own safety; RL owns efficiency,” shared-policy MARL, or a generic `policy → Max-Pressure → actuated → fixed-time` ladder are historical Ideate candidates superseded by [`docs/adr/0001-reliable-ai-platform-boundary.md`](docs/adr/0001-reliable-ai-platform-boundary.md). The required A1 controller is cooperative Max-Pressure, with recovery `Max-Pressure → actuated → fixed-time`. DQN is optional row 15 work after the cooperative core freezes. LLM-controller alternatives remain rejected; Synapse is non-actuating and cannot reach TraCI. Personas remain research-informed, not interview-validated; the planned expert interviews were not completed.

---

# STAGE 2 — DEFINE

## 2.1 What the Empathize stage gathered

- **8 evidence-based personas:** Amara (74, pedestrian with cane), David (41, delivery driver), Chidi (27, bus commuter), Rosa (52, depot controller), Marcus (34, paramedic), Yuki (47, traffic engineer), Maria (38, parent near an arterial), Omar (55, duty officer).
- **Verified evidence trail (33 rows):** 2× perceived pedestrian wait (Vallyon 2009); 30 s compliance cliff (TfL/NZTA); assistive walking speeds 0.6–0.8 m/s; wait valued ≈2× in-vehicle (DfT TAG); −7%/min ALS survival (*PLOS One* 2022); +20–30 s arterial cost of closely spaced preemption (Nelson & Bullock 2000); reliability ratio 0.4 (DfT TAG A1.3); SCATS ships override + audit trails as product features; SCOOT degrades under congestion; 6.4M US children ≤250 m of major roads (Kingsley 2014); incidents = 25–30% of congestion (FHWA).
- **Method note carried forward:** personas are research-informed artifacts, not interview-validated profiles; five expert interviews were planned as future validation but were not completed, and no interview quotes are claimed as Evidence.

## 2.2 POV statements (User + Need + Insight)

Following the POV format — *[User] needs [need] because [insight]*:

1. **Amara** needs *a crossing that both arrives quickly and gives her enough time to finish* because **perceived waits double actual waits, compliance collapses after 30 s, and clearance standards assume 1.07–1.2 m/s walkers, not her 0.8 m/s.**
2. **David** needs *predictable journeys, not just shorter ones* because **variability costs ~half the mean trip** (reliability ratio 0.4) and a late van misses delivery windows all day.
3. **Chidi** needs *buses to arrive at regular headways* because **waiting is valued at twice in-vehicle time and bunching is self-reinforcing** — three buses at once after a 20-minute gap.
4. **Rosa** needs *to see why priority was granted or denied and to intervene safely* because **unexplained rejections erode trust** and production systems treat override + audit trails as core features (SCATS 2022).
5. **Marcus** needs *signals ahead to clear the way and recover afterwards* because **every minute of ALS delay cuts cardiac-arrest survival ~7%**, while poorly spaced preemption bills +20–30 s to everyone else.
6. **Yuki** needs *automation she can diagnose, override and disable* because **adaptive control degrades silently under congestion** (SCOOT 1986) and she is accountable for whatever it does.
7. **Maria** needs *pollution near the school gate to fall without being displaced onto her street* because **6.4M US children attend school within 250 m of major roads** and a city-wide average hides exactly the harm she fears.
8. **Omar** needs *alerts that say what is wrong, why, and how much to trust them* because **incidents drive 25–30% of congestion, false alarms destroy trust, and a frozen dashboard can look normal while the system is degraded.**

## 2.3 Human-centered problem statement

> **Street users — pedestrians, drivers, bus riders, emergency crews and the people who run the network — need signal control that treats their distinct needs (time to cross, predictable trips, regular buses, fast emergency passage, clean air near homes) as first-class objectives with visible trade-offs, because today each need is handled by a separate mechanism that optimizes vehicle throughput, hides who pays for whom, and degrades silently when conditions or communications fail.**

Framing check (per the framework): this is pitched from the *users'* needs, not the system-builder's wish. Contrast the rejected non-human-centered version: "We need to demonstrate a five-agent MARL system with ≥5% delay improvement." That is an objective, not a problem statement — it now lives where it belongs, in the hypothesis list (H1–H8).

## 2.3 How-might-we questions

Per persona:
- **HMW-P1:** How might we give pedestrians a walk phase that comes before frustration turns into red-running, while never shortening the time they need to finish?
- **HMW-P2:** How might we make journeys predictable — reliably under 20 minutes, not 20 minutes on average?
- **HMW-P3:** How might we make buses arrive evenly rather than in packs, using only levers a traffic light controls?
- **HMW-P4:** How might we make every automated priority decision explainable and reversible by the controller?
- **HMW-P5:** How might we get an ambulance through a congested corridor *and* restore normal traffic afterwards, with the cost to others on the record?
- **HMW-P6:** How might we let an engineer diagnose a degraded controller and regain command in one bounded action?
- **HMW-P7:** How might we prove that cleaner arterials did not simply export pollution to residential streets?
- **HMW-P8:** How might we distinguish "nothing wrong", "suspected incident" and "we can't see" — and say which, every time?

**Integrated HMW (the project's spine):**
> **How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable — while making the trade-offs between road users explicit, auditable, and safe when things fail?**

## 2.4 Constraints and success criteria

| Constraint | Statement |
|---|---|
| Safety | No conflicting greens, ever; pedestrian clearance never truncated; preemption uses a defined transition sequence |
| Authority | One actuation authority (A1); all other agents advise |
| Evidence | Every feature survives an ablation or is cut; baselines get equal tuning effort; common random numbers; pre-registered hypotheses (H1–H8) |
| Honesty | Simulation ≠ deployment evidence; emissions are proxies; no lives-saved claims from simulated EV times; best-episode reporting forbidden |
| Feasibility | Tiered build (MVP by week 6); cut features, not rigor; solo/student compute budget |
| Ethics | Equity KPIs reported; override + fallback always available; reason codes on every decision |

**Success criteria:** the prototype answers the eight research questions with paired, pre-registered statistics; every persona's KPI dictionary entry is measured; strengths *and* limitations are evidenced; negative results are reported as findings.

## 2.5 Prioritized core problems (Define output → Ideate input)

1. **P-Core-1 (efficiency):** Signal control optimized for vehicle throughput leaves network-level efficiency gains unrealized *and unverifiable* — RL claims fail on realistic networks (RESCO), so any claim must be earned against Max-Pressure, not asserted.
2. **P-Core-2 (beyond flow):** Five objectives (EV, pedestrian, transit, emissions, incidents) are managed by conflicting mechanisms; nothing found arbitrates them together.
3. **P-Core-3 (trust & control):** The people accountable (Yuki, Omar, Rosa) cannot diagnose, override or audit what "intelligent" control decides; silent degradation is the documented norm.
4. **P-Core-4 (fairness & equity):** Mean-delay optimization hides starvation and displacement — on streets (Maria) and across user classes (Amara vs David).
5. **P-Core-5 (fragility):** Communication, sensors and agents fail; controllers evaluated under perfect V2X are untested where it matters (Finkelberg 2022; H6).

---

# STAGE 3 — IDEATE

Per the framework: divergence first (Brainstorm/Brainwrite, Worst Possible Idea), then convergence (SCAMPER-informed feature generation, morphological chart, weighted decision matrix).

## 3.1 Divergence — Brainstorm/Brainwrite (raw ideas, unjudged)

Grouped by theme; IDs reused in the convergence step.

*Flow (F):*
- F1 RL per junction, shared weights · F2 Graph attention between neighbours (CoLight-style) · F3 Regional hierarchical managers (T-REX FMA2C-style) · F4 Auction/bidding between junctions for green time · F5 LLM decides phases · F6 MPC by forked simulation · F7 Gate-based phases from pressure only (Max-Pressure as-is) · F8 GNN that predicts arrivals to drive phases directly

*Emergency (E):*
- E1 Corridor-wide green wave with queue pre-clearance · E2 Learned preemption (EMVLight-style) · E3 Blue-light red-running (SUMO device) · E4 Drone/scout vehicle ahead of EV · E5 Always-priority for EVs regardless of load

*Multimodal (M):*
- M1 Unconditional bus TSP · M2 Conditional lateness-gated TSP with occupancy-valued bids · M3 Leading pedestrian intervals everywhere · M4 Bus holding at stops for headway regularity · M5 GLOSA for pedestrians (walk-speed advisories)

*Sustainability (S):*
- S1 Direct CO2 reward in RL · S2 λ_eco dual update with delay budget · S3 GLOSA speed advice to connected vehicles · S4 Eco-routes for a CV fraction · S5 Hard emission caps per junction

*Situation/prediction (P):*
- P1 Historical-average forecasts only · P2 LightGBM → LSTM → GNN ladder · P3 Oracle forecasts (upper bound) · P4 Incident detection by EWMA/CUSUM residuals · P5 Deep detector (CV/detection models on synthetic imagery)

*Communication/coordination (C):*
- C1 Perfect comms assumption · C2 Channel emulator with latency/loss sweeps · C3 All-to-all message flooding · C4 Region-sharded message brokers · C5 LLM in the control loop as orchestrator

## 3.2 Worst Possible Idea (divergent technique, inverted for insight)

| Deliberately bad idea | Why it's bad (evidence) | Insight it yields |
|---|---|---|
| Let the LLM set the lights directly | Latency/reliability wrong for second-scale control (CoLLMLight needs async caching); AgentSUMO has no control loop; no seeds/CIs | LLM earns the **explainer/advisor** seat; actuation stays deterministic + RL (becomes the Synapse-layer design) |
| Give every agent equal right to change signals | Contradictory orders, unrecoverable deadlocks | **Single actuation authority** (Rule 2) with request/bid patterns |
| Prioritize every EV request instantly, always | Closely spaced preemption costs +20–30 s arterial, +7.6% side-street (Nelson & Bullock) | **Corridor coordination + logged civilian-delay budget** (A2 design) |
| Give the bus a green every cycle | Unconditional TSP wastes recovery minutes; SCOOT's −39% came from *conditional* priority | **Lateness-gated, occupancy-valued bids** (A3 design) |
| Optimize CO2 directly as the RL reward | Direct CO2 reward proved inefficient and parameter-sensitive; emissions track delay at junctions | **Proxy rewards (stops/idle) + emissions as KPI + λ_eco weight** (A5 design) |
| Trust sensors fully, assume perfect comms | Controllers are highly sensitive to delay/packet loss (Finkelberg 2022); RESCO showed sensing fragility | **Three sensing regimes + channel emulator + heartbeat/TTL** (H6 core) |
| Report the best episode of each method | RESCO's results table does this and it flatters RL | **Pre-registered hypotheses, paired stats, rliable-style intervals** |

## 3.3 SCAMPER on the existing signal controller

| Letter | Prompt applied to "a fixed-time signal controller" | CoFlow-5 feature it generates |
|---|---|---|
| **S**ubstitute | Substitute measured queues for assumed demand | Max-Pressure as baseline/fallback (B2) |
| **C**ombine | Combine local control with neighbour outflow messages | A1 neighbour messaging (Surtrac template) |
| **A**dapt | Adapt rolling-horizon re-planning from adaptive systems | A1's 5–10 s decision epochs with staged transitions |
| **M**odify/Magnify | Magnify "who matters": count *people*, not vehicles | Person-weighted delay; occupancy-valued bids (A3) |
| **P**ut to other use | Use the same detector data for prediction | A4's forecast + incident-detection dual output |
| **E**liminate | Eliminate the assumption that communication works | Channel emulator; local-rule degradation (H6) |
| **R**everse/Re-arrange | Reverse who acts: specialists advise, one authority acts | Role-decomposed hierarchy (the A1–A5 design) |

## 3.4 Morphological chart (convergence instrument 1)

| Dimension | Option A | Option B | Option C | **Chosen** |
|---|---|---|---|---|
| Information scope | Local only | +Neighbour exchange | +Network forecasts | **B at micro, C at macro (layered)** |
| Decision authority | One central brain | Independent junctions | Single actuator + advisors | **C** |
| Cooperation pattern | None | Blackboard pub-sub | Contract-net requests + bids | **B + C (pub-sub for state, requests for priority)** |
| Learning method | Fixed-time/actuated rules | Rules + RL policy | Pure RL | **Rules own safety; RL owns efficiency** |
| Arbitration | First-come | Fixed priority tiers | Tiers + net-benefit auction within tier | **C** |
| Failure behaviour | Fail loud, halt | Silent degradation | Watchdog ladder + local rules | **C** |
| LLM role | Controller | Advisor with veto | Explainer/analyst, no actuation | **C** |

## 3.5 Weighted decision matrix (convergence instrument 2)

Criteria weights chosen from stakeholder needs: Safety 0.25, Scalability 0.15, Evidence-risk 0.20 (RESCO fragility), Auditability 0.20, Compute 0.10, Innovation 0.10. Scores 1–5.

| Architecture | Safety | Scalability | Evidence-risk | Auditability | Compute | Innovation | **Weighted** |
|---|---|---|---|---|---|---|---|
| One central RL brain | 2 | 1 | 3 | 2 | 1 | 3 | **1.95** |
| Independent junctions (B3) | 3 | 5 | 2 | 3 | 5 | 1 | **3.15** |
| **Single actuator + advisors + tiers/bids (CoFlow-5)** | 5 | 4 | 4 | 5 | 3 | 4 | **4.30** |
| Fully hierarchical regional MARL | 4 | 3 | 3 | 4 | 2 | 4 | **3.45** |

The chosen architecture also wins qualitatively: it is the only option in which safety is structural (masking + one writer), every objective is logged with a reason code, and each agent can be *proved useless* by ablation (H8) rather than assumed useful.

## 3.6 Idea disposition (divergent ideas → final design)

| Kept → where | Parked → why | Rejected → why |
|---|---|---|
| F1→A1 core · F2→[ADV] · F3→[ADV] · F7→B2/fallback | F4 auction *between junctions* (complexity vs benefit unproven) | F5 LLM-phases, F6 MPC-forked-sim (compute) |
| E1→A2 · E2→[ADV] learned preemption | — | E3 unsafe upper bound (baseline only) · E5 contradicts civilian budget |
| M2→A3 core · M4→[ADV] bus holding | M3 LPI (real-world proven but SUMO support limited) | M1 unconditional TSP (evidence contradicts) |
| S2→A5 core · S3/S4→[ADV] | — | S1 direct CO2 reward (evidence: inefficient) · S5 hard caps (brittle) |
| P2→A4 ladder · P3→oracle ablation · P4→A4 detection | P5 deep CV detector (out of scope) | P1 historical-average only (too weak for 30–120 s arrivals) |
| C2→channel emulator core · C4→[ADV] sharding | — | C1 perfect comms (the gap we're attacking) · C5 LLM-in-loop (latency/reliability) |

## 3.7 What Ideate hands to Prototype & Test

1. The **chosen architecture** (single actuator + advisors, pub-sub + contract-net, watchdog ladder) becomes the §6 design and the P-1..P-9 pattern set in the design-patterns analysis.
2. The **decision matrix and idea disposition** become the report's "justified choices" evidence — the Ideate stage's deliverable per the brief.
3. Unproven ideas carry **test obligations**: every parked/rejected idea that reappears in [ADV] must be reached by ablation or explicitly marked untested.
4. The **integrated HMW** is the assignment's own challenge question, now grounded in persona evidence — the "How might we" slide in the presentation comes straight from §2.3.
5. Fidelity ladder (Prototype stage): paper/UML → one junction → corridor → 4×4 grid → integrated five-agent system → realistic network + dashboard, each rung with a stated learning goal — then Test via the pre-registered H1–H8 matrix.
</arg_value></tool_call>Both stage deliverables are saved as one document: **"CoFlow-5 — Design Thinking: Define & Ideate Stages"**. Quick map of what's inside, so you can lift sections straight into the report:

**Stage 2 — Define** (everything human-centered, per the IxDF framing):
- **Synthesis** of the Empathize inputs — the 8 personas and the key verified evidence they contribute.
- **8 POV statements** in the User–Need–Because form, each anchored to its evidence (e.g., Amara's because *perceived waits are 2× actual and clearance assumes 1.07–1.2 m/s walkers*).
- **Human-centered problem statement** — pitched from the users' needs, with the rejected "company-wish" version shown for contrast and relocated to the hypothesis list where it belongs.
- **Eight per-persona "How might we" questions** plus the integrated HMW, which lands exactly on the assignment's challenge wording ("efficient, adaptive, sustainable") while adding the auditability angle.
- **Constraints and success criteria**, and **five prioritized core problems** that become the ideation prompts.

**Stage 3 — Ideate** (diverge then converge, using the techniques the framework names):
- **Brainstorm/Brainwrite:** ~25 raw ideas across six themes (F/E/M/S/P/C), each with an ID.
- **Worst Possible Idea:** seven deliberately terrible ideas (LLM sets the lights, always-preempt EVs, direct-CO2 reward, perfect-comms assumption…) each inverted into the insight that actually shaped the design.
- **SCAMPER** applied to a conventional fixed-time controller — each letter generates a real CoFlow-5 feature (person-weighted delay, neighbour outflow messages, the watchdog ladder).
- **Morphological chart:** six design dimensions × options, with the chosen column marked.
- **Weighted decision matrix:** the role-decomposed architecture scores 4.30 vs 3.15 (independent agents) and 1.95 (central brain), with stakeholder-derived criterion weights.
- **Idea disposition table:** every divergent idea traced to kept / parked / rejected with reasons — this is what proves to your marker that ideation was real and not reverse-rationalized.
- **Hand-off to Prototype & Test:** the matrix and disposition feed the report's justification section; the HMW becomes the presentation slide.

That completes all three pasted stages: Empathize (saved earlier as personas & journeys v2), Define, and Ideate. Next in the Design Thinking sequence is Prototype — which is the week-1 build: pin SUMO, run Max-Pressure and fixed-time on a 4×4 grid, and measure simulation speed. That step needs a compute budget before anything runs, so it starts whenever you grant one.The framework you've pasted (Interaction Design Foundation's Design Thinking stages) maps directly onto the work already done for CoFlow-5: the **Empathize** stage deliverables exist (the eight personas, journey maps and the verified evidence trail), and what's missing is the **Define** and **Ideate** stage outputs in exactly the form IxDF prescribes — POV statements, a human-centered problem statement, "How might we" questions, then divergent ideation (Brainstorm / Brainwrite / Worst Possible Idea / SCAMPER) converging into the chosen architecture. Here it is:

<artifact identifier="coflow5-define-ideate" type="markdown" title="CoFlow-5 — Design Thinking: Define & Ideate Stages">
# CoFlow-5 — Design Thinking: Define & Ideate

**Stages 2 and 3 of the design thinking process** (Interaction Design Foundation framework), applied to the five-agent traffic management project. The Empathize stage is already delivered — see the *CoFlow-5: User Personas, User Journeys & Evidence* document, whose verified evidence trail (Vallyon 2009, NZTA RR440, DfT TAG A1.3, Nelson & Bullock 2000, Kingsley 2014, FHWA, SCATS/Surtrac product evidence, RESCO/T-REX/Finkelberg) is the raw material for everything below.

---

## Stage 2 — DEFINE

### 2.1 Organizing the Empathize findings

The empathy research produced eight stakeholder groups whose needs frequently *conflict* rather than merely coexist: pedestrians need long clearance and short waits; drivers need predictable trips; bus riders need regular headways; paramedics need passage and recovery; engineers need override and explanations; residents need emissions cut without displacement; operators need trustworthy alerts. The literature adds the system-level insight that adaptive control degrades silently and RL results are fragile outside synthetic grids (RESCO).

Synthesized into two structures: **person-value statements** (what each user needs, and the evidence for it) and a **human-centered problem statement** pitched from the users' needs — not from the team's wish to build a five-agent system.

### 2.2 Person–Need–Insight (POV) statements

1. **Amara — pedestrian with a cane (74):** needs *crossing time that both arrives quickly and lets her finish at 0.8 m/s* because **perceived wait doubles actual wait and compliance collapses after ~30 s**, while clearance standards assume 1.07–1.2 m/s.
2. **David — delivery driver:** needs *predictable trips, not just faster ones* because **variability is priced at ~half the mean trip cost** (reliability ratio 0.4) and one unknown 20-minute jam breaks his whole delivery schedule.
3. **Chidi — bus commuter:** needs *buses that come at regular intervals* because **his waiting time is valued twice as highly as riding time and bunching is self-reinforcing** — the longest gap is followed by three buses at once.
4. **Marcus — paramedic:** needs *corridors that clear the way AND recover afterwards* because **each minute of ALS delay cuts survival ~7%**, yet isolated preemption just moves the bottleneck downstream and bills strangers for his gain.
5. **Rosa — depot controller:** needs *to see why priority was granted or denied and intervene safely* because **unexplained rejections erode trust** and override-with-audit-trail is what production systems (SCATS) already ship.
6. **Yuki — traffic engineer:** needs *automation she can diagnose, override and disable* because **adaptive control degrades silently under congestion** (SCOOT) and she is accountable for everything it does.
7. **Maria — parent on an arterial:** needs *emissions to fall near the school without being displaced onto her street* because **network means hide exactly the local deterioration she lives with**, and her children are among the 6.4M US children within 250 m of a major road.
8. **Omar — duty officer:** needs *alerts that say what's wrong, why, and whether the data is trustworthy* because **incidents cause 25–30% of congestion and a frozen dashboard can look normal while the system is degraded**.

### 2.3 The human-centered problem statement

> **How might we make urban traffic signals serve *people* — pedestrians, riders, responders, residents and the operators accountable for them — rather than only vehicle throughput; so that every objective is explicitly represented, every trade-off between users is visible and auditable, and the system degrades safely and honestly when sensors, communications or its own learning fail?**

(The rejected, non-human-centered version — "we need to demonstrate a five-agent MARL system" — is exactly the framing IxDF warns against: a company-wish, not a user need.)

### 2.4 "How might we" questions (bridge into Ideate)

- **HMW-1 (flow):** How might we manage signals so that *predictability and fairness* — not just average delay — improve, on networks where published RL methods have failed to beat Max-Pressure?
- **HMW-2 (emergency):** How might we get an ambulance through a corridor *and* return the network to normal, with the civilian cost logged per mission?
- **HMW-3 (multimodal):** How might we give buses and pedestrians *conditional* priority that wins exactly when they need it, without starving cars?
- **HMW-4 (prediction):** How might we make forecasts *earn their place* in the loop, with the system showing when prediction helps, when it is stale, and when it hurts?
- **HMW-5 (sustainability):** How might we cut stop-and-go emissions *where people breathe* and prove the gains were not displaced?
- **HMW-6 (trust):** How might we give the engineer and duty officer *explainable, overridable, fail-safe* control that stays safe when communication degrades?
- **HMW-7 (integration):** How might we arbitrate five competing objectives under one actuation authority so every decision carries a reason code?

### 2.5 Constraints and success criteria (Define output)

| Constraint | Success criterion |
|---|---|
| Safety is non-negotiable | Zero conflicting greens; clearance never truncated; violations = system failure, not a KPI trade-off |
| Evidence over claims | Every hypothesis (H1–H8) falsifiable with pre-registered metrics; baselines tuned with equal effort |
| Human oversight | Reason codes on 100% of decisions; override subject to safety interlocks; watchdog fallback ladder |
| Simulation ≠ deployment | All targets are proposed acceptance criteria; emission outputs labelled proxies; no lives-saved claims |
| Feasibility for a solo/team project | Tiered build (Tier 0 by week 6 satisfies the brief); cut features, not rigor |

---

## Stage 3 — IDEATE

### 3.1 Divergent techniques (Brainstorm / Brainwrite)

Raw ideas generated without filtering, grouped by HMW (brainwrite-style: each idea attributed to the evidence it came from, so the report can trace idea → evidence):

**From HMW-1:** (a) shared-policy MARL per junction; (b) Max-Pressure as fallback; (c) graph attention between neighbours; (d) corridor progression offsets; (e) P95-travel-time-aware phase choice; (f) queue-spillback detection via receiving-lane occupancy.
**From HMW-2:** (a) corridor preemption with queue pre-clearance; (b) time-dependent EV routing on predicted times; (c) severity-ranked multi-EV sequencing; (d) post-passage recovery mode; (e) detector-triggered fallback preemption.
**From HMW-3:** (a) lateness-gated TSP; (b) occupancy-valued priority bids; (c) leading pedestrian intervals; (d) slow-walker clearance extension; (e) bus-holding for headway regularity.
**From HMW-4:** (a) 30–120 s arrival prediction per approach; (b) 5–30 min link forecasts; (c) incident detection via EWMA/CUSUM on forecast residuals; (d) oracle-forecast ablation; (e) confidence-gated forecast consumption.
**From HMW-5:** (a) λ_eco dual-update weight; (b) stop/idle proxy rewards; (c) emission surrogate on HBEFA ground truth; (d) link-level displacement maps; (e) GLOSA speed advice to connected vehicles.
**From HMW-6:** (a) pub-sub message bus with TTL/staleness discounting; (b) channel emulator (latency/loss sweeps); (c) watchdog ladder (policy → Max-Pressure → actuated → fixed-time); (d) reason-coded decision log; (e) one-click override under interlocks.
**From HMW-7:** (a) priority tiers (EV → incident → pedestrian deadline → transit → flow → eco); (b) net-benefit auction within tiers; (c) anti-thrash cooldowns; (d) message-flood budget; (e) LLM explainer over the audit log.

### 3.2 Worst Possible Idea (deliberately inverted, then mined)

| Worst idea | Why it's terrible | The insight it yields |
|---|---|---|
| Give the LLM direct control of the lights | Latency/reliability unfit for second-scale control; no deployable evidence | The LLM must sit **outside** the control loop — explainer and analyst only |
| Let all five agents write to signals directly | Conflicting orders guarantee unsafe transitions | **One actuation authority**; specialists advise |
| Always preempt for EVs, no logging | Closely spaced preemption costs others +20–30 s; cost hidden | Corridor coordination **with a per-mission civilian-delay budget** |
| Give the bus a green every cycle | Wastes recovery minutes when the bus is early; hurts everyone else | Priority must be **conditional on lateness/occupancy** |
| Optimize raw CO2 as the RL reward | Direct CO2 rewards proved inefficient and parameter-sensitive | Eco acts through **proxy rewards + a weight**, emissions stay a KPI |
| Trust all sensors and comms | Controllers are highly sensitive to delay/packet loss; sensing assumptions break algorithms | Robustness is a **first-class hypothesis (H6)**, tested with a channel emulator |
| Report only the best episode | RESCO's results tables flatter methods this way | **Pre-registered hypotheses, paired statistics, never best-episode reporting** |

### 3.3 SCAMPER applied to the existing traffic light

- **Substitute:** replace average-delay objective with person-weighted delay (people, not vehicles).
- **Combine:** combine per-junction control with neighbour projected-outflow messages (the Surtrac template).
- **Adapt:** adapt preemption practice to corridor-level coordination with queue pre-clearance.
- **Modify/Magnify:** magnify observability — reason codes, confidence, staleness, fallback activations as first-class outputs.
- **Put to other use:** use the same detector stream for both forecasting and incident detection (A4).
- **Eliminate:** eliminate the assumption that communication is free — build the channel emulator and test degradation.
- **Reverse:** reverse the control direction — instead of one brain controlling everything, specialists advise and one authority acts; slow advisory agents, fast local control.

### 3.4 Convergent techniques — morphological chart and decision matrix

**Morphological chart (design dimensions × options):**

| Dimension | Option 1 | Option 2 | Option 3 | Chosen |
|---|---|---|---|---|
| Who acts on signals | Central brain | Independent junctions | One authority + advisors | **Option 3** |
| Cooperation | None (independent) | Message board (blackboard) | Bidding/auction | **Blackboard + requests/bids** |
| Learning | All rule-based | All learned | Rules for safety, learned for efficiency | **Hybrid** |
| Timescales | Single | Two-tier (seconds/minutes) | Three-tier | **Two-tier** (control 5–10 s; advisory seconds–minutes) |
| LLM role | In the loop | Explainer/what-if only | None | **Option 2** |
| Communication | Perfect | Emulated degradation | No comms | **Emulated, with local fallback** |

**Weighted decision matrix (criterion weights chosen from stakeholder needs; score 1–5):**

| Criterion (weight) | Central RL brain | Independent junctions | Hierarchical regional | **Role-decomposed (chosen)** |
|---|---|---|---|---|
| Safety (0.25) | 2 | 3 | 4 | **5** |
| Auditability/trust (0.20) | 2 | 3 | 3 | **5** |
| Scalability (0.15) | 1 | 4 | 3 | **4** |
| Evidence-risk (0.20) | 3 | 4 | 2 | **4** |
| Innovation (0.10) | 3 | 1 | 4 | **5** |
| Compute feasibility (0.10) | 1 | 5 | 2 | **3** |
| **Weighted total** | 2.15 | 3.20 | 3.20 | **4.55** |

The role-decomposed design wins on the criteria the stakeholders themselves ranked highest (safety, auditability), while matching the incumbents on feasibility — and it is the only option in which every "beyond traffic lights" topic from the brief has a named owner (A2–A5) that can be ablated.

### 3.5 Ideas carried forward → and where they went

The converged concept is exactly the CoFlow-5 architecture already specced: **A1 Flow** (sole actuator; shared-policy masked RL with Max-Pressure fallback and arbitration), **A2 Emergency**, **A3 Multimodal**, **A4 Situation**, **A5 Sustainability**, coordinated over a pub/sub + request/reply bus behind a deterministic safety layer, with the LLM as explainer/analyst and the whole thing falsified by H1–H8. Every ideated idea above maps to a numbered design element or a [ADV] tier item; parked ideas (LLM in-loop, direct-CO2 reward, perfect-comms assumption) are recorded as *considered and rejected with evidence* — which is itself a Design Thinking deliverable.