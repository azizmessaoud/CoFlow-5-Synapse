# CoFlow-5 — User Personas, User Journeys & Possible Solutions

**Version 2 — consolidated.** Merges the verified evidence trail with the external review's corrections: targets are now labelled as *proposed acceptance criteria*, SMART wording tightened, traceability given one primary accountable agent per persona, and validation activities added.

**Tunis simulation setting:** Empathize roles are people who already exist in Grand Tunis practice (TRANSTU, municipal/MEHAT signalisation, urgent-intervention vehicles, ANPE AQ governance). Primary Evidence is Tunisian law/agencies/open data/operator practice; SCATS/Surtrac/SCOOT/DfT/FHWA are **transfer** patterns for Possible Solutions. SUMO uses OSM + official scheduled TRANSTU GTFS + labelled synthetic/calibrated road demand — not a live cabinet. Detail: `.scratch/coflow5-empathize/research/tunisia-practice-evidence.md` and `coflow5-empathize-pack.md` Evidence §A–B.

**Claims note (use this wording in the report):** *The personas are research-informed design artifacts, not profiles validated through interviews. Tunisian institutional Evidence grounds who the personas are; transfer literature motivates product needs. Neither establishes exact numerical targets. SMART objectives combine those needs with proposed engineering acceptance criteria; simulation tests them against baselines and does not claim Tunis field performance, measured air quality, or lives saved.*

---

## 0. Flags — claims NOT to make (kept from the verification pass)

1. "Perceived wait is 1.5× actual" — the measured figure is **2×** (Vallyon, Turner & Hodgson, ATRF 2009).
2. "MUTCD 2023 allows 0.8 m/s" — unverified; MUTCD 2009 §4E uses 3.5 ft/s (1.07 m/s). Verify the 2023 edition before citing.
3. Any "X% of engineers distrust AI control" — no quantitative survey exists; use the SCATS/Surtrac product-documentation evidence.
4. Rider-abandonment percentages — no hard number exists; the 2024 bunching review supports only qualitative "mode-shift risk".
5. Public opinion on AI infrastructure — vendor surveys only (EY, n≈2,000); directional at best.
6. A universal "average incident detection delay" — not found; FHWA TIM measures are agency-specific. We measure and report our own.
7. "Flashover in 3–5 minutes" — no primary source located; do not use.
8. **Simulation emissions (SUMO/HBEFA) are proxies**, not ANPE measurements or personal exposure — any exposure-weighted indicator must be labelled as a proxy with documented weights. Simulated EV time savings must not be translated into predicted lives saved.
9. Unfinished trips must be handled explicitly in P2's metrics, or congested scenarios will look artificially good.
10. IMATM interview counts and Table 9 digits are placeholders — not Tunis field Evidence.
11. Official TRANSTU GTFS is **scheduled**, not live AVL; synthetic Tunis road demand is not observed loops.
12. Rosa/Yuki exist as Tunisian job classes; that does **not** mean Tunis already runs SCATS/Surtrac.

---

## 1. The personas — needs, journeys, evidence, possible solutions

Each persona follows: **need → journey (pain → solution) → evidence → design implication → what to test.**

### P1 — Amara, 74: the pedestrian who needs enough time
**Profile:** Tunis-centre pedestrian with cane (~0.8 m/s; assistive-device speeds: cane 0.8, walker 0.6, wheelchair 1.1, amputee 0.7 m/s — LaPlante & Kaese, ITE); crosses a busy avenue twice daily to shops and TRANSTU.
**Need:** *"I need to know the crossing will give me enough time, even when traffic is busy."*

| Journey stage | Experience & pain point | Possible CoFlow-5 response |
|---|---|---|
| Approaches | Needs an accessible way to request a crossing | Accessible push-button + pedestrian detection |
| Requests | Uncertainty whether the request registered | Clear visual/audible acknowledgement |
| Waits | Long waits cause fatigue; may encourage unsafe crossing | Wait-aware priority escalation; no repeated deferral |
| Crosses | Standard clearance may not fit her pace | Conservative clearance timing; occupancy-based extension where reliable |
| Arrives | Must finish before conflicting traffic is released | Safety interlocks preserved; clearance failures logged |

**Evidence (Tunis → transfer):** Grand Tunis crossings serve mixed ages (CODATU mobility context). Transfer: perceived wait ≈ **2× actual** (Vallyon, Turner & Hodgson, ATRF 2009); frustration grows disproportionately beyond **20–30 s** and 2/3 cross on red beyond it (NZTA RR440 2009; TfL; DfT LTN 2/95); MUTCD 2009 clearance assumes 1.07 m/s, HCM recommends 1.0 m/s when >20% of users are 65+; blind pedestrians have documented completion difficulties (Bentzen et al., *JVIB* 2005).
**Design implication:** design for slower pedestrians, not the average; *reduced waiting* and *adequate crossing time* are two separate requirements.
**What to test:** mean and P95 wait, % waits >30 s, clearance truncations (defined operationally: any release of conflicting traffic while a detected pedestrian remains on the crossing). **A P95 of 40 s is a tail target, not a maximum-wait guarantee** — the proposed hard cap (40 s) is a separate acceptance criterion, tested under stated detection and walking-speed assumptions.

