# CoFlow-5 Ideate Finalization — Persona-Led Agentic-AI Architecture

**Status:** Design Thinking Ideate addendum. This does not reopen Empathize or claim Prototype/Test completion.

1. **CAPTURE 1=d:** the decision matrix is the source of truth; the presentation view is derived from it.
2. **CAPTURE 2=b:** use prototype-safe data now and design later connectors; do not ship fragile scraping or live operations.
3. **CAPTURE 3=b:** keep five top-level domain agents; only bounded Synapse research, data-quality, and explanation sub-agents may be added.
4. **HMW:** How might we use data and cooperating intelligent agents to make Grand Tunis traffic more efficient, adaptive, and sustainable while keeping trade-offs safe, explicit, auditable, and honest when data or agents fail?
5. **ADR-0001:** A1 alone writes signals using cooperative Max-Pressure behind the safety mask; A2–A5 publish typed advice; recovery is `Max-Pressure -> actuated -> fixed-time`; Synapse never reaches TraCI.

**Working roster fixed by professor / PR #3:** P1 Amara, P2 David, P3 Chidi, P4 Rosa, P5 Marcus, P6 Yuki, P7 Omar. Maria and Leila are not personas. I-6 spillback belongs to David and Yuki. I-7 is a deferred optional A5 system KPI with no persona.

**Evidence wording:** This source supports the mechanism or measurement approach; it does not establish the Tunisian magnitude.

---

## A. Decision matrix — source of truth

`Carry` fits existing roles. `Stretch` needs a deferred connector or bounded Synapse sub-agent. `Break` violates authority or honesty and must be `Reject`.

