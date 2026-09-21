# CoFlow-5 — System Requirements Book

**Title:** Full system requirements from Design Thinking Stages 1–3  
**Product:** CoFlow-5 × SUMO (five-agent traffic orchestration)  
**Status:** Baseline for professor verification — **not yet implemented**  
**Date:** 20 September 2026  
**Companions:** persona canvases [`docs/presentation/personas-canvas.html`](docs/presentation/personas-canvas.html); short architecture note [`docs/presentation/system-design-for-professor.md`](docs/presentation/system-design-for-professor.md); Empathize pack [`coflow5-empathize-pack.md`](coflow5-empathize-pack.md)

> [!IMPORTANT]
> **Historical/superseded architecture note (ADR-0001):** This book remains evidence for Design Thinking Stages 1–3 and keeps its requirement IDs unchanged. Later ADR-0001 supersedes passages that label shared-policy MARL as “Core A1” or place an unspecified policy before Max-Pressure. The required A1 controller is cooperative Max-Pressure; required recovery is `Max-Pressure → actuated → fixed-time`; optional DQN may precede Max-Pressure only after the cooperative core freezes. LLM-controller alternatives remain rejected, and Synapse cannot actuate or reach TraCI. Personas are research-informed, not interview-validated.

**One-sentence summary:** CoFlow-5 Empathizes with eight people and a verified evidence trail; Defines human-centred needs (not “cut vehicle delay”); Ideates a five-agent hybrid where only A1 writes lights, others ask over a message bus, and an LLM may explain the log but never control SUMO.

---

# Design thinking prompt

The course requires **Design Thinking**. Stages 1–3 below are the **prompt we executed**. Stage definitions follow the Interaction Design Foundation model (Empathize, Define, Ideate; illustrations and teaching text: Teo Yu Siang and the Interaction Design Foundation, CC BY-NC-SA 3.0). This book **applies** those stages to CoFlow-5; it does not reprint their article.

| Stage | Prompt (what we had to do) | CoFlow-5 output in this book |
|---|---|---|
| **1 Empathize** | User-centric research: understand users, needs, and underlying problems; consult experts; observe; set aside “throughput-only” assumptions | §1 — 8 personas, journeys, **why each persona exists (evidence)**, claim flags |
| **2 Define** | Organise Empathize findings; state **human-centred** problems (not company wishes); open Ideate with How-might-we | §2 — POV statements, HMW, system problem statement |
| **3 Ideate** | Many ideas, other viewpoints; Brainstorm / Worst Possible Idea / SCAMPER; then **choose** what to build | §3 — solutions per persona **with evidence why**, rejected ideas, architecture comparison, chosen 5-agent design |
| **4–5** (next) | Prototype and Test | §8 — SUMO build order and experiments; not executed |

**Course How-might-we (student brief):** *How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?*

**Human-centred refinement (Define):** *How might we do that for every person on the network — walker, rider, driver, paramedic, operator, resident — not only the average car?*

### What Empathize / Define / Ideate mean here (short)

- **Empathize:** gain insight into users before inventing robots. Experts = literature and product docs (DfT, FHWA, SCATS, Surtrac). Observation = journey maps. Immersion = SUMO as a stand-in for the street (not a substitute for interviews — personas are **research-informed**, not field-validated).
- **Define:** the problem is **not** “we need 15% less average delay.” It is “Amara needs to finish crossing; David needs to know how long the trip will take; …”
- **Ideate:** expand then **cut**. Worst Possible Idea and SCAMPER force bad designs into the open so the five-agent choice is justified, not assumed.

---

## Related context (feeds Ideate, not extra personas)

| Source | What it is | How CoFlow-5 uses it |
|---|---|---|
| **AgentSUMO** (LLM + SUMO scenarios) | Agentic scenario generation / what-if | Pattern for **advisory** simulation queries. **Not** the control loop. Synapse may draft scenarios; A1 still owns TraCI. |
| **Stop-and-go / Project Green Light-style** | Arterial smoothing, fewer stops | Motivates A1 coordination and A5 (stops drive extra emissions). Our KPI: stops/vehicle and proxy emissions, not Google’s product. |
| **Bus lanes, TSP, bike lanes, calming** | Civic project prioritisation | SUMO **can** compare those layouts later. **MVP requirements** are signal agents + safety. Optional analyses: bus-route intersections for TSP/lanes; underserved corridors; bike-lane candidates; speeding/calming sites. Data for funding arguments — **after** A1 vs Max-Pressure runs. |

