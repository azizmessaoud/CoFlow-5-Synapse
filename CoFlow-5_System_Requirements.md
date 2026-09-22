# CoFlow-5 — System Requirements Document

**Product:** CoFlow-5 (five-agent traffic orchestration on Eclipse SUMO)  
**Document type:** Short SRS. The full Design Thinking + evidence book is [CoFlow-5_System_Requirements_Book.md](CoFlow-5_System_Requirements_Book.md).  
**Status:** Requirements baseline for professor review — **software not yet implemented**  
**Study setting:** Urban corridor (Tunis centre as the working city in persona sheets)  
**Related artifacts:** [coflow5-empathize-pack.md](coflow5-empathize-pack.md), [docs/presentation/system-design-for-professor.md](docs/presentation/system-design-for-professor.md), [docs/presentation/personas-canvas.html](docs/presentation/personas-canvas.html)

> [!IMPORTANT]
> **Historical/superseded architecture note (ADR-0001):** Requirement IDs in this legacy SRS remain stable, but ADR-0001 governs their current interpretation. Any “learned policy → Max-Pressure” wording in FR-S4 describes only an optional DQN branch; the required controller and recovery path are `cooperative Max-Pressure → actuated → fixed-time`. Reinforcement learning is not required. Only A1 may write signals, and Synapse/LLM components remain outside the Control plane with no TraCI capability. Personas remain research-informed, not interview-validated.

**Process note:** Stages follow the Interaction Design Foundation Design Thinking model. Empathize, Define, and Ideate are complete; a controlled Prototype and partial technical Test evidence are gated through Row 10c. Human validation and multi-seed inference remain incomplete. Problem statements are written from **users’ needs**, not from “we need a five-agent demo.”

**Honesty note:** User Personas are **research-informed design artifacts**, not interview-validated field profiles. Numeric targets are **proposed acceptance criteria** to test against baselines, not results already achieved.

---

## 0. How to read this document

| Section | Design Thinking stage | What the professor can check |
|---|---|---|
| 1 | Empathize | Users, pains, evidence, claim flags |
| 2 | Define | Human-centred problem statements and How-might-we questions |
| 3 | Ideate | Chosen solution shape vs rejected ideas |
| 4–7 | Requirements | Shall-statements, agents, communication, quality |
| 8 | Build | Order of implementation and verification |
| 9 | Traceability | Need → requirement → agent → test |

**Shall** = required in the system we will build.  
**Should** = required unless a later ablation shows it does not earn its keep.  
**Must not** = forbidden claim or behaviour.

---

## 1. Stage 1 — Empathize (users and needs)

Aim: set aside “smart lights for throughput” and record **who is hurt, when, and what evidence supports that**.

### 1.1 Users (eight User Personas)

| ID | Name | Role | Core need (in their words) |
|---|---|---|---|
| P1 | Amara, 74 | Pedestrian with a cane (~0.8 m/s) | Enough time to cross, even when the street is busy |
| P2 | David, 41 | Delivery driver | Know how long the trip will actually take |
| P3 | Chidi, 27 | Frequent bus rider | Regular buses, not three at once after a long wait |
| P4 | Rosa, 52 | Bus depot controller | See why priority was given or refused; act before service breaks |
| P5 | Marcus, 34 | Ambulance crew | Get through safely **and** let traffic recover |
| P6 | Yuki, 47 | Traffic engineer | Automation that she can still control and explain |
| P7 | Maria, 38 | Parent by a school street | Cleaner main road must not dump exhaust on her street |
| P8 | Omar, 55 | Incident duty officer | Know what is wrong, why, and whether the data is still trustworthy |

Alternate names in the IMATM report (Amine, Karim, Nadia, Hichem, Emna, Leila) are the **same jobs under other names**. Do not add them as extra people.

### 1.2 Problems seen in User Journeys (pain, not features)

- Crossing is designed for the **average** walker; slow walkers run out of green; long waits push people onto red.
- “Faster on average” can hide **worse worst days** for deliveries.
- Unconditional bus priority can speed a bus that is already early and **bunch** the rest.
- Operators cannot defend a decision with **no reason code**.
- A green for an ambulance is useless if the **exit is blocked**; recovery is part of the journey.
- Stale sensors can look “normal” on a frozen screen.
- Network-wide emission “wins” can **displace** queues to the school gate.
- False alerts destroy trust; an anomaly is not yet a **cause**.