### P2 — David, 41: the delivery driver who needs predictability
**Profile:** delivery-van / peak corridor driver in Grand Tunis (CODATU–AFD: daily congestion); 60+ time-sensitive stops per day.
**Need:** "I can plan around a longer trip if I know how long it will actually take."

| Journey stage | Experience & pain point | Possible CoFlow-5 response |
|---|---|---|
| Plans | Variable travel times break schedules | Corridor reliability characterised from historical + live data |
| Enters the arterial | Poor coordination causes repeated stops | Neighbouring-junction coordination for progression |
| Hits surge/incident | Planned arrival becomes unreliable | Shared queue/incident information between agents; adaptive coordination |
| Completes the route | Small delays compound into missed windows | Evaluate upper-tail journey times, not just average speed |

**Evidence (Tunis → transfer):** Congestion variance is a stated Grand Tunis mobility stress (CODATU–AFD). Transfer: travel-time variability priced at a reliability ratio of **0.4** (DfT TAG Unit A1.3); incidents cause **~25%** of congestion (FHWA); each avoided HDV stop saves ≤**0.32 kg CO2 / 1.8 g NOx** (Deschle et al., *Energies* 2022).
**Design implication:** a system that improves the mean while producing more extreme delays fails David.
**What to test:** P95 travel time (computed from recorded trip times, with unfinished/teleported trips counted as failures so congestion cannot hide), stops per vehicle, completed trips. **Target P95 −5% vs Max-Pressure under surge is a proposed experimental criterion**, not a literature-established number.

### P3 — Chidi, 27: the bus commuter who needs regular service
**Profile:** rides a TRANSTU high-frequency corridor; official GTFS is the schedule — regularity is the lived service under peak congestion.
**Need:** "Buses should arrive regularly — not three at once after a long wait."

| Journey stage | Experience & pain point | Possible CoFlow-5 response |
|---|---|---|
| Arrives at stop | Irregular service makes the wait unpredictable | Headway monitoring to identify irregularity |
| Waits | Long gap, then buses arrive together | Conditional priority for the bus following an unusually large gap — not every bus |
| Rides | Signal delays compound lateness | Coordinated priority across neighbours, pedestrian clearance preserved |
| Connects | Unreliable arrivals break connections | Evaluate passenger waiting and regularity, not only bus travel time |

**Evidence (Tunis → transfer):** Official TRANSTU GTFS on `catalogue-data.transport.tn` documents scheduled offer (not live AVL); CODATU notes strained collective transport under congestion. Transfer: wait time valued ≈ **2× in-vehicle** (DfT TAG A1.3; Wardman mean 1.80); bunching is a self-reinforcing loop (Newell & Potts 1964; Daganzo 2009; 2024 review); SCOOT bus priority cut Southampton bus journey times by up to **39%** (Hounsell & McDonald 1986).
**Design implication:** faster buses are not better-spaced buses; priority must respond to headway conditions and coordinate with operator holding practices.
**What to test:** headway variance, passenger waiting, bus journey time, additional car delay. Proposed acceptance criteria: headway variance **−15% vs no priority**, ≤**3%** additional car delay — experimental targets.

### P4 — Rosa, 52: the dépôt controller who needs understandable decisions
**Profile:** TRANSTU dépôt / régulation — supervises bus operations and disruption (real operator units; she does not own the light cabinet).
**Need:** "Show me why a bus got — or was denied — priority, and let me respond before service breaks down."

| Journey stage | Experience & pain point | Possible CoFlow-5 response |
|---|---|---|
| Starts her shift | Information scattered across systems | Consolidated view: bus positions, headways, priority status |
| Spots a gap | Ordinary variation vs developing disruption | Flag unusual headways with confidence and supporting observations |
| Reviews a decision | Unexplained rejections erode trust | Reason codes: "pedestrian clearance active", "downstream queue full" |
| Intervenes | Needs action without unsafe instructions | Authorised priority requests within signal-safety and network constraints |
| Reviews the incident | No history → no explanation | Timestamped audit trail of requests, decisions, overrides, outcomes |

**Evidence (Tunis → transfer):** TRANSTU organisational practice includes dépôts and trafic/régulation. Transfer: SCATS ships manual override and full audit trails as product features (SCATS Core brochure, Transport NSW 2022) — the pattern Rosa’s Possible Solution needs, not a Tunis deployment claim.
**Design implication:** transparency and control are core requirements, not dashboard extras.
**What to test:** reason-code coverage, task-completion time, controller comprehension of decisions; if predictive warnings are included, **warning lead time ≥5 min** evaluated *with* missed-event and false-alarm rates (existing override features do not establish feasibility of a 5-minute predictive warning — that is a proposed feature, tested on S6/S9).