**Supervisor presentation title:** CoFlow-5 Empathize — who suffers, five helpers, how they talk (kid-friendly text in **Appendix A**).

---

# Stage 1 — Empathize

### What this stage required of us

User-centric research: who suffers from congestion, what they need, what problems sit under any product we might build. Consult experts, map journeys, do not assume “smarter lights for cars” is enough.

### Who suffers (Empathize sketch)

```
EMPATHIZE — Who suffers from traffic congestion?

  Driver              Needs predictable journeys          → David
  Bus passenger       Needs reliable arrival times        → Chidi
  Emergency crew      Needs immediate, safe passage       → Marcus
  Pedestrian          Needs safe and fair crossing time   → Amara
  City operator /     Needs explainable, controllable
  police / engineer   decisions                           → Rosa, Yuki, Omar
  Resident / parent   Needs harm not dumped on their street → Maria
```

### How we Empathized (methods)

| Requirement of the stage | CoFlow-5 action |
|---|---|
| Consult experts | Literature: DfT TAG, FHWA, SCATS, Surtrac, *PLOS One* ALS, Kingsley school exposure, RESCO/T-REX on RL limits |
| Observe users | Journey maps for 8 personas (crossing, corridor, depot, ambulance, control room, school street, incident desk) |
| Immerse in environment | Planned SUMO worlds (4×4, later RESCO / realistic nets). **Not yet run** as the product; Empathize used published networks as **context**, not as our measured results |
| Set aside assumptions | 33-row evidence trail; **claim flags**; IMATM Tunis survey digits treated as placeholders |

### The 8 personas (Empathize output)

| ID | Persona | Who | Need (their words) |
|---|---|---|---|
| P1 | Amara, 74 | Pedestrian, cane ~0.8 m/s | Enough crossing time even when busy |
| P2 | David, 41 | Delivery driver, 60+ stops/day | Know how long the trip will actually take |
| P3 | Chidi, 27 | High-frequency bus rider | Regular buses, not three at once |
| P4 | Rosa, 52 | Depot controller | Why priority was given or refused |
| P5 | Marcus, 34 | Paramedic | Safe passage **and** recovery |
| P6 | Yuki, 47 | Traffic engineer | Control the system, not be trapped by it |
| P7 | Maria, 38 | Parent by a school | No pollution moved onto her street |
| P8 | Omar, 55 | Duty officer | Trust alerts and data age |

IMATM names (Amine, Karim, Nadia, Hichem, Emna, Leila) = **same roles**, Tunis colour. Do not stack as 14 people.

### Why each persona exists — evidence and the solution it justifies

Evidence **motivates the need**. It does **not** set our numeric targets. Targets in the right column are **proposed tests**.

#### P1 Amara — why she is in the book

| | |
|---|---|
| **If we omitted her** | Lights sized for 1.07 m/s walkers strand cane users; wait designed for cars only. |
| **Evidence (why this need is real)** | Perceived wait ≈ **2×** actual (Vallyon, Turner & Hodgson, ATRF 2009) — **not** 1.5×. Frustration / red walking after **20–30 s** (NZTA RR440 2009; TfL; DfT LTN 2/95 normally 40 s, up to 60 s). Assistive speeds: cane **0.8**, walker **0.6** m/s (LaPlante & Kaese, ITE). MUTCD 2009 clearance **1.07 m/s**; HCM **1.0 m/s** if >20% aged 65+. Blind pedestrians: completion difficulty (Bentzen et al., *JVIB* 2005). LPI reduces ped crashes in field studies (FHWA-HRT-18-060). |
| **Journey pain** | Uncertain request; long wait; green too short; conflicting traffic while still on the crossing. |
| **Solution (Ideate)** | Wait-aware priority; acknowledgement; conservative clearance / occupancy extension; **hard interlock** — no conflicting green while she is detected on the crossing. Agent **A3** asks; **A1** enforces. |
| **Why this solution (not another)** | Unconditional “always long green” starves the arterial (David/Marcus). App-only request **excludes** her. Evidence separates **wait** vs **crossing time** — both required. |
| **Proposed test** | Mean & P95 wait; % waits >30 s; **zero clearance truncations**. 40 s cap = hypothesis, not a law. |

#### P2 David — why he is in the book

