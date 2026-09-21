# CoFlow-5 — Design Thinking Empathize pack

**How might we** use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?

This is the **Empathize** deliverable for the presentation: four top-level sections only. User Personas are research-informed design artifacts, not interview-validated profiles. Numerical targets later in Possible Solution are **proposed acceptance criteria**, not achieved results.

**Traceability spine:** need → Evidence → pain (User Journey) → Possible Solution → evaluation measure.

| Design Thinking stage | Where it lives in this pack |
|---|---|
| Empathize | User Personas, User Journeys, Evidence |
| Define | Needs stated under each User Persona; SMART table under Possible Solution |
| Ideate | Possible Solution (per-persona responses, matrix, shared scenario) |
| Prototype | Three end-to-end journeys under Possible Solution |
| Test | Validation plan under Possible Solution (proposed, not completed) |

Roster is the v2 seed (eight User Personas, including operators). The IMATM report’s six Tunis names are an **alternate roster**, not extra people to append. IMATM Table 9 digits and interview counts are self-labelled placeholders and are **not** Evidence.

---

## USER PERSONAS

| ID | User Persona | Profile | Need |
|---|---|---|---|
| P1 | **Amara, 74** | Walks with a cane (~0.8 m/s). Assistive-device speeds: cane 0.8, walker 0.6, wheelchair 1.1, amputee 0.7 m/s (LaPlante & Kaese, ITE). Crosses the high street twice daily to shops and transit. | *I need to know the crossing will give me enough time, even when traffic is busy.* |
| P2 | **David, 41** | Delivery-van driver, 60+ time-sensitive stops per day. | *I can plan around a longer trip if I know how long it will actually take.* |
| P3 | **Chidi, 27** | Rides a high-frequency corridor with no timetable — regularity is the service. | *Buses should arrive regularly — not three at once after a long wait.* |
| P4 | **Rosa, 52** | Depot controller; supervises bus operations and disruption. | *Show me why a bus got — or was denied — priority, and let me respond before service breaks down.* |
| P5 | **Marcus, 34** | Urban ambulance crew. | *Get us through safely, and make sure traffic recovers after we pass.* |
| P6 | **Yuki, 47** | Traffic engineer; accountable for safe network performance. | *Automation should support my decisions — not leave me responsible for a system I cannot control.* |
| P7 | **Maria, 38** | Lives near an arterial; walks her child to a nearby school. | *Cleaner traffic on the main road must not mean more exhaust outside our homes.* |
| P8 | **Omar, 55** | Duty officer; monitors incidents and coordinates response. | *Tell me what's wrong, why you think so, and whether I can still trust the data.* |

**Not in this roster (do not silently merge):** IMATM P-1–P-6 (Amine, Karim, Nadia, Hichem, Emna, Leila) cover overlapping needs under different names and a Tunis study area. Map them, do not stack them.

---

## USER JOURNEYS

Pain only. Responses sit under Possible Solution.

### P1 — Amara

| Stage | Experience and pain |
|---|---|
| Approaches | Needs an accessible way to request a crossing |
| Requests | Uncertainty whether the request registered |
| Waits | Long waits cause fatigue; may encourage unsafe crossing |
| Crosses | Standard clearance may not fit her pace |
| Arrives | Must finish before conflicting traffic is released |

Design implication: design for slower pedestrians, not the average. Reduced waiting and adequate crossing time are two separate requirements.

### P2 — David

| Stage | Experience and pain |
|---|---|
| Plans | Variable travel times break schedules |
| Enters the arterial | Poor coordination causes repeated stops |
| Hits surge/incident | Planned arrival becomes unreliable |
| Completes the route | Small delays compound into missed windows |

Design implication: a system that improves the mean while producing more extreme delays fails David.

### P3 — Chidi

| Stage | Experience and pain |
|---|---|
| Arrives at stop | Irregular service makes the wait unpredictable |
| Waits | Long gap, then buses arrive together |
| Rides | Signal delays compound lateness |
| Connects | Unreliable arrivals break connections |

Design implication: faster buses are not better-spaced buses.

### P4 — Rosa

| Stage | Experience and pain |
|---|---|
| Starts her shift | Information scattered across systems |
| Spots a gap | Ordinary variation vs developing disruption |
| Reviews a decision | Unexplained rejections erode trust |
| Intervenes | Needs action without unsafe instructions |
| Reviews the incident | No history → no explanation |

Design implication: transparency and control are core requirements, not dashboard extras.

### P5 — Marcus

| Stage | Experience and pain |
|---|---|
| Trip begins | Signals don't know the ambulance is coming |
| Approaches a queue | Green alone doesn't help if the exit is blocked |
| Crosses the junction | Abrupt transitions endanger others |
| Continues along the corridor | Isolated priority moves the bottleneck ahead |
| Leaves the area | Queues and disrupted buses remain |
| Reviews the mission | Faster EV travel alone hides the cost |

Design implication: treat passage **and** recovery as one journey. Do not convert simulated time savings into predicted lives saved.

### P6 — Yuki

| Stage | Experience and pain |
|---|---|
| Monitors | Needs to know agents, sensors, comms are healthy |
| Reviews odd behaviour | Unexpected decisions hard to diagnose |
| Hits failure | Stale data or late decisions make adaptive control unreliable |
| Intervenes | Needs a predictable way to regain control |
| Restores normal | Switching back too early recreates the problem |

Design implication: intelligent control must include predictable failure behaviour.

### P7 — Maria

| Stage | Experience and pain |
|---|---|
| Leaves home | Queuing vehicles create local exhaust and noise |
| Walks to school | Frequent acceleration and idling |
| At the school gate | Network gains may hide local deterioration |
| After a system change | A smoother arterial may mean longer side-street queues |
| Looks for evidence | A city-wide percentage explains nothing locally |

Design implication: evaluate *where* benefits and burdens land, not just totals.

### P8 — Omar

| Stage | Experience and pain |
|---|---|
| Monitors | Normal fluctuation hides emerging incidents |
| Receives an alert | False alarms destroy trust |
| Investigates | Queue could mean incident, demand, or sensor failure |
| Coordinates | Uncoordinated local changes spread congestion |
| Loses comms | A frozen dashboard can look normal while degraded |
| Closes the incident | Clearing the obstruction ≠ clearing the queues |

Design implication: distinguish “no problem detected” from “insufficient reliable data”.

### Shared journey (one ambulance, one school, one crossing)

Personas collide on the same network. Reference scenario: an ambulance passes Maria's school street while Amara is mid-crossing and Chidi's delayed bus approaches.

| Moment | Stakeholders | Pain if unmanaged |
|---|---|---|
| Emergency request arrives | Marcus, Yuki | Unauthenticated or unassessed request |
| Crossing occupied | Amara, Marcus | Conflicting traffic released while she is still on the crossing |
| Passage prepared | Marcus, David, Chidi | Isolated green; bottleneck moves one junction ahead |
| Bus priority denied | Chidi, Rosa | No recorded reason |
| Queues build nearby | David, Maria | Spillback and exhaust at the school gate |
| Communications fail at one junction | Yuki, Omar | Dashboard looks normal while control is degraded |
| Ambulance leaves | All | Instant snap-back recreates the problem |
| Event reviewed | Rosa, Yuki, Omar | No shared timeline of benefits, costs, failures |

---

## EVIDENCE

### Claim flags (do not present as Evidence)

1. “Perceived wait is 1.5× actual” — measured figure is **2×** (Vallyon, Turner & Hodgson, ATRF 2009).
2. “MUTCD 2023 allows 0.8 m/s” — unverified; MUTCD 2009 §4E uses 3.5 ft/s (1.07 m/s).
3. Any “X% of engineers distrust AI control” — no quantitative survey; use SCATS/Surtrac product documentation.
4. Rider-abandonment percentages — not found; bunching literature supports qualitative mode-shift risk only.
5. Public opinion on AI infrastructure — vendor surveys only (EY); directional at best.
6. A universal “average incident detection delay” — not found; measure our own.
7. “Flashover in 3–5 minutes” — no primary source; do not use.
8. SUMO/HBEFA outputs are **emission proxies**, not air-quality or exposure measurements. Simulated EV time savings must not be translated into predicted lives saved.
9. Unfinished/teleported trips must count in P2 metrics, or congestion looks artificially good.
10. IMATM interview counts, Table 9 digits marked ▲, and “assumed protocol” figures are **placeholders**, not Evidence.
11. CoFlow-5 PDF slides (Gemini Notebook) are architecture statements, not cited Evidence.