### P5 — Marcus, 34: the paramedic who needs safe emergency passage
**Profile:** urban ambulance / urgent-intervention crew under Tunisian priority-vehicle rules.
**Need:** "Get us through safely, and make sure traffic recovers after we pass."

| Journey stage | Experience & pain point | Possible CoFlow-5 response |
|---|---|---|
| Trip begins | Signals don't know the ambulance is coming | Authenticated priority request with position and route |
| Approaches a queue | Green alone doesn't help if the exit is blocked | Coordinated pre-clearance of queues where feasible |
| Crosses the junction | Abrupt transitions endanger others | Pedestrian clearance, intergreen and conflict protection preserved |
| Continues along the corridor | Isolated priority moves the bottleneck ahead | Shared ETA information between neighbouring agents |
| Leaves the area | Queues and disrupted buses remain | Controlled recovery sequence to restore coordination |
| Reviews the mission | Faster EV travel alone hides the cost | Log EV journey time, civilian person-delay, recovery time per mission |

**Evidence (Tunis → transfer):** Décret 2000-149 lists priority / urgent-intervention vehicles; Code de la route requires yielding when special signals are used — legal priority ≠ cleared exit. Transfer: each minute of ALS delay ≈ **−7%** cardiac-arrest survival-to-discharge (*PLOS One* 2022); EVP field results −14.2% (Cary NC) to −18–23% (Houston); closely spaced preemption costs others +20–30 s arterial time and up to +7.6% side-street delay (Nelson & Bullock, TRR 1727).
**Design implication:** treat passage **and** recovery as one journey. Do not convert simulated time savings into predicted lives saved.
**What to test:** EV journey time vs no priority *and* vs conventional preemption (targets −25% / −10% are proposed criteria), civilian person-delay, safety-constraint violations (target: zero), recovery time.

### P6 — Yuki, 47: the traffic engineer who needs reliable control
**Profile:** municipal / MEHAT-facing traffic engineer for signalisation lumineuse; accountable for safe network performance (plans may be old; permanent detection not assumed).
**Need:** "Automation should support my decisions — not leave me responsible for a system I cannot control."

| Journey stage | Experience & pain point | Possible CoFlow-5 response |
|---|---|---|
| Monitors | Needs to know agents, sensors, comms are healthy | Operating mode, data freshness, communication status, active faults |
| Reviews odd behaviour | Unexpected decisions hard to diagnose | Decision history: inputs, constraints, actions, reason codes |
| Hits failure | Stale data or late decisions make adaptive control unreliable | Watchdogs for missed deadlines, invalid inputs, communication loss |
| Intervenes | Needs a predictable way to regain control | **Authorised override taking precedence subject to mandatory signal-safety interlocks** — override can never enable conflicting greens or unsafe transitions; plus a fallback ladder (watchdog → Max-Pressure → actuated → fixed-time) |
| Restores normal | Switching back too early recreates the problem | Health checks + controlled transition before resuming cooperative control |

**Evidence (Tunis → transfer):** MEHAT UGOSMREPSL and municipalities own luminous signalling duties — the job exists. Transfer: SCATS ships manual intervention and audit trails (2022); SCOOT loses benefits under congestion (Hounsell & McDonald 1986); Surtrac’s executor falls back to default durations on sensor/network failure (Smith et al., CMU pilot). Tunisian SUMO studies already use simulation to compare static vs adaptive control (Othmani et al.).
**Design implication:** "intelligent" control must include predictable failure behaviour; un-diagnosable optimisation is useless to an operator.
**What to test:** decision-log completeness, control latency (<100 ms target), fallback activation time, recovery under sensor/comms failure — plus a usability task: can she identify the fault and select the correct mode?

### P7 — Maria, 38: the parent who does not want pollution displaced
**Profile:** lives near a Grand Tunis arterial; walks her child to a nearby school (CODATU: congestion linked to air pollution stress).
**Need:** "Cleaner traffic on the main road must not mean more exhaust outside our homes."

| Journey stage | Experience & pain point | Possible CoFlow-5 response |
|---|---|---|
| Leaves home | Queuing vehicles create local exhaust and noise | Residential links included in monitoring, not just the corridor |
| Walks to school | Frequent acceleration and idling | Coordination adjusted to cut unnecessary stops where safe |
| At the school gate | Network gains may hide local deterioration | Emissions reported separately for school-adjacent links and periods |
| After a system change | A smoother arterial may mean longer side-street queues | Link-by-link displacement check vs baseline |
| Looks for evidence | A city-wide percentage explains nothing locally | Before/after map: where emissions fell, rose, or stayed |