| | |
|---|---|
| **If we omitted him** | We would optimise mean delay and call it success while delivery rounds collapse on bad days. |
| **Evidence** | Reliability ratio **0.4** (DfT TAG A1.3). Incidents ~**25%** of congestion (FHWA). Avoided HDV stop ≤**0.32 kg CO2 / 1.8 g NOx** (Deschle et al., *Energies* 2022) — links him to Maria’s air. |
| **Journey pain** | Plans break; repeated stops; surge/incident; small delays stack. |
| **Solution** | Neighbour coordination; queue-aware adjustment; P95 **including unfinished/teleported trips**. Agent **A1**. |
| **Why** | Mean-only optimisation is the Worst Possible Idea we inverted. TAG prices **variability**, not only minutes. |
| **Proposed test** | P95 vs Max-Pressure under surge (e.g. −5% — **proposed**); stops/vehicle. |

#### P3 Chidi — why he is in the book

| | |
|---|---|
| **If we omitted him** | “Faster buses” that bunch still fail the passenger. |
| **Evidence** | Wait valued ~**2×** in-vehicle (DfT TAG A1.3; Wardman mean 1.80, n=138). Bunching self-reinforces (Newell & Potts 1964; Daganzo 2009; 2024 reviews). SCOOT bus priority cut Southampton bus times up to **−39%** (Hounsell & McDonald 1986) — feasibility, not our guarantee. Holding literature: headway-based holding under disruption. |
| **Journey pain** | Unpredictable wait; bunch; lateness compounds; missed connection. |
| **Solution** | **Conditional** priority after a large gap / lateness — not every bus; pedestrian clearance preserved. Agent **A3**. |
| **Why** | Always-green-for-buses is a documented Worst Idea (starves cross traffic, can worsen bunching). Wait weight 2× says passenger wait > bus speed. |
| **Proposed test** | Headway variance −15% vs no-priority at ≤3% extra car delay — **proposed**. No invented “riders quit %”. |

#### P4 Rosa — why she is in the book

| | |
|---|---|
| **If we omitted her** | A black-box grant of TSP cannot be operated. |
| **Evidence** | SCATS ships **manual override and audit trails** as product features (SCATS Core, Transport NSW 2022). No quantitative “engineers distrust AI %”. |
| **Journey pain** | Scattered screens; unexplained denial; no history. |
| **Solution** | Dashboard; **reason codes**; authorised request inside safety; log. Agent **A1** (audit). |
| **Why** | Production ATC already treats explanation as core, not a dashboard extra. |
| **Proposed test** | 100% reason-code coverage; operator task (explain a denial). “5 min warning” only with FAR/miss — not claimed proven. |

#### P5 Marcus — why he is in the book

| | |
|---|---|
| **If we omitted him** | Either no EV path, or preemption that wrecks the corridor and cuts Amara. |
| **Evidence** | ALS delay ~**−7%/min** survival-to-discharge in *PLOS One* 2022 (aOR 0.93, n=4,278) — **must not** become “our sim saved lives”. EVP field about **−14% to −23%** (Cary, Houston). Closely spaced preemption: arterial **+20–30 s**, side-street **+7.6%** (Nelson & Bullock, TRR 1727). |
| **Journey pain** | Lights unaware; green into a full exit; isolated preemption moves the jam; no recovery; cost to others hidden. |
| **Solution** | Authenticated request; **pre-clearance**; in-crossing pedestrian first; corridor ETA; **recovery**; log EV time **and** civilian delay. Agent **A2** asks; **A1** acts. |
| **Why** | Green-only preemption is unsafe/useless at spillback (Empathize + Karim/IMATM narrative). Literature shows **externality** of preemption — we must meter it. |
| **Proposed test** | EV time vs none and vs conventional preemption (e.g. −25% / −10% **proposed**); civilian delay; **zero** safety violations. |

#### P6 Yuki — why she is in the book

| | |
|---|---|
| **If we omitted her** | Adaptive control with no owner when it fails. |
| **Evidence** | SCATS intervention + audit (2022). SCOOT **loses benefits under congestion** (Hounsell & McDonald 1986). Surtrac **falls back** to default durations on sensor/network failure (Smith et al., CMU). |
| **Journey pain** | Unknown health; undiagnosable actions; stale data; unsafe takeover; snap-back too early. |
| **Solution** | Mode / freshness / faults; full decision history; watchdog; override **with interlocks**; ladder Max-Pressure → actuated → fixed-time. Agent **A1**. |
| **Why** | Field systems already fallback; LLM-in-the-loop contradicts latency/reliability (CoLLMLight, SCATS). |
| **Proposed test** | Injected faults trigger fallback; override cannot create conflicting greens; log completeness; latency measured (target <100 ms — proposed). |