**Shared collision (one network):** ambulance + Amara mid-crossing + Chidi’s late bus + Maria’s school street. A solution for one user can cost another.

### 1.3 Evidence (motivates needs; does not set our targets)

Selected primary-source anchors (full trail: Empathize pack §EVIDENCE):

| Need | Finding | Source (short) |
|---|---|---|
| Pedestrian wait | Perceived wait ≈ **2×** actual (not 1.5×) | Vallyon, Turner & Hodgson, ATRF 2009 |
| Pedestrian wait | Frustration / red-crossing after **20–30 s** | NZTA RR440; TfL; DfT LTN 2/95 |
| Walking speed | Cane ~0.8 m/s; MUTCD clearance 1.07 m/s | LaPlante & Kaese; MUTCD 2009 §4E |
| Reliability | Reliability ratio **0.4** | DfT TAG A1.3 |
| Bus wait | Wait valued ~**2×** in-vehicle time | DfT TAG A1.3; Wardman |
| Bunching | Self-reinforcing irregularity | Daganzo 2009; Newell & Potts 1964 |
| EMS | ALS delay associated with lower survival (~7%/min in one study) | *PLOS One* 2022 — **do not** turn our sim seconds into lives saved |
| Preemption cost | Closely spaced preemption: arterial **+20–30 s** | Nelson & Bullock, TRR 1727 |
| Operators | SCATS ships override + audit as product features | Transport NSW 2022 |
| Incidents | ~**25–30%** of metro congestion delay | FHWA |
| Emissions | Avoided heavy-vehicle stop has a documented CO2/NOx saving | Deschle et al., *Energies* 2022 — **proxy**, not air quality |

### 1.4 Claim flags (must not appear as requirements or results)

1. Perceived wait is 1.5× (use **2×**).  
2. Unverified MUTCD 2023 0.8 m/s (use MUTCD 2009 1.07 m/s unless 2023 is checked).  
3. “X% of engineers distrust AI.”  
4. Rider-abandonment percentages.  
5. Vendor public-opinion surveys as hard evidence.  
6. A universal “average incident detection delay.”  
7. “Flashover in 3–5 minutes.”  
8. SUMO/HBEFA as measured **air quality** or **personal exposure**.  
9. Simulated ambulance time as **lives saved**.  
10. IMATM Table 9 / interview counts as real field results (file labels them placeholders).  
11. Unfinished/teleported trips omitted from P95 (hides congestion).

---

## 2. Stage 2 — Define (human-centred problem statements)

**Wrong (company wish):** “We need a five-agent AI to raise network throughput by 5%.”

**Right (user need):** people who share one street need **enough time to cross, predictable trips, regular buses, explainable priority, safe emergency passage with recovery, operator control, no dumped pollution, and trustworthy alerts** — without one group paying in secret.

### 2.1 Point-of-view statements

| ID | Point of view |
|---|---|
| POV-1 | Amara needs enough crossing time **and** a wait that is not exhausting, because the light today is sized for faster walkers. |
| POV-2 | David needs **predictable** travel time, because variable delay breaks a delivery round even when the average looks fine. |
| POV-3 | Chidi needs **regular** headways, because bunching is the service failure, not mean bus speed. |
| POV-4 | Rosa needs a **reason she can read** for every grant or denial of priority, because she is accountable when service breaks. |
| POV-5 | Marcus needs a **cleared path and a recovery**, because a green at a blocked exit and a wrecked network after the call both fail the mission. |
| POV-6 | Yuki needs **known modes and a safe takeover**, because she remains responsible when automation fails. |
| POV-7 | Maria needs **local** emission and queue checks, because a corridor “win” can move harm to the school street. |
| POV-8 | Omar needs alerts that separate **incident / jam / dead data**, because false certainty is worse than a labelled unknown. |

### 2.2 How-might-we (bridge to Ideate)

**HMW-0 (brief):** How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?

Refined (human-centred):