**Evidence (Tunis → transfer):** Loi 2007-34 / ANPE RNSQA monitor ambient AQ (including traffic-type stations); that is not the same as measuring her school-gate street. Transfer: 6.4M US children (13.5%) attend school within 250 m of a major road (Kingsley et al., *IJERPH* 2014); avoided HDV stop saves ≤0.32 kg CO2 / 1.8 g NOx (Deschle 2022). **SUMO/HBEFA = proxy, not ANPE.**
**Design implication:** evaluate *where* benefits and burdens land, not just totals. **SUMO/HBEFA outputs are emission estimates and proxies, not air-quality or exposure measurements** — any exposure-weighted indicator is labelled as a proxy with documented weights.
**What to test:** CO2/NOx per link, changes near sensitive locations, stops per vehicle, additional person-delay. **A displacement acceptance rule is defined before testing** (proposed rule: no statistically significant increase in mean NOx proxy on any residential link adjacent to a school, at α=0.05 with Holm correction — the rule is pre-registered, then applied).

### P8 — Omar, 55: the duty officer who needs trustworthy alerts
**Profile:** monitors incidents and coordinates the operational response.
**Need:** "Tell me what's wrong, why you think so, and whether I can still trust the data."

| Journey stage | Experience & pain point | Possible CoFlow-5 response |
|---|---|---|
| Monitors | Normal fluctuation hides emerging incidents | Compare observed vs expected; highlight persistent anomalies |
| Receives an alert | False alarms destroy trust | Grouped alerts with severity, supporting observations, uncertainty |
| Investigates | Queue could mean incident, demand, or sensor failure | Neighbour conditions, sensor health, data freshness for diagnosis |
| Coordinates | Uncoordinated local changes spread congestion | Bounded response recommendations; incident status shared with agents |
| Loses comms | A frozen dashboard can look normal while degraded | Stale data marked; degradation alert; active fallback mode shown |
| Closes the incident | Clearing the obstruction ≠ clearing the queues | Recovery tracked to stabilisation; event timeline retained |

**Evidence (Tunis → transfer):** Peak disruption and recovery are part of Grand Tunis congestion reality (CODATU context); no Tunisian universal detection-delay benchmark found. Transfer: incidents contribute **25–30%** of metro congestion (FHWA; Puget Sound 2006); FHWA TIM measures roadway/incident clearance and secondary crashes — we measure and report our own FAR/miss rates.
**Design implication:** evaluate detection speed *with* false alarms and missed incidents; the system must distinguish "no problem detected" from "insufficient reliable data".
**What to test:** detection delay, false-alarm rate, missed-incident rate, recovery time, communication-loss alerting — **by incident severity, not one average.** These are **exploratory benchmarking objectives** (no pre-existing thresholds to inherit); the proposed acceptance thresholds will be set after the week-3 pilot measures noise. Method: interpretable EWMA/CUSUM on forecast residuals first — an anomaly does not establish its cause.

---

## 1b. World truths → metrics catalogue (transfer)

Full table: `.scratch/coflow5-empathize/research/world-truths-and-metrics.md`. Empathize pack Evidence §D summarises. **Insight alignment (I-1…I-10):** `.scratch/coflow5-empathize/research/insight-evidence-alignment.md` and Empathize pack Evidence §E. SMART numbers below are **proposed tests**, not FHWA/DfT mandates. IMATM Table 9 ▲ digits are **not** Evidence.

| Truth / insight | Standard metrics the world uses | Our persona owner |
|---|---|---|
| I-1 Reliability > mean delay | P95 TT, buffer index, planning time index, on-time %; unfinished trips as failures | David |
| I-2 Empty green / plan waste | AoG %, queue by movement, split failure, green occupancy | David, Yuki |
| I-6 Spillback / residential push | Downstream queue; blocked events; residential link burden | David, Maria, Yuki |
| I-4 Ped wait cliff ~20–30 s | Call→WALK delay; mean/P95 wait; % >30 s; clearance truncations; completion | Amara |
| I-5 Conditional transit priority | Headway CV; passenger wait; grant/deny + reason; extra car delay | Chidi, Rosa |
| I-3 EVP has externality / needs space | EV TT; civilian person-delay; recovery time; zero safety breaches | Marcus |
| I-8/I-9 Operable ATC needs takeover | Reason-code coverage; log completeness; latency; fallback time; freshness | Yuki, Rosa |
| I-10 Incidents dominate the delay tail | Detection delay, FAR, miss; roadway/incident clearance; by severity | Omar |
| I-7 Emissions are local; stops are the lever | Link CO₂/NOx **proxy**; stops near receptors; displacement rule | Maria |

Appraisal anchors only: DfT reliability ratio **0.4**; transit wait ≈**2×** in-vehicle; MUTCD/HCM walk **1.07 / 1.0** m/s.

