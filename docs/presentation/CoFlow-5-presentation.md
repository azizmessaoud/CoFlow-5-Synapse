# CoFlow-5 Synapse — presentation brief

ESPRIT 4DS. Validation of Empathize and Ideation, for Fedi Baccar.

The link to show: user research → evidence → personas → needs and pain points → problem statement → ideas → selected solution.

**Claim we may make.** The system evaluates a constrained incident response in simulation and keeps a record of each decision.

**Claims we do not make.** Prevents accidents in Tunisia. Lives saved. Measured air quality. A Tunis deployment. A winner from one seed.

Ages, jobs, and the sentences on the persona cards are design readings. They are not interviews. Portraits are illustrations.

The six personas in this arc are Amara, David, Chidi, Rosa, Marcus, and Omar. Yuki and Maria are not in this set.

**Control rule.** Only A1 writes the signal, through the safety mask and the signal executor. A2, A3, A4, and A5 request. Synapse explains the log or abstains. The language model never reaches TraCI.

Deck that matches this brief, in 15 slides: `docs/presentation/CoFlow-5-Empathize-Ideation-15.pptx`.

---

## 1. Empathize — problem context

A signal decision hits several people at once.

| What is happening | Why it matters here |
|---|---|
| A light changes while someone is still crossing. | Pedestrians were 28% of 2023 deaths in the WHO investment case that quotes ONSR. The 2024 strategy names older people and people with disabilities. |
| A better average can hide a trip that never finishes. | Vehicle occupants carry most of the health cost in that same case. |
| Buses bunch, then an early bus is treated as urgent. | TRANSTU reported 187.4 million paying passengers in 2018. That is not this year’s headway. |
| A refusal, a full exit, or a stale sensor can look like nothing. | The reader, the crew, and the duty officer each need a record they can check. |

2023 deaths are published as both **2,273** and **1,216**, with the same **5,796** crashes. Show both. Do not average them.

No public adaptive-signal network in Tunis was found.

---

## 2. Empathize — target users

| Who is affected | What the source names | Persona |
|---|---|---|
| Pedestrians, and older people and people with disabilities | 28% of 2023 deaths in the investment case. Named in the 2024 strategy. | Amara |
| Occupants of motor vehicles | Most of the health cost in that case. | David |
| TRANSTU passengers in Greater Tunis | 187.4 million paying passengers in 2018. | Chidi |
| The reader of the crash record | ONSR compiles the national record. One reader, not a second controller. | Rosa |
| Road emergency crews | Civil Protection answers those calls. We did not ride with them. | Marcus |
| The person who must trust the alert | A residual is not a cause. | Omar |

---

## 3. Empathize — user research and evidence

| Method | Status | What it supports |
|---|---|---|
| Interviews | Not collected | Nothing. No quote. |
| Questionnaires | Not collected | Nothing. No percentage from us. |
| Observation / ride-along | Not done | Nothing about a Tunis crew or a specific crossing. |
| Existing data | Used | WHO profile, WHO/UNIATF investment case quoting ONSR, La Presse briefing 17 Jan 2025, INS republished counts, TRANSTU 2018 report. |
| Literature | Used | Clearance guidance, appraisal guidance on wait and reliability, an audit-trail product analogy, a Taipei minute figure labelled as not Tunis. |
| Our simulation | One matched seed | 71, 84, and 70 of 84 trips. Mixed. No winner. Not a Tunis result. |

### Published figures

| Figure | Number | Source |
|---|---|---|
| Reported road deaths, 2019 | 2,273 (84% male) | WHO country profile, Global status report on road safety 2023 |
| WHO estimate, 2021 | 2,004 (interval 1,786–2,222; 16.3 per 100,000) | Same WHO profile |
| Crashes, 2023 | 5,796 | Investment case quoting ONSR, and La Presse briefing of ONSR, 17 Jan 2025. Same total in both accounts. |
| Deaths, 2023, investment case | 2,273 (injuries 7,909) | WHO / Health / Interior investment case quoting ONSR |
| Deaths, 2023, press briefing | 1,216 | La Presse, 17 Jan 2025 |
| Least protected users, investment case | Pedestrians 28%, motorcyclists 32%, cyclists 2% | Same investment case. More than 82% of fatalities male. |
| Cause classes in the 2025 briefing | Inattention about 42% of crashes; speeding about 14% of crashes and about 30% of deaths; unsafe pedestrian crossing about 8% of crashes | La Presse briefing of the ONSR 2024 balance sheet. Cause classes, not a model of our junction. |
| 2024 national, that briefing | 5,687 crashes, 1,169 deaths, 7,786 injuries | Same article |
| Tunis governorate, 2024 | 953 crashes, 136 deaths, 1,146 injuries | Same article. Highest crash count among governorates. Not one intersection. |
| TRANSTU paying passengers | 187.4 million in 2018, bus and rail | TRANSTU activity report 2018. Not current ridership. |

### One simulation record

Matched seed 37. One seed. Mixed. No winner. The classroom watch scene is seed 53 and is not this row.

| Controller | Trips finished | Mean wait | P95 wait |
|---|---|---|---|
| Fixed-time | 71 / 84 | 13.17 s | 33 s |
| Actuated | 84 / 84 | 10.35 s | 16 s |
| Cooperative Max-Pressure | 70 / 84 | 14.21 s | 25 s |

Source: `harness/work/10c-evidence-page/artifacts/evidence-page.txt`. Unfinished trips stayed in the count. That is David’s evidence. It is not a Tunis result.

---

## 4. Empathize — key findings

1. The people harmed are named in official counts: pedestrians, occupants, and public-transport passengers. The 2024 strategy also names older people and people with disabilities.
2. Two death totals exist for 2023, 2,273 and 1,216, beside the same 5,796 crashes. A single death number would hide that.
3. A mean can improve while trips stay unfinished. On seed 37, actuated finished more trips. Max-Pressure did not win.
4. No public adaptive-signal network in Tunis was found. A 2018 passenger total is not today’s bus gap.
5. An alert that names a cause, or a stale sensor shown as healthy, would go beyond the evidence.

---

## 5. Empathize — personas

Each card is a reading of one group in the evidence. The statement is a synthesis, not a quote. The portrait file is an illustration.

### Amara — 74 — retired pedestrian; uses a cane

Affected while she is still in the crossing.

- **Situation.** Crosses a busy central street for shops and transit. Tunis design context, as an assumption.
- **Statement.** “I need enough time to finish crossing, even when traffic is busy.”
- **Need.** Acknowledgement, shorter waiting, and enough clearance to finish.
- **Fear.** Cars receive green while she is still crossing.
- **Uses.** Push-button, audible or visual feedback. No phone required.
- **Rejects.** Shortened clearance, inaccessible apps, invented success claims.
- **Evidence.** Perceived wait about twice observed wait in one New Zealand study. Clearance guidance about 1.07 m/s, and slower where needed. Pedestrians 28% of 2023 deaths in the investment case. The 2024 strategy names older people and people with disabilities.
- **Problem.** Clearance assumes a faster walk than hers.
- **Measure, proposed.** Mean, P95, and max wait, plus zero clearance truncations. A fixture count of zero truncations is not crashes prevented.

### David — 41 — delivery-van driver

Affected on the trip that does not finish. The “more than 60 stops” day is a design reading.

- **Statement.** “I can plan around a longer trip if I know how long it will actually take.”
- **Need.** Predictable journeys, fewer stops, and visible incidents.
- **Fear.** A better mean hides unfinished or extreme trips.
- **Uses.** Work phone, GPS, and the delivery round.
- **Rejects.** Best-case headlines and deleted unfinished trips.
- **Evidence.** Appraisal guidance uses 0.4 as a reliability ratio for journey-time variability. Occupants carry most of the investment case’s health cost. Seed 37 is mixed.
- **Problem.** A better average hides the late or unfinished trip.
- **Measure, proposed.** Completed and unfinished trips, P95 and max duration, stops and standstill.

### Chidi — 27 — frequent bus passenger

Affected by a long gap between buses.

- **Situation.** High-frequency corridor, where regularity is the service.
- **Statement.** “Buses should arrive regularly — not three at once after a long wait.”
- **Need.** Priority only for a late bus or a large headway gap.
- **Fear.** Three buses arrive together after one long gap.
- **Uses.** A passenger app when it exists. Otherwise the stop.
- **Rejects.** Priority for every bus, and pedestrian clearance sacrificed for transit.
- **Evidence.** TRANSTU 187.4 million paying passengers in 2018, not this year. Waiting time is valued above in-vehicle time in appraisal guidance.
- **Problem.** Buses bunch, then the early bus is treated as urgent.
- **Measure, proposed.** Lateness, headway variation, a passenger-wait proxy, and the effect on other traffic.

### Rosa — 52 — incident-report reader

Affected by a refusal that has no reason. She does not change the light.

- **Statement.** “Show me why priority was granted or denied, and let me respond safely.”
- **Need.** Positions, headways, confidence, reason codes, and a joined audit trail.
- **Fear.** A black box refuses priority and leaves no history.
- **Uses.** Depot tools, a vehicle-location screen, radio, and a dashboard.
- **Rejects.** Unsupported predictions, and an override outside the safety mask.
- **Evidence.** ONSR compiles the crash record. SCATS documents monitoring, manual intervention, and audit trails. That is an analogy, not a Tunis control room we visited.
- **Problem.** A refusal with no reason cannot be checked after the shift.
- **Measure, proposed.** Reason-code coverage, and an explanation of one yes and one no.