### Per-persona Evidence (motivates the need; does not set the target)

| User Persona | Finding |
|---|---|
| Amara | Perceived wait ≈ **2×** actual (Vallyon, Turner & Hodgson, ATRF 2009). Frustration grows after **20–30 s**; 2/3 cross on red beyond it (NZTA RR440 2009; TfL; DfT LTN 2/95: max preset normally 40 s, up to 60 s). MUTCD 2009 clearance 1.07 m/s; HCM 1.0 m/s if >20% users 65+. Blind pedestrians: completion difficulties (Bentzen et al., *JVIB* 2005). |
| David | Reliability ratio **0.4** (DfT TAG A1.3). Incidents ~**25%** of congestion (FHWA). Avoided HDV stop ≤**0.32 kg CO2 / 1.8 g NOx** (Deschle et al., *Energies* 2022). |
| Chidi | Wait valued ≈ **2×** in-vehicle (DfT TAG A1.3; Wardman mean 1.80, n=138). Bunching is self-reinforcing (Newell & Potts 1964; Daganzo 2009; 2024 review). SCOOT bus priority: bus times **−39%** Southampton (Hounsell & McDonald 1986). |
| Rosa | SCATS ships manual override and full audit trails (SCATS Core brochure, Transport NSW 2022). |
| Marcus | Each minute of ALS delay ≈ **−7%** survival-to-discharge (aOR 0.93, n=4,278; *PLOS One* 2022). EVP field −14.2% (Cary) to −18–23% (Houston). Closely spaced preemption: arterial **+20–30 s**, side-street **+7.6%** (Nelson & Bullock, TRR 1727). |
| Yuki | SCATS intervention + audit (2022). SCOOT loses benefits under congestion (Hounsell & McDonald 1986). Surtrac falls back to default durations on sensor/network failure (Smith et al., CMU). |
| Maria | 6.4M US children (13.5%) attend school within 250 m of a major road (Kingsley et al., *IJERPH* 2014). HBEFA/SUMO figures are proxies. |
| Omar | Incidents **25–30%** of metro congestion (FHWA; Puget Sound 2006). No universal detection-delay benchmark. |

### Evidence trail (verified sources)