---

## 2. SMART objectives (corrected framing)

**Framing:** the SMART objectives combine *evidence-informed stakeholder needs* with *proposed engineering acceptance criteria*. Numerical targets are tested against explicit baselines; they are not achieved results and are not thresholds universally established by the literature.

| # | Persona | Specific | Measurable | Achievable | Relevant (evidence) | Time-bound |
|---|---|---|---|---|---|---|
| P1 | Amara | Cut her wait and guarantee crossing completion | Mean ≤20 s; P95 ≤40 s (tail target); hard cap 40 s on service delay, tested under stated detection/speed assumptions; zero clearance truncations (operational definition in §P1) | A3 escalation + slow-walker detection are rule-based first — no RL needed for her floor guarantee | 2× perceived wait; 30 s compliance cliff; assistive speeds 0.6–0.8 m/s | Constraint from Tier 0 (week 6); every eval episode |
| P2 | David | Make trips predictable, not just faster | P95 and stops/vehicle reported per scenario; all trips including unfinished ones counted; proposed target P95 −5% vs MP under surge | P95 computed from recorded trip times — free to compute | Reliability ratio 0.4 (DfT TAG) | Every scenario S1–S10; headline result week 11 |
| P3 | Chidi | Regular headways, not faster buses | Proposed: headway variance −15% vs no priority at ≤3% extra car delay | Conditional TSP is deterministic logic; proven at scale (SCOOT −39%) | Wait ≈ 2× in-vehicle value; bunching loop | A3 live week 8; H3 transit subtest on S6 by week 11 |
| P4 | Rosa | Understandable, intervenable priority decisions | 100% reason-code coverage; authorised intervention within safety constraints; predictive warnings evaluated on lead time ≥5 min *with* missed-event and false-alarm rates | Reason codes are a logging feature, not ML | SCATS ships override + audit trail as product features | Logging from Tier 0; instrumentation-readiness review week 5; audit at gate G3 (week 10) |
| P5 | Marcus | Faster passage with the cost billed honestly | Proposed: EV time −25% vs none, −10% vs conventional preemption, civilian person-delay ≤5% increase, per-mission log | Corridor preemption buildable in SUMO; EMVLight achieved −42.6% in simulation (feasibility, not a guarantee) | −7%/min survival; +20–30 s cost of poor spacing | A2 live week 7; H2 on S4 by week 11 |
| P6 | Yuki | Command of the network at all times | 100% decisions logged; per-decision latency <100 ms; fallback ladder activation time measured; **override precedence always subject to mandatory safety interlocks** | Watchdog + audit discipline proven in SCATS/Surtrac | Adaptive degradation under congestion (SCOOT 1986) | Watchdog live from Tier 0; usability task at G2/G3 |
| P7 | Maria | Emissions cut near her school, without displacement | CO2/NOx per link reported; exposure indicator labelled as proxy with documented weights; **pre-registered displacement acceptance rule**; proposed: measurable exposure-weighted gain at ≤3% delay cost | λ_eco update + HBEFA KPIs implementable; displacement check is a per-link diff | 6.4M US children ≤250 m of major roads; ≤0.32 kg CO2 per avoided stop | A5 live week 9; H5 Pareto sweep by week 11 |
| P8 | Omar | Trustworthy alerts and visible degradation | Detection delay, FAR, missed-incident rate, recovery time **reported per severity class**; degradation alerting on comms loss. **Exploratory benchmarking objective** — thresholds set after the week-3 pilot | EWMA/CUSUM first; benchmark is ours to define | Incidents = 25–30% of congestion; no universal detection benchmark exists | A4 alerts week 6; H4/H6 sweeps (S3/S7) by week 11 |

**Schedule note (fix applied):** reason-code instrumentation readiness is reviewed at **week 5**; full auditability is audited at **gate G3 (week 10)** — consistent with Tier 0 completing in week 6.

---

## 3. Traceability — one primary accountable agent per persona

Cross-cutting objectives are appropriate for a multi-agent system; what matters is clear accountability. Each persona has **one primary accountable agent** and **one main falsifiable evaluation**; supporting agents and cross-cutting tests are recorded separately.