### Marcus — 34 — urban ambulance crew

Affected himself, and the people his priority delays. He stands for Civil Protection. We did not ride with a crew.

- **Statement.** “Get us through safely, and make sure traffic recovers after we pass.”
- **Need.** A trusted route and ETA request, a downstream check, and controlled recovery.
- **Fear.** A green light into a full link only moves the queue.
- **Uses.** Dispatch tablet, GPS, radio, lights, and siren.
- **Rejects.** Cutting an occupied crossing, and translating simulation seconds into casualties.
- **Evidence.** Civil Protection answers road emergencies. One Taipei cohort associated each extra ALS minute with 7% lower adjusted odds. That citation is not a Tunis result. Preemption can add network delay. This simulation does not output lives saved.
- **Problem.** A green light into a full exit only moves the queue.
- **Measure, proposed.** Emergency time, civilian delay, downstream rejection, and recovery. Not lives saved.

### Omar — 55 — network duty officer

Affected when a queue might be a crash, extra demand, or a dead sensor. Portrait file: `p8-omar.png`. He is the sixth card.

- **Statement.** “Tell me what is wrong, why you think so, and whether I can still trust the data.”
- **Need.** Severity, observations, uncertainty, freshness, and a data-health warning.
- **Fear.** False alarms, or a frozen screen that hides the real condition.
- **Uses.** Radio, a camera wall, incident tools, and a dashboard.
- **Rejects.** Alerts without evidence, and an anomaly presented as a proven cause.
- **Evidence.** The detector has classes. An anomaly does not name a cause. An estimate that incidents are about 25–30% of congestion is a US citation, not a map of these junctions.
- **Problem.** A residual can be a crash, extra demand, or a sensor that has gone quiet.
- **Measure, proposed.** Detection delay, false alarms, misses, stale data, and recovery.

---

## 6. Empathize — needs and pain points

| Who | Need | Pain | Expectation |
|---|---|---|---|
| Amara | Enough time to finish | Cars go green while she is still crossing | The conflicting green stays held |
| David | The real duration, including the bad trip | A better mean hides the unfinished trip | Unfinished trips stay on the page |
| Chidi | A regular gap | Three buses after one long wait | An early bus gets nothing |
| Rosa | A reason she can read later | A refusal with no history | A citation, or an abstention |
| Marcus | A path through, then recovery | Green into a full exit | The exit is checked. Delay to others is logged |
| Omar | A class he can trust | A frozen screen, or a guessed cause | Freshness is shown. Stale stays stale |

---

## 7. Ideation — problem statement

How might a simulated signal serve the person still crossing, the unfinished trip, the bus gap, the reader of the refusal, the crew at a full exit, and the officer who must not be told a residual is a cause — while only one component writes the light, and every decision keeps a source?

The problem is not “reduce deaths in Tunisia.” That result is not something this evidence can support.

Out of scope for the claim: lives saved, measured air, a Tunis deployment, and a winner from one seed.

---

## 8. Ideation — how might we

These questions were written from the needs table. They were not collected in a workshop with users.

| Who | How might we… |
|---|---|
| Amara | …hold the conflicting green until the crossing finishes, and count every time it is cut? |
| David | …show unfinished trips beside the mean, so a better average cannot hide the tail? |
| Chidi | …give green only after an unusual gap, and give an early bus nothing? |
| Rosa | …explain one grant or one denial with a reason code, or abstain? |
| Marcus | …check the exit before green, then recover, without cutting the crossing? |
| Omar | …publish the class, the confidence, and the freshness, and refuse to name the cause? |

---

## 9. Ideation — ideas generated

Method: one idea per persona need, written beside the source, then kept or refused. Not SCAMPER. Not a user workshop. The refused column is part of the evidence.

| Who | Idea we kept | Idea we refused |
|---|---|---|
| Amara | Hold the green. Count truncations. | A camera that guesses her ability. |
| David | Keep unfinished trips in the count. | A scraped live map treated as his trip. |
| Chidi | Priority only after a real gap. | Green for every bus. |
| Rosa | One cited explanation, or abstain. | A chatbot that negotiates the phase. |
| Marcus | Request, exit check, then recovery. | An always-green corridor, or “lives saved.” |
| Omar | Class, confidence, freshness. | A news scrape that declares a crash. |

Also refused: a scraped map colour or a news post treated as a ground-truth crash; a heatmap with no denominator; a sentence that writes the light.

### Selection criteria

A kept idea must:

1. Name the person affected. A solution with no person is dropped.
2. Point at published data, literature, or a labelled simulation row.
3. Invent nothing: no interview quote, no survey percentage, no Tunis digit we do not have.
4. Leave the light to one writer. Specialists may request. Only A1, through the safety mask, sets the phase.
5. Leave a record. Rosa can read a grant, a denial, or an abstention.

