# CoFlow-5 Synapse — Final Project Book

**Subtitle:** From Design Thinking proxy validation to a working, evidence-based traffic simulation product in 12 weeks  
**Team:** Aziz Messaoud, Eya Laourine, Fares Ben Kacem, Mohamed Aymen Hamzaoui, Oumayma Saddouri, Ranim Ben Salem (ESPRIT 4DS)  
**Planned proxy-validation day:** Wednesday, 23 September 2026 (team ± professor; not stakeholder interviews)  
**Delivery window:** 23 September–15 December 2026  
**Status:** Design Thinking Stages 1–3 are complete as research-informed work; User Personas are not interview-validated; a working controlled Prototype and partial technical Test evidence are gated through Row 10c; multi-seed, stakeholder, and product-layer validation remain incomplete  
**Product:** A reliable AI decision platform for urban traffic simulation  
**Course challenge:** *How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?*

> [!IMPORTANT]
> This book is the professor-facing contract. Wednesday 23 September is **proxy validation**: the six builders walk User Personas, User Journeys, and Possible Solutions. It is not stakeholder interviews and does not establish deployment impact. Gated simulations now provide mixed one-seed evidence, not a performance-superiority claim. Numeric persona targets remain proposed acceptance criteria until their named evaluations and stakeholder validation are completed.

> [!IMPORTANT]
> ADR-0001, ADR-0002, and ADR-0003 govern implementation. Cooperative Max-Pressure is the required A1 controller. DQN is optional. Only A1 may write traffic signals. Synapse cannot access TraCI or actuate SUMO. Six people work as three pairs; only one sealed queue row is active. Course success is rows 01–09. Hosted API/UI is read-only over tagged evidence; Docker is not the native smoke test.

---

## How to use this book

1. **Before proxy validation:** read Chapters 1–8 and prepare the cards in Chapter 9.
2. **During proxy validation:** use the neutral questions and record disagreement, not only approval. Do not rewrite the Empathize pack that night.
3. **During implementation:** follow the sealed queue in `harness/queue.tsv` and ADR-0002 (one active row).
4. **During testing:** use Chapters 19–21 to collect reproducible evidence.
5. **Before submission:** use the definition of done and honesty checklist in Chapters 22–23.

The detailed source documents remain authoritative where this book summarizes them:

- [Course brief](docs/source/course-brief.md)
- [Empathize pack](coflow5-empathize-pack.md)
- [Define and Ideate record](coflow5-define-ideate.md)
- [Design Thinking record](.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md)
- [Canonical requirements](.kiro/specs/coflow5-reliable-agentic-platform/requirements.md)
- [Canonical design](.kiro/specs/coflow5-reliable-agentic-platform/design.md)
- [Canonical tasks](.kiro/specs/coflow5-reliable-agentic-platform/tasks.md)
- [Architecture decision ADR-0001](docs/adr/0001-reliable-ai-platform-boundary.md)
- [Delivery envelope ADR-0002](docs/adr/0002-six-builders-one-queue-row.md)
- [Later CI/CD ADR-0003](docs/adr/0003-cicd-devops-mlops.md)

---

# Part I — Understand the project

## 1. The project in simple words

Traffic lights usually focus on moving vehicles. Real streets include pedestrians, bus passengers, delivery drivers, emergency crews, residents, engineers, and incident operators. Their needs can conflict.

CoFlow-5 gives five domain agents different responsibilities, but it does **not** give all of them control of the lights:

- **A1 Flow** is the only authority that may change traffic signals.
- **A2 Emergency** requests safe emergency passage.
- **A3 Multimodal** represents pedestrians and conditional transit priority.
- **A4 Situation** forecasts traffic and warns about anomalies or missing information.
- **A5 Sustainability** advises about stop-and-go and local emission proxies.
- **Synapse** reads evidence and explains decisions. It is not a sixth controller.

The product must continue safely if advisers, messages, forecasting, retrieval, or an LLM fail.

## 2. The 5W1H

The requested “five Ws” are **Who, What, Where, When, and Why**. We add **How** so the project is actionable.

| Question | CoFlow-5 answer |
|---|---|
| **Who?** | Eight research-informed User Personas; six named builders (Aziz, Eya, Fares, Aymen, Oumayma, Ranim); a professor/reviewer. Wednesday’s walkthrough is proxy validation, not interviews with the personas. |
| **What?** | A reproducible SUMO prototype where five domain agents cooperate, only A1 writes lights, and every important decision is logged and testable. |
| **Where?** | First in a controlled 4×4 SUMO benchmark; later in a bounded Tunis OSM + official TRANSTU scheduled-GTFS showcase with synthetic/calibrated road demand clearly labelled. |
| **When?** | Proxy-validate assumptions on 23 September 2026; build and test over 12 weeks; freeze the reliable core before optional additions. |
| **Why?** | Average vehicle delay hides pedestrian safety, trip reliability, bus regularity, emergency externalities, local environmental displacement, and operational failure. |
| **How?** | Design Thinking → sealed requirements → native smoke test → evidence bundle → safety and baselines → cooperative Max-Pressure → typed requests → failure injection → paired evaluation → product interface. |

## 3. Five Whys root-cause analysis

**Observed problem:** urban signal control can report a good average while failing important people.

1. **Why can a good average still fail people?** Because pedestrians, transit, emergencies, residents, and operators have different outcomes that one average hides.
2. **Why are those outcomes hidden?** Because each need is often handled by a separate mechanism and their trade-offs are not recorded together.
3. **Why are trade-offs not recorded together?** Because there is no shared typed request, arbitration, reason-code, and evidence contract.
4. **Why is that dangerous?** Because agents, sensors, messages, controllers, and models can fail or become stale without a visible, deterministic response.
5. **Why does CoFlow-5 exist?** To make authority, safety, cooperation, evidence, and recovery explicit and testable before claiming intelligence.

**Root design need:** one safe authority must arbitrate bounded specialist advice and produce evidence that can be independently checked.

## 4. Product vision and boundaries

### 4.1 Vision

> CoFlow-5 Synapse is a reliable AI decision platform that makes simulated urban traffic decisions constrained, measurable, explainable, and recoverable when components fail.

### 4.2 What the product must be

- A working and reproducible SUMO prototype.
- A cooperative five-domain-agent design with one signal authority.
- A scientific comparison against fixed-time and actuated baselines.
- A failure-tested system with immutable evidence.
- A product that remains usable without a hosted LLM.

### 4.3 What the product must not become

- An LLM traffic-light controller.
- Five chatbots pretending to be traffic agents.
- A required reinforcement-learning project.
- A best-episode demonstration without fair baselines.
- A simulated result presented as field deployment evidence.

## 5. Three meanings of success

| Boundary | Required scope | What “done” means |
|---|---|---|
| **Course/reliability success** | Queue rows 01–09 | Reproducible scenario, evidence bundle, safety, baselines, Max-Pressure, A2/A3 requests, failure recovery, paired evaluation. |
| **Full portfolio product** | Queue rows 01–14 plus 10b/10c | Adds matched Max-Pressure trip KPIs, a deterministic evidence page, A4/A5, bounded Synapse agents, FastAPI, React view, and Tunis showcase. |
| **Optional experiment** | Queue row 15 | DQN uses the same safety/evaluation contract after the cooperative core freezes. It may remain unbuilt. |