| ID | How might we… |
|---|---|
| HMW-1 | …give slow pedestrians enough time to finish crossing **without** making waits so long that people step out on red? |
| HMW-2 | …make journey **tails** better for delivery drivers, not only the mean? |
| HMW-3 | …give priority to the **late** bus without speeding an early bus into a bunch, and without cutting a pedestrian already on the crossing? |
| HMW-4 | …make every priority decision **auditable** for a depot controller in one screen? |
| HMW-5 | …move an ambulance by clearing **space ahead**, then restore the corridor, while logging delay to others? |
| HMW-6 | …let an engineer **take back** control without ever creating two conflicting greens? |
| HMW-7 | …cut estimated emissions near a school **without** shifting queues onto residential links? |
| HMW-8 | …alert a duty officer with **why** and **data age**, including when we simply do not know? |
| HMW-9 | …keep lights **correct for one second** even if the talking AI or the radio is dead? |

### 2.3 System problem statement (Define output)

> People who walk, drive, ride the bus, respond to emergencies, operate the network, live by a school, or manage incidents **need a traffic system that co-arbitrates their competing needs on one street, records why a request won or lost, stays safe when sensors or messages fail, and does not hide harm in averages** — because today’s control mostly optimises vehicles through a junction and treats everyone else as a side channel.

---

## 3. Stage 3 — Ideate (chosen solution vs rejected)

### 3.1 Ideas generated then **rejected** (and why)

| Idea | Why not |
|---|---|
| LLM as A1 / “AI orchestrates the lights” | Latency and failure mode wrong for 1 s control; if LLM dies, lights must not notice |
| Fully centralised brain over the whole city | Joint action space explodes; single point of failure |
| Independent RL at every junction with no arbitration | Evidence (T-REX, RESCO): degrades under incidents and on realistic nets |
| Unconditional bus and EV green | Bunching; blocked-exit green; pedestrian cut-off; unlogged externality |
| Auction only, no safety mask | RL will find illegal phases |
| Best-episode reporting | Overstates performance (RESCO) |

### 3.2 Idea selected (the system we require)

**CoFlow-5:** five specialised agents, **one writer** to the lights, a **noticeboard + one-round request**, a **hard safety mask**, a **fallback ladder**, and an optional **explainer** that only reads logs.

| Pattern | Role |
|---|---|
| Single actuation authority | Only A1 writes to SUMO |
| Safety mask | Illegal greens never executed |
| Pub/sub blackboard | `state/`, `forecast/`, `alerts/`, `eco/` |
| Contract-net (one round) | A2/A3 request; A1 + reason code |
| Priority tiers then bid | Safety / in-crossing person → EV → pedestrian deadline → late bus → flow → eco |
| Watchdog ladder | Policy → Max-Pressure → actuated → fixed-time |
| LLM as explainer | RAG + words from the log; never TraCI |

---

## 4. System context and actors

**In scope:** SUMO simulation (≥ 1.24), TraCI/libsumo, five agents, message bus, decision log, evaluation harness vs baselines. Optional Synapse (LLM) **off** the control path.

**Out of scope for this baseline:** live city deployment, claiming air-quality improvement, claiming lives saved, GitHub-scale ops.

**External systems:** Eclipse SUMO (world), optional Postgres/pgvector (docs for RAG), optional dashboard for Rosa/Yuki/Omar.

---

## 5. Functional requirements

IDs are the baseline. Traceability is in §9.

### 5.1 Safety and actuation (A1)

| ID | Requirement |
|---|---|
| FR-S1 | The system **shall** prohibit conflicting greens and truncated pedestrian clearance (no release of conflicting traffic while a detected pedestrian remains on the crossing). |
| FR-S2 | Only A1 **shall** send signal commands to SUMO. |
| FR-S3 | A1 **shall** apply a deterministic safety mask to every candidate action before execution. |
| FR-S4 | If inputs are invalid, heartbeats are missing, or the learned policy times out, A1 **shall** step the watchdog: learned policy → Max-Pressure → actuated → fixed-time. |
| FR-S5 | Authorised human override **shall** take precedence **only** inside the same safety mask (override must not enable conflicting greens). |

### 5.2 Requests and arbitration

