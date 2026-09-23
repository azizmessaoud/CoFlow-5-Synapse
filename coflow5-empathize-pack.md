# CoFlow-5 — Design Thinking Empathize pack

**How might we** use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?

This is the **Empathize** deliverable for the presentation: four top-level sections only. User Personas are research-informed design artifacts, not interview-validated profiles. Numerical targets later in Possible Solution are **proposed acceptance criteria**, not achieved results.

**Study setting (simulation):** Grand Tunis — street users and operators who already exist in Tunisian practice (TRANSTU, municipal / MEHAT signalisation, urgent-intervention vehicles, ANPE air-quality governance). CoFlow-5 is a **SUMO decision lab** on that setting (OSM + official scheduled TRANSTU GTFS + labelled synthetic/calibrated road demand). It is not a live Tunis cabinet deployment.

**Evidence rule:** Tunisian law, agencies, open data, and operator practice come first. International ATC (SCATS, Surtrac, SCOOT, DfT, FHWA) is **transfer** Evidence for product needs — not a claim that Tunis already runs those systems. Detail: `.scratch/coflow5-empathize/research/tunisia-practice-evidence.md`.

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

Profiles are Tunis-practice roles. Speeds and clearance figures that are not Tunisian statutes cite transfer standards (ITE / MUTCD / HCM) and stay labelled as such.

| ID | User Persona | Tunis practice profile | Need |
|---|---|---|---|
| P1 | **Amara, 74** | Older pedestrian with cane (~0.8 m/s assistive band — LaPlante & Kaese, ITE). Crosses a central Tunis avenue twice daily to market, pharmacy, and TRANSTU stops. App-only requests would exclude her. | *I need to know the crossing will give me enough time, even when traffic is busy.* |
| P2 | **David, 41** | Delivery / peak-hour road user on a congested Grand Tunis corridor (CODATU–AFD: daily congestion after modal shift to cars). Plans around variance more than mean speed. | *I can plan around a longer trip if I know how long it will actually take.* |
| P3 | **Chidi, 27** | TRANSTU bus (or métro feeder) rider on a high-frequency line. Official GTFS gives the *schedule*; lived service is regularity and bunching under congestion. | *Buses should arrive regularly — not three at once after a long wait.* |
| P4 | **Rosa, 52** | TRANSTU dépôt / régulation controller — bus districts and depots are real operator units; she supervises headways and disruption, not the traffic-light cabinet. | *Show me why a bus got — or was denied — priority, and let me respond before service breaks down.* |
| P5 | **Marcus, 34** | Ambulance / urgent-intervention crew. Tunisian law already lists priority vehicles and requires other road users to yield when special signals are used (Décret 2000-149; Code de la route). | *Get us through safely, and make sure traffic recovers after we pass.* |
| P6 | **Yuki, 47** | Municipal / MEHAT-facing traffic engineer accountable for signalisation lumineuse and safe network performance. Plans may be old; permanent detectors are not assumed. | *Automation should support my decisions — not leave me responsible for a system I cannot control.* |
| P7 | **Maria, 38** | Parent living near an arterial; walks a child to school. National AQ monitoring exists (ANPE); her street-front exposure is still often unmeasured. | *Cleaner traffic on the main road must not mean more exhaust outside our homes.* |
| P8 | **Omar, 55** | Duty officer / incident desk coordinating peak disruption with police, TRANSTU, and the signal owner. | *Tell me what's wrong, why you think so, and whether I can still trust the data.* |

**Not in this roster (do not silently merge):** IMATM P-1–P-6 (Amine, Karim, Nadia, Hichem, Emna, Leila) cover overlapping needs under Tunis colour names. Map them, do not stack them.

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