#### P7 Maria — why she is in the book

| | |
|---|---|
| **If we omitted her** | Corridor optimisation can dump queues and exhaust on the school street. |
| **Evidence** | **6.4M** US children (13.5%) in school ≤250 m of a major road (Kingsley et al., *IJERPH* 2014). ~33% of US public schools ≤400 m (Appatova et al. 2008). Stop-start NOx/CO2 from Deschle 2022. **HBEFA/SUMO = proxies, not air quality.** |
| **Journey pain** | Idling at home; walk to school; hidden local deterioration; city-wide % explains nothing. |
| **Solution** | Link-level proxy maps; school-adjacent periods; **pre-registered displacement rule**. Agent **A5**. |
| **Why** | Stop-and-go / “green wave” ideas without a **where** check recreate Maria’s harm. |
| **Proposed test** | No statistically significant mean NOx-proxy rise on school-adjacent residential links (α=0.05, Holm) — **proposed rule**, then applied. |

#### P8 Omar — why he is in the book

| | |
|---|---|
| **If we omitted him** | Incidents (large share of delay) stay invisible or drown him in false alarms. |
| **Evidence** | Incidents **25–30%** of metro congestion delay (FHWA; Puget Sound 2006). TIM metrics exist (clearance, secondary crashes) — **no** universal detection-delay number. |
| **Journey pain** | Hidden incidents; false alarms; jam vs crash vs dead sensor; frozen dashboard; recovery ignored. |
| **Solution** | Residual vs forecast (EWMA/CUSUM first); grouped alerts; stale flag; “unknown” ≠ “clear”. Agent **A4**. |
| **Why** | Worst Idea: treat all sensor values equally. Finkelberg-type work: comms reliability is rarely tested — we **require** drop tests. |
| **Proposed test** | Delay / FAR / miss / recovery **by severity** after a noise pilot — exploratory, not copied from a fake world average. |

### Claim flags (Empathize constraint on the whole book)

Do not write as facts: wait 1.5×; unverified MUTCD 2023 0.8 m/s; “X% distrust AI”; rider-abandon %; EY as hard evidence; universal detection delay; flashover 3–5 min; HBEFA as air quality; sim EV time as lives saved; IMATM Table 9 as measured; P95 without unfinished trips.

### Empathize deliverable

Personas, journeys, evidence trail, solutions seeds — **complete for Stage 1**. Interviews not done; say so.

---

# Stage 2 — Define

### What this stage required of us

Organise Empathize. State problems **from users**, not from “we need 15% less delay.” Then open How-might-we toward Ideate.

#### Wrong (company-centric)

> We need to reduce average vehicle delay by 15% with five AI agents.

#### Right (human-centric)

> Amara needs to cross without exhaustion or being cut off.  
> David needs to know how long the trip will take.  
> Chidi needs regular buses, not bunches.  
> Rosa needs to understand a denial.  
> Marcus needs a path **and** a recovery.  
> Yuki needs to remain in command when automation fails.  
> Maria needs cleaner air **here**, not pollution moved.  
> Omar needs alerts he can trust, including “we do not know.”

### POV statements

| ID | Point of view |
|---|---|
| POV-1 | Amara needs enough **and** tolerable wait because lights are built for faster walkers. |
| POV-2 | David needs **tails**, because averages lie. |
| POV-3 | Chidi needs **headways**, because speed ≠ service. |
| POV-4 | Rosa needs a **readable reason**, because she is accountable. |
| POV-5 | Marcus needs **space ahead and recovery**, because a green into a full link fails. |
| POV-6 | Yuki needs **known modes and safe takeover**. |
| POV-7 | Maria needs **local** checks. |
| POV-8 | Omar needs **cause vs data-death** separated. |

### System POV

> Urban traffic control is broken when it optimises **vehicle throughput** and treats people as interchangeable delay. Amara, David, Chidi, Rosa, Marcus, Yuki, Maria, and Omar each need a system that **sees them, protects them, and explains itself**.

### How-might-we