| idea_id | persona | pain / HMW | insight | data needed | honesty label | agent (A1–A5 / Synapse±sub) | evidence / metric | architecture fit (Carry / Stretch / Break) | future risk if shipped | Now / Later / Reject | reason |
|---|---|---|---|---|---|---|---|---|---|---|---|
| AM-01 | Amara | Request may not register | I-4 | Button event and acknowledgement time | simulation-test | A3 | Call-to-ack latency; missing acknowledgements | Carry | Broken button looks accepted | Later | Useful after request-channel evidence exists |
| AM-02 | Amara | Wait and completion are separate | I-4 | Call time; presence; phase; crossing occupancy | transfer-method | A3 | Mean and P95 wait; percent over 30 s; zero truncations | Carry | Bad occupancy sensor could hold or release wrongly | Now | Transparent deadline and clearance state fit A3 and the safety mask |
| AM-03 | Amara | Fixed clearance may not fit slower walkers | I-4 | Crossing length and declared design-speed band | transfer-assumption | A3 | Completion before conflicting green | Carry | Imported speed becomes a false Tunis law | Later | Keep conservative configurable assumptions, not biometric inference |
| AM-04 | Amara | App-only requests exclude her | I-4 | Physical call and accessible-channel status | Tunis-practice | A3 | Request success by channel | Carry | Digital channel silently becomes mandatory | Later | Multi-channel input is persona-fit but outside current evidence slice |
| AM-05 | Amara | Repeated deferral creates unsafe pressure | I-4 | Consecutive deny count and active higher-tier reasons | team-judgment | A3 | Maximum consecutive deferrals; reason coverage | Carry | Emergency storms can starve crossing service | Later | Needs explicit anti-starvation policy and safety review |
| AM-06 | Amara | She needs understandable status | I-4 | Immutable request and disposition events | transfer-pattern | Synapse-explanation | Explanation task success; citation completeness | Stretch | Fluent text could contradict the signal state | Later | Explain frozen events only and fall back to deterministic text |
| AM-07 | Amara | Crazy idea: phone camera estimates walking ability | I-4 | Video or biometric inference | privacy-risk | Synapse-research | No valid project metric | Break | Privacy harm and unsafe classification | Reject | Unnecessary sensitive inference and no control-grade evidence |
| AM-08 | Amara | Worst idea: LLM decides when WALK ends | I-4 | Prompt and camera feed | rejected-claim | Synapse | Safety violations | Break | Non-deterministic clearance truncation | Reject | Synapse has no actuation and clearance is deterministic |
| DV-01 | David | Mean improvement can hide severe late trips | I-1 | Completed and unfinished trip records | simulation-test | A1 | P95 travel time; buffer index; unfinished as failures | Carry | Teleports omitted and tail looks better | Later | Metric is mandatory but the selected Now idea adds coordination |
| DV-02 | David | Poor coordination creates repeated stops | I-1,I-2,I-6 | Queues; receiving capacity; neighbour outflow; freshness | transfer-method | A1 | P95; stops per vehicle; spillback events | Carry | Stale neighbour state amplifies spillback | Now | Cooperative Max-Pressure already carries bounded neighbour evidence |
| DV-03 | David | Empty or ineffective green wastes capacity | I-2 | Green occupancy; arrivals on green; served demand | transfer-method | A1 | Arrivals on green; split failure; green occupancy | Carry | Weak detectors turn absence into false emptiness | Later | Add only with data-quality state and no Tunis prevalence claim |
| DV-04 | David | Weather changes the normal demand regime | I-1 | Archived rain; fog code; model; time alignment | external-context | A4 | P95 and residual error by weather regime | Stretch | Correlation gets narrated as crash causation | Later | Weather is a regime tag, not proof of cause |
| DV-05 | David | Roadworks can invalidate expected routes | I-6 | Official or labelled roadwork geometry and validity | official-or-unverified | A4 | Detection delay; affected-route reliability | Stretch | Expired closure remains active | Later | Requires a versioned official connector and expiry rules |
| DV-06 | David | Heatmap may reveal recurrent unreliable links | I-1,I-6 | Trip traces aggregated by link and time window | derived-method | Synapse-data-quality | Link P95; sample count; window | Stretch | Pretty sparse cells imply certainty | Later | Derived view must expose denominator, method, and window |
| DV-07 | David | Crazy idea: scrape map traffic colours as truth | I-1 | Proprietary map tiles | scrape-risk | Synapse-research | No auditable ground truth | Break | Licence breach and unexplained vendor score | Reject | OSM geometry is allowed; proprietary display scraping is not evidence |
| DV-08 | David | Worst idea: LLM changes phases to meet delivery promises | I-1 | Prompts and private schedules | rejected-claim | Synapse | No safe metric | Break | Private benefit overrides public safety | Reject | A1 alone actuates and no persona receives private signal control |
| CH-01 | Chidi | Faster buses can still arrive in packs | I-5 | Vehicle arrivals and passenger-weighted headways | simulation-test | A3 | Headway CV; excess wait; bunching events | Carry | Sparse service makes CV unstable | Later | Establish denominators and service regime first |
| CH-02 | Chidi | Schedule is not live position | I-5 | TRANSTU GTFS hash; service dates; feed version | scheduled-not-live | A3 | Schedule coverage and feed-validity checks | Carry | Expired feed presented as operating truth | Later | Required provenance seam before transit scenarios scale |
| CH-03 | Chidi | Large gaps need conditional priority | I-5 | Observed headway gap; lateness; occupancy proxy; active constraints | transfer-method | A3 | Headway CV; passenger wait; extra car delay; grant and deny reasons | Carry | Repeated bids starve pedestrians or general flow | Now | Typed expiring request fits A3 and A1 arbitration |
| CH-04 | Chidi | Signal priority cannot solve all bunching | I-5 | Dwell and stop-holding scenario parameters | theory-transfer | A3 | Gap recovery with and without holding | Stretch | System credits signals for depot or dwell failures | Later | What-if only until operations evidence supports the lever |
| CH-05 | Chidi | Riders need a reason when priority is denied | I-5 | Message disposition and blocking reason code | transfer-pattern | Synapse-explanation | Citation and reason-code coverage | Carry | Explanation omits who paid for priority | Later | Explain immutable A1 disposition with trade-off fields |
| CH-06 | Chidi | Unusual headway may signal disruption | I-5 | Expected and observed headway residuals; feed age | transfer-method | A4 | FAR; miss; residual by severity | Carry | Planned frequency change triggers false incident | Later | Condition baseline on service calendar and freshness |
| CH-07 | Chidi | Crazy idea: every bus gets green immediately | I-5 | Bus detection only | team-judgment | A3 | Extra car and pedestrian delay | Carry | Unbounded transit requests cause starvation | Reject | Technically messageable but contradicts conditional person-based priority |
| CH-08 | Chidi | Worst idea: infer live buses from GTFS schedule | I-5 | Static GTFS only | rejected-claim | A3 | Position error cannot be measured | Break | Fictional buses drive requests | Reject | Scheduled offer is not AVL or live observation |
| RO-01 | Rosa | Information is scattered | I-8 | Bus requests; dispositions; headways; source freshness | Tunis-practice | Synapse-data-quality | Join completeness; stale-source count | Stretch | Mismatched clocks create a false timeline | Later | Bounded read-only joining is useful after source identities are stable |
| RO-02 | Rosa | She cannot justify a grant or denial | I-8,I-9 | Immutable request; A1 decision; constraints; reason codes | transfer-pattern | Synapse-explanation | Explanation task success; supported citation rate; abstention | Carry | Fluent explanation hides a missing event | Now | Frozen-event retrieval plus verifier directly serves her need |
| RO-03 | Rosa | She needs warning before headway collapse | I-8 | Headway residual and confidence over time | simulation-test | A4 | Warning lead; FAR; miss by severity | Carry | Alert fatigue causes warnings to be ignored | Later | Gate after Omar alert contract and operator threshold review |
| RO-04 | Rosa | Intervention must not become signal control | I-9 | Approved transit request schema and operator identity | authority-bound | A3 | Authorized request rate; A1 disposition | Carry | Request UI is mistaken for direct override | Later | Rosa may request; only A1 may execute a legal action |
| RO-05 | Rosa | Shift review needs a shared timeline | I-8,I-9 | Joined message, decision, fault, and outcome IDs | evidence-join | Synapse-explanation | Join resolution; unsupported statement count | Carry | Cross-run events are merged | Later | Reuse immutable run, scenario, event, and message identities |
| RO-06 | Rosa | Data-quality worker could flag missing AVL later | I-8 | Future AVL feed metadata and heartbeat | future-connector | Synapse-data-quality | Freshness and completeness state | Stretch | Sub-agent silently repairs or invents positions | Later | Worker may flag and abstain, never impute control facts |
| RO-07 | Rosa | Crazy idea: autonomous LLM negotiates green time | I-9 | Conversation state | rejected-claim | Synapse | No deterministic authority proof | Break | Hidden negotiation bypasses priority tiers | Reject | Typed requests and deterministic arbitration replace conversation |
| RO-08 | Rosa | Worst idea: erase denied requests to reduce clutter | I-8,I-9 | Mutable audit store | rejected-claim | Synapse | Audit completeness failure | Break | Accountability and error analysis disappear | Reject | Denials and expired messages remain immutable evidence |
| MC-01 | Marcus | Local green is useless if exit is blocked | I-3 | Route; ETA; downstream occupancy; active crossing | Tunis-practice | A2 | EV stops; downstream space at arrival | Carry | Occupancy is stale and pre-clear fills the exit | Later | Foundational state for the selected corridor request |
| MC-02 | Marcus | Passage and recovery are one mission | I-3 | Authenticated route; ETA; corridor queues; crossing; expiry | transfer-method | A2 | EV travel time; civilian person-delay; recovery; zero safety breaches | Carry | Spoofed or replayed priority causes corridor disruption | Now | Expiring corridor pre-clear bid fits A2 and A1 authority |
| MC-03 | Marcus | Multiple emergency requests may conflict | I-3 | Authenticated request IDs; ETA; severity class; routes | team-judgment | A2 | Conflict count; bounded arbitration reasons | Carry | Priority thrash blocks both corridors | Later | Needs explicit anti-thrash and tie policy before scale |
| MC-04 | Marcus | Weather may alter travel-time uncertainty | I-3 | Archived weather regime joined to mission scenario | external-context | A4 | ETA residual by regime | Stretch | Weather is blamed for every delay | Later | Context only; no crash-cause inference |
| MC-05 | Marcus | Review must show civilian cost | I-3 | Mission event; affected trips; recovery window | simulation-test | Synapse-explanation | Benefit-cost timeline with supported fields | Carry | Faster EV result becomes a lives-saved headline | Later | Explain time and externality only; preserve claim flag |
| MC-06 | Marcus | Official incident feed could corroborate later | I-3 | Source class; incident ID; location; validity; confidence | future-connector | A4 | Corroboration state and age | Stretch | Duplicate or late incident is treated as current | Later | Connector needs deduplication, provenance, and expiry |
| MC-07 | Marcus | Crazy idea: infer ambulance from siren audio scrape | I-3 | Ambient audio | privacy-risk | A4 | Unknown precision in this project | Break | False priority and privacy harm | Reject | Use authenticated scenario requests, not unverified audio inference |
| MC-08 | Marcus | Worst idea: always-green corridor with no recovery | I-3 | Emergency flag only | rejected-claim | A2 | Civilian delay and safety failure | Break | Gridlock, unsafe transitions, and no recovery | Reject | Safety mask, downstream space, expiry, and recovery are mandatory |
| YK-01 | Yuki | She needs to know whether agents are healthy | I-8 | Heartbeats; deadlines; data age; board health | transfer-pattern | A1 | Health coverage; stale-source detection | Carry | Heartbeat storm crowds out useful messages | Later | Define bounded health topic and aggregation first |
| YK-02 | Yuki | She must diagnose and regain command | I-8,I-9 | Controller mode; faults; rejected actions; freshness; transitions | transfer-pattern | A1 | Log completeness; fallback activation; interlock integrity | Carry | Frozen dashboard shows healthy while fallback runs | Now | Deterministic watchdog and visible recovery ladder fit current design |
| YK-03 | Yuki | Local optimisation can move spillback | I-6 | Queue; receiving capacity; blocked-junction events | transfer-method | A1 | Spillback count; neighbouring delay and flow | Carry | Incomplete network view creates oscillation | Later | Add bounded neighbour state and conservative stale handling |
| YK-04 | Yuki | Override must preserve mandatory safety | I-9 | Authorized operator; requested mode; safety-mask result | authority-bound | A1 | Override audit; rejected unsafe overrides | Carry | Credential misuse or social pressure bypasses policy | Later | Override selects bounded mode, never conflicting greens |
| YK-05 | Yuki | Map or signal-plan drift can invalidate assumptions | I-8 | OSM snapshot; plan source; validation findings; version | data-governance | Synapse-data-quality | Unresolved geometry and plan discrepancies | Stretch | Bad turn or phase mapping reaches evaluation | Later | Human-reviewed discrepancy report before scenario acceptance |
| YK-06 | Yuki | Research worker can compare policy evidence | I-9 | Allow-listed documents and citation ledger | transfer-pattern | Synapse-research | Retrieval relevance; source-scope labels | Stretch | Transfer guidance is narrated as Tunisian law | Later | Worker must retain jurisdiction and evidence class |
| YK-07 | Yuki | Crazy idea: self-resuming AI after any fault | I-9 | Model confidence only | team-judgment | Synapse | Unsafe resume count | Break | Repeated failure loop without health proof | Reject | Resume requires deterministic health checks and human-governed policy |
| YK-08 | Yuki | Worst idea: give Synapse a TraCI emergency tool | I-9 | LLM tool call | rejected-claim | Synapse | Boundary test failure | Break | Second writer and prompt-mediated actuation | Reject | Capability isolation, not prompting, prevents actuation |
| OM-01 | Omar | Normal fluctuation hides disruption | I-10 | Forecast and observed counts, speeds, queues, occupancy | simulation-test | A4 | Residual distribution by regime | Carry | Baseline drift creates repeated alarms | Later | Establish residual evidence before thresholding |
| OM-02 | Omar | He needs transparent first-line anomaly alerts | I-10 | Time-aligned residuals; source health; expiry; context | transfer-method | A4 | Detection delay; FAR; miss; recovery by severity | Carry | Missing vision is classified as normal | Now | EWMA/CUSUM is explainable, bounded, and already fits A4 |
| OM-03 | Omar | Abrupt regime changes evade fixed thresholds | I-10 | Residual sequence and change score | exploratory-method | A4 | Change-point lead, FAR, miss | Carry | Tuning on one incident overfits the detector | Later | Compare chronologically after transparent baseline |
| OM-04 | Omar | Weather changes expected traffic patterns | I-10 | Archived rain, fog, wind, model resolution and age | external-context | A4 | Residual error and alert rates by regime | Stretch | Weather association is sold as causal crash proof | Later | Weather conditions the baseline; it does not establish incident cause |
| OM-05 | Omar | Several weak sources may corroborate an event | I-10 | Official incident archive; simulation injection; sensor residuals | mixed-source | A4 | Source-agreement state; FAR and miss | Stretch | Rumour or scrape outweighs official and sensor evidence | Later | Use source classes and confidence, not equal-vote fusion |
| OM-06 | Omar | Heatmap should show anomaly and recovery clusters | I-10 | Geocoded alerts; denominator; severity; time window | derived-method | Synapse-data-quality | Cluster count; sample support; recovery window | Stretch | Visual density is mistaken for crash risk | Later | Method, denominator, uncertainty, and window stay visible |
| OM-07 | Omar | Crazy idea: news scraper declares accidents live | I-10 | Unverified articles and social posts | scrape-risk | Synapse-research | No ground-truth guarantee | Break | Rumour triggers operational response | Reject | Scrapes can suggest research leads only, never ground-truth incidents |
| OM-08 | Omar | Worst idea: LLM invents cause and response from a queue spike | I-10 | Alert summary prompt | rejected-claim | Synapse | Unsupported-claim rate | Break | Anomaly becomes fabricated incident and unsafe advice | Reject | Synapse explains recorded alternatives and abstains when cause is unknown |

### A.1 Two-minute professor view — derived from chosen `Now` rows

Each line is one persona, one agent, one metric, and the first way that idea fails.

| Persona | Say this | Agent | Metric | First failure |
|---|---|---|---|---|
| Amara | A wait deadline, and the crossing stays protected until she finishes | A3 | Wait tail, and zero clearance truncations | A bad occupancy sensor can look like an empty crossing |
| David | Neighbouring junctions coordinate, and a blocked exit counts | A1 | P95 travel time, stops, spillback | Stale news from the next junction can make the queue worse |
| Chidi | A bus asks for green only after an unusual gap | A3 | Headway variation, passenger wait, extra car delay | A storm of bus requests can starve everyone else |
| Rosa | The page explains why a request was granted or denied, with a citation, or it abstains | Synapse explanation | Supported explanation, and abstention | Fluent text can hide a missing event |
| Marcus | An authenticated corridor request, then recovery after he passes | A2 | Ambulance time, civilian delay, recovery, safety | A spoofed or replayed request can disrupt the corridor |
| Yuki | Health, fallback, and the safety interlock stay visible | A1 | Fallback time, complete log, interlock intact | A frozen screen can look healthy while control has already fallen back |
| Omar | A residual alert with an explicit statement of whether the sensors can see | A4 | Detection delay, false alarms, misses, recovery, by severity | Stale, missing, invalid, or poisoned data can be shown as a normal road |

**Source rows:** Amara `AM-02`; David `DV-02`; Chidi `CH-03`; Rosa `RO-02`; Marcus `MC-02`; Yuki `YK-02`; Omar `OM-02`.

**Close on Omar:** The highest-risk failure is presenting a network we cannot see as a healthy network.

**Roster and authority:** The roster is seven personas. Yuki is P6. Maria and Leila are not personas. A1 still writes every signal. The explanation page never reaches the simulator.

---

## B. Per-persona ideation — architecture lens

### B.1 Amara — accessible crossing