Personas collide on the same Tunis-centre corridor in simulation. Reference scenario: an urgent-intervention vehicle (Marcus) passes Maria's school street while Amara is mid-crossing and Chidi's delayed TRANSTU bus approaches.

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
3. Any “X% of engineers distrust AI control” — no quantitative survey; use SCATS/Surtrac product documentation as *transfer* practice only.
4. Rider-abandonment percentages — not found; bunching literature supports qualitative mode-shift risk only.
5. Public opinion on AI infrastructure — vendor surveys only (EY); directional at best.
6. A universal “average incident detection delay” — not found; measure our own.
7. “Flashover in 3–5 minutes” — no primary source; do not use.
8. SUMO/HBEFA outputs are **emission proxies**, not ANPE measurements or personal exposure. Simulated EV time savings must not be translated into predicted lives saved.
9. Unfinished/teleported trips must count in P2 metrics, or congestion looks artificially good.
10. IMATM interview counts, Table 9 digits marked ▲, and “assumed protocol” figures are **placeholders**, not Evidence.
11. CoFlow-5 PDF slides (Gemini Notebook) are architecture statements, not cited Evidence.
12. Official TRANSTU **GTFS is scheduled offer**, not confirmed live bus positions. Synthetic/calibrated Tunis road demand is not observed loop data.
13. Do not claim Tunis already operates SCATS, Surtrac, or SCOOT because Rosa/Yuki exist as jobs.
14. IMATM insight **mechanism** statements may guide Empathize; IMATM Table 9 ▲ digits (empty-green %, EV −8.1%, 19% unfinished crossings, headway CV path, r=0.81, 7%/31% incident share, etc.) stay **placeholders**, not Evidence — see §E.

### A. Tunisia practice (primary for this simulation)

| Topic | Finding | Source |
|---|---|---|
| Public operator | TRANSTU operates Grand Tunis bus, métro léger, and TGM; publishes fleet/availability and passenger traffic. | TRANSTU “Parc et Trafic”; Ministère des Transports open-data org page |
| Depots / régulation | Bus districts and multiple **dépôts**; metro traffic/exploitation services — Rosa’s job class is institutional, not imported. | TRANSTU organisational reporting (dépôts / trafic) |
| Scheduled data for sim | Official TRANSTU GTFS and stop référentiel on `catalogue-data.transport.tn` — usable as scheduled truth in SUMO. | Ministère des Transports CKAN |
| Congestion context | Urban agglomerations face daily congestion, air pollution, and road-safety stress after car-oriented growth and strained collective transport. | CODATU / AFD *Vers une mobilité urbaine durable en Tunisie* |
| Priority vehicles | Law lists priority / urgent-intervention vehicles and equipment rules; other users must yield when special signals are used. | Décret n° 2000-149 (2000); Code de la route sanction tables (Décret 2010-262) |
| Signal ownership | MEHAT UGOSMREPSL follows luminous signalling on the classified network; municipalities operate local junctions — Yuki’s accountability exists. | MEHAT Ponts et chaussées org pages |
| Air quality governance | ANPE runs the national ambient network (incl. traffic-type stations); Loi 2007-34; NT 106.04. Street-gate exposure ≠ city monitor. | ANPE RNSQA; Loi 2007-34 |
| Local SUMO practice | Tunisian intersection studies already compare static vs adaptive lights in SUMO+Python for queues, energy, emissions. | Othmani et al. (ICAIGE / Logistiqua Tunisian case studies) |

### B. Per-persona Evidence (Tunis practice → transfer; motivates need, does not set target)

| User Persona | Insight | Tunisia practice | Transfer (not Tunis field proof) |
|---|---|---|---|
| Amara | I-4 | Central Tunis crossings serve mixed ages; slow walkers are excluded if clearance assumes “young legs.” | Perceived wait ≈ **2×** (Vallyon et al., ATRF 2009); 20–30 s compliance cliff (NZTA RR440; TfL; DfT LTN 2/95); MUTCD/HCM clearance 1.07→1.0 m/s for older shares. |
| David | I-1, I-2, I-6 | CODATU–AFD: daily Grand Tunis congestion — variance is the lived cost; limited detection makes empty-green waste plausible. | Reliability ratio **0.4** (DfT TAG A1.3); incidents ~**25%** of congestion (FHWA); ATSPM AoG / spillback MOEs. |
| Chidi | I-5 | TRANSTU schedules exist in GTFS; peak congestion and unstable collective service make regularity the rider need. | Wait ≈ **2×** in-vehicle (DfT TAG; Wardman); bunching loop (Newell & Potts; Daganzo); SCOOT bus priority feasibility −39% Southampton. |
| Rosa | I-8, I-9 | TRANSTU dépôt / régulation must manage disruption without owning the signal cabinet. | SCATS ships override + audit as product features (Transport NSW 2022) — what her Possible Solution must look like. |
| Marcus | I-3 | Priority vehicle status is legal (2000-149); siren does not create downstream space. | ALS delay–survival literature (**not** lives saved from sim); US EVP benefits **and** arterial/side-street costs of dense preemption (Nelson & Bullock). |
| Yuki | I-8, I-9 | Local signal owners exist (municipal / MEHAT); adaptive black boxes without explainability will be switched off. | SCATS intervention; Surtrac fallback on sensor/network failure; SCOOT loss of benefit under congestion. |
| Maria | I-6, I-7 | Congestion–pollution link is a stated Tunisian urban issue; ANPE monitors ambient AQ, not every school street. | Near-road school exposure literature (Kingsley); stop-linked emission proxies (Deschle); HBEFA/SUMO = proxy. |
| Omar | I-10 | Peak incidents and recovery are part of congestion reality (CODATU context); no Tunisian universal detection-delay KPI found. | FHWA TIM share 25–30%; clearance / secondary-crash metrics — define our own FAR and miss rates. |