| Persona | Primary accountable agent | Main evaluation | Supporting agents / cross-cutting tests |
|---|---|---|---|
| P1 — Amara | A3 (pedestrian priority) | H3 pedestrian subtest: wait targets + clearance integrity | A1 enforces the constraint (H1 safety regression) |
| P2 — David | A1 (coordination/arbitration) | H1 reliability test (P95 under surge) | H4 supports with incident analysis; A5 offsets |
| P3 — Chidi | A3 (transit priority) | H3 transit subtest: headway gain within car-delay budget | A2 can deny priority (conflict test on S9) |
| P4 — Rosa | A1 (arbitration/audit) | Auditability test: complete reason-coded decision records + operator task success | Dashboard (A3 views); G3 audit |
| P5 — Marcus | A2 (emergency priority) | H2: EV time vs two baselines at bounded civilian delay | A4 predicted times; recovery KPI on S9 |
| P6 — Yuki | A1 (fallback & safety layer) | Robustness tests: fallback activation, log completeness, latency | H6 sweeps (S7); override-with-interlocks test |
| P7 — Maria | A5 (sustainability) | H5: exposure-weighted reduction with pre-registered displacement rule | A1 delay budget; link-level equity map |
| P8 — Omar | A4 (situation awareness) | Incident benchmarking (S3): delay/FAR/missed rate/recovery | H4 forecast-quality ablation; H6 degradation alerts |