| Field | Content |
|---|---|
| Need / HMW | Give Amara a crossing that arrives before repeated deferral creates unsafe pressure and still gives enough protected time to complete. |
| Insight IDs | I-4: wait, clearance, and completion are separate; imported standards are transfer assumptions, not Tunisian law. |
| Brainstorm 8 | AM-01 `[A3 Carry Later]` acknowledgement; AM-02 `[A3 Carry Now]` wait and occupancy state; AM-03 `[A3 Carry Later]` configurable slow-walker clearance; AM-04 `[A3 Carry Later]` physical accessible channel; AM-05 `[A3 Carry Later]` anti-starvation; AM-06 `[Synapse Stretch Later]` frozen-event explanation; AM-07 `[Break Reject]` biometric camera; AM-08 `[Break Reject]` LLM WALK termination. |
| Worst Possible Idea -> invert | Let generated text end WALK; invert to deterministic clearance and conflict interlocks whose evidence Synapse can only explain. |
| Chosen Now line | AM-02: A3 publishes wait, presence, and crossing state; A1 and the safety mask preserve completion before conflicting release. |
| Later / Reject | Later: acknowledgement, configurable assumptions, channel access, anti-starvation, explanation. Reject: sensitive inference and any LLM actuation. |
| Data it needs | Button and detector events with source, timestamp, freshness, confidence, crossing geometry, and explicit simulation or transcribed-plan label. |
| Metric | Call-to-WALK delay; mean and P95 wait; percent over 30 s; completion; zero clearance truncations. Thresholds remain proposed tests. |
| Future problem they hit first | A failed or stale occupancy detector can create the dangerous ambiguity between “crossing clear” and “we cannot see.” |

### B.2 David — reliable journeys

| Field | Content |
|---|---|
| Need / HMW | Improve predictable upper-tail journeys, not only the mean, without pushing queues into neighbouring approaches. |
| Insight IDs | I-1 upper-tail reliability; I-2 ineffective green; I-6 downstream spillback and burden. |
| Brainstorm 8 | DV-01 `[A1 Carry Later]` P95 accounting; DV-02 `[A1 Carry Now]` neighbour-aware Max-Pressure; DV-03 `[A1 Carry Later]` ATSPM-like measures; DV-04 `[A4 Stretch Later]` weather regimes; DV-05 `[A4 Stretch Later]` roadworks; DV-06 `[Synapse Stretch Later]` reliability heatmap; DV-07 `[Break Reject]` proprietary map scrape; DV-08 `[Break Reject]` delivery-directed LLM phases. |
| Worst Possible Idea -> invert | Optimize a private delivery promise with an LLM; invert to public, deterministic A1 arbitration evaluated on all completed and unfinished trips. |
| Chosen Now line | DV-02: A1 consumes bounded fresh neighbour state in cooperative Max-Pressure and reports tail reliability plus spillback. |
| Later / Reject | Later: richer MOEs, weather, roadworks, and derived maps. Reject: scrape-as-truth and private or generated actuation. |
| Data it needs | SUMO queues/trips now; OSM snapshot and synthetic demand labels; later official roadworks and probe or loop connectors with validity windows. |
| Metric | P95 travel time, buffer index or PTI, stops per vehicle, arrivals on green, split failure, spillback; unfinished trips count as failures. |
| Future problem they hit first | A stale neighbour queue can make a cooperative action locally plausible but network-harmful. |

### B.3 Chidi — regular transit

| Field | Content |
|---|---|
| Need / HMW | Make high-frequency TRANSTU service regular rather than simply faster, while keeping other users inside an explicit delay budget. |
| Insight IDs | I-5: passenger-weighted delay and bunching are related but distinct mechanisms. |
| Brainstorm 8 | CH-01 `[A3 Carry Later]` headway metrics; CH-02 `[A3 Carry Later]` GTFS provenance; CH-03 `[A3 Carry Now]` conditional request; CH-04 `[A3 Stretch Later]` holding what-if; CH-05 `[Synapse Carry Later]` denial explanation; CH-06 `[A4 Carry Later]` headway anomaly; CH-07 `[Carry Reject]` unconditional green; CH-08 `[Break Reject]` scheduled-as-live inference. |
| Worst Possible Idea -> invert | Treat every scheduled trip as a live late bus; invert to explicit scheduled truth plus observed or simulated positions and expiring conditional requests. |
| Chosen Now line | CH-03: A3 requests priority only after a large observed headway gap or lateness condition; A1 records grant or deny reasons. |
| Later / Reject | Later: validation, anomaly, explanation, and holding studies. Reject: unconditional TSP and fabricated live positions. |
| Data it needs | Official scheduled TRANSTU GTFS with archive hash and service dates; SUMO vehicle observations now; later separately authenticated AVL. |
| Metric | Headway mean, variance and CV; passenger wait; bunching events; bus travel time; grants, denials, reasons; extra car delay. |
| Future problem they hit first | Expired GTFS or a planned frequency change can look like bunching unless schedule validity and observation freshness are separated. |

### B.4 Rosa — understandable transit decisions

| Field | Content |
|---|---|
| Need / HMW | Let Rosa justify and respond to transit-priority decisions without pretending she owns the signal cabinet. |
| Insight IDs | I-8 observability for improvement; I-9 explanation, adoption, and controlled intervention. |
| Brainstorm 8 | RO-01 `[Synapse Stretch Later]` source join; RO-02 `[Synapse Carry Now]` cited explanation; RO-03 `[A4 Carry Later]` headway warning; RO-04 `[A3 Carry Later]` authorized request; RO-05 `[Synapse Carry Later]` timeline; RO-06 `[Synapse Stretch Later]` AVL quality worker; RO-07 `[Break Reject]` LLM negotiation; RO-08 `[Break Reject]` erased denials. |
| Worst Possible Idea -> invert | Hide denied requests; invert to immutable dispositions and an explanation that abstains if the request, decision, or policy citation is missing. |
| Chosen Now line | RO-02: the explanation sub-agent retrieves one frozen request and decision, cites supporting policy, verifies facts, and answers or abstains. |
| Later / Reject | Later: multi-source view, warnings, request UI, shift timeline, future AVL quality. Reject: conversational arbitration and mutable audit. |
| Data it needs | Message and decision IDs, reason codes, headway observations, policy chunks, source timestamps, and operator authorization records. |
| Metric | Join and reason coverage; supported-citation rate; abstention correctness; operator task success; no cross-run merge. |
| Future problem they hit first | An eloquent explanation can conceal a missing or cross-run event unless identity and claim verification fail closed. |

### B.5 Marcus — safe passage and recovery

| Field | Content |
|---|---|
| Need / HMW | Prepare downstream space for an authenticated urgent-intervention vehicle and restore normal operation with civilian cost visible. |
| Insight IDs | I-3: emergency priority is constrained by downstream storage and clearance, not only signal colour. |
| Brainstorm 8 | MC-01 `[A2 Carry Later]` space check; MC-02 `[A2 Carry Now]` corridor bid and recovery; MC-03 `[A2 Carry Later]` competing EV policy; MC-04 `[A4 Stretch Later]` weather ETA context; MC-05 `[Synapse Carry Later]` mission review; MC-06 `[A4 Stretch Later]` official incident connector; MC-07 `[Break Reject]` siren inference; MC-08 `[Break Reject]` always-green. |
| Worst Possible Idea -> invert | Hold a corridor green indefinitely; invert to authenticated expiring requests, protected crossings, downstream checks, bounded civilian externality, and recovery. |
| Chosen Now line | MC-02: A2 publishes an authenticated expiring pre-clear request; A1 arbitrates it and logs passage, externality, and recovery. |
| Later / Reject | Later: richer space, multi-EV, weather, review, official-feed corroboration. Reject: unauthenticated detection and unbounded preemption. |
| Data it needs | Simulation-authenticated route and ETA now; occupancy and crossing state; later official CAD or incident connectors only under agreements and provenance controls. |
| Metric | EV travel time and stops; downstream occupancy; civilian person-delay; recovery time; zero safety violations. Never translate time into lives saved. |
| Future problem they hit first | A spoofed, duplicated, or replayed priority message can make valid control logic serve a false mission. |