| Topic | Finding | Figure | Source |
|---|---|---|---|
| Pedestrian wait | Frustration after 20–30 s; 2/3 cross on red beyond | 20–30 s | NZTA Research Report 440 (2009) |
| Pedestrian wait | Perceived wait = 2× actual | 2× | Vallyon, Turner & Hodgson, ATRF (2009) |
| Pedestrian wait | Compliance drops after 30 s | 30 s | TfL TTM Handbook via London Assembly Q (2019) |
| Pedestrian wait | Ped-actuated max preset normally 40 s, up to 60 s | 40–60 s | DfT LTN 2/95 (1995) |
| Pedestrian wait | Tolerable wait 20 s (light)–120 s (heavy); avoid cycles >90 s | — | Austroads Part 7 (1994) via NZTA RR440 |
| Accessibility | LPI: NYC −28% ped crashes; PA −58.7%; FHWA CMF 0.87 | — | FHWA-HRT-18-060 (2018) |
| Accessibility | City-scale LPI: collisions −5.45%, ped injuries −14.7% | — | Sze, CUNY (2019); *Nature Cities* (2025) |
| Accessibility | Assistive speeds: cane 0.8, walker 0.6, wheelchair 1.1, amputee 0.7 m/s | — | LaPlante & Kaese (ITE) |
| Accessibility | Clearance 3.5 ft/s (1.07 m/s); 1.0 m/s if >20% users 65+ | — | MUTCD 2009 §4E; FHWA HCM Ch.13 (1998) |
| Accessibility | Blind pedestrians: locating, aligning, onset, completion difficulties | — | Bentzen et al., *JVIB* (2005) |
| Transit value | Wait valued 2× in-vehicle (mean 1.80, n=138) | 2× | DfT TAG A1.3; Wardman meta-analysis |
| Transit value | US walking/waiting 2–5× in-vehicle | — | Pratt (1999) via TCRP/Litman |
| Bus bunching | Longer waits, overcrowding, trust loss; self-reinforcing | — | TR Part C (2024); Newell & Potts (1964); Daganzo (2009) |
| Holding | Headway-based holding best under disruption | — | van der Werff, van Oort, Cats & Hoogendoorn |
| Transit priority | SCOOT bus priority: bus times −39% | −39% | Hounsell & McDonald (1986) |
| EMS benchmarks | NFPA 1710 turnout/travel/alarm times | — | NFPA 1710 (2020); IAFF (2022) |
| EMS benchmarks | NHS Cat 1 / Cat 2 response standards | — | NHS England / Nuffield Trust |
| EMS survival | Each min ALS delay: survival −7% (aOR 0.93) | −7%/min | *PLOS One* (2022) |
| EMS survival | −6%/min; <8 min → 2.1× survival | −6%/min | BMC (2025) |
| EVP benefit | Cary −14.2%; Houston −18–23% | — | USFA; USDOT ITS JRS |
| EVP cost | Closely spaced preemptions: arterial +20–30 s; side-street +7.6% | — | Nelson & Bullock, TRR 1727 (2000) |
| Engineer tooling | SCATS: manual intervention + audit + incident corridors | — | SCATS Core brochure, Transport NSW (2022) |
| Engineer tooling | SCOOT loses benefits under congestion | — | Hounsell & McDonald (1986) |
| Engineer tooling | Surtrac fallback to default durations | — | Smith et al., CMU Surtrac pilot |
| Exposure | 6.4M US children (13.5%) ≤250 m of a major road | — | Kingsley et al., *IJERPH* (2014) |
| Exposure | ~33% of US public schools ≤400 m; 12% ≤100 m | — | Appatova et al. (2008) |
| Emissions | Avoided HDV stop ≤0.32 kg CO2, 1.8 g NOx | — | Deschle et al., *Energies* 15:1242 (2022) |
| Driver value | Reliability ratio 0.4 (cars/LGV) | 0.4 | DfT TAG A1.3 §6.3.4 |
| Non-recurring congestion | Incidents 25%, weather 15%, work zones 10% | 25% | FHWA |
| Incident share | 25–30% of metro congestion delay | — | FHWA Freeway Mgmt Handbook; Puget Sound (2006) |
| TIM metrics | Roadway/incident clearance; secondary crashes | — | FHWA-JPO-13-062; FHWA-HOP-15-028 |
| Public opinion | Vendor survey only — directional | — | EY *(Claim flag: not Evidence)* |

---

## POSSIBLE SOLUTION

Not a built system. Candidates to prototype and compare. Primary accountable agent is for evaluation, not a promise that the agent already exists.

### Per-persona responses (maps onto User Journey stages)

**Amara:** accessible push-button + pedestrian detection; visual/audible acknowledgement; wait-aware priority with no repeated deferral; conservative clearance and occupancy-based extension where reliable; safety interlocks; log clearance truncations (conflicting traffic released while a detected pedestrian remains on the crossing). Proposed tests: mean wait, P95 wait (tail; 40 s is not a hard-cap guarantee), % waits >30 s, zero truncations. Proposed hard cap 40 s is a separate criterion under stated detection and walking-speed assumptions.

**David:** corridor reliability from historical + live data; neighbour coordination; shared queue/incident information; evaluate P95 including unfinished/teleported trips as failures. Proposed: P95 **−5% vs Max-Pressure under surge**.

**Chidi:** headway monitoring; **conditional** priority for the bus after an unusually large gap (not every bus); coordinated priority with pedestrian clearance preserved; evaluate passenger wait and regularity, not only bus travel time. Proposed: headway variance **−15% vs no priority** at **≤3%** extra car delay.

**Rosa:** consolidated view of positions, headways, priority status; unusual-headway flags with confidence; reason codes (“pedestrian clearance active”, “downstream queue full”); authorised requests within safety and network constraints; timestamped audit trail. Proposed: 100% reason-code coverage; ≥5 min predictive warning only if scored with misses and false alarms.