*(If a persona's "M" cannot be tied to a falsifiable claim, it is a wish, not a target — all eight pass with this table.)*

---

## 4. The shared journey — one ambulance, one school, one crossing

Personas interact on the same network; a solution for one can cost another. Reference scenario for S9: an ambulance passes Maria's school street while Amara is mid-crossing and Chidi's delayed bus approaches.

| Moment | Stakeholders affected | Proposed system response |
|---|---|---|
| Emergency request arrives | Marcus, Yuki | Authenticate the request; assess corridor condition |
| Crossing occupied | Amara, Marcus | Pedestrian clearance preserved before conflicting traffic is released |
| Passage prepared | Marcus, David, Chidi | Coordinated queue pre-clearance; competing priority deferred |
| Bus priority temporarily denied | Chidi, Rosa | Reason recorded; Rosa sees emergency precedence |
| Queues build nearby | David, Maria | Spillback and link-level emissions monitored; no prolonged recovery queues at the school gate |
| Communications fail at one junction | Yuki, Omar | Degraded operation announced; junction switched to safe local fallback |
| Ambulance leaves | All | Gradual re-coordination; pedestrian waits, headways and queues reassessed |
| Event reviewed | Rosa, Yuki, Omar | Shared timeline of decisions, benefits, costs, failures |

**Design principle:** cooperation *with explicit safeguards* — no agent optimises its own objective while hiding costs imposed on other users.

---

## 5. Solutions matrix (candidates to prototype and compare)

| Persona | Core need | Possible solution | Evidence of success (proposed criterion) |
|---|---|---|---|
| Amara | Accessible, safe crossing | Wait-aware priority; conservative clearance; accessible acknowledgement | Lower waits, zero clearance truncations |
| David | Predictable journeys | Neighbour coordination; queue-aware adjustment | Lower P95; fewer stops |
| Chidi | Regular service | Conditional headway-gap priority | Reduced headway variance and passenger wait |
| Rosa | Understandable decisions | Dashboard, reason codes, authorised intervention | Complete records; successful operator tasks |
| Marcus | Safe passage + recovery | Authenticated corridor priority; pre-clearance; controlled recovery | Faster EV trips at bounded civilian delay |
| Yuki | Reliable control | Health monitoring; safety-constrained override; fallback ladder | Correct fallback behaviour; timely diagnosis |
| Maria | Fair distribution | Link-level emissions; displacement checks | Gains near sensitive locations, no hidden deterioration |
| Omar | Trustworthy awareness | Anomaly detection with uncertainty; stale-data warnings | Acceptable FAR with clear degradation alerting |

---

## 6. Validation plan (proposed, not completed)

| Activity | Participants | What it establishes |
|---|---|---|
| Accessible crossing walkthrough | Older pedestrians, mobility-aid users | Whether acknowledgement, waiting conditions and crossing information are usable |
| Journey interview/diary | Delivery drivers, bus passengers | Where unpredictability hurts most in practice |
| Dashboard task test | Bus controllers, traffic engineers | Can users explain a decision, identify a fault, choose a response |
| Emergency-response walkthrough | Emergency-service representatives | Whether request → passage → recovery matches operations |
| Neighbourhood map review | Parents, residents, school reps | Which locations/times belong in the environmental checks |
| Incident tabletop exercise | Duty officers | Do alerts support investigation without overload |

If stakeholder access is limited, run clearly labelled **proxy walkthroughs** and acknowledge the limitation in the report.

---

## 7. Recommended prototype scope — three end-to-end journeys

1. **Everyday accessibility & reliability:** Amara requests a crossing while David and Chidi traverse a busy corridor. Tests pedestrian protection, bus regularity and general-traffic delay together.
2. **Emergency passage & recovery:** Marcus receives corridor priority; Rosa and Yuki inspect decisions; the prototype measures disruption and recovery for everyone else.
3. **Incident or communication failure:** Omar gets an alert while Yuki checks health and activates fallback. Tests whether the system distinguishes congestion, suspected incident and missing data — with Maria's neighbourhood in the evaluation to catch displaced queues or emissions.

For each: **Before** (baseline situation) → **Intervention** (what agents know and decide) → **User experience** → **Trade-offs** (who pays) → **Evidence** (simulation, logs, usability feedback) → **Limitations** (where it fails).

**Traceability spine for every journey:** user need → supporting evidence → pain point → proposed solution → evaluation measure.

---

## 8. Report-ready conclusion

CoFlow-5's personas show traffic management cannot be judged by vehicle throughput alone: Amara needs accessible crossing time; David needs predictable journeys; Chidi needs regular buses; Rosa needs understandable decisions; Marcus needs safe passage *and* recovery; Yuki needs operational control; Maria needs environmental improvement without displacement; Omar needs trustworthy alerts. The supplied evidence motivates the design; simulation and stakeholder validation establish whether the solutions meet the needs. Success means demonstrating benefits, exposing trade-offs, and staying safe and transparent when conditions deteriorate.

---

## 9. Evidence trail (verified sources)

| Topic | Finding | Figure | Source |
|---|---|---|---|
| Pedestrian wait | Frustration disproportionate after 20–30 s; 2/3 cross on red beyond | 20–30 s | NZTA Research Report 440 (2009) |
| Pedestrian wait | Perceived wait = 2× actual (measured) | 2× | Vallyon, Turner & Hodgson, ATRF (2009) |
| Pedestrian wait | Compliance drops after 30 s | 30 s | TfL Temporary Traffic Management Handbook via London Assembly Q (2019) |
| Pedestrian wait | Ped-actuated max preset "normally 40 s… up to 60 s" | 40–60 s | DfT Local Transport Note 2/95 (1995) |
| Pedestrian wait | Tolerable wait 20 s (light) – 120 s (heavy); avoid cycles >90 s | — | Austroads Part 7 (1994) via NZTA RR440 |
| Accessibility | LPI: NYC −28% ped crashes; PA −58.7%; FHWA CMF 0.87 (p<0.05) | — | FHWA-HRT-18-060 (2018) |
| Accessibility | City-scale LPI: collisions −5.45%, ped injuries −14.7% (12,987 intersections) | — | Sze, CUNY (2019); *Nature Cities* (2025) |
| Accessibility | Assistive-device speeds: cane 0.8, walker 0.6, wheelchair 1.1, amputee 0.7 m/s | — | LaPlante & Kaese (ITE) via FHWA/MUTCD docket |
| Accessibility | Clearance: 3.5 ft/s (1.07 m/s); 1.0 m/s if >20% users 65+ | — | MUTCD 2009 §4E; FHWA HCM Ch.13 procedures (1998) |
| Accessibility | Blind pedestrians: locating, aligning, walk onset, completion difficulties | — | Bentzen et al., *JVIB* (2005) |
| Transit value | Wait valued 2× in-vehicle (mean 1.80, n=138) | 2× | DfT TAG Unit A1.3; Wardman meta-analysis |
| Transit value | US walking/waiting 2–5× in-vehicle | — | Pratt (1999) via TCRP/Litman |
| Bus bunching | Longer waits, overcrowding, trust loss, mode-shift risk; self-reinforcing | — | TR Part C review (2024); Newell & Potts (1964); Daganzo (2009) |
| Holding | Headway-based holding best under disruption | — | van der Werff, van Oort, Cats & Hoogendoorn |
| Transit priority | SCOOT bus priority: bus times −39% (Southampton) | −39% | Hounsell & McDonald (1986) |
| EMS benchmarks | NFPA 1710: turnout ≤60 s (EMS)/80 s (fire); travel ≤240 s; alarm ≤480 s (90%) | — | NFPA 1710 (2020); IAFF (2022) |
| EMS benchmarks | NHS Cat 1 mean 7 min, 90% ≤15 min; Cat 2 mean 18 min, 90% ≤40 min | — | NHS England / Nuffield Trust |
| EMS survival | Each min ALS delay: survival −7% (aOR 0.93), good neuro −9% (n=4,278) | −7%/min | *PLOS One* (2022) |
| EMS survival | −6%/min; <8 min response → 2.1× survival (n=5,433) | −6%/min | BMC (2025) |
| EVP benefit | Cary NC −14.2%; SW PA −14–23%; Houston −18–23% | — | USFA applied research; USDOT ITS JRS |
| EVP cost | Closely spaced preemptions: arterial +20–30 s; side-street +7.6% | — | Nelson & Bullock, TRR 1727 (2000); Haghani & Kluger (2025) |
| Engineer tooling | SCATS ships manual intervention + audit trail + incident corridors | — | SCATS Core brochure, Transport NSW (2022) |
| Engineer tooling | SCOOT loses benefits under congestion | — | Hounsell & McDonald (1986) |
| Engineer tooling | Surtrac falls back to default durations on sensor/network failure | — | Smith et al., CMU Surtrac pilot report |
| Exposure | 6.4M US children (13.5%) ≤250 m of a major road; majority-Black schools 18% more likely | — | Kingsley et al., *IJERPH* (2014) |
| Exposure | ~33% of US public schools ≤400 m; 12% ≤100 m | — | Appatova et al. (2008) |
| Emissions | Avoided HDV stop saves ≤0.32 kg CO2, 1.8 g NOx; stopped >5× NOx of slow-down | — | Deschle et al., *Energies* 15:1242 (2022) |
| Driver value | Reliability ratio 0.4 (cars/LGV), 0.58–0.7 freight | 0.4 | DfT TAG Unit A1.3 §6.3.4 |
| Non-recurring congestion | Incidents 25%, weather 15%, work zones 10% | 25% | FHWA |
| Incident share | 25–30% of metro congestion delay | — | FHWA Freeway Mgmt Handbook Ch.10; Puget Sound (2006) |
| TIM metrics | Roadway/incident clearance time, secondary crashes; New Orleans ≤30 min for 75% | — | FHWA-JPO-13-062; FHWA-HOP-15-028 |
| Public opinion | >2/3 believe AI helps city living; traffic #1 opportunity; trust conditional | — | EY survey *(vendor — directional only)* |
</arg_value></tool_call>Saved as v2 of the personas artifact — the definitive Empathize deliverable. What changed in this version, so you can defend each change in the report:

- **Evidence vs targets separated** throughout: every numerical target is now a *proposed acceptance criterion* tested against baselines (e.g., EMVLight's −42.6% is cited as feasibility evidence, not a guarantee CoFlow-5 will match it).
- **P1 fixed:** P95 ≤40 s is explicitly a tail target, with the 40 s hard cap stated separately and clearance truncation given an operational definition (conflicting traffic released while a detected pedestrian remains on the crossing).
- **P2 fixed:** P95 computed from recorded trips with unfinished/teleported trips counted as failures, so congested scenarios can't look artificially good.
- **P4/P8 reframed:** the "≥5 min warning" is now a proposed feature evaluated *with* missed-event and false-alarm rates; P8's metrics are explicitly labelled an exploratory benchmarking objective (thresholds set after the week-3 pilot).
- **P6 fixed:** operator override takes precedence *subject to mandatory signal-safety interlocks* — override can never enable conflicting greens.
- **P7 fixed:** the displacement acceptance rule is pre-registered (no significant NOx-proxy increase on residential links adjacent to receptors, α=0.05, Holm), and the exposure indicator is labelled a proxy throughout.
- **Traceability corrected:** one primary accountable agent + one main falsifiable evaluation per persona, with supporting agents in a separate column — replacing the false "exactly one hypothesis each" claim.
- **Schedule fixed:** week 5 is now an instrumentation-readiness review; full audit at G3 (week 10), consistent with Tier 0 at week 6.

All three Empathize deliverables now live in the two saved artifacts (verified design doc + personas/journeys/solutions v2), each persona traceable through need → evidence → pain point → solution → evaluation measure. The next concrete step in the plan is week-1's: pin the SUMO version, get Max-Pressure and fixed-time running on a 4×4 grid, and measure simulation speed — that needs a compute budget to be granted before I can run anything.All done — the plan is now fully complete. Here's where the CoFlow-5 project materials stand:

**Saved deliverables (two artifacts):**
1. **Verified design document** — the full CoFlow-5 design with 16 literature claims checked against primary sources (four corrected: SURTRAC figures, CityLight deployment claim, rliable repo, the 29× pollution figure), the gap section rewritten on evidence, and corrected references with arXiv IDs/DOIs.
2. **Personas, journeys & solutions (v2)** — the final Empathize deliverable: eight personas with journey maps, possible solutions, the corrected SMART table, single-primary-agent traceability, the shared ambulance/school/crossing journey, the validation plan, and the full 33-row evidence trail.

**Key corrections carried into the final version**, each traceable in the report:
- Evidence vs targets separated — all numeric targets are proposed acceptance criteria, not literature-established thresholds.
- P1: P95 ≤40 s as a tail target, 40 s hard cap separate, clearance truncation operationally defined.
- P2: unfinished/teleported trips counted as failures in P95.
- P6: override precedence subject to mandatory signal-safety interlocks.
- P7: pre-registered displacement acceptance rule; exposure metrics labelled as proxies.
- P8: exploratory benchmarking objective until the week-3 pilot sets thresholds.
- Schedule: week 5 = instrumentation-readiness review, full audit at G3.

**Next step when you're ready:** week 1's build work — pin SUMO, get Max-Pressure and fixed-time running on a 4×4 grid, and measure simulation speed to set your seed budget. That requires remote compute, and this session's budget is currently $0.00, so nothing runs until a budget is granted. Say the word when you want to start, and I'll propose the exact smoke-test setup with costs before spending anything.