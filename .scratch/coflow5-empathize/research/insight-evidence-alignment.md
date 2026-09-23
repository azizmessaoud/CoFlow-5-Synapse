# Insight → Evidence → Metric alignment (Empathize check)

**Rule:** An insight is a *mechanism* claim Empathize can design against. Evidence must be cited primary sources (Tunisia practice or transfer literature). IMATM Table 9 digits marked ▲ and interview quotes are **placeholders** — they motivated the insight wording in an earlier draft, they are **not** Evidence.

**Spine:** Insight → Tunis practice (if any) → Transfer Evidence → Forbidden digits → Owner persona(s) → Metric → Possible Solution seed.

IMATM source IDs (Amine…) map to CoFlow roster; do not stack people.

| IMATM | CoFlow |
|---|---|
| Amine P-1 | David |
| Karim P-2 | Marcus |
| Nadia P-3 | Amara |
| Hichem P-4 | Chidi (+ Rosa for ops) |
| Emna P-5 | Yuki (+ Rosa for transit audit) |
| Leila P-6 | Maria |
| (incident desk) | Omar |

---

## I-1 — Predictability valued more than mean speed

| Field | Detail |
|---|---|
| **Insight** | Users pay for certainty (over-buffering); variance of journey time matters more than its mean. |
| **Tunis practice** | CODATU–AFD: daily Grand Tunis congestion after modal shift — lived cost is unreliable trips, not only longer means. |
| **Transfer Evidence** | DfT TAG A1.3 reliability ratio **0.4** (cars/LGV); FHWA reliability MOEs (P95, buffer, PTI — TAT Vol. 6). |
| **Not Evidence** | IMATM ▲ mean 27.4 / P90 46.1 / BTI 0.68 / “74% leave ≥15 min early”; “leave 40 min early” quote. |
| **Owner** | David (primary). |
| **Metric** | P95 travel time; buffer index / PTI optional; stops/veh; **unfinished/teleported trips = failures**. |
| **Possible Solution seed** | Neighbour coordination; queue/incident sharing; evaluate upper tail, not mean-only. |
| **SMART note** | P95 −5% vs Max-Pressure under surge = **proposed test**, not TAG mandate. |

## I-2 — Fixed-time plans waste green on empty approaches

| Field | Detail |
|---|---|
| **Insight** | Plans that cannot observe demand structurally serve green to empty approaches while other queues wait. |
| **Tunis practice** | Fixed-time / limited detection is the realistic default for many junctions (MEHAT/municipal ownership; permanent detectors not assumed). Local SUMO studies already compare static vs adaptive. |
| **Transfer Evidence** | FHWA ASCT / ATSPM: % arrivals on green, split failure, green occupancy, empty-approach waste as recoverable inefficiency. |
| **Not Evidence** | IMATM ▲ “21.3% empty green” / “>30% at worst three”. |
| **Owner** | David + Yuki (system health / plan quality). |
| **Metric** | AoG %; split failure; served v/c / green occupancy; approach delay. |
| **Possible Solution seed** | Demand-responsive legal phases (Max-Pressure / actuated); never claim Tunis empty-green %. |

## I-3 — Emergency priority is a network (space) problem

| Field | Detail |
|---|---|
| **Insight** | Green at the stop line fails if the exit is full; space must be created ahead. **Rejected false framing:** “drivers won’t yield” — capacity/space is the binding constraint. |
| **Tunis practice** | Décret **2000-149** + Code de la route: priority / urgent-intervention status and yield duty exist; they do **not** clear downstream queues. |
| **Transfer Evidence** | Nelson & Bullock TRR 1727 (preemption externality +20–30 s / side-street +7.6%); US EVP field travel-time cuts; Surtrac-style corridor coordination patterns. |
| **Not Evidence** | IMATM ▲ “local preemption −8.1%”, “63% still stopped”, “4–8 min lost per peak run”; **simulated minutes → lives saved**. |
| **Owner** | Marcus (primary); Yuki (safety interlocks); Amara (in-crossing outranks). |
| **Metric** | EV TT vs no-priority **and** vs local-only preemption; EV stops; civilian person-delay; recovery time; **zero** clearance/safety breaches. |
| **Possible Solution seed** | Authenticated corridor pre-clear + recovery; pedestrian clearance preserved. |
| **SMART note** | −25% / −10% / ≤5% civilian = proposed; ALS −7%/min literature must not become a lives-saved claim from SUMO. |

## I-4 — Pedestrian timing calibrated to a fictional “average” walker

| Field | Detail |
|---|---|
| **Insight** | Fixed clearance sized for a design median/average excludes slower walkers; wait and crossing time are **two** requirements. |
| **Tunis practice** | Mixed-age central Tunis crossings; app-only request paths exclude low digital comfort (design implication, not a survey %). |
| **Transfer Evidence** | Perceived wait ≈**2×** (Vallyon ATRF 2009); compliance stress **20–30 s** (NZTA RR440; TfL; DfT LTN 2/95 presets 40–60 s); MUTCD 1.07 m/s; HCM 1.0 m/s if many 65+; ITE assistive **0.6–0.8 m/s**; Bentzen *JVIB* completion difficulties. |
| **Not Evidence** | IMATM ▲ “12 s green / 18 s needed”, “19% unfinished”, “median 1.24 / 15th 0.79”; “MUTCD 2023 allows 0.8 m/s”; “wait feels 1.5×”. |
| **Owner** | Amara. |
| **Metric** | Call→WALK delay; mean/P95 wait; % waits >30 s; clearance truncations; crossing completion before conflicting green. |
| **Possible Solution seed** | Accessible request + ack; wait-aware service; conservative clearance / occupancy extension; hard interlock. |
| **SMART note** | Mean ≤20 s / P95 ≤40 s / hard cap 40 s = **proposed engineering criteria** (stricter than “presets up to 60 s”); not literature-mandated floors. |

## I-5 — Transit delay is person-unfair and self-amplifying

| Field | Detail |
|---|---|
| **Insight** | Bus delay ≈ car delay *per vehicle* while carrying many passengers; bunching compounds via dwell feedback. |
| **Tunis practice** | TRANSTU scheduled GTFS exists; CODATU: strained collective transport under congestion — regularity is the rider need. |
| **Transfer Evidence** | Wait valued ≈**2×** in-vehicle (DfT TAG; Wardman ~1.80); Newell & Potts / Daganzo bunching; SCOOT TSP feasibility −39% Southampton (**feasibility, not our target**). |
| **Not Evidence** | IMATM ▲ “bus delay 1.12× cars”, “CV 0.18→0.57”; rider-abandonment %. |
| **Owner** | Chidi (passenger); Rosa (régulation / priority decisions). |
| **Metric** | Headway mean/CV/variance; passenger wait; bus TT; request/grant/deny + reason; extra car delay budget. |
| **Possible Solution seed** | Conditional priority after large gap/lateness — not every bus; pedestrian clearance preserved. |
| **SMART note** | Headway variance −15% at ≤3% car delay = proposed. |

## I-6 — Local optimisation produces downstream harm

| Field | Detail |
|---|---|
| **Insight** | Maximising one junction’s throughput can cause spillback and push traffic onto residential streets. |
| **Tunis practice** | Dense centre corridors + school/residential frontage (CODATU urban stress) — displacement is plausible; no Tunis % claimed. |
| **Transfer Evidence** | ASCT/Max-Pressure downstream-capacity logic; ATSPM queue / oversaturation; Surtrac coordination under short links. |
| **Not Evidence** | IMATM ▲ “+11% local throughput / +34% blocked / +26% residential flow”. |
| **Owner** | David (reliability under surge); Maria (displacement); Yuki (network mode). |
| **Metric** | Downstream queue/occupancy; blocked-junction / spillback events; residential link flow or delay; P95 under surge. |
| **Possible Solution seed** | Downstream-aware arbitration (A1); no greedy specialist wins alone. |

## I-7 — Externalities fall on non-users; stops beat volume as the lever

| Field | Detail |
|---|---|
| **Insight** | Idling/stop-start burdens residents who don’t control signals. **Partial reject:** “congestion volume” alone — **stops** are the actionable lever for signal control. |
| **Tunis practice** | CODATU congestion–pollution link; ANPE ambient network ≠ school-gate street monitor (Loi 2007-34). |
| **Transfer Evidence** | Kingsley near-road schools; Deschle avoided-stop emission factors; HBEFA/SUMO as **proxy only**. |
| **Not Evidence** | IMATM ▲ “r=0.81 stops vs 0.46 VKT”; measured Tunis street AQ from SUMO. |
| **Owner** | Maria. |
| **Metric** | CO₂/NOx **proxy** per link/period; stops near receptors; pre-registered displacement rule. |
| **Possible Solution seed** | Link-level reporting; eco weight with delay budget; before/after map. |

## I-8 — Without observability, no improvement and no accountability

| Field | Detail |
|---|---|
| **Insight** | If the operator cannot forecast or measure a timing change, the rational default is to change nothing. |
| **Tunis practice** | Municipal/MEHAT signal owners exist; annual manual counts / complaint-driven change are the honest low-instrumentation baseline (role fact — not IMATM shadowing quotes). |
| **Transfer Evidence** | FHWA ATSPM purpose (continuous measures); SCATS audit trails; Tunisian SUMO static-vs-adaptive method papers as *lab* observability. |
| **Not Evidence** | IMATM shadowing quotes; “plans from 2016” as verified municipal fact. |
| **Owner** | Yuki (primary); Rosa (transit priority observability). |
| **Metric** | Decision log completeness; before/after KPI availability; reason-code coverage. |
| **Possible Solution seed** | Instrumented evidence bundle; shadow/baseline comparison language in Test. |

## I-9 — Unexplainable controllers get switched off

| Field | Detail |
|---|---|
| **Insight** | Measured delay reduction is not enough; operators must defend decisions to complainants/directors. |
| **Tunis practice** | Same signal-owner and TRANSTU régulation accountability — adoption risk is organisational. |
| **Transfer Evidence** | SCATS override + audit as shipped features; Surtrac operator monitoring (Rapid View); no quantitative “X% distrust AI” survey. |
| **Not Evidence** | Any “engineers distrust AI %”; Emna prototype-review quote as interview Evidence. |
| **Owner** | Yuki (signal); Rosa (TSP deny/grant). |
| **Metric** | 100% reason codes where required; override with **safety interlocks**; usability task (explain / choose mode). |
| **Possible Solution seed** | Reason codes; authorised override; Synapse explains logs — never actuates. |

## I-10 — Worst experiences are non-recurrent; static plans ignore them

| Field | Detail |
|---|---|
| **Insight** | Incidents/events dominate the delay **tail**; average-day plans have no response. |
| **Tunis practice** | Peak disruption is part of Grand Tunis congestion reality (CODATU); Omar’s duty-desk role coordinates police/TRANSTU/signal owner. |
| **Transfer Evidence** | FHWA incidents ~**25–30%** of metro congestion delay; TIM metrics (roadway/incident clearance, secondary crashes); **no universal detection-delay number**. |
| **Not Evidence** | IMATM ▲ “7% of time / 31% of delay”, “recovery 18–26 min”. |
| **Owner** | Omar (primary); David (tail); Marcus (response); Yuki (degraded mode). |
| **Metric** | Detection delay, FAR, miss rate, recovery **by severity**; comms-loss / stale-data alerts; P95 under incident scenarios. |
| **Possible Solution seed** | Residual-based alerts with uncertainty; degrade honestly; recovery tracked past clearance. |

---

## Check results (devil in the details)

| Check | Status |
|---|---|
| Eight personas only; IMATM names mapped not stacked | Pass |
| Table 9 ▲ digits excluded from Evidence | Pass — listed under Not Evidence per insight |
| Tunis law/agencies used only for roles that exist | Pass |
| SCATS/Surtrac/SCOOT labelled transfer | Pass |
| Amara SMART mean≤20 / P95≤40 labelled proposed, not MUTCD | Pass (explicit SMART note) |
| Marcus lives-saved barred | Pass (claim flag 8) |
| Maria HBEFA ≠ ANPE | Pass |
| Omar no universal detect KPI | Pass |
| I-2 empty green has metric owners (AoG / split failure) | Pass — added |
| I-6 spillback shared David/Maria/Yuki | Pass — added |
| I-3 rejected “drivers are the obstacle” recorded | Pass |
| I-7 partial reject volume→stops recorded | Pass |

## Empathize vs later stages

- **Empathize:** insights + Evidence + journeys (pain).
- **Define:** needs / HMWs / SMART (proposed).
- **Ideate/Prototype/Test:** Possible Solutions and SUMO metrics — do not back-fill Empathize Evidence with simulation targets presented as literature.