**Marcus:** authenticated priority with position and route; coordinated queue pre-clearance; pedestrian clearance, intergreen, conflict protection preserved; shared ETA along the corridor; controlled recovery; log EV time, civilian person-delay, recovery per mission. Proposed: EV time **−25% vs none**, **−10% vs conventional preemption**, civilian person-delay **≤5%** increase, zero safety-constraint violations. Do not claim lives saved from simulation.

**Yuki:** operating mode, data freshness, comms status, faults; decision history (inputs, constraints, actions, reason codes); watchdogs for missed deadlines, invalid inputs, comms loss; **authorised override subject to mandatory signal-safety interlocks** (override cannot enable conflicting greens); fallback ladder watchdog → Max-Pressure → actuated → fixed-time; health checks before resume. Proposed: 100% decisions logged; latency <100 ms; usability task (identify fault, select mode).

**Maria:** monitor residential links, not only the corridor; cut unnecessary stops where safe; report emissions for school-adjacent links and periods; link-by-link displacement check; before/after map. **HBEFA/SUMO = proxy.** Pre-registered displacement rule (proposed): no statistically significant increase in mean NOx proxy on any residential link adjacent to a school (α=0.05, Holm).

**Omar:** compare observed vs expected; grouped alerts with severity, observations, uncertainty; neighbour conditions + sensor health + freshness; bounded recommendations; stale data marked; degradation alert; fallback mode shown; recovery tracked to stabilisation. Exploratory benchmarks (thresholds after week-3 pilot): detection delay, FAR, missed-incident rate, recovery — **by severity**, not one average. Method: EWMA/CUSUM on forecast residuals first; an anomaly does not establish its cause.

### Solutions matrix

| User Persona | Core need | Possible Solution | Proposed success criterion |
|---|---|---|---|
| Amara | Accessible, safe crossing | Wait-aware priority; conservative clearance; acknowledgement | Lower waits; zero clearance truncations |
| David | Predictable journeys | Neighbour coordination; queue-aware adjustment | Lower P95; fewer stops |
| Chidi | Regular service | Conditional headway-gap priority | Reduced headway variance and passenger wait |
| Rosa | Understandable decisions | Dashboard, reason codes, authorised intervention | Complete records; successful operator tasks |
| Marcus | Safe passage + recovery | Authenticated corridor priority; pre-clearance; recovery | Faster EV trips at bounded civilian delay |
| Yuki | Reliable control | Health monitoring; safety-constrained override; fallback ladder | Correct fallback; timely diagnosis |
| Maria | Fair distribution | Link-level emissions; displacement checks | Gains near sensitive locations; no hidden deterioration |
| Omar | Trustworthy awareness | Anomaly detection with uncertainty; stale-data warnings | Acceptable FAR; clear degradation alerting |

### Shared-journey responses

| Moment | Possible Solution |
|---|---|
| Emergency request | Authenticate; assess corridor |
| Crossing occupied | Pedestrian clearance **before** conflicting release |
| Passage prepared | Coordinated pre-clearance; competing priority deferred |
| Bus priority denied | Reason recorded; Rosa sees emergency precedence |
| Queues nearby | Spillback and link-level emissions watched; no prolonged recovery queues at the school gate |
| Comms fail | Degraded operation announced; junction to safe local fallback |
| Ambulance leaves | Gradual re-coordination; waits, headways, queues reassessed |
| Review | Shared timeline of decisions, benefits, costs, failures |

Principle: cooperation with explicit safeguards — no specialist hides costs imposed on other users.

### Define — SMART (proposed criteria, not literature thresholds)

