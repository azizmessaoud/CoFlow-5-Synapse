# World truths and standard metrics in traffic management

Purpose: Empathize transfer layer — what modern cities and agencies treat as established practice and how they **measure** it. Does **not** override Tunisian primary practice Evidence. Numerical CoFlow targets remain **proposed** acceptance criteria, not world-mandated thresholds.

Sources (canonical): FHWA ASCT MOEs (HOP-13-031), FHWA ATSPM (HOP-20-002 / EDC), Traffic Analysis Toolbox Vol. 6 reliability addendum, DfT TAG A1.3, FHWA TIM handbooks, HCM pedestrian procedures, SCOOT/SCATS/Surtrac product-ops patterns.

## World truths (practice, not slogans)

1. **Mean delay is not enough.** Travelers and freight care about **reliability** (upper-tail travel time). Agencies report P90/P95, buffer index, planning time index — not only averages (FHWA TAT Vol. 6; DfT TAG reliability ratio).
2. **Empty green and spillback matter.** Serving green to an empty approach wastes capacity; greening into a full exit moves the queue and can block cross streets (ASCT MOEs: arrivals on green, queue, oversaturation; Max-Pressure / Surtrac practice).
3. **Pedestrian wait has a compliance cliff.** Frustration rises after ~20–30 s; longer waits increase red walking (NZTA RR440; TfL; DfT LTN 2/95). Clearance must match **who is present**, not only the design median walk speed (MUTCD/HCM older-user guidance).
4. **Transit priority is person-based and conditional.** Unconditional “always green for buses” can starve others and fail to fix bunching; headway/lateness-triggered priority + holding is the modern practice story (SCOOT TSP; bunching theory).
5. **Emergency priority has an externality.** Preemption helps the EV but can cost arterial and side-street delay if dense or local-only; passage **and** recovery are one mission (Nelson & Bullock; EVP field studies).
6. **Operators need audit + override + fallback.** Production ATC (SCATS, Surtrac) ships intervention, logging, and safe degradation when sensors/comms fail — black-box optimisation without takeover is not operable (SCATS Core; Surtrac pilot).
7. **Incidents punch above their time share.** Non-recurring events (often ~25–30% of metro congestion delay in US handbooks) need TIM metrics: detection/verification, roadway clearance, incident clearance, secondary crashes (FHWA TIM) — **no universal detection-delay number**.
8. **Sustainability is spatial.** Network-wide % gains can hide displacement onto residential/school links; stop-start often drives local emission proxies more than volume alone (exposure literature; HBEFA/SUMO as **proxy** only).
9. **Simulation is a lab.** SUMO/ASCT before-after studies compare policies under stated demand; they do not by themselves prove city-wide field AQ, lives saved, or Tunis cabinet performance.

## Standard metric families (what the world reports)

### A. Intersection / arterial (ATSPM + ASCT MOEs)

| Metric | What it means | Typical use |
|---|---|---|
| Approach / link delay | Extra time vs free-flow or free green | Core MOE |
| Travel time / speed (route, link) | End-to-end mobility | Before/after ASCT |
| Volume / throughput | Vehicles or persons served | Capacity claims |
| Queue length by movement | Storage, spillback risk | Oversaturation |
| Stops per vehicle / per mile | Stop-start discomfort + eco proxy | Coordination quality |
| % arrivals on green (AoG) | Progression quality | Purdue Coordination Diagram |
| Platoon ratio | AoG vs random | HCM-style progression |
| Split failure (Purdue) | Demand not served in green | Capacity failure |
| Green occupancy / v/c served | How hard green is used | Saturation |
| Cycle length / split / offset drift | Plan health | Maintenance |
| Yellow/red actuations | Dilemma / red-light risk signal | Safety ops |

### B. Reliability (freight / car users)

| Metric | Definition (usual) |
|---|---|
| P90 / P95 travel time | Upper-tail journey time |
| Buffer time | P95 − mean (or median variant) |
| Buffer index | (P95 − mean) / mean |
| Planning time index (PTI) | P95 / free-flow travel time |
| Misery index | Mean of worst ~5% / free-flow (or ~97.5 TTI) |
| On-time % | Share within median+10%/+25% or speed thresholds |
| Reliability ratio (appraisal) | Value of variability vs mean (DfT TAG **0.4** cars/LGV) |