Rows 01–09 and the new matched trip follow-up are never rewritten or cut. Approved order after Row 09: 10 -> 10b -> 10c -> 12 -> 11 -> 13 -> 14; Row 15 stays blocked. If time is lost, cut 15, 14, 13, then 11 before weakening deterministic evidence or control proof.

## 5.1 Chosen methodology spine

This is the **one** method CoFlow-5 uses. It is not a catalog of every multi-agent textbook.

| Layer | What it is | CoFlow-5 status |
|---|---|---|
| Design Thinking (IxDF) | Empathize → Define → Ideate → Prototype → Test | Stages 1–3 done as research-informed work. Stages 4–5 planned. |
| Sealed harness queue | One row, one contract, machine `gate.json` | Prototype/Test execute as rows 01–09, then 10 -> 10b -> 10c -> 12 -> 11 -> 13 -> 14; optional 15 stays blocked. |
| Data Science loop | Problem → success → data → EDA → prep → baseline → model → evaluation → error analysis → iteration → deployment → monitoring | Lives **inside** Prototype/Test, not instead of Design Thinking. |
| Course outcomes (`SUMO_forStudents`) | Working prototype, experiments, baseline comparison, honest limits | Evidence over complexity. Native Windows smoke test before Docker/WSL. |

Rejected as the chosen method: independent RL, LLM signal control, five conversational agents, and “best episode” reporting.

---

# Part II — Design Thinking

## 6. Design Thinking status

| Stage | Status before 23 September | Output | Next proof needed |
|---|---|---|---|
| **1. Empathize** | Complete as research-informed work | Personas, User Journeys, Evidence, Possible Solutions, Claim flags | Proxy-validate assumptions with the team ± professor; do not call it interviews. |
| **2. Define** | Complete | POV statements, human-centred problem, How-might-we questions | Check that the problem and priorities match real experiences. |
| **3. Ideate** | Complete | Divergent ideas, rejected ideas, decision comparison, chosen architecture | Test whether the solution concepts are understandable and acceptable. |
| **4. Prototype** | Planned | SUMO system and product interfaces | Build through sealed queue rows and produce artifacts. |
| **5. Test** | Planned | Baselines, ablations, fault tests, stakeholder and product evaluation | Run matched experiments and report strengths and limitations. |

Wednesday’s session is **proxy validation**. It does **not** turn any User Persona into an interview-validated person. It records who in the team (± professor) discussed which assumptions, what changed on correction cards, and what remains **Not tested**.

## 7. Empathize — the eight User Personas

These profiles are research-informed design tools. Ages and situations help the team reason about needs; they are not claims about interviewed individuals.

### 7.1 Amara — pedestrian accessibility

- **Profile:** 74, walks with a cane at an illustrative pace near 0.8 m/s.
- **Need:** enough time to finish crossing and tolerable waiting before the crossing begins.
- **Journey pain:** uncertain acknowledgement, fatigue while waiting, standard timing that may not fit her pace, and risk of conflicting traffic before she finishes.
- **Evidence basis:** perceived pedestrian wait can be about twice actual wait; frustration and non-compliance rise with long waits; published walking-speed guidance may not represent slower users.
- **Possible Solution:** A3 publishes waiting and active-crossing state; A1 preserves clearance through a deterministic mask.
- **Why this solution:** app-only access would exclude some people, while permanently long greens could starve other movements. Waiting and clearance need separate controls.
- **Validation question:** “Tell us about the last difficult crossing you experienced. What made it difficult before, during, and after crossing?”
- **Prototype evidence:** mean/P95/maximum wait and zero clearance truncations.

### 7.2 David — journey reliability

- **Profile:** 41, delivery driver with many time-sensitive stops.
- **Need:** predictable journeys, not only a lower average.
- **Journey pain:** repeated stops and one severe delay can break the rest of a route.
- **Evidence basis:** transport appraisal values variability; incidents form a material part of congestion; stop-and-go has operational and emission costs.
- **Possible Solution:** cooperative Max-Pressure uses queues and downstream capacity; evaluation reports tails and unfinished trips.
- **Why this solution:** average delay alone can look good while the worst trips become worse.
- **Validation question:** “When does unpredictability cause more harm than a journey that is consistently longer?”
- **Prototype evidence:** mean and P95 travel time, variability, stops, unfinished trips, and teleports.

### 7.3 Chidi — bus regularity

- **Profile:** 27, frequent bus passenger.
- **Need:** regular buses rather than a long gap followed by several buses.
- **Journey pain:** uncertain waiting, bunching, accumulated signal delay, and missed connections.
- **Evidence basis:** waiting is commonly valued more negatively than in-vehicle time; bus bunching is self-reinforcing; conditional signal priority has demonstrated feasibility.
- **Possible Solution:** A3 requests bounded priority only when lateness or a headway gap justifies it.
- **Why this solution:** unconditional bus priority can waste green time, worsen other traffic, and still fail to repair headways.
- **Validation question:** “What matters more in your experience: a faster bus once aboard, or knowing when the next bus will arrive?”
- **Prototype evidence:** lateness, headway variation, passenger-oriented wait, and externality to other traffic.

### 7.4 Rosa — explainable priority

- **Profile:** 52, bus depot controller.
- **Need:** understand why priority was accepted or rejected and intervene safely.
- **Journey pain:** scattered information, unexplained decisions, and missing history.
- **Evidence basis:** production traffic-control products include intervention and audit functions; no unsupported “engineer distrust percentage” is used.
- **Possible Solution:** reason-coded events, request dispositions, controller state, and a read-only explanation view.
- **Why this solution:** an attractive dashboard without immutable decision evidence cannot support accountability.
- **Validation question:** “What minimum information would let you explain a denied priority request to another operator?”
- **Prototype evidence:** reason-code coverage, event completeness, and an operator explanation task.

### 7.5 Marcus — emergency passage and recovery

- **Profile:** 34, paramedic.
- **Need:** useful safe passage through a corridor and controlled recovery afterwards.
- **Journey pain:** a green is useless when the exit is blocked; unsafe transitions threaten others; isolated preemption can move congestion downstream.
- **Evidence basis:** response delay matters, but simulation cannot establish lives saved; field preemption can improve response while imposing measurable delay on others.
- **Possible Solution:** A2 sends an authenticated, expiring corridor request with ETA, urgency, benefit, and civilian externality; A1 checks downstream space and active crossings.
- **Why this solution:** always-preempt designs hide externality and can grant a movement that has nowhere to go.
- **Validation question:** “What information must a signal system know before emergency priority would be useful rather than dangerous?”
- **Prototype evidence:** emergency travel effect, civilian delay, rejected unsafe requests, and recovery time—never lives saved.

### 7.6 Yuki — operational control

- **Profile:** 47, traffic engineer accountable for network operation.
- **Need:** diagnose, override, disable, and safely restore automation.
- **Journey pain:** silent degradation, stale information, unexplained actions, and unsafe takeover.
- **Evidence basis:** established adaptive systems provide fallback, intervention, and audit behavior.
- **Possible Solution:** one-writer authority, controller health, data freshness, safety-tested override, and deterministic recovery.
- **Why this solution:** prompts cannot enforce a safety boundary; capabilities and tests must enforce it.
- **Validation question:** “What would you need to see before switching an adaptive controller to a fallback mode?”
- **Prototype evidence:** correct fault detection, transition records, safe override, and complete decision history.

### 7.7 Maria — local environmental fairness

- **Profile:** 38, parent living near an arterial and walking to school.
- **Need:** improvements on the main road must not move queues and exhaust to her street.
- **Journey pain:** city-wide averages hide local stop-and-go and displacement near homes or schools.
- **Evidence basis:** many schools are located near major roads; SUMO/HBEFA outputs represent emission proxies, not measured exposure or air quality.
- **Possible Solution:** A5 publishes bounded eco advice; evaluation checks link-level proxy displacement near selected sensitive links.
- **Why this solution:** optimizing a network total can transfer harm spatially.
- **Validation question:** “Which locations and times would you check before believing that a traffic change helped your neighbourhood?”
- **Prototype evidence:** link-level proxy maps and displacement checks with explicit limitations.

### 7.8 Omar — trustworthy situation awareness

- **Profile:** 55, incident duty officer.
- **Need:** know what may be wrong, why the system thinks so, and whether data is trustworthy.
- **Journey pain:** false alarms, ambiguity between incidents and ordinary congestion, stale dashboards, and incomplete recovery.
- **Evidence basis:** incidents contribute materially to congestion; no universal incident-detection delay threshold is assumed.
- **Possible Solution:** A4 compares forecasts with observations, uses transparent residual detection, includes confidence and expiry, and distinguishes “no alert” from “insufficient data.”
- **Why this solution:** stale or missing observations must not be interpreted as clear roads.
- **Validation question:** “What evidence would make you investigate an alert, and what would make you ignore it?”
- **Prototype evidence:** forecast error, alert delay, false alerts, misses, stale-state handling, and recovery by severity.

## 8. Define and Ideate results

### 8.1 Human-centred problem statement

> Street users—pedestrians, drivers, bus riders, emergency crews, residents, and the people who run the network—need signal control that treats their different needs as first-class objectives with visible trade-offs, because separate mechanisms optimize vehicle throughput, hide who pays for whom, and can degrade silently when conditions or communication fail.

### 8.2 Refined How-might-we

> How might we use data and intelligent agents to make urban traffic efficient, adaptive, and sustainable for every person on the network—not only the average car—while making trade-offs auditable and preserving safe control when components fail?

### 8.3 Ideas considered

The team used Brainstorm/Brainwrite, Worst Possible Idea, SCAMPER, a morphological comparison, and a weighted decision comparison. The important value of these methods is not a score by itself; it is showing that alternatives were considered before choosing a technology.

| Alternative | Benefit | Main problem | Decision |
|---|---|---|---|
| Central AI or RL controller | Can use broad network state | Single failure point, hard to audit, training and safety risk | Rejected as required architecture. |
| Independent junction controllers | Simple and scalable | Weak coordination and specialist priority | Keep only as a comparator concept. |
| Five equal signal-writing agents | Represents multiple objectives | Conflicting commands and unclear responsibility | Rejected. |
| One deterministic authority plus advisers | Explicit authority, inspectable trade-offs, graceful failure | Requires careful message and evidence contracts | Chosen. |
| Hierarchical learned control | Potential regional coordination | Too expensive and risky for the schedule | Future research only. |

### 8.4 Worst ideas converted into principles

| Deliberately bad idea | Principle learned |
|---|---|
| Let an LLM set phases | Synapse is read-only and structurally separated from TraCI. |
| Give all agents write access | Exactly one writer exists for each signal. |
| Always grant emergency or bus priority | Requests are conditional, bounded, and externalities are recorded. |
| Optimize average delay only | Report tails, unfinished trips, stakeholder outcomes, and displacement. |
| Trust every message forever | Use TTL, confidence, schema validation, idempotency, and stale handling. |

### 8.5 Why the chosen idea fits beginner delivery

- Max-Pressure is understandable and does not require training.
- A2/A3/A5 can begin as transparent rules.
- The message board can run in one Python process.
- Every optional technology enters only after a simpler interface passes tests.
- The system remains academically useful even when a feature produces a null result.

---

# Part III — Proxy validation (Wednesday 23 September 2026)

Wednesday is a **proxy validation** walkthrough by the six builders, optionally with the professor. It is not stakeholder interviews. The six students are not Amara, David, or Marcus.

## 9. Proxy-validation objective and boundaries

### 9.1 What tomorrow can proxy-validate

- Whether the needs and journeys sound accurate or incomplete.
- Whether the human-centred problem is understandable.
- Whether Possible Solutions address the pain described.
- Whether the priority order creates unacceptable conflicts.
- Whether the architecture and explanation concept make sense to participants.

### 9.2 What tomorrow cannot validate

- Traffic-performance improvement before simulation.
- Safety correctness before tests.
- Air-quality improvement from an interview or HBEFA proxy.
- Lives saved from simulated emergency travel time.
- Statistical representativeness from a small convenience sample.
- Deployment readiness.

### 9.3 Who is in the room

The six builders. A professor may join. Direct lived-experience stakeholders are **not** scheduled. Label every sheet **proxy**. Do not invent quotes. Do not code a teammate as `V-PED-01` “Amara.”

## 10. Named proxy-validation roles

| Person | Wednesday’s role | Deliverable |
|---|---|---|
| **Aziz Messaoud** | Facilitator and timekeeper | Keeps questions neutral and session on time. |
| **Eya Laourine** | Consent and note lead | Records who spoke, exact concern, and uncertainty. |
| **Ranim Ben Salem** | Persona and User Journey presenter | Shows cards without defending them. |
| **Oumayma Saddouri** | Possible Solution and architecture cards | Walks the shared scenario and one-writer diagram. SUMO is not run. |
| **Fares Ben Kacem** | Skeptic and Claim-flag checker | Stops leading questions and unsupported interpretations. |
| **Mohamed Aymen Hamzaoui** | Synthesis and decision recorder | Keep / revise / remove / test later. |

Everyone listens. Nobody argues to “win approval.” The only prototype in the room is cards plus the architecture diagram.

## 11. Preparation checklist for tonight

- Print or export the eight canvases from [personas-canvas.html](docs/presentation/personas-canvas.html).
- Prepare one problem card, one architecture card, and five agent cards. These are Possible Solutions, not a built system.
- Prepare the shared journey: ambulance approaches while Amara is crossing, a late bus arrives, queues grow near Maria’s school street, and communication fails.
- Create one Appendix A sheet per builder plus one for a professor if present.
- Open the existing [Design Thinking presentation](docs/presentation/CoFlow-5-Synapse-DT-4DS.pptx) and [professor design note](docs/presentation/system-design-for-professor.md).
- Rehearse the introduction once: “We are testing our assumptions. User Personas are research-informed. SUMO is not built.”
- **30-minute fallback:** unprompted experience, one relevant User Persona, shared scenario, one failure question, ranking. Do not rush all eight personas.