| ID | Question |
|---|---|
| HMW-0 | How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable? |
| HMW-R | …for **every person** on the network, not just the average driver? |
| HMW-1…8 | One HMW per persona (crossing time vs wait; P95; conditional TSP; audit; pre-clear+recover; interlocked override; displacement; trustworthy alerts) |
| HMW-9 | How might lights stay **correct for one second** if the LLM or the radio is dead? |

### Define deliverable

Problem statement + 8 needs + POV + HMW. **Done.**

---

# Stage 3 — Ideate

### What this stage required of us

Many ideas; other angles; Brainstorm and Worst Possible Idea first; then SCAMPER / comparison to **pick** a design.

### 3.1 Brainstorm — solution per persona (chosen line)

| Persona | Possible solution | Why this (evidence link) | Agent |
|---|---|---|---|
| Amara | Wait-aware priority + conservative clearance + ack | 2× wait; 0.8 m/s; 30 s cliff | A3 → A1 |
| David | Neighbour coordination + queue-aware + P95 | TAG 0.4; unfinished trips | A1 |
| Chidi | Conditional headway-gap priority | Bunching theory; wait 2× | A3 → A1 |
| Rosa | Dashboard + reason codes + authorised ask | SCATS audit/override | A1 |
| Marcus | Auth corridor + pre-clear + recovery + cost log | EVP externality TRR 1727 | A2 → A1 |
| Yuki | Health + interlocked override + fallback ladder | SCOOT/Surtrac failure modes | A1 |
| Maria | Link-level proxies + displacement rule | Kingsley; HBEFA-as-proxy | A5 → A1 |
| Omar | Residual alerts + stale flags | FHWA incident share; no universal FAR | A4 → A1 |

### 3.2 Worst Possible Idea → design principle

| Worst idea | What it reveals (requirement) |
|---|---|
| One central AI owns every light | Single failure → **decentralised fallback** (FR-S4) |
| Prioritise every bus always | Starves others → **conditional** TSP (FR-A2) |
| Ignore pedestrians when traffic is heavy | Unsafe → **hard clearance** (FR-S1) |
| Optimise average delay only | Hides tails → **P95 / max wait** (NFR-5) |
| Trust all sensor data equally | Stale looks like crash → **TTL + health** (CR-2, FR-U2) |
| Let agents hide costs | Unfair → **reason codes + civilian delay** (FR-A3, FR-O3) |
| LLM presses the buttons | Latency/reliability → **LLM never TraCI** (FR-O4) |

### 3.3 SCAMPER

| Letter | Applied to CoFlow-5 |
|---|---|
| Substitute | Fixed-time **as fallback**, not as the only plan |
| Combine | Pedestrian + transit in **A3** (same specialist, different bids) |
| Adapt | Max-Pressure as **watchdog**, not the only controller |
| Modify | Reward / bids include **eco proxies**, not delay alone |
| Put to other use | Reason codes for **trust** (Rosa), not only debug |
| Eliminate | Unlimited priority — **bound** every request |
| Reverse | What if the person **already on the crossing** outranks the ambulance? **Yes** (FR-A4) |

### 3.4 Architecture alternatives

| Architecture | Pros | Cons | Verdict |
|---|---|---|---|
| One central RL brain | Global in theory | Explodes; one failure | Reject (upper-bound toy only) |
| Independent junctions | Simple | No priority; unstable under incidents (T-REX) | Baseline |
| Shared-policy MARL + messages | Scale; coordinate | Heterogeneous junctions (RESCO) | **Core A1** |
| Hierarchical regional | Steadier under incidents | Costly to train | Later / advanced |
| Auction among specialists | Explicit trade-offs | Needs values/confidence | **Arbitration** |
| LLM orchestrator | Words | Latency, reliability | **Explainer only** |

### 3.5 Chosen design — hybrid role-decomposed hierarchy

```
PERSONAS ──► AGENTS ──► MESSAGE BUS ──► SAFETY ──► SUMO

  A1 Coord   A2 Emerg   A3 Ped/Trans   A4 Lookout   A5 Green
      │          │           │              │           │
      └──────────┴───────────┴──────────────┴───────────┘
                           │
                    MESSAGE BUS
              Pub/Sub · Req/Reply · Heartbeat · TTL
                           │
                    SAFETY LAYER
              Interlocks · Clearance · Masked override
                           │
                    SUMO (TraCI / libsumo)
                    Only A1 writes

KEY:  A1 decides · A2 requests · A3 protects · A4 detects · A5 checks
RULE: Safety first · Boss is boss · Backup plans
```