---

## 10. Ideation — selected solution

Advisers request. One writer decides. The record stays.

| Need | What the selected concept does |
|---|---|
| Amara finishes the crossing | A3 asks. A1 holds the conflicting green. Truncations are counted. |
| David sees the bad trip | Unfinished trips stay beside the mean. |
| Chidi gets a gap, not a bunch | A3 asks only for a late bus or a large gap. Pedestrian clearance stays ahead of the bus. |
| Rosa can check the no | One cited reason, or an abstention. She does not write the signal. |
| Marcus is not sent into a full exit | A2 asks. A1 checks the exit, then recovers: Max-Pressure, then actuated, then fixed-time. Civilian delay is logged. |
| Omar is not told a guessed cause | A4 publishes the class, the confidence, and the freshness. Stale data leaves A1 on local control. |

Incident packs change the street inside SUMO. The language model explains the log, or abstains. It never writes the light.

This evaluates incident response in simulation and keeps the evidence. It does not prevent accidents in Tunisia.

---

## 11. How the selected concept runs

These slides describe the concept. The flood scene is a demo script. It is not a saved Tunis result, and it is not a measured flood run.

### Provenance

The collection table comes before any map. A stale feed is labelled stale.

| Feed | What the row must carry | If it is stale |
|---|---|---|
| OpenStreetMap | Snapshot date, licence, and the edges it covers | Show the date. Do not call it today’s speed. Row 14 is not started. |
| Weather | Station, junction, and hour, or the row is absent | No join means no weather layer. Rain is not a cause. |
| Incident | Type, place, start, duration, severity, source, confidence | An old incident stays marked stale. It does not look live. |
| SUMO run | run id and scenario hash | A saved run is not a live city. |
| Survey | Who was asked, how many, the date, the answers | No file means the cell stays empty. |

### Literature and SUMO

Literature motivates the need. SUMO holds a labelled assumption. It does not hold an invented Tunis digit.

| Person | Literature may say | SUMO may hold | SUMO must not hold |
|---|---|---|---|
| Amara | Slower clearance is required where people walk slowly | A labelled walking band and a counted truncation | Her age, or a Tunis crossing we did not measure |
| David | The tail matters, not only the mean | Unfinished trips kept in the count | A winner from one seed |
| Chidi | Waiting is costly for passengers | Priority only after an unusual gap | Today’s TRANSTU headway |
| Marcus | Priority can add delay elsewhere | Exit check, recovery, civilian delay | Lives saved |
| Omar | An incident is not the same as a dead sensor | Class, confidence, and freshness | A guessed cause |

### One incident engine

Flood, weather, emergency, police, accident, and a combined pack are packs, not extra AIs. The same network stays. Only the pack changes. SUMO applies the restriction.

Every pack carries: type, location, start, duration, severity, edges, confidence, source.

### Closed loop

Observe → A4 → A2, A3, and A5 → A1 → safety mask → SUMO → measure → Synapse.

The six personas are the acceptance criteria for that record, not decoration.

| Person | Acceptance |
|---|---|
| Amara | Crossing stays protected. Truncations are counted. |
| David | Unfinished trips stay in the count. |
| Chidi | An early bus gets nothing. Clearance stays ahead of the bus. |
| Rosa | Every grant and every denial has a reason code. |
| Marcus | The exit is checked. Civilian delay is logged. Not lives saved. |
| Omar | State, confidence, and freshness. Stale shows as stale. |

### Demo script, not a saved result

- Pick settings and run. The SUMO window is the live picture. Ops panels start empty. Empty is not a hidden all-clear.
- One grid, mixed demand labelled as demand, heavy rain, then a flood pack, an ambulance request with an expiry, and a chosen compliance share.
- The flood closes edge E17. Queues form on the approaches. Route B is an advisory. Acceptors may reroute. A refusal stays.
- A4 may publish queue up, speed down, travel time up, availability down, a class of incident or congestion, a confidence, and fresh or stale. It may not say “crash confirmed” without a crash file, and it may not name the cause.
- A5 may request Route B and describe impact as a projection. A3 may request protection for the crossing and for transit clearance. Neither calls TraCI.
- A2 asks. A1 alone decides with cooperative Max-Pressure. The mask passes. The executor writes the phase. Rosa reads the reason code.
- Numbers on the proof slide are measured fields from that run: wait, trips, emergency delay, truncations, accept, refuse. A blank is not filled in later. Synapse cites the incident, the event, and the policy, or abstains.

---

## 12. What to say at the end

User research, then evidence, then personas, then needs, then the problem, then the ideas, then the selected solution.

No lives saved. No measured air. No Tunis deployment. No winner.