## 12. Two-hour proxy-validation workshop

| Time | Activity | Neutral prompt | Output |
|---|---|---|---|
| 0–10 min | Welcome, consent, boundaries | “We are testing our assumptions, not testing you.” | Participant code and consent status. |
| 10–25 min | Experience first | “Tell us about a recent traffic experience relevant to you.” | Unprompted needs and pain points. |
| 25–50 min | Persona and User Journey review | “What feels accurate, missing, exaggerated, or wrong?” | Corrections by persona/journey stage. |
| 50–65 min | Define validation | “How would you describe the real problem in your own words?” | Revised problem language and priorities. |
| 65–85 min | Possible Solution cards | “Which response helps? What new harm might it create?” | Keep/revise/remove and trade-offs. |
| 85–100 min | Shared conflict scenario | “Who should be protected first, and what information is missing?” | Priority and information requirements. |
| 100–110 min | Failure scenario | “What should happen if messages, forecasts, or explanations stop?” | Recovery and trust expectations. |
| 110–120 min | Ranking and close | “Choose the three needs we must prove first.” | Ranked needs and follow-up permission. |

For a 30-minute individual session, use experience first, one relevant persona, the shared scenario, one failure question, and final ranking. Do not rush through all eight personas with every individual.

## 13. Validation questions

### 13.1 Experience and need

1. Tell us about the last time this traffic problem affected you.
2. What was the hardest moment, and why?
3. What information or action was missing?
4. What did you do to cope?
5. Which outcome matters more than average travel time?

### 13.2 Solution and trade-off

1. What part of this Possible Solution would help?
2. What part would you not trust?
3. Who might be harmed when this person receives priority?
4. What should never be automated?
5. What evidence would convince you the system worked?

### 13.3 Avoid leading questions

Do not ask: “Do you like our five-agent AI solution?”  
Ask: “How would you expect the system to respond here, and why?”

Do not ask: “Is our safety rule good?”  
Ask: “What must never happen during this crossing?”

Do not ask: “Would an explanation increase trust?”  
Ask: “What would you need to know before accepting this decision?”

## 14. Validation decision rules

Use qualitative evidence honestly. A small session discovers problems; it does not estimate population percentages.

| Status | Meaning | Team action |
|---|---|---|
| **Green—supported** | Multiple independent observations, or a relevant domain participant plus existing Evidence, support the need without a critical contradiction. | Keep wording; still test in Prototype/Test. |
| **Amber—uncertain** | Feedback is mixed, access is indirect, or important information is missing. | Revise the assumption and schedule a targeted test. |
| **Red—contradicted/risky** | A safety concern, misunderstood need, or serious unintended consequence appears. | Stop that solution path and reopen the relevant requirement before implementation. |
| **Not tested** | No suitable participant or activity addressed the assumption. | Keep it explicitly unvalidated. |

Architecture locks such as one writer and non-actuating Synapse are safety/product decisions. Proxy validation may improve interfaces and needs, but changing those locks requires a formal ADR—not a workshop vote.

## 15. End-of-day proxy-validation outputs

The Empathize pack body is **frozen** tonight. Corrections live on cards.