**Five agents (control plane):**

| Agent | Name | Role | Serves |
|---|---|---|---|
| **A1** | Coordinator / Light Boss | Sole actuator; arbitration | David, Rosa, Yuki (control) |
| **A2** | Emergency Responder | Corridor ask + pre-clear | Marcus |
| **A3** | Pedestrian & Transit Guardian | Crossing + conditional bus | Amara, Chidi |
| **A4** | Lookout | Forecast, residuals, health | Omar, Yuki |
| **A5** | Green Guardian | Eco weights, displacement watch | Maria |

**Synapse (LLM):** RAG + explanations from the **log**. **Not** a sixth writer. AgentSUMO-style what-if stays **advisory**.

**Three rules (normative):**

1. **Safety first** — never two fighting greens; in-crossing person finishes.  
2. **Boss is boss** — only A1 pushes TraCI.  
3. **Backup plans** — dead radio → local A1; dead policy → Max-Pressure → actuated → fixed-time.

### 3.6 Adjacent ideas (stop-and-go, Green Light, bus/bike)

Keep as **optional analyses** once the spine runs:

- Arterial stop-and-go reduction (A1 coordination + A5 stop KPI).  
- Bus-route junctions: candidates for **lanes / TSP** (data for cities, not MVP code).  
- Underserved corridors: extra bus would cut car demand (scenario, AgentSUMO-like).  
- Bike lane / calming sites from speeding or delay maps.

These **must not** delay Tier 0 (A1 vs Max-Pressure).

### Ideate deliverable

8 evidenced solutions; 7 worst-ideas → principles; SCAMPER; 6 architectures; **chosen 5-agent + bus + safety**. **Done.**

---

# System requirements (shall)

**Shall** = required. **Should** = keep unless ablation kills it. **Must not** = forbidden.

### Safety and actuation

| ID | Requirement |
|---|---|
| FR-S1 | Prohibit conflicting greens and truncated pedestrian clearance. |
| FR-S2 | Only A1 sends signal commands to SUMO. |
| FR-S3 | Deterministic safety mask on every action. |
| FR-S4 | Watchdog: policy → Max-Pressure → actuated → fixed-time. |
| FR-S5 | Human override **inside** the same mask. |

### Requests

| ID | Requirement |
|---|---|
| FR-A1 | A2 authenticated EV request in a 5–10 s epoch. |
| FR-A2 | A3 pedestrian escalation + **conditional** bus bids. |
| FR-A3 | One-round accept/reject + **reason code**. |
| FR-A4 | Tiers: in-crossing/safety → EV → pedestrian deadline → conditional transit → flow → eco. |
| FR-A5 | Within a tier, net-benefit bids; discount stale/low confidence. |
| FR-A6 | Controlled recovery after EV passage. |

### Situation, eco, explain

| ID | Requirement |
|---|---|
| FR-O1 | A4 **should** publish forecasts and residual alerts with age/confidence. |
| FR-O2 | A5 **should** publish eco weights from **labelled proxies**. |
| FR-O3 | Log: time, inputs, constraints, action, reason codes, request ids. |
| FR-O4 | LLM **shall not** write TraCI. |
| FR-O5 | Absent LLM ⇒ control unchanged. |

### Operators

| ID | Requirement |
|---|---|
| FR-U1 | Rosa: positions, headways, priority, reason. |
| FR-U2 | Yuki: mode, freshness, faults, fallback. |
| FR-U3 | Omar: grouped alerts; stale flag; unknown ≠ clear. |

### Communication

| ID | Requirement |
|---|---|
| CR-1 | Pub/sub topics `state/`, `forecast/`, `alerts/`, `eco/`. |
| CR-2 | TTL + heartbeat on every message. |
| CR-3 | A1 still acts if the board is empty. |
| CR-4 | A2/A3 use request/reply, not a second TraCI writer. |
| CR-5 | In-process pub/sub first; Redis only if split-host demo. |
| CR-6 | Harness **shall** drop/delay messages. |

### Quality and evaluation