| ID | Requirement |
|---|---|
| FR-A1 | A2 **shall** be able to submit an authenticated emergency request (position, route/ETA) within a 5–10 s decision epoch. |
| FR-A2 | A3 **shall** be able to submit pedestrian wait-escalation and **conditional** bus bids (late / large headway gap — not every bus). |
| FR-A3 | A1 **shall** accept or reject each request in **one round** and write a **reason code**. |
| FR-A4 | Arbitration **shall** apply tiers: in-crossing pedestrian / safety → emergency → pedestrian deadline → conditional transit → general flow → eco. |
| FR-A5 | Within a tier, A1 **should** rank feasible bids by net benefit (benefit minus estimated externality) and discount stale or low-confidence messages. |
| FR-A6 | After an emergency passage, A1 **shall** run a controlled recovery (not an instant snap-back). |

### 5.3 Situation, environment, explain

| ID | Requirement |
|---|---|
| FR-O1 | A4 **should** publish short-horizon forecasts and residual-based anomaly alerts with a confidence/age field. |
| FR-O2 | A5 **should** publish eco weights / hot-spot flags derived from SUMO/HBEFA **proxies**, labelled as estimates. |
| FR-O3 | The decision log **shall** store timestamp, inputs used, constraints, action, reason codes, and originating request ids. |
| FR-O4 | The optional LLM **shall not** write TraCI. It **may** only read the log and retrieved docs to explain a decision. |
| FR-O5 | If the LLM process is absent, control **shall** be unchanged. |

### 5.4 Operator-facing (Rosa, Yuki, Omar)

| ID | Requirement |
|---|---|
| FR-U1 | Rosa **shall** see bus positions, headways, priority yes/no, and the reason code. |
| FR-U2 | Yuki **shall** see operating mode, data freshness, faults, and active fallback. |
| FR-U3 | Omar **shall** see grouped alerts with supporting observations and a stale-data flag; “nothing detected” **shall** be distinct from “insufficient data.” |

---

## 6. Communication requirements

| ID | Requirement |
|---|---|
| CR-1 | Agents **shall** communicate via a pub/sub board with topics `state/`, `forecast/`, `alerts/`, `eco/` (names may map 1:1 in code). |
| CR-2 | Every published message **shall** carry a TTL/expiry and a producer heartbeat. |
| CR-3 | Consumers **shall** ignore or discount expired messages; A1 **shall** still act on local observation if the board is empty. |
| CR-4 | A2/A3 requests **shall** use an explicit request/reply (contract-net), not a second TraCI writer. |
| CR-5 | First implementation **shall** use in-process pub/sub; a split-process bus **should** be added only if a two-machine demo is required. |
| CR-6 | The evaluation harness **shall** be able to drop or delay messages (communication-failure tests). |

---

## 7. Quality, data, and evaluation requirements (non-functional)

| ID | Requirement |
|---|---|
| NFR-1 | Simulation step **shall** be 1 s compatible with SUMO TraCI/libsumo. |
| NFR-2 | A1 decision latency **should** stay under 100 ms in the intended hardware class (proposed; to be measured). |
| NFR-3 | Baselines **shall** include at least fixed-time, actuated, and Max-Pressure, with comparable tuning effort. |
| NFR-4 | Comparisons **shall** use common random numbers / paired runs; **must not** report only best episodes. |
| NFR-5 | Unfinished and teleported trips **shall** count as failures in reliability metrics (P95). |
| NFR-6 | Emission outputs **shall** be labelled HBEFA/SUMO **proxies**. |
| NFR-7 | Every run **shall** log software git hash and SUMO version. |
| NFR-8 | Numeric persona targets (e.g. 40 s wait cap, EV −25%) **shall** be tested as **hypotheses**, not advertised as proven. |

### 7.1 Proposed acceptance criteria (Define → Test; not yet measured)