### B.6 Yuki — diagnosable and governable automation

| Field | Content |
|---|---|
| Need / HMW | Show Yuki the operating mode, evidence health, decision history, and one bounded way to regain command without bypassing safety. |
| Insight IDs | I-8 observability; I-9 override and adoption; I-6 spillback; I-2 demand visibility. |
| Brainstorm 8 | YK-01 `[A1 Carry Later]` bounded health; YK-02 `[A1 Carry Now]` visible fallback; YK-03 `[A1 Carry Later]` spillback mode; YK-04 `[A1 Carry Later]` interlocked override; YK-05 `[Synapse Stretch Later]` geometry discrepancy; YK-06 `[Synapse Stretch Later]` policy research; YK-07 `[Break Reject]` self-resume; YK-08 `[Break Reject]` Synapse TraCI tool. |
| Worst Possible Idea -> invert | Give the LLM an emergency control tool; invert to capability isolation, deterministic mode transitions, safety-constrained override, and read-only explanation. |
| Chosen Now line | YK-02: A1 and the supervisor expose health, faults, and `Max-Pressure -> actuated -> fixed-time` transitions with interlock evidence. |
| Later / Reject | Later: health aggregation, network burden, override, data QA, policy retrieval. Reject: confidence-only resume and any second writer. |
| Data it needs | Mode and fault events, heartbeats, data age, safety-mask dispositions, OSM and plan versions, document jurisdiction, and operator authorization. |
| Metric | Decision-log completeness; latency; stale-source detection; fallback activation; override audit; safety-interlock integrity. |
| Future problem they hit first | The monitoring path can freeze independently, showing healthy automation while A1 has degraded or fallen back. |

### B.7 Omar — trustworthy incident awareness

| Field | Content |
|---|---|
| Need / HMW | Distinguish normal traffic, anomaly, likely incident, sensor failure, and insufficient vision while communicating uncertainty and recovery. |
| Insight IDs | I-10: non-recurrent events disproportionately affect the delay tail; no universal detection-delay threshold exists. |
| Brainstorm 8 | OM-01 `[A4 Carry Later]` residual baseline; OM-02 `[A4 Carry Now]` EWMA/CUSUM; OM-03 `[A4 Carry Later]` change point; OM-04 `[A4 Stretch Later]` weather condition; OM-05 `[A4 Stretch Later]` source fusion; OM-06 `[Synapse Stretch Later]` anomaly heatmap; OM-07 `[Break Reject]` news truth; OM-08 `[Break Reject]` invented cause. |
| Worst Possible Idea -> invert | Let an LLM name an accident from one queue spike; invert to residual evidence, alternate explanations, explicit vision state, bounded recommendations, and abstention. |
| Chosen Now line | OM-02: A4 issues expiring EWMA/CUSUM residual alerts with severity, confidence, source age, alternatives, and recovery state. |
| Later / Reject | Later: change points, weather-conditioned baselines, fusion, and heatmaps. Reject: scraping as truth and generated incident facts. |
| Data it needs | Time-aligned observations, forecast residuals, source heartbeat and age, simulation incident truth for testing, archived weather context, and later official records. |
| Metric | Detection and verification delay; FAR; missed incidents; recovery by severity; incident-scenario P95; stale-data alert rate. |
| Future problem they hit first | Missing, stale, or poisoned observations are misclassified as “nothing wrong” instead of “we cannot see.” |

---

## C. Omar / A4 anomaly detection — Ideate on its own

### C.1 What counts as an anomaly

| Class | Observable signal | What it does not prove | Vision state |
|---|---|---|---|
| Incident injection | Abrupt residual in flow, speed, queue, or occupancy | Real collision or its cause | anomaly |
| Sensor failure | Flatline, impossible jump, disagreement, missing heartbeat | Road incident | insufficient_data |
| Demand surge | Correlated rise across approaches relative to baseline | Collision | anomaly |
| Weather regime shift | Rain, fog, or wind context plus changed residual distribution | Weather caused a crash | context_changed |
| Stale data | Age exceeds source-specific validity | Network is normal | stale |
| Message loss | Sequence gap, TTL expiry, or board silence | Adviser has no concerns | degraded |
| Unusual headway | Transit residual against valid service calendar | Traffic incident | anomaly |
| Spillback onset | Receiving capacity collapse and blocked movement | Exact initiating cause | likely_network_disruption |

An anomaly is a measurable departure from an expected regime. `Likely incident` requires stronger evidence than `anomaly`; neither is a causal finding. `No anomaly detected` is valid only while required data sources are fresh and sufficiently complete.

### C.2 Detection-method brainstorm and disposition

| Method | Strength | Weakness | Disposition |
|---|---|---|---|
| Persistence or seasonal baseline | Transparent minimum comparator | Misses contextual changes | Now baseline |
| EWMA on forecast residual | Smooths noise and exposes sustained shift | Parameter sensitivity | Now detector |
| CUSUM on forecast residual | Detects cumulative small shifts | Requires reset and drift policy | Now detector |
| Change-point detection | Captures abrupt regime boundaries | Easy to overfit on few incidents | Later comparison |
| Isolation method | Multivariate non-linear candidate | Harder operator explanation | Later, only after transparent baseline |
| Weather-conditioned baseline | Reduces regime false alarms | Weather grid is not junction truth | Later connector |
| Multi-source fusion | Can distinguish incident from sensor failure | Conflicting provenance and timing | Later connector |
| LLM incident classifier | Fluent summaries | Can invent labels and cause | Reject |

### C.3 SCAMPER on A4 anomaly detection

| Letter | Prompt | Ideate result |
|---|---|---|
| Substitute | Replace raw threshold with forecast residual | Baseline-relative evidence rather than fixed queue folklore |
| Combine | Combine residual, freshness, neighbour state, and source class | Alert distinguishes disruption from failed vision |
| Adapt | Adapt TIM severity and recovery language | Metrics by severity; clearance is not full recovery |
| Modify | Magnify uncertainty and alternatives | Confidence, data age, and alternate explanations become required fields |
| Put to other use | Use the same residuals for transit and spillback | Shared method, domain-specific thresholds and labels |
| Eliminate | Remove cause claims from first alert | “Anomaly” remains separate from “likely incident” |
| Reverse | Ask what would disprove the alert | Counter-evidence and verifier checks before escalation |

### C.4 Morphological chart