| ID | Requirement |
|---|---|
| NFR-1 | 1 s SUMO step, TraCI/libsumo. |
| NFR-2 | Measure A1 latency (proposed <100 ms). |
| NFR-3 | Baselines: fixed-time, actuated, Max-Pressure. |
| NFR-4 | Paired / CRN stats; **must not** headline best episodes. |
| NFR-5 | Unfinished/teleports count as failures in P95. |
| NFR-6 | HBEFA labelled proxy. |
| NFR-7 | Git hash + SUMO version on every run. |
| NFR-8 | Persona numbers are **hypotheses**. |

---

# Build order (Prototype / Test plan)

| Step | What | Professor verifies |
|---|---|---|
| 0 | Pin SUMO, small net, fixed-time + actuated | Runs with **no** learned agent |
| 1 Tier 0 | A1 + mask + watchdog vs Max-Pressure | Honest result, including negative |
| 2 Tier 1 | Bus + A2 A3 A5 + codes | Ablations |
| 3 Tier 2 | A4 + message-loss | Degrades, does not deadlock |
| 4 Optional | LLM from logs | Kill LLM, lights unchanged |

**Cut LLM before cutting statistics. Cut features before cutting rigor.**

**Must not:** LLM writes TraCI; A2–A5 before Tier 0; lives saved; “air quality” from HBEFA.

**Prototype journeys:** (1) Amara+David+Chidi everyday; (2) Marcus recovery; (3) Omar/Yuki/Maria incident or radio loss.

---

# Traceability

| Need | Evidence (why) | Solution | Req | Agent | Test |
|---|---|---|---|---|---|
| Amara cross | 2× wait; 0.8 m/s; 30 s | Wait-aware + mask | FR-S1, FR-A2, FR-A4 | A3/A1 | Truncations, waits |
| David P95 | TAG 0.4 | Coordination | NFR-5 | A1 | P95, stops |
| Chidi regular | Bunching; wait 2× | Conditional TSP | FR-A2 | A3 | Headway var |
| Rosa why | SCATS audit | Reason codes | FR-A3, FR-U1 | A1 | Coverage |
| Marcus pass | EVP + externality | Pre-clear + recover | FR-A1, FR-A6 | A2 | EV + civilian |
| Yuki control | SCOOT/Surtrac | Ladder + interlock | FR-S4, FR-S5 | A1 | Fault inject |
| Maria local | Kingsley; proxy | Displacement rule | FR-O2, NFR-6 | A5 | Link map |
| Omar trust | FHWA 25–30%; no universal FAR | Residuals + stale | FR-O1, FR-U3, CR-6 | A4 | FAR by severity |
| Survive death | Latency literature | Board optional | FR-O5, CR-3 | A1 | Drop messages |

---

# Report-ready close

**Stage 1:** Eight personas; journeys; verified sources (wait 2×, TAG 0.4, bunching, EVP cost, SCATS audit, school exposure, incident share); claim flags.

**Stage 2:** Not “cut delay 15%.” POV: control that only sees cars fails people. HMW: agents and data for **every** person, and for the second the radio dies.

**Stage 3:** Brainstorm, Worst Idea, SCAMPER, six architectures. Chosen: **A1 Coordinator, A2 Emergency, A3 Ped/Transit, A4 Lookout, A5 Green Guardian**, message bus, safety layer, LLM explainer only.

---

# Appendix A — Kid-friendly agent text (supervisor slides)

Use this language in talks; **this book’s shalls** remain the technical truth.

1. **A1 Light Boss** — only robot who pushes the buttons; listens then chooses; tries not to make anyone wait forever.  
2. **A2 Siren Helper** — megaphone: *clear the way*; still cannot break Rule 1 if someone is on the crossing.  
3. **A3 Bus & Walker Buddy** — late bus may get help; walk sign long enough.  
4. **A4 Lookout** — warns of jams/crashes; does not freeze A1 if quiet.  
5. **A5 Sky Protector** — fewer stop–start puffs; must not dump smoke on Maria’s street.

Walkie-talkies = message bus. If batteries die, A1 uses its own eyes (Rule 3).

---

# Appendix B — Document map

| File | Role |
|---|---|
| This book | Requirements + DT Stages 1–3 + evidence-why |
| `coflow5-empathize-pack.md` | Four headings: Personas, Journeys, Evidence, Possible Solution |
| `docs/presentation/personas-canvas.html` | Printable canvases |
| `docs/presentation/system-design-for-professor.md` | Agents / bus / build checklist |
| `CoFlow-5_System_Requirements.md` | Short SRS (same shall-IDs) |

**Owner:** CoFlow-5 team. **Baseline:** 20 September 2026.