### C. Evidence trail (verified sources)

#### Tunisia / simulation setting

| Topic | Finding | Figure | Source |
|---|---|---|---|
| Operator | TRANSTU bus + métro + TGM; publishes parc and trafic | — | transtu.tn Parc et Trafic |
| Open data | Scheduled TRANSTU GTFS + stop référentiel | scheduled, not live | catalogue-data.transport.tn |
| Mobility stress | Daily congestion, AQ, road safety after car growth / strained TC | — | CODATU–AFD Tunis valorisation |
| EV / priority law | Priority and urgent-intervention vehicle list + signal rules | — | Décret 2000-149 |
| Yield duty | Failure to free the way for announced priority vehicles is sanctioned | — | Code de la route / Décret 2010-262 |
| Signalisation | UGOSMREPSL: lighting + luminous signalling on classified network | — | MEHAT |
| Ambient AQ | National monitoring network; traffic station type exists | — | ANPE RNSQA; Loi 2007-34 |
| Local method | Tunisian intersections in SUMO: adaptive vs static for energy/emissions/queues | — | Othmani et al. Tunisian case studies |

#### Transfer practice (international)

| Topic | Finding | Figure | Source |
|---|---|---|---|
| Pedestrian wait | Frustration after 20–30 s; 2/3 cross on red beyond | 20–30 s | NZTA Research Report 440 (2009) |
| Pedestrian wait | Perceived wait = 2× actual | 2× | Vallyon, Turner & Hodgson, ATRF (2009) |
| Pedestrian wait | Compliance drops after 30 s | 30 s | TfL TTM Handbook via London Assembly Q (2019) |
| Pedestrian wait | Ped-actuated max preset normally 40 s, up to 60 s | 40–60 s | DfT LTN 2/95 (1995) |
| Pedestrian wait | Tolerable wait 20 s (light)–120 s (heavy); avoid cycles >90 s | — | Austroads Part 7 (1994) via NZTA RR440 |
| Accessibility | LPI: NYC −28% ped crashes; PA −58.7%; FHWA CMF 0.87 | — | FHWA-HRT-18-060 (2018) |
| Accessibility | Assistive speeds: cane 0.8, walker 0.6, wheelchair 1.1, amputee 0.7 m/s | — | LaPlante & Kaese (ITE) |
| Accessibility | Clearance 3.5 ft/s (1.07 m/s); 1.0 m/s if >20% users 65+ | — | MUTCD 2009 §4E; FHWA HCM Ch.13 (1998) |
| Accessibility | Blind pedestrians: locating, aligning, onset, completion difficulties | — | Bentzen et al., *JVIB* (2005) |
| Transit value | Wait valued 2× in-vehicle (mean 1.80, n=138) | 2× | DfT TAG A1.3; Wardman meta-analysis |
| Bus bunching | Longer waits, overcrowding, trust loss; self-reinforcing | — | TR Part C (2024); Newell & Potts (1964); Daganzo (2009) |
| Transit priority | SCOOT bus priority: bus times −39% | −39% | Hounsell & McDonald (1986) |
| EMS survival | Each min ALS delay: survival −7% (aOR 0.93) | −7%/min | *PLOS One* (2022) |
| EVP benefit | Cary −14.2%; Houston −18–23% | — | USFA; USDOT ITS JRS |
| EVP cost | Closely spaced preemptions: arterial +20–30 s; side-street +7.6% | — | Nelson & Bullock, TRR 1727 (2000) |
| Engineer tooling | SCATS: manual intervention + audit + incident corridors | — | SCATS Core brochure, Transport NSW (2022) |
| Engineer tooling | SCOOT loses benefits under congestion | — | Hounsell & McDonald (1986) |
| Engineer tooling | Surtrac fallback to default durations | — | Smith et al., CMU Surtrac pilot |
| Exposure | 6.4M US children (13.5%) ≤250 m of a major road | — | Kingsley et al., *IJERPH* (2014) |
| Emissions | Avoided HDV stop ≤0.32 kg CO2, 1.8 g NOx | — | Deschle et al., *Energies* 15:1242 (2022) |
| Driver value | Reliability ratio 0.4 (cars/LGV) | 0.4 | DfT TAG A1.3 §6.3.4 |
| Incident share | 25–30% of metro congestion delay | — | FHWA Freeway Mgmt Handbook; Puget Sound (2006) |
| TIM metrics | Roadway/incident clearance; secondary crashes | — | FHWA-JPO-13-062; FHWA-HOP-15-028 |
| Public opinion | Vendor survey only — directional | — | EY *(Claim flag: not Evidence)* |