| Dimension | Option A | Option B | Option C | Chosen Now |
|---|---|---|---|---|
| Detection | Raw threshold | EWMA/CUSUM residual | Black-box classifier | EWMA/CUSUM residual |
| Evidence | Score only | Observed, expected, residual, source ages | Generated narrative | Structured evidence fields |
| Action bound | Direct phase change | Typed alert and bounded investigation suggestion | Automatic incident declaration | Typed alert only |
| Vision | Healthy by default | Fresh, stale, degraded, insufficient | Hidden | Explicit state |
| Context | Ignore weather | Regime tag with source metadata | Weather as cause | Regime tag only |
| Explanation | No rationale | Deterministic fields plus cited Synapse rendering | LLM intuition | Verified rendering or abstention |

### C.5 FAR versus miss by severity

There is no universal detection-delay or acceptable-FAR number. The evaluation reports detection delay, FAR, miss rate, verification delay, and recovery **by pre-registered severity class**. Thresholds are exploratory team choices after a noise pilot, not FHWA mandates or Tunis field measurements. A severe missed incident and a low-severity false alert do not carry equal operational cost; the report shows the trade-off rather than compressing it into one average.

### C.6 Chosen A4 alert contract

```text
A4Alert
  run_id
  scenario_hash
  message_id
  correlation_id
  created_at
  simulation_time
  expires_at
  ttl_seconds
  target_id
  anomaly_class
  alert_state              # normal | anomaly | likely_incident | degraded | stale | insufficient_data
  severity                 # info | low | medium | high | critical
  observed_values
  expected_values
  residual_values
  detector_method
  detector_parameters_hash
  threshold_or_change_score
  model_version
  confidence
  data_quality_state
  source_observed_times
  source_received_times
  max_data_age_seconds
  missing_sources
  alternate_explanations
  counter_evidence
  reason_codes
  bounded_recommendation
  evidence_references
  recovery_state
```

Contract rules:

1. `normal` is forbidden when a required source is stale, missing, invalid, or untrusted.
2. Every alert expires; consumers reject it after `expires_at`.
3. Confidence is not a probability of a crash unless a calibrated model and label contract establish that meaning.
4. `likely_incident` requires corroboration rules; A4 still does not assert a legal or causal finding.
5. A bounded recommendation may request investigation, source verification, or a what-if run; it never contains a signal command.

### C.7 Weather, roads, incidents, near-miss signals, and heatmaps

| Input or product | Allowed use | Honesty label | Rejected inference |
|---|---|---|---|
| Archived rain or fog | Condition baseline and compare residual performance | reanalysis-context | Weather caused this crash |
| OSM hazard or geometry tags | Scenario design lead with snapshot provenance | open-map-not-survey | Tag proves a current hazard |
| Official crash or incident archive | Retrospective labels within documented scope | official-archive | Archive is complete or live |
| News or social scrape | Research lead for human verification only | unverified-scrape | Ground-truth operational incident |
| SUMO incident injection | Known test onset and severity | simulation-truth | Real Tunis occurrence or prevention outcome |
| Spacing, TTC, or hard-brake surrogate | Explicitly defined risk/conflict indicator | surrogate-metric | Observed collision or accident prevention |
| Anomaly cluster heatmap | Counts or rates by cell, method, denominator, and window | derived-view | Dark cell proves danger or cause |
| Recovery heatmap | Time from clearance to selected stable KPI band | derived-view | Road clearance equals network recovery |
| Spillback burden heatmap | Blocked events or delay by link and window | derived-view | Personal exposure or measured air quality |

### C.8 What Synapse may explain versus invent

Synapse may fetch the exact A4 alert, retrieve allow-listed policy or method text, explain observed-versus-expected evidence, list source ages and alternatives, compare a bounded what-if, and abstain. A research sub-agent may gather candidate public sources; a data-quality sub-agent may check schema, licence metadata, freshness, and contradictions; an explanation sub-agent may render verified evidence. None may invent a missing observation, incident, cause, confidence, severity, citation, or action. None can access TraCI, the signal executor, active scenario mutation, or A1 authority.

---

## D. Data collection ideation — Now versus Later

| Data class | Now source | Later connector | Scrape/official/sim? | Persona | Agent | Dirty-data risk | Honesty label |
|---|---|---|---|---|---|---|---|
| Road geometry / maps | Versioned OSM extract | Human-reviewed municipal updates | open map | All seven | Scenario registry; A1 envelope | Missing lanes, turns, restrictions, stale topology | ODbL attribution; extract timestamp and hash; no warranty |
| Intersections / plans | OSM plus labelled synthetic or manually transcribed plan | MEHAT or municipal plan import | mixed | Yuki, Amara | A1 safety envelope | Wrong phases, conflicts, ownership, or transcription | Distinguish OSM, synthetic, and transcribed fields |
| Scheduled transit | Official scheduled TRANSTU GTFS | Authenticated AVL or GTFS-Realtime later | official scheduled | Chidi, Rosa | A3 | Expired calendar, missing version, schedule treated as position | Scheduled offer is not live operation |
| Accidents / incidents | Documented public archive plus SUMO injection | Police, CAD, road-authority, or open incident API | mixed | Omar, Marcus | A4 | Duplicates, late records, location error, rumour as fact | Source class, validity, confidence; simulation is test truth only |
| Weather | Archived Open-Meteo reanalysis with named model | National or warning API | external model | Omar, David | A4 | Grid mismatch, update lag, timezone error, over-causal story | Regime context; not junction observation or crash proof |
| Volumes / speeds | SUMO and explicitly synthetic or calibrated demand | Probe, loop, or camera-derived aggregate | usually simulation | David, Yuki | A1, A4 | Synthetic demand presented as observed Tunis traffic | Record demand source, calibration evidence, seed, and hash |
| Spacing / headway | SUMO trajectories and configured detectors | Connected-vehicle or AVL aggregate later | usually simulation | David, Chidi, Marcus | A1, A3, A4 | Undefined distance metric or false danger statement | Define spacing, headway, TTC, and aggregation separately |
| Pedestrian demand | SUMO calls and presence fixtures | Privacy-preserving counts or accessible button telemetry | mixed | Amara | A3 | Missing slow walkers, failed detector, app-only selection bias | Completion and wait evidence; no biometric inference |
| Emission proxies | HBEFA through SUMO | No air-quality substitution; optional comparison only | simulation proxy | — system KPI | A5 | Proxy labelled as measured exposure or AQ | I-7 optional only; no persona and no measured air quality |
| Heatmaps | Derived grids or links from frozen evidence | Same method over later approved feeds | derived | Omar, Yuki | Synapse read-only views | Sparse cells, arbitrary bins, colour implying certainty | Publish method, denominator, sample count, window, CRS, and uncertainty |

### D.1 Required source envelope

Every acquired or derived dataset should retain:

```text
source_id, source_class, publisher, source_url
jurisdiction, licence_id, attribution_text
retrieved_at, observed_at_or_valid_period, expires_at
schema_version, source_version, content_hash
spatial_reference, temporal_resolution, spatial_resolution
collection_method, simulation_or_observed, uncertainty_notes
quality_state, missingness_summary, transformation_hash
```