| # | User Persona | Specific | Measurable | Achievable | Relevant (Evidence) | Time-bound |
|---|---|---|---|---|---|---|
| P1 | Amara | Cut wait; guarantee completion | Mean ≤20 s; P95 ≤40 s (tail); hard cap 40 s under stated assumptions; zero truncations | Rule-based A3 escalation first | 2× perceived wait; 30 s cliff; 0.6–0.8 m/s | Tier 0 week 6; every episode |
| P2 | David | Predictable, not just faster | P95 and stops/vehicle; unfinished counted; P95 −5% vs MP under surge | P95 from recorded trips | Reliability ratio 0.4 | S1–S10; headline week 11 |
| P3 | Chidi | Regular headways | Headway variance −15% vs no priority at ≤3% extra car delay | Conditional TSP | Wait ≈ 2× in-vehicle; bunching | A3 week 8; H3 on S6 week 11 |
| P4 | Rosa | Understandable, intervenable | 100% reason codes; authorised intervention; warnings with FAR | Logging, not ML | SCATS override + audit | Log from Tier 0; G3 week 10 |
| P5 | Marcus | Faster passage, honest cost | EV −25% / −10%; civilian delay ≤5%; per-mission log | SUMO preemption feasible | −7%/min; +20–30 s externality | A2 week 7; H2 on S4 week 11 |
| P6 | Yuki | Command at all times | 100% logged; latency <100 ms; fallback time; override + interlocks | Watchdog proven in SCATS/Surtrac | SCOOT degradation | Watchdog from Tier 0 |
| P7 | Maria | Cut near school, no displacement | CO2/NOx per link; proxy labelled; pre-registered displacement rule | λ_eco + HBEFA + per-link diff | 6.4M children ≤250 m | A5 week 9; H5 week 11 |
| P8 | Omar | Trustworthy alerts | Delay/FAR/miss/recovery per severity; comms-loss alerting | EWMA/CUSUM first | Incidents 25–30%; no inherited threshold | A4 week 6; H4/H6 week 11 |

### Accountable agent (evaluation, not actuation by LLM)

| User Persona | Primary agent | Main evaluation |
|---|---|---|
| Amara | A3 pedestrian | H3 wait + clearance integrity |
| David | A1 coordination | H1 P95 under surge |
| Chidi | A3 transit | H3 headway within car-delay budget |
| Rosa | A1 arbitration/audit | Reason-coded records + operator task |
| Marcus | A2 emergency | H2 EV time vs two baselines |
| Yuki | A1 fallback/safety | Fallback, log completeness, latency |
| Maria | A5 sustainability | H5 exposure-weighted gain + displacement rule |
| Omar | A4 situation | Incident delay/FAR/miss/recovery |

A1 is the only actuation authority in the wider CoFlow-5 design. That is architecture context, not a new Empathize finding. The LLM is not a Possible Solution for signal control.

### Prototype (three journeys)

1. **Everyday accessibility and reliability:** Amara requests a crossing while David and Chidi use the corridor.
2. **Emergency passage and recovery:** Marcus gets corridor priority; Rosa and Yuki inspect decisions; measure disruption and recovery for everyone else.
3. **Incident or communication failure:** Omar is alerted; Yuki checks health and fallback; Maria’s neighbourhood catches displaced queues or emissions.

For each: Before → Intervention → User experience → Trade-offs (who pays) → Evidence (simulation, logs, usability) → Limitations.

### Test (proposed)

| Activity | Participants | What it establishes |
|---|---|---|
| Accessible crossing walkthrough | Older pedestrians, mobility-aid users | Acknowledgement, waiting, crossing information |
| Journey interview/diary | Delivery drivers, bus passengers | Where unpredictability hurts |
| Dashboard task test | Bus controllers, traffic engineers | Explain a decision, identify a fault, choose a response |
| Emergency-response walkthrough | Emergency-service representatives | Request → passage → recovery |
| Neighbourhood map review | Parents, residents, school reps | Locations/times for environmental checks |
| Incident tabletop | Duty officers | Alerts support investigation without overload |

If stakeholder access is limited, run labelled **proxy walkthroughs** and say so in the report.

### Presentation close

Traffic management cannot be judged by vehicle throughput alone. Amara needs accessible crossing time; David needs predictable journeys; Chidi needs regular buses; Rosa needs understandable decisions; Marcus needs passage *and* recovery; Yuki needs operational control; Maria needs environmental improvement without displacement; Omar needs trustworthy alerts. Evidence motivates the design. Simulation and stakeholder validation decide whether Possible Solutions meet the needs.