### D. World truths + standard metrics (transfer; for Test design)

Canonical detail: `.scratch/coflow5-empathize/research/world-truths-and-metrics.md` (FHWA ASCT MOEs HOP-13-031; ATSPM HOP-20-002; TAT Vol. 6 reliability; DfT TAG; FHWA TIM).

**World truths (established practice)**

1. Mean delay is not enough — report **P90/P95**, buffer / planning-time indices (reliability).
2. Empty green and **spillback** waste capacity and move bottlenecks.
3. Pedestrian wait has a **~20–30 s compliance cliff**; clearance must fit who is crossing.
4. Transit priority should be **conditional** (headway/lateness), not unconditional always-green.
5. Emergency priority has **civilian externality**; measure passage **and** recovery.
6. Operable ATC needs **audit, override, and fallback** when sensors/comms fail.
7. Incidents punch above their time share (~**25–30%** US metro delay handbooks); TIM uses clearance + secondary crashes — **no universal detection-delay number**.
8. Sustainability is **spatial** — network % can hide school-street displacement; HBEFA/SUMO = **proxy**.
9. Simulation compares policies under stated demand; it does not prove Tunis field AQ or lives saved.

**Metric families → personas (what we log in SUMO)**

| Family | Standard metrics (world) | Primary User Personas |
|---|---|---|
| Intersection / arterial | Delay, travel time, queue, stops, % arrivals on green, split failure, v/c | David, Yuki |
| Reliability | P95 TT, buffer time/index, planning time index, on-time %; unfinished trips as failures | David |
| Pedestrian / VRU | Call→WALK delay; mean/P95 wait; % >30 s; clearance truncations; completion | Amara |
| Transit / TSP | Headway mean/CV; passenger wait; bus TT; request/grant/deny + reason; extra car delay | Chidi, Rosa |
| Emergency / EVP | EV TT vs baselines; EV stops; civilian person-delay; recovery time; zero safety breaches | Marcus |
| TIM / incidents | Detection delay, FAR, miss rate; roadway/incident clearance; recovery by severity | Omar |
| Operator health | Reason-code coverage; log completeness; decision latency; fallback activation; data freshness | Yuki, Rosa |
| Environment (proxy) | CO₂/NOx per link (HBEFA); stops near receptors; pre-registered displacement rule | Maria |

**Appraisal / handbook anchors (not our SMART targets)**

| Anchor | Figure | Source |
|---|---|---|
| Reliability ratio (cars/LGV) | 0.4 | DfT TAG A1.3 |
| Wait vs in-vehicle (transit) | ≈2× (meta ~1.80) | DfT TAG; Wardman |
| Ped wait compliance stress | 20–30 s; presets often 40–60 s | NZTA; TfL; DfT LTN 2/95 |
| Incident share of metro delay | ~25–30% | FHWA handbooks |
| Clearance design speed | 1.07 m/s; 1.0 m/s if many 65+ | MUTCD; HCM |

CoFlow SMART numbers (e.g. P95 −5%, headway −15%) remain **proposed experimental criteria**, not FHWA/DfT mandates.

### E. Insight → Evidence → Metric check (devil in the details)

Canonical matrix: `.scratch/coflow5-empathize/research/insight-evidence-alignment.md`.  
Citation precision ledger: `.scratch/coflow5-empathize/research/citation-ledger.md`.

**Wording rule:** *This source supports the mechanism or measurement approach; it does not establish the Tunisian magnitude.*

Each Empathize insight is a **mechanism**. Evidence is Tunis practice + transfer literature. IMATM Table 9 ▲ figures are **not** Evidence. Metrics are **measurement needs**, not proven Tunis magnitudes.