### D.2 Official-source findings applied to the roadmap

- **OSM:** data is ODbL; attribution to OpenStreetMap contributors and licence visibility are required. The snapshot is geometry input, not surveyed cabinet truth. Do not derive OSM data from copyrighted map displays.
- **GTFS Schedule:** a dataset is a versioned set of schedule files. Check service calendars, `feed_start_date`, `feed_end_date`, `feed_version`, stable source URL, retrieval time, and archive hash. Static schedule does not provide live vehicle positions.
- **Open-Meteo history:** the archive uses modelled reanalysis combining observations and estimation. Store model and grid resolution; ERA5 and ERA5-Land can have a documented update delay. It is contextual evidence, not a junction weather sensor.
- **FHWA TIM:** roadway-clearance, incident-clearance, verification, and secondary-event measures are transfer measurement methods. CoFlow does not inherit a universal threshold.
- **TRANSTU:** PR #3 establishes the Ministry catalogue dataset as official scheduled GTFS. Capture the catalogue’s exact licence metadata before redistribution; until checked, mark licence `to verify` rather than assuming it.

### D.3 Roadmap boundary

**Now:** fixed OSM snapshot, archived official scheduled GTFS, archived weather, documented public archives where licence permits, and deterministic SUMO injections. **Later design only:** traffic APIs, collision records, roadworks, weather alerts, probes, loops, cameras, AVL, and CAD. **Not Now:** fragile scraping, undisclosed proprietary map extraction, live Tunis claims, near-real-time alerting as a shipped feature, or automatic actuation from any external connector.

---

## E. Future problems the architecture has not yet faced

| risk_id | Cluster | Future problem | First persona affected | Mitigation owner | Architecture stress | Ideate seed, not full build |
|---|---|---|---|---|---|---|
| FP-01 | Data / sensing | OSM topology drifts after the scenario snapshot | Yuki | Synapse-data-quality | Stretch | Snapshot diff plus human-approved remap |
| FP-02 | Data / sensing | GTFS calendar expires while the simulation still calls it current | Chidi | A3 | Carry | Validity gate and explicit unavailable state |
| FP-03 | Data / sensing | Weather API is unavailable or returns a coarser model | Omar | A4 | Carry | Cached provenance and context-absent mode |
| FP-04 | Control / safety | A second writer appears through an admin or integration tool | Yuki | A1 executor | Break | Capability test and single-writer token |
| FP-05 | Control / safety | Emergency pressure tempts premature pedestrian release | Amara | Safety mask | Carry | In-crossing state outranks emergency request |
| FP-06 | Control / safety | Repeated preemption and resume produce oscillation | Marcus | A1 supervisor | Carry | Cooldown, recovery state, and health-before-resume |
| FP-07 | Multi-agent coordination | A2 and A3 publish conflicting high-value requests | Marcus | A1 arbitration | Carry | Fixed safety tiers plus reasoned same-tier bounds |
| FP-08 | Multi-agent coordination | TTL expiry storm removes many inputs in one epoch | Yuki | Message board | Carry | Bounded expiry processing and degraded health event |
| FP-09 | Multi-agent coordination | Heartbeat or advisory flood delays useful messages | Yuki | Message board | Carry | Per-topic quotas, aggregation, and backpressure |
| FP-10 | Anomaly / trust | Alert fatigue makes Omar ignore a real severe event | Omar | A4 | Carry | Severity grouping, deduplication, FAR review |
| FP-11 | Anomaly / trust | Anomaly is presented as a known cause | Omar | A4 | Carry | Alternate explanations and cause-unknown reason code |
| FP-12 | Anomaly / trust | Frozen dashboard looks healthy during source loss | Omar | Synapse-data-quality | Stretch | Independent freshness clock and insufficient-data banner |
| FP-13 | Burden / trade-offs | Local gain pushes spillback onto neighbouring links | David | A1 | Carry | Downstream capacity and link-level burden review |
| FP-14 | Burden / trade-offs | Transit priority regularizes buses but worsens pedestrian waits | Chidi | A1 arbitration | Carry | Cross-persona KPI budget and denial reason |
| FP-15 | Burden / trade-offs | A5 proxy is read as measured local air quality | Yuki | A5 | Carry | Proxy watermark and no-persona system-KPI section |
| FP-16 | Operations / adoption | Yuki disables automation because she cannot explain recovery | Yuki | A1 plus Synapse-explanation | Carry | Mode timeline, reasons, and deterministic fallback view |
| FP-17 | Operations / adoption | Rosa cannot justify why a transit request was denied | Rosa | Synapse-explanation | Carry | Request-decision-policy join or abstention |
| FP-18 | Operations / adoption | Audit events exist but clocks or IDs do not join | Rosa | Evidence store | Carry | Canonical IDs, source times, received times, join gate |
| FP-19 | Evaluation honesty | A simulation result is described as Tunis deployment evidence | David | Evaluation harness | Carry | Claim-class lint and setting label |
| FP-20 | Evaluation honesty | EV time reduction becomes a lives-saved claim | Marcus | Evaluation harness | Carry | Forbidden-claim gate and mission-time wording |
| FP-21 | Evaluation honesty | Best episode or one seed becomes a superiority headline | Yuki | Evaluation harness | Carry | Paired seeds, intervals, all outcomes, honest nulls |
| FP-22 | Security / misuse | Emergency priority is spoofed, replayed, or duplicated | Marcus | A2 ingress | Stretch | Authentication, nonce, expiry, route plausibility, audit |
| FP-23 | Security / misuse | External feed is poisoned to create false congestion | Omar | Synapse-data-quality | Stretch | Source trust, schema checks, cross-source disagreement |
| FP-24 | Security / misuse | A Synapse tool or prompt exposes TraCI or active mutation | Yuki | Architecture boundary | Break | No capability, forbidden imports, runtime kill invariance |

### E.1 Cluster ownership summary

- **Data and sensing:** Chidi and Yuki feel version drift first; A3 and data-quality checks must fail unavailable rather than silently impute.
- **Safety and coordination:** Amara and Marcus feel conflicting priorities first; the mask, A1 tiers, TTL, quotas, and recovery state remain deterministic.
- **Trust and operations:** Omar, Rosa, and Yuki feel stale vision, alert fatigue, and audit gaps first; structured evidence precedes generated explanation.
- **Burden and honesty:** David and Chidi reveal displaced costs; Marcus and Yuki expose claim creep; cross-persona metrics and claim gates keep the story honest.
- **Security:** Marcus feels spoofed priority and Omar feels poisoned feeds; authentication and provenance are advisory ingress controls, while Synapse remains capability-isolated.

---

## F. Architecture convergence — finalized card

### F.1 Chosen architecture