**CoFlow honesty:** unfinished/teleported SUMO trips must count as failures or P95 lies.

### C. Pedestrians / VRU

| Metric | Definition |
|---|---|
| Pedestrian delay (ATSPM) | Call → start of WALK |
| Mean / P95 ped wait; % waits >30 s | Compliance-risk lens |
| Clearance truncations | Conflicting release while pedestrian still on crossing |
| Crossing completion rate | Finished before conflicting green |
| Assumed walk speed vs observed percentiles | 1.07 m/s MUTCD default; 1.0 m/s if many 65+; assistive ~0.6–0.8 m/s |

### D. Transit (TSP / regularity)

| Metric | Definition |
|---|---|
| Bus journey time / delay vs schedule | Speed |
| Headway mean, variance, CV | Regularity (high-frequency lines) |
| Excess wait time / passenger waiting | Person-centred |
| Bunching events | Close pairs + long gaps |
| Priority requests / grants / denials + reason codes | Operability (Rosa) |
| Additional car delay from TSP | Externality budget |
| Schedule adherence / on-time performance | Where timetables exist |

### E. Emergency / EVP

| Metric | Definition |
|---|---|
| EV travel time (scene / hospital legs) | Benefit |
| Stops for EV | Local green without space still fails |
| Civilian person-delay / side-street delay | Externality |
| Recovery time to re-coordination | After preemption |
| Safety-constraint violations | Must be zero |

Do **not** convert simulated minutes into lives saved.

### F. Incidents / TIM (Omar)

| Metric | Definition |
|---|---|
| Detection delay | Onset → detect (agency-defined) |
| Verification delay | Detect → confirm |
| Roadway clearance / incident clearance | FHWA TIM |
| False-alarm rate (FAR) | Trust |
| Missed-incident rate | Safety |
| Secondary crashes | Outcome |
| Share of delay from incidents | Often ~25–30% US metro handbooks |

Thresholds are **agency-set**; CoFlow reports exploratory benchmarks by severity.

### G. Operator / system health (Yuki / Rosa)

| Metric | Definition |
|---|---|
| Reason-code coverage | % decisions with readable cause |
| Decision log completeness | Inputs, constraints, action, outcome |
| Control / decision latency | Time to legal action |
| Fallback activation time | Watchdog → Max-Pressure → actuated → fixed-time |
| Data freshness / comms loss alerts | Stale vs healthy |
| Override count + interlock integrity | Human authority without conflicting greens |

### H. Environment — optional proxies in sim (no Empathize persona)

| Metric | Definition |
|---|---|
| CO₂ / NOx (HBEFA/SUMO) per link / period | **Proxy**, not ANPE |
| Stops near receptors | Often stronger local lever than VKT |
| Exposure-weighted proxy | Documented weights |
| Displacement check | No significant worsening on school-adjacent links (pre-registered rule) |

## Persona → metric map (Empathize evaluation)

| Persona | Primary metrics | World-truth anchor |
|---|---|---|
| Amara | Ped delay/wait, % >30 s, clearance truncations, completion | Compliance cliff; slow walkers |
| David | P95 TT, buffer/PTI, stops/veh, completion incl. unfinished | Reliability > mean |
| Chidi | Headway CV/variance, passenger wait, bus TT, extra car delay | Conditional TSP; bunching |
| Rosa | Request/grant/deny + reason codes, task time | Audit/override practice |
| Marcus | EV TT vs baselines, civilian delay, recovery, zero safety breaches | EVP externality |
| Yuki | Log completeness, latency, fallback time, freshness | Operable ATC |
| *(deferred)* | Link CO₂/NOx proxy, stops/vehicle | Optional system KPI — not parent persona |
| Omar | Detect/FAR/miss, clearance, recovery by severity | TIM; no universal detect KPI |

## Claim flags for metrics

- Do not present CoFlow SMART numbers (e.g. P95 −5%, headway −15%) as FHWA/DfT mandates — they are **proposed tests**.
- Do not treat HBEFA as measured Tunis AQ.
- Do not invent a universal incident detection-delay standard.
- ATSPM names describe **what to log**; they do not require every metric in the SUMO MVP.