| Insight | Mechanism (safe wording) | Empathize Evidence (allowed) | Not Evidence | Owner | Metric (need) |
|---|---|---|---|---|---|
| **I-1** | Upper-tail predictability can matter more than a small mean cut | CODATU congestion context; TAG A1.3 RR **0.4** (UK appraisal); P95/buffer/PTI methods | Tunis WTP; ▲ BTI 0.68 / 74% leave early | David | P95 TT; unfinished = fail |
| **I-2** | Unobserved demand → empty/ineffective green as structural waste | Limited detection as realistic assumption; ATSPM AoG / split failure | Tunis empty-green %; ▲ 21.3% | David, Yuki | AoG %; split failure; green occupancy |
| **I-3** | EVP constrained by downstream **space**, not only local signal state | Décret 2000-149 priority+yield; Nelson & Bullock *TRR* 1727 externality | Drivers-won’t-yield frame; lives saved; ▲ −8.1% | Marcus (+Amara) | EV TT; stops; downstream occ.; recovery; zero breaches |
| **I-4** | Wait, clearance, completion are separate; standards ≠ Tunis law | Wait ≈2×; 20–30 s stress; MUTCD/HCM/ITE as **transfer assumptions** | ▲ 12 s/18 s / 19%; MUTCD 2023 0.8 m/s | Amara | Wait P95; % >30 s; truncations; completion |
| **I-5** | (a) Bus delay hits many passengers; (b) bunching amplifies waiting | TRANSTU GTFS + strained TC; wait>IVT; Daganzo bunching; SCOOT −39% **feasibility** | Bus≈car delay ratio as Tunis fact; abandon % | Chidi, Rosa | Headway CV; passenger wait; reason codes |
| **I-6** | Local greed can spill back / burden residential links | Downstream-aware ATC MOEs; design risk under CODATU density | Tunis displacement %; ▲ +11/+34/+26 | David, Maria, Yuki | Spillback; residential delay/flow |
| **I-7** | Stop-and-go is an actionable emissions lever; volume alone is too coarse | ANPE ≠ street gate; Deschle HDV×signals; Kingsley context; HBEFA **proxy** | “Volume causes it”; ▲ r=0.81; sim AQ | Maria | Stops near receptors; proxy; displacement rule |
| **I-8** | Without measurement, accountable improvement is blocked | Signal-owner role; ATSPM continuous measures; SCATS audit **pattern** | Tunis “change nothing” statistic; shadowing quotes | Yuki, Rosa | KPI availability; log completeness |
| **I-9** | Without explanation, operators cannot justify/govern automation | SCATS override+audit; Surtrac monitor/fallback; **no** distrust % | AI-distrust %; prototype quotes as Evidence | Yuki, Rosa | Explanation task; override; interlocks |
| **I-10** | Non-recurrent events dominate the delay **tail** | CODATU disruption context; FHWA **US** ~25–30% incident share; TIM metrics | 25–30% as Tunis estimate; ▲ 7%/31% | Omar | Detect/miss/FAR; recovery; incident P95 |

**Rejected / refined (keep visible):**
- I-3: “drivers won’t yield” → **space/storage** problem.
- I-7: “volume drives local emissions” → **stop-and-go** as signal-controllable lever.

**SMART ↔ insight:** P1↔I-4; P2↔I-1+I-2+I-6; P3↔I-5; P4↔I-8+I-9 (transit); P5↔I-3; P6↔I-8+I-9 (signals); P7↔I-6+I-7; P8↔I-10.

**Gate before submission:** every `from-prior-pack` locus in the citation ledger needs human page/DOI verify (Deschle digit table, NZTA 20–30 s sentence, FHWA 25–30% edition, Wardman/Hounsell/Surtrac/SCATS brochure URLs).

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