| Component | Final authority and message role | Future-survival rule |
|---|---|---|
| A1 Flow | Sole actuator; cooperative Max-Pressure; deterministic safety mask; reads valid advice | If advice or forecasts disappear, continue safely and recover `Max-Pressure -> actuated -> fixed-time` |
| A2 Emergency | Publishes authenticated, expiring corridor pre-clear and recovery requests | Never writes signals; rejects replay, impossible route, stale ETA, and unauthenticated source |
| A3 Multimodal | Publishes pedestrian clearance/deadline state and conditional transit-priority requests | In-crossing protection is safety state; schedule is not live position; requests expire |
| A4 Situation | Publishes forecast residuals, anomaly/degradation alerts, and weather regime tags | Distinguish anomaly, likely incident, stale, degraded, insufficient data, and normal |
| A5 Sustainability | Publishes optional stop/emission-proxy and geographic burden advice | I-7 has no persona; proxy never becomes measured air quality and loses to safety or spillback |
| Message board | Typed `state/`, `forecast/`, `alerts/`, `eco/`, `priority_request/`, `replies/`, and `health/` topics | IDs, TTL, confidence, provenance, bounded storage, dispositions, quotas, and fault injection |
| Synapse plus bounded sub-agents | Retrieve, research allow-listed sources, check data quality, explain frozen evidence, verify, abstain, and draft human-reviewed what-if requests | No TraCI, executor, active mutation, incident invention, second identity, or generated decision event |

### F.2 What is agentic and what is not

**Agentic:** typed cooperating specialists with distinct observations, goals, permissions, expiring messages, deterministic arbitration, evidence feedback, and graceful degradation; plus a bounded read-only Synapse workflow that can retrieve, verify, retry within limits, pause for approval, and abstain.

**Not agentic:** an LLM traffic-light boss, five chatbots debating phases, an unbounded autonomous scraper, a dashboard that invents missing facts, or independent controllers with equal signal authority.

### F.3 Rejected architecture alternatives

| Alternative | Persona failure | ADR failure | Disposition |
|---|---|---|---|
| Central LLM controller | Amara cannot rely on deterministic clearance; Yuki cannot prove timing or recovery | Synapse would gain actuation and latency-dependent control | Reject |
| Multiple specialist signal writers | Marcus, Chidi, and Amara issue conflicting priorities without one accountable decision | Violates sole A1 writer and deterministic arbitration | Reject |
| Fully learned microservice per agent | Omar and Rosa receive opaque, version-fragmented evidence; the team cannot evaluate all interactions | Exceeds compute and evaluation envelope; hides typed in-process semantics | Reject |

---

## G. Ideate techniques and convergence record

### G.1 Worst Possible Idea x 7 -> inversion

| Persona | Worst idea | Inversion carried forward |
|---|---|---|
| Amara | LLM ends WALK | Deterministic clearance and crossing interlock |
| David | LLM serves private delivery promises | Public cooperative Max-Pressure and tail evaluation |
| Chidi | Static schedule is treated as live bus position | Scheduled/observed separation and conditional request |
| Rosa | Denials are erased or negotiated conversationally | Immutable dispositions and verified explanation |
| Marcus | Always-green emergency corridor | Authenticated expiring pre-clear, externality, recovery |
| Yuki | Synapse gets a TraCI override tool | Capability isolation and interlocked deterministic modes |
| Omar | LLM declares cause from a queue spike | Residual evidence, alternatives, degradation, abstention |

### G.2 Weighted architecture matrix

Weights are **team judgment**, not empirical Evidence: Safety 25%, Honesty 20%, Persona fit 20%, Feasibility 15%, Auditability 10%, Architecture fit 10%. Scores are 1–5. Any `Break` or failed safety/honesty condition is rejected regardless of total.

| Architecture | Safety 25 | Honesty 20 | Persona fit 20 | Feasibility 15 | Auditability 10 | Architecture fit 10 | Weighted / 5 | Decision |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Five typed agents plus bounded Synapse | 5 | 5 | 5 | 4 | 5 | 5 | 4.85 | Now architecture |
| Central LLM controller | 1 | 1 | 2 | 3 | 2 | 1 | 1.60 | Reject |
| Multiple signal writers | 1 | 2 | 3 | 3 | 1 | 1 | 1.90 | Reject |
| Fully learned agent microservices | 2 | 2 | 3 | 1 | 2 | 2 | 2.05 | Reject |

A ±5 percentage-point sensitivity move between non-safety criteria does not change the decision. Safety and honesty remain hard gates, so none of the three rejected alternatives can win by reweighting.

### G.3 Final disposition

**Now:** one bounded, testable idea per persona: AM-02, DV-02, CH-03, RO-02, MC-02, YK-02, OM-02. **Later:** deferred connectors, richer methods, and bounded Synapse workers only after typed interfaces, provenance, and failing-then-passing gates exist. **Reject:** second writers, LLM control, scrape-as-truth, scheduled-as-live inference, hidden degradation, mutable audit, sensitive unnecessary inference, and unbounded priority.

The architecture can carry the selected ideas because specialists remain typed and advisory, A1 remains the only actuator, and every uncertain data source can become unavailable without generated text filling the gap. Its hardest unsolved future is not a more complex controller: it is preserving the distinction between **“nothing abnormal was detected”** and **“the system lacks trustworthy vision.”**

---

## Source and honesty register for this addendum

| Source | Use | Limit |
|---|---|---|
| Professor decision and PR #3, head `832dc38` | Seven-person roster and I-1–I-10 ownership | Draft PR status does not turn placeholders into Evidence |
| ADR-0001 | Authority, recovery, data/evaluation priority, Synapse boundary | Wins over historical MARL language |
| Tunis practice and citation ledgers in PR #3 | Persona mechanisms, source classes, transfer wording | Open page/DOI checks remain open where ledger says `from-prior-pack` |
| OpenStreetMap copyright and licence page | ODbL attribution and reuse boundary | Geometry is not guaranteed signal-plan truth |
| GTFS Schedule Reference | Dataset version, validity, calendars, attribution fields | Static schedule is not GTFS-Realtime or AVL |
| Open-Meteo Historical Weather API | Reanalysis source, model, resolution, update lag | Modelled context is not a junction observation or causal crash proof |
| FHWA TIM performance measures | Detection, verification, clearance, secondary-event method | US transfer method; no universal Tunis threshold |
| NIST AI RMF 1.0 | General valid, reliable, safe, secure, resilient, transparent, explainable governance lens | Voluntary and non-sector-specific; not traffic-domain magnitude Evidence |

## Claim flags

- No lives saved are inferred from simulated emergency travel time.
- HBEFA and SUMO are emission proxies, not measured air quality or exposure.
- No live Tunis loops, cabinet operation, AVL, crash feed, or deployment impact is claimed without verified evidence.
- Scraped news and map displays are not ground-truth incidents or lawful substitutes for licensed data.
- Simulation can test risk indicators, conflict proxies, detection, and response support; it does not establish accident prevention.
- No best-episode or one-seed superiority headline is allowed.