| Persona | Proposed criterion (test later) |
|---|---|
| Amara | Mean wait and P95 wait reported; **zero** clearance truncations; 40 s treated as a **tested cap**, not a literary law |
| David | P95 vs Max-Pressure under surge (proposed −5%); unfinished trips included |
| Chidi | Headway variance vs no-priority (proposed −15%) at bounded extra car delay (proposed ≤3%) |
| Rosa | 100% of grants/denials have a reason code |
| Marcus | EV time vs no-priority and vs conventional preemption; civilian delay logged; **zero** safety violations |
| Yuki | Fallback activates on injected faults; override cannot break the mask |
| Maria | Per-link proxy map; pre-registered “no significant NOx-proxy rise on school-adjacent residential links” |
| Omar | Detection delay, false-alarm and miss rates **by severity**; thresholds after a noise pilot |

---

## 8. Agents, build order, and verification

### 8.1 Agent count

**Five** agents (A1–A5). LLM is **not** agent six of the control plane.

| Agent | Writes lights? |
|---|---|
| A1 Flow | Yes |
| A2 Emergency | No |
| A3 Multimodal | No |
| A4 Situation | No |
| A5 Sustainability | No |
| Synapse LLM | No |

### 8.2 Required implementation order (shall)

| Step | Build | Professor verifies |
|---|---|---|
| 0 | Pin SUMO, 4×4 (or equivalent) net, fixed-time + actuated | World runs with **no** learned agent |
| 1 Tier 0 | A1 + safety mask + watchdog vs Max-Pressure | Honest comparison; MVP can stop here |
| 2 Tier 1 | Bus + A2, A3, A5 + reason codes | Ablation: each extra agent off |
| 3 Tier 2 | A4 + message-loss sweeps | Degrades, does not deadlock |
| 4 Optional | LLM explainer from logs | Killing LLM does not change lights |

If a tier slips: **cut features, not statistical rigor. Cut the LLM before cutting evaluation.**

### 8.3 Forbidden implementation (must not)

- LLM or A2–A5 writing TraCI.  
- Adding A2–A5 before A1 vs Max-Pressure runs.  
- Best-episode tables as the headline result.  
- “Lives saved” or “air quality improved” from this simulation.

---

## 9. Traceability matrix

| User need | POV / HMW | Requirements | Primary agent | Later test |
|---|---|---|---|---|
| Enough time to cross | POV-1 / HMW-1 | FR-S1, FR-A2, FR-A4 | A3 (A1 enforces) | Clearance truncations, waits |
| Predictable trips | POV-2 / HMW-2 | FR-S2, NFR-5 | A1 | P95, stops |
| Regular buses | POV-3 / HMW-3 | FR-A2, FR-A4 | A3 | Headway variance |
| Explainable priority | POV-4 / HMW-4 | FR-A3, FR-O3, FR-U1 | A1 | Reason-code coverage |
| EV passage + recovery | POV-5 / HMW-5 | FR-A1, FR-A6, FR-S1 | A2 | EV time, civilian delay |
| Safe operator control | POV-6 / HMW-6 | FR-S4, FR-S5, FR-U2 | A1 | Fault injection, override |
| No dumped pollution | POV-7 / HMW-7 | FR-O2, NFR-6 | A5 | Link-level proxy map |
| Trustworthy alerts | POV-8 / HMW-8 | FR-O1, FR-U3, CR-2 | A4 | FAR / miss / stale flags |
| Survive radio/LLM death | HMW-9 | FR-S4, FR-O5, CR-3, CR-6 | A1 | Message-drop sweeps |

---

## 10. Stages 4–5 (not yet executed)

**Prototype (planned):** (1) everyday crossing with Amara + David + Chidi; (2) ambulance passage and recovery; (3) incident or communication failure with Omar, Yuki, Maria.

**Test (planned):** walkthroughs and SUMO experiments against §7.1; proxy walkthroughs labelled as such if real stakeholders are unavailable.

These stages **do not** change the requirements in §§5–8 until an experiment **falsifies** a shall. A failed numeric target is a result, not a silent rewrite of Empathize.

---

## 11. Acceptance of this document

The professor can treat this file as the **system requirements baseline** if all of the following hold:

1. Problem statements are user-centred (Define), not “we need more AI.”  
2. Empathize users and claim flags are respected.  
3. Five agents, one writer, board + one-round asks, LLM off the loop.  
4. Build order in §8.2 is the delivery plan.  
5. Numbers in §7.1 are tests, not trophies.

**Document owner:** CoFlow-5 design team  
**Baseline date:** 20 September 2026