| User Persona | Core need | Insight | Possible Solution | Proposed success criterion |
|---|---|---|---|---|
| Amara | Accessible, safe crossing | I-4 | Wait-aware priority; conservative clearance; acknowledgement | Lower waits; zero clearance truncations |
| David | Predictable journeys | I-1, I-2, I-6 | Neighbour coordination; queue-aware / downstream-aware adjustment | Lower P95; fewer stops; watch AoG/spillback |
| Chidi | Regular service | I-5 | Conditional headway-gap priority | Reduced headway variance and passenger wait |
| Rosa | Understandable decisions | I-8, I-9 | Dashboard, reason codes, authorised intervention | Complete records; successful operator tasks |
| Marcus | Safe passage + recovery | I-3 | Authenticated corridor priority; pre-clearance; recovery | Faster EV trips at bounded civilian delay |
| Yuki | Reliable control | I-8, I-9 | Health monitoring; safety-constrained override; fallback ladder | Correct fallback; timely diagnosis |
| Maria | Fair distribution | I-6, I-7 | Link-level emissions; stop lever; displacement checks | Gains near sensitive locations; no hidden deterioration |
| Omar | Trustworthy awareness | I-10 | Anomaly detection with uncertainty; stale-data warnings | Acceptable FAR; clear degradation alerting |

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

| # | User Persona | Specific | Measurable | Achievable | Relevant (Evidence ↔ insight) | Time-bound |
|---|---|---|---|---|---|---|
| P1 | Amara | Cut wait; guarantee completion | Mean ≤20 s; P95 ≤40 s (tail); hard cap 40 s under stated assumptions; zero truncations — **proposed**, not MUTCD floors | Rule-based A3 escalation first | **I-4**; Tunis mixed-age crossings; transfer 2× wait / 30 s cliff / 0.6–0.8 m/s | Tier 0 week 6; every episode |
| P2 | David | Predictable, not just faster | P95 and stops/vehicle; unfinished counted; AoG/spillback watched; P95 −5% vs MP under surge **proposed** | P95 from recorded trips | **I-1, I-2, I-6**; CODATU; TAG 0.4; ATSPM AoG | S1–S10; headline week 11 |
| P3 | Chidi | Regular headways | Headway variance −15% vs no priority at ≤3% extra car delay **proposed** | Conditional TSP | **I-5**; TRANSTU GTFS; wait 2×; bunching; SCOOT feasibility only | A3 week 8; H3 on S6 week 11 |
| P4 | Rosa | Understandable, intervenable | 100% reason codes; authorised intervention; warnings with FAR | Logging, not ML | **I-8, I-9** (transit); TRANSTU dépôt; SCATS audit **pattern** | Log from Tier 0; G3 week 10 |
| P5 | Marcus | Faster passage, honest cost | EV −25% / −10%; civilian delay ≤5%; per-mission log **proposed**; never lives saved | SUMO preemption feasible | **I-3**; Décret 2000-149; EVP cost literature | A2 week 7; H2 on S4 week 11 |
| P6 | Yuki | Command at all times | 100% logged; latency <100 ms; fallback time; override + interlocks | Watchdog in transfer ATC | **I-8, I-9** (signals); MEHAT/municipal owner; Surtrac/SCATS fallback | Watchdog from Tier 0 |
| P7 | Maria | Cut near school, no displacement | CO2/NOx per link; proxy labelled; pre-registered displacement rule | λ_eco + HBEFA + per-link diff | **I-6, I-7**; ANPE ≠ street gate; stops lever; HBEFA proxy | A5 week 9; H5 week 11 |
| P8 | Omar | Trustworthy alerts | Delay/FAR/miss/recovery per severity; comms-loss alerting | EWMA/CUSUM first | **I-10**; FHWA 25–30%; no universal detect KPI | A4 week 6; H4/H6 week 11 |

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
| Dashboard task test | TRANSTU régulation, municipal traffic engineers | Explain a decision, identify a fault, choose a response |
| Emergency-response walkthrough | Urgent-intervention / SAMU representatives | Request → passage → recovery under 2000-149 rules |
| Neighbourhood map review | Parents, residents, school reps | Locations/times for environmental checks vs ANPE monitors |
| Incident tabletop | Duty officers | Alerts support investigation without overload |

If stakeholder access is limited, run labelled **proxy walkthroughs** and say so in the report. Do not upgrade IMATM placeholders into interview Evidence.

### Presentation close

Empathize for this simulation starts in **Tunisian practice**: TRANSTU riders and dépôt staff, priority vehicles under Tunisian law, municipal/MEHAT signal owners, and residents who live the Congestion–AQ trade-off. Amara needs accessible crossing time; David needs predictable journeys; Chidi needs regular TRANSTU service; Rosa needs understandable priority decisions; Marcus needs passage *and* recovery; Yuki needs operational control; Maria needs local improvement without displacement; Omar needs trustworthy alerts. International ATC citations transfer product patterns. SUMO tests Possible Solutions — it does not prove Tunis field performance.