1. Register of the six builders (± professor), method = **proxy validation**.
2. Assumption log with Green/Amber/Red/**Not tested**.
3. Persona and User Journey correction cards without invented quotes.
4. Possible Solution decisions: keep, revise, remove, or test later.
5. A dated proxy-validation summary listing limitations. n = team (± professor). Any undiscussed persona is **Not tested**.

Do not mark Empathize interview-validated. Do not run SUMO.

---

# Part IV — System design

## 16. Architecture and authority

```text
Eclipse SUMO
     |
     v
Observation Adapter -----> typed observations --------------------+
     |                                                             |
     +----> A1 Flow                                                 |
     +----> A2 Emergency ---- request ------------------+           |
     +----> A3 Multimodal -- request/state ------------+           |
     +----> A4 Situation ---- forecast/alert ----------+           |
     +----> A5 Sustainability - eco advice ------------+           |
                                                        v           |
                                                Typed Message Board |
                                                        |           |
                                                        +----> A1 --+
                                                               |
                                                               v
                                                    Deterministic Safety Mask
                                                               |
                                                               v
                                                     A1 Signal Executor
                                                               |
                                                               v
                                                         Eclipse SUMO

Messages + decisions + faults + trips ---> Run Evidence Bundle
Run Evidence Bundle --------------------> Evaluation / API / Synapse
Approved documents ---------------------> Retrieval ------> Synapse
Synapse verified answer ----------------> API ------------> React UI
```

### 16.1 Capability rules

| Component | May do | Must not do |
|---|---|---|
| Observation adapter | Read SUMO through TraCI/libsumo and create typed observations | Choose traffic policy. |
| A1 controller/executor | Arbitrate and execute safety-approved signal commands | Accept LLM text as a command or bypass the mask. |
| A2–A5 | Read approved observations and publish typed advice | Import TraCI/libsumo or access the signal executor. |
| Evidence/evaluation | Read immutable artifacts and calculate results | Actuate signals. |
| Synapse/API/UI | Read approved evidence and retrieval interfaces | Reach TraCI, mutate active state, or mint replacement evidence IDs. |

One A1 executor may exist per controlled junction, and executors may share controller code. “One writer” means exactly one authorized writer for each signal, under the single A1 authority.

### 16.2 Multi-agent patterns — keep, optional, reject

Source: the Ideate pattern inventory, interpreted under ADR-0001. Micro = one junction, one decision epoch. Macro = the network and five-agent society. CoFlow-5 trades optimality for auditability, safety, and graceful degradation.

| ID | Pattern | Decision | Limitation (what can fail) | Trade-off |
|---|---|---|---|---|
| P-1 | Single actuation authority | **Keep.** Only A1 writes signals. | A1 is a single point of failure per junction. | Safety/accountability vs an adviser never being able to fix a bad A1 choice except by asking. |
| P-2 | Deterministic safety mask | **Keep.** | A mask is only as good as the junction conflict model. | Restrictiveness vs remaining legal under failure. |
| P-3 | Blackboard / pub-sub | **Keep.** In-process first. | Forecast–action feedback loops; hard to see who used a message unless IDs are logged. | Loose coupling vs causal accountability. |
| P-4 | Contract-net request/reply | **Keep** for A2/A3. | Request values are estimates; one round in 5–10 s bounds how many claims fit. | Explicit negotiation vs decision latency. |
| P-5 | Bid-based arbitration | **Keep** inside priority tiers. | Externality estimates are wrong at spillback; bids can inflate. | Explainability vs global optimality. An auction is not claimed optimal. |
| P-6 | Shared-policy MARL | **Optional** row 15. Not Core A1. | Heterogeneous junctions; correlated failure if one policy is wrong everywhere. | Sample efficiency vs per-junction fit. |
| P-7 | Hierarchical timescales | **Keep.** A1 in seconds; advisers slower. | Timescale boundary creates staleness. | Reactivity vs anticipation. |
| P-8 | Watchdog recovery ladder | **Keep.** Required path: cooperative Max-Pressure → actuated → fixed-time. Optional DQN, if ever enabled, fails into Max-Pressure first. | Triggers on symptoms, not slow well-formed degradation; network-wide synchronized fallback is itself a shock. | Responsiveness vs false fallbacks. |
| P-9 | Heartbeat / TTL / stale handling | **Keep.** | A frozen dashboard can look normal. | Trust vs pretending missing data is “clear.” |
| P-10 | LLM as explainer | **Keep as Synapse layer.** Reject as controller. | Fluent wrong reasons are worse than terse true ones. | Interpretability vs faithfulness. |

**Rejected:** LLM signal write; five conversational agents; independent RL with no one-writer rule; throughput-only optimization; RoadwayVR as a runtime dependency.

Priority tiers above any auction: person already crossing → emergency → pedestrian deadline → late bus → general flow → eco.

## 17. How the agents communicate

### 17.1 Decision loop

1. SUMO advances by one simulation step.
2. The adapter creates stable observations.
3. A2–A5 publish bounded messages when they have relevant evidence.
4. A1 reads messages valid at the current simulation time.
5. Duplicate, expired, malformed, unsupported, contradictory, or out-of-order messages receive a recorded disposition.
6. A1 considers local pressure, downstream space, phase timing, legal actions, and valid requests.
7. A1 applies the settled priority tiers and same-tier benefit/externality comparison.
8. The safety mask accepts or rejects the proposal.
9. The executor writes only an accepted action and creates an immutable decision event.

### 17.2 Message envelope

```text
MessageEnvelope
  run_id
  scenario_hash
  message_id
  correlation_id
  source_agent
  destination_or_topic
  created_at
  simulation_time
  expires_at
  priority_class
  confidence
  schema_version
  payload_type
  payload
  provenance
```

Required topics are `state`, `forecast`, `alerts`, `eco`, `requests`, `replies`, and `health`.

The first board is in-process and transport-independent. Redis is permitted only after a demonstrated split-process requirement and must not change agent logic.

### 17.3 Priority order

```text
1. Active safety or a pedestrian already crossing
2. Emergency
3. Pedestrian waiting deadline
4. Conditional late transit
5. General flow
6. Sustainability
```

Within one tier, A1 compares documented benefit and externality. Every accepted, rejected, or deferred request references its original `message_id` and records a reason code.

### 17.4 Important edge cases

| Situation | Required behavior |
|---|---|
| Emergency arrives while a pedestrian is crossing | Finish the pedestrian clearance before granting a conflicting emergency movement. |
| Two emergency requests conflict | Use a deterministic rule and record both outcomes. |
| Late bus conflicts with a pedestrian deadline | The pedestrian deadline wins. |
| A4 is silent or stale | Mark forecasting unavailable and continue local Max-Pressure. |
| A5 requests an eco phase during spillback | Reject or defer it with a reason code. |
| A human override is unsafe | Reject it through the same safety mask. |
| Synapse or the LLM dies | Traffic actions remain unchanged. |

## 18. Safety and recovery

The required recovery ladder is:

```text
COOPERATIVE_MAX_PRESSURE
          -> ACTUATED
          -> FIXED_TIME
```

If optional DQN is later enabled:

```text
OPTIONAL_DQN
          -> COOPERATIVE_MAX_PRESSURE
          -> ACTUATED
          -> FIXED_TIME
```

Controller failure triggers can include invalid output, missed decision deadline, unavailable controller, repeated rejected actions, corrupt observations, and planned fault injection. Adviser failure normally removes that adviser’s input; it does not stop healthy local Max-Pressure.

Every transition records previous mode, next mode, trigger, simulation time, and health evidence.

---

# Part V — Requirements and outputs

## 19. Full requirement set

### 19.1 Foundation

| ID | Requirement |
|---|---|
| R0 | Preserve Design Thinking traceability and the eight User Personas. |
| R1 | Produce a working prototype, experiments, baselines, and honest strengths/limitations. |
| R2 | Make runs reproducible with versions, hashes, seeds, status, timing, and artifacts. |
| R3 | Enforce one-writer authority and deterministic signal safety. |

### 19.2 Cooperation

| ID | Requirement |
|---|---|
| R4 | Use cooperative Max-Pressure as required A1 control and operate without RL. |
| R5 | Use typed, expiring, confidence-tagged, idempotent messages with dispositions. |
| R6 | Provide safe emergency requests, downstream checks, arbitration, and recovery. |
| R7 | Protect pedestrian clearance and provide conditional late-transit priority. |

### 19.3 Intelligence and evidence

| ID | Requirement |
|---|---|
| R8 | Provide bounded A4 situation and A5 sustainability advice with limitations. |
| R9 | Demonstrate deterministic failure recovery and unchanged control when Synapse fails. |
| R10 | Run paired evaluation, ablations, failure sweeps, tails, and error classification. |
| R11 | Define data schemas, chronological ML splits, transformations, sources, and limitations. |

### 19.4 Product and delivery

| ID | Requirement |
|---|---|
| R12 | Ground Synapse answers in immutable events and allow-listed policy, with template/abstention. |
| R13 | Expose typed API and operator views for runs, evidence, explanations, and bounded what-if work. |
| R14 | Join traces, version configurations, protect credentials, and regression-test changes. |
| R15 | Protect the three critical workstreams and cut optional complexity before rigor. |

The full acceptance wording remains in [requirements.md](.kiro/specs/coflow5-reliable-agentic-platform/requirements.md).

## 20. Product outputs

### 20.1 Per-run evidence

```text
RunManifest
  run_id
  status
  created_at / started_at / finished_at
  source_revision
  SUMO_version
  scenario_hash
  configuration_hash
  controller_name / version
  model_versions
  seeds
  fault_schedule_hash
  timings
  artifact_references
  invalidation_reason
```

High-volume state, message, decision, trip, forecast, fault, transition, and KPI records use compact Parquet artifacts. DuckDB reads them for analysis. Every reported KPI resolves to one valid manifest.

### 20.2 Identity contract

- `run_id`: one execution context.
- `scenario_hash`: identity of frozen scenario inputs.
- `configuration_hash`: controller, demand, and fault configuration.
- `event_id`: immutable decision, fault, transition, or explanation target.
- `message_id`: immutable advisory publication and disposition reference.

No API, UI, trace, RAG, or report layer may invent a replacement identity.

### 20.3 Stakeholder and system metrics

| Area | Required measures |
|---|---|
| Safety | Conflicting greens, clearance truncations, rejected illegal actions. |
| Flow/reliability | Mean/P95 travel time and delay, variability, queues, stops, unfinished trips, teleports. |
| Specialists | Emergency travel and civilian delay; pedestrian waits; transit headway/lateness; link-level emission proxies. |
| Reliability | Message and controller faults, mode transitions, recovery, reproducibility. |
| Synapse/product | Retrieval recall, citation validity, event consistency, abstention, latency, cost, fallback. |

### 20.4 Operator product

The stable product capabilities are:

- create and cancel a bounded scenario run;
- read run status, manifest, events, and comparisons;
- inspect controller mode, messages, requests, decisions, and reason codes;
- request a cited explanation or receive a template/abstention;
- draft and approve a bounded what-if request.

The hosted React interface reads precomputed SUMO evidence. Continuous cloud simulation or training is not promised.

## 21. Testing and honesty contract

### 21.1 Test layers

1. Schema and deterministic property tests.
2. Frozen single-junction integration tests.
3. Controller, safety, and cooperation acceptance tests.
4. Message, adviser, controller, retrieval, provider, and Synapse fault tests.
5. Paired scenario evaluation and explanation golden tests.

### 21.2 Required reliability demonstration

- Kill Synapse: the same Control-plane inputs produce the same actions.
- Drop all adviser messages: local Max-Pressure continues.
- Silence A4: forecast state becomes unavailable, not “normal.”
- Fail Max-Pressure: actuated and fixed-time recovery become visible.
- Remove retrieval or fail the provider: return a template, structured facts, or abstention.

### 21.3 Claims that remain forbidden

- No lives-saved claim from simulated emergency time.
- No measured-air-quality claim from SUMO/HBEFA.
- No invented interview quote or interview count.
- No best-training-episode headline.
- No P95 that silently drops unfinished or teleported trips.
- No claim that a proposed target has already been achieved.

---

# Part VI — Six beginners delivering in three months

## 22. Team operating model

Six named beginners work as three pairs. Only one sealed queue row is active (ADR-0002).

| Pair | People | Primary learning area | Typical ownership |
|---|---|---|---|
| **Pair A — Control** | Aziz Messaoud, Fares Ben Kacem | SUMO, observations, A1, safety, controllers | Rows 01, 03, 04, 05, and recovery support. |
| **Pair B — Data/Evaluation** | Mohamed Aymen Hamzaoui, Oumayma Saddouri | scenarios, manifests, Parquet, DuckDB, KPIs | Rows 02, 08, 09, later A4/A5 evidence, Tunis data. |
| **Pair C — Cooperation/Product** | Eya Laourine, Ranim Ben Salem | messages, A2/A3, later API, Synapse, UI | Rows 06, 07, 11, 12, 13. |

This is expertise ownership, not permission to create silos. For each active row:

- one pair drives implementation;
- one pair writes/runs independent tests and checks joins;
- one pair prepares reproduction notes, demo evidence, and beginner explanation;
- roles rotate so every member builds, tests, and explains;
- only machine tests and files can pass a row.

Emails: aziz.messaoud@esprit.tn, eya.laourine@esprit.tn, fares.benkacem@esprit.tn, mohamedaymen.hamzaoui@esprit.tn, oumayma.saddouri@esprit.tn, ranim.bensalem@esprit.tn.

## 23. Beginner learning path

### Month 1 skills

- Git branches, small commits, pull-request review, and safe merge habits.
- Python 3.11 virtual environments, typing, dataclasses/Pydantic, and pytest.
- SUMO networks, routes, phases, TraCI/libsumo, seeds, and outputs.
- JSON manifests, hashes, Parquet, DuckDB, and simple descriptive statistics.
- Safety invariants and why baselines come before AI models.

### Month 2 skills

- Max-Pressure, phase-transition masks, and failure-state machines.
- Typed messages, TTL, idempotency, reason codes, and fault injection.
- Paired experimental design, ablation, tails, and honest null results.
- FastAPI contracts and read-only evidence access.
- A4 forecasting only after persistence and simple baselines.

### Month 3 skills

- Retrieval provenance, citations, deterministic verification, and abstention.
- React views over stable API schemas and precomputed artifacts.
- Golden evaluation cases, traces, latency, and cost.
- Reproducible demo packaging and limitations writing.
- Presenting team results separately from individual contributions.

## 24. Weekly working rhythm

Capacity assumption to confirm tomorrow: **6–8 hours per person per week** outside class. If the actual capacity is lower, protect rows 01–09 and cut optional product polish.

- **Three 15-minute check-ins per week:** blocker, current row, next test.
- **One 90-minute paired build session:** implement only the active row.
- **One 60-minute gate/review session:** another pair reproduces tests and artifacts.
- **One 45-minute learning session:** the driver explains the row in beginner language.
- **One integration rule:** no later-row feature merges before the current row gates.

## 25. Twelve-week implementation plan

### Week 1 — 23–29 September: validate and unblock

**Active target:** validation plus row 01.

- Run the Design Thinking validation and record corrections.
- Install native Python 3.11.9; keep native SUMO 1.27.1.
- Create the controlled minimal scenario required by the row 01 contract.
- Measure TraCI/libsumo throughput, memory, and artifact bytes.
- Pass the two named tests and create `gate.json` only after all artifacts exist.

**Win:** another team member can run the native smoke test from one documented command.

### Week 2 — 30 September–6 October: establish product truth

**Active target:** row 02 evidence bundle.

- Define run/scenario/configuration identities and status transitions.
- Produce the manifest and compact analytical artifacts.
- Query one complete run with DuckDB.
- Detect missing/corrupt artifacts and invalidate the run.
- Explain the full evidence chain to all six members.

**Win:** one frozen run has one trustworthy evidence bundle.

### Week 3 — 7–13 October: protect the signal boundary

**Active target:** row 03 safety mask.

- Isolate SUMO reads and writes behind the adapter.
- Give only the A1 executor the signal-write capability.
- Encode legal transitions, minimum green, yellow/all-red, and pedestrian clearance.
- Generate reason-coded rejections for illegal proposals.
- Run forbidden-import and safety-property tests.

**Win:** proposed illegal actions never become executed commands.

### Week 4 — 14–20 October: build fair baselines

**Active target:** row 04.

- Implement fixed-time and actuated control.
- Freeze matched scenarios and seeds.
- Record unfinished trips, teleports, standstills, and tails.
- Verify both controllers use identical evidence contracts.
- Produce the first honest comparison table.

**Win:** the project has credible baselines before claiming intelligence.

### Week 5 — 21–27 October: required cooperative control

**Active target:** row 05.

- Implement local/cooperative pressure scoring and downstream blocking.
- Consider only legal candidate actions.
- Record selected action, alternatives, and reason codes.
- Run Max-Pressure with an empty message board.
- Compare it with fixed-time and actuated on matched seeds.

**Win:** required A1 works without any specialist or learned controller.

### Week 6 — 28 October–3 November: typed communication

**Active target:** row 06.

- Implement `MessageEnvelope` and domain payload schemas.
- Implement publish/read, TTL, idempotency, bounded storage, and dispositions.
- Add malformed, duplicate, expired, contradictory, and empty-board tests.
- Keep the transport behind an interface.
- Demonstrate that A1 continues without the board.

**Win:** cooperation is inspectable and cannot stop local control.

### Week 7 — 4–10 November: human-centred specialists

**Active target:** row 07.

- Implement A2 expiring emergency corridor requests.
- Implement A3 crossing state, waiting deadline, and conditional transit request.
- Test downstream blockage, active crossing, two emergencies, and early bus cases.
- Record accepted/rejected request IDs and externalities.
- Map outputs back to Amara, Chidi, Marcus, and Rosa.

**Win:** A2/A3 ask; only A1 acts; critical edge cases are visible.

### Week 8 — 11–17 November: break the system on purpose

**Active target:** row 08.

- Inject message loss, delay, duplication, expiry, and malformed payloads.
- Silence advisers and A4 placeholders.
- Fail Max-Pressure and observe actuated/fixed recovery.
- Kill Synapse or its placeholder process and compare action sequences.
- Record all mode transitions and failures.

**Win:** the system degrades safely instead of freezing or hiding failure.

### Week 9 — 18–24 November: evaluate and freeze the core

**Active target:** row 09.

- Build matched experiment cells across controller, demand, incidents, faults, and seeds.
- Run A2/A3 on/off ablations.
- Report safety, efficiency, emergency, pedestrian, transit, and robustness metrics.
- Preserve null/negative results and classify failure types.
- Freeze the rows 01–09 reliability slice.

**Win:** the minimum course product is reproducible and professor-verifiable.

### Week 10 — 25 November–1 December: complete advice and matched evidence

**Sequential targets:** row 10, then 10b, then 10c; each starts only after the prior gate passes.

- Gate A4 persistence/simple-baseline forecasting, EWMA/CUSUM detection, and stale/silent behavior.
- Gate deterministic A5 emission-proxy advice and displacement reporting.
- Add matched Max-Pressure `trips.parquet` and `run_kpis.parquet` without changing locked Row 05.
- Build the deterministic real-run English page with trip KPIs, requests, reason codes, safety, and limits.

**Win:** advice and all three matched controllers have professor-verifiable evidence before explanation.

### Week 11 — 2–8 December: bounded explanations, then product views

**Sequential targets:** row 12, then row 11, then row 13; each starts only after the prior gate passes.

- Build allow-listed retrieval with pinned `all-MiniLM-L6-v2`, stable chunks, provenance, and local search.
- Bound shared `Qwen/Qwen2.5-1.5B-Instruct` roles: S1 plans and waits, S2 explains frozen evidence, and S3 audits or abstains.
- Keep deterministic templates available and prove that killing Synapse cannot change traffic actions.
- Add the read-only FastAPI over frozen evidence, then the React precomputed-evidence view.

**Win:** a reviewer can inspect one event, its reason, supporting policy, comparison, and limitation without giving an LLM signal authority.

### Week 12 — 9–15 December: showcase and submission

**Target:** row 14 if capacity permits, followed by final verification.

- Import a bounded Tunis OSM network and version the source.
- Import official TRANSTU scheduled GTFS and label it correctly.
- Use clearly labelled synthetic/calibrated road demand.
- Keep the controlled grid as the scientific benchmark.
- Re-run critical tests, prepare the reliability demo, report, and contribution statements.

**Win:** a polished local showcase is added without replacing controlled evidence. If row 14 cannot gate, present it as future work and keep rows 01–09 evidence complete.

Row 15 DQN is deliberately absent from this 12-week critical plan.

## 26. Weekly definition of ready and done

### Ready to start a row

- The previous row has a passing, hash-bound gate.
- The active contract has been read by all six members.
- Inputs, tests, and expected artifacts are understood.
- A driver pair, verifier pair, and evidence pair are assigned.
- No unresolved human decision is being guessed.

### Done with a row

- Contract hash matches the gate.
- Every named test exits zero.
- Every required artifact exists and parses.
- Applicable identities and joins resolve.
- Forbidden-import, schema, and safety checks pass.
- `openDeltas` is zero and `decidedBy` is `tests-and-files`.

A student, pair, or chat response cannot declare a row done.

## 27. Risk register and cuts

| Risk and observable trigger | Response |
|---|---|
| Native toolchain missing or inconsistent | Stop in `harness/BLOCKED`; fix row 01 before adding libraries. |
| Simulation throughput/storage fails the measured budget | Reduce observation/log frequency or scenario size; keep safety and paired evaluation. |
| A feature fails to improve its intended KPI | Report the null result and cut the feature if it adds risk. |
| Message/forecast complexity delays the core | Keep the in-process board and deterministic advisers; do not add Redis. |
| Dashboard, RAG, or LLM distracts from experiments | Cut rows 13/12/11 before any row 01–09 requirement. |
| Team skill gap creates one-person ownership | Pair, rotate verifier duties, require reproduction by another member. |
| Tunis data is incomplete or unrealistic | Label limits and retain the controlled grid as the only primary comparison. |
| Evidence or participant feedback contradicts a claim | Correct the book and requirement; do not defend a preferred feature. |

Do not reduce seed count merely to obtain significance. Use pilot variance and report uncertainty.

---

# Part VII — Final presentation and verification

## 28. Professor demonstration

A short reliability-first demonstration should show:

1. Start one frozen scenario and display its manifest and IDs.
2. Show fixed-time, actuated, and Max-Pressure comparisons on matched evidence.
3. Show one A2/A3 request, A1 disposition, safety decision, and reason code.
4. Drop messages and fail the controller to make recovery visible.
5. Kill Synapse, show unchanged traffic actions, then retrieve a template/cited explanation from evidence.

The headline is not “AI improved traffic by X%” unless valid final evidence supports it. The stronger headline is: **authority, evidence, failure, and trade-offs are measurable.**

## 29. Final submission package

- This final project book with validation results appended.
- Reproduction instructions and pinned environment.
- Architecture and authority-boundary diagram.
- Selected valid run evidence bundles.
- Evaluation report with baselines, ablations, faults, and limitations.
- A 90-second reliability demo or live equivalent.
- Team result and separate individual-contribution pages.
- Future-work list containing optional DQN and any cut rows.

## 30. Final definition of product success

### Minimum reliable product

Rows 01–09 pass their machine gates and demonstrate:

- one safe signal writer;
- fixed-time, actuated, and cooperative Max-Pressure;
- bounded A2/A3 cooperation;
- deterministic recovery and fault evidence;
- paired, honest, stakeholder-aware evaluation.

### Full portfolio target

Rows 10, 10b, 10c, 12, 11, 13, and 14 additionally provide bounded A4/A5 advice, matched Max-Pressure trip KPIs, a deterministic evidence page, three bounded Synapse roles, FastAPI, React evidence views, and a correctly labelled Tunis showcase.

### Optional research

DQN may be evaluated only after feature freeze. Max-Pressure matching or beating DQN is an acceptable result. The required product must still pass if DQN is never started.

---

# Appendix A — Proxy-validation templates (23 September 2026)

Builders are **not** recorded as the User Personas they present.

## A0. Team register (proxy session)

| Name | Email | Wednesday role |
|---|---|---|
| Aziz Messaoud | aziz.messaoud@esprit.tn | Facilitator |
| Eya Laourine | eya.laourine@esprit.tn | Notes |
| Ranim Ben Salem | ranim.bensalem@esprit.tn | Persona cards |
| Oumayma Saddouri | oumayma.saddouri@esprit.tn | Possible Solution / architecture cards |
| Fares Ben Kacem | fares.benkacem@esprit.tn | Skeptic / Claim flags |
| Mohamed Aymen Hamzaoui | mohamedaymen.hamzaoui@esprit.tn | Keep/revise/remove board |
| Professor (if present) |  | Observer; still proxy, not an interviewed User Persona |

Method: **proxy validation**. n = 6 team (± 1 professor). SUMO is not run.

## A1. Participant/session record

```text
Date/time:
Participant code:
Relevant experience/role (broad, non-identifying):
Direct stakeholder or proxy participant:
Consent to notes: yes / no
Consent to anonymous quotation: yes / no
Facilitator:
Note taker:
Limitations:
```

## A2. Assumption card

```text
Assumption ID:
Persona or HMW:
We currently believe:
Existing Evidence supporting it:
What would contradict it:
Neutral question/activity:
Participant observation (no interpretation yet):
Status: Green / Amber / Red / Not tested
Decision: Keep / Revise / Remove / Test later
Requirement or artifact affected:
Owner and due date:
```

## A3. Persona correction card

```text
Persona:
Journey stage discussed:
What seemed accurate:
What was missing:
What seemed wrong or exaggerated:
Participant's priority in their own words:
Possible Solution concern:
Team interpretation:
Follow-up evidence needed:
```

## A4. Validation summary

```text
Session date: 23 September 2026
Method: proxy validation
Number and types of sessions:
Direct stakeholder participants: 0 (not scheduled)
Proxy participants: six builders ± professor
Needs supported:
Needs revised:
Needs contradicted:
Possible Solutions revised or removed:
Safety/authority concerns:
New assumptions:
Not-tested assumptions (any undiscussed User Persona):
Requirement-change proposals:
Known limitations: team is not the people the User Personas describe; Empathize pack body not rewritten tonight
Decision approvers:
```

## A5. Proxy-validation decision board

| Assumption | Persona/HMW | Method | Status | Keep/revise/remove/test later | Owner |
|---|---|---|---|---|---|
| Crossing wait and clearance are separate needs | Amara | Card walkthrough (proxy) |  |  | Ranim |
| Reliability matters beyond mean time | David | Experience + ranking (proxy) |  |  | Ranim |
| Regularity matters beyond bus speed | Chidi | Journey trade-off (proxy) |  |  | Ranim |
| Reason codes support accountable intervention | Rosa/Yuki | Decision walkthrough (proxy) |  |  | Fares |
| Priority must include downstream space and recovery | Marcus | Shared scenario (proxy) |  |  | Oumayma |
| Local displacement must be visible | Maria | Map review (proxy) |  |  | Oumayma |
| “Unknown” must differ from “clear” | Omar | Failure tabletop (proxy) |  |  | Fares |
| One writer plus advisers is understandable | All | Architecture card (proxy) |  |  | Aziz |

---

# Appendix B — Core schemas in beginner language

## B1. Observation

“What SUMO currently says is happening”: queues, occupancy, current phase, elapsed phase time, pedestrian/transit/emergency presence, downstream space, waits, and data freshness.

## B2. Message

“What a specialist says A1 should consider”: source, time, expiry, confidence, request/advice type, evidence, expected benefit, and externality.

## B3. Decision event

“What A1 considered and did”: legal alternatives, message IDs, selected action, rejected requests, constraints, reason code, controller mode, and executed command.

## B4. Explanation

“What the operator sees”: immutable event facts, cited policy support, known limitations, and a clear fallback or abstention when support is missing.

---

# Appendix C — Glossary

| Term | Meaning |
|---|---|
| **Ablation** | Run the same experiment with one agent/feature off to test whether it adds value. |
| **Actuated control** | Rule-based signals responding to detected demand. |
| **Claim flag** | A statement the project must not make without valid evidence. |
| **Confidence interval** | A range describing uncertainty in an estimated difference. |
| **Control plane** | The safety-critical code that observes SUMO and executes legal actions. |
| **Cooperative Max-Pressure** | Required controller using queue pressure, downstream conditions, and bounded valid requests. |
| **Evidence bundle** | Manifest and artifacts that make one run reproducible and auditable. |
| **Idempotency** | Processing the same message/request again does not create a second effect. |
| **Join key** | Identifier used to connect records without guessing, such as `run_id`. |
| **Paired seeds** | Controllers run on matched random scenarios so differences are fairer. |
| **Proxy validation** | Team or professor walkthrough of research-informed User Personas; not an interview with the person the profile describes. |
| **Parquet/DuckDB** | Compact analytical files and a local query engine used for experiment evidence. |
| **Reason code** | Structured explanation for accepting, rejecting, deferring, or recovering. |
| **Synapse** | Non-actuating layer that retrieves evidence and explains immutable decisions. |
| **TTL** | Time-to-live; after expiry, a message cannot influence a later decision. |
| **User Persona** | Research-informed stakeholder profile, not automatically an interviewed person. |

---

# Appendix D — Evidence and authority map

| Need | Primary source file |
|---|---|
| Course authority | [`docs/source/course-brief.md`](docs/source/course-brief.md) |
| User Personas, User Journeys, Evidence, Possible Solutions | [`coflow5-empathize-pack.md`](coflow5-empathize-pack.md) |
| POV, HMW, ideation methods, chosen/rejected ideas | [`coflow5-define-ideate.md`](coflow5-define-ideate.md) |
| Current Design Thinking status | [`.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md`](.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md) |
| Settled architecture boundary | [`docs/adr/0001-reliable-ai-platform-boundary.md`](docs/adr/0001-reliable-ai-platform-boundary.md) |
| Six-person delivery envelope | [`docs/adr/0002-six-builders-one-queue-row.md`](docs/adr/0002-six-builders-one-queue-row.md) |
| Later CI/CD and MLOps | [`docs/adr/0003-cicd-devops-mlops.md`](docs/adr/0003-cicd-devops-mlops.md) |
| Multi-agent pattern inventory | [`coflow5-design-patterns.md`](coflow5-design-patterns.md) |
| Full acceptance requirements | [`.kiro/specs/coflow5-reliable-agentic-platform/requirements.md`](.kiro/specs/coflow5-reliable-agentic-platform/requirements.md) |
| Component and communication design | [`.kiro/specs/coflow5-reliable-agentic-platform/design.md`](.kiro/specs/coflow5-reliable-agentic-platform/design.md) |
| Implementation sequence | [`.kiro/specs/coflow5-reliable-agentic-platform/tasks.md`](.kiro/specs/coflow5-reliable-agentic-platform/tasks.md) |
| Active work order | [`harness/queue.tsv`](harness/queue.tsv) |
| Presentation assets | [`docs/presentation/`](docs/presentation/) |

---

**Book owner:** CoFlow-5 team (Aziz, Eya, Fares, Aymen, Oumayma, Ranim)  
**Baseline prepared:** Tuesday, 22 September 2026  
**Next scheduled update:** after proxy validation on Wednesday, 23 September 2026  
**Current implementation truth:** Row 01 remains blocked until native Windows Python 3.11.9 is installed; no Prototype/Test result exists yet.
