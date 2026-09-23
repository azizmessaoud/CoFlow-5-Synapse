# Kiro prompt — Ideate finalization: agentic AI architecture (post-Empathize)

Copy everything below the line into Kiro.

Output style: https://github.com/ayghri/i-have-adhd  
Harness pattern: https://github.com/flyrank-bih/harness-engineering-playbook  
Do not copy Shopify themes. Lift router / evidence / gate discipline only.

---

## 0. Read first (order)

1. `AGENT_GUIDE.md`
2. `docs/adr/0001-reliable-ai-platform-boundary.md`  ← **wins on conflict**
3. `docs/source/course-brief.md`
4. `.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md`
5. `CONTEXT.md`
6. `coflow5-empathize-pack.md` (Evidence §A–E)
7. `.scratch/coflow5-empathize/research/insight-evidence-alignment.md`
8. `.scratch/coflow5-empathize/research/citation-ledger.md`
9. `.scratch/coflow5-empathize/research/tunisia-practice-evidence.md`
10. `.scratch/coflow5-empathize/research/world-truths-and-metrics.md`
11. `coflow5-define-ideate.md` (historical Ideate — mark superseded bits; do not revive MARL-as-required-A1)
12. `.kiro/steering/product.md`
13. `.kiro/steering/output-style.md`

## 1. What Empathize already locked (do not reopen)

**Study setting:** Grand Tunis simulation (OSM + official **scheduled** TRANSTU GTFS + labelled synthetic/calibrated road demand). Not a live cabinet.

**Eight personas only** (map IMATM Tunis names; do not stack):

| ID | Persona | Role | Insight owners |
|---|---|---|---|
| P1 | Amara | Slow pedestrian | I-4 |
| P2 | David | Delivery / reliability | I-1, I-2, I-6 |
| P3 | Chidi | TRANSTU rider | I-5 |
| P4 | Rosa | TRANSTU dépôt / régulation | I-8, I-9 (transit) |
| P5 | Marcus | Urgent-intervention / ambulance | I-3 |
| P6 | Yuki | Municipal / MEHAT signal engineer | I-8, I-9 (signals) |
| P7 | Maria | Parent near arterial / school | I-6, I-7 |
| P8 | Omar | Incident / duty desk | I-10 (+ anomaly detection focus) |

**Evidence rule:** Tunis practice primary; transfer literature = mechanism/metric method.  
**Not Evidence:** IMATM Table 9 ▲, interview placeholders, SUMO outputs as field proof, SMART thresholds as literature, lives saved from sim, “Tunis empty-green %”, AI-distrust %.

**Wording rule:** *This source supports the mechanism or measurement approach; it does not establish the Tunisian magnitude.*

**Architecture non-negotiables (ADR-0001):**
- Only **A1** writes signals (cooperative Max-Pressure required).
- Recovery: Max-Pressure → actuated → fixed-time.
- A2–A5 advise only (messages with TTL/confidence).
- **Synapse** explains / retrieves / evaluates / what-if — **never TraCI**.
- DQN optional later; must not block the queue.
- Claim flags stay: no lives saved, no measured AQ from HBEFA, no best-episode headline.

## 2. Job for THIS Kiro session

**Focus = Design Thinking Ideate finalization + agentic AI architecture.**  
SUMO is the world/simulator — **not** the problem to solve in this session.

Deliver a **persona-driven ideation pack** that:

1. Finalizes ideas per persona (chosen / rejected / deferred).
2. Deep-dives **Omar / A4 anomaly detection** as its own Ideate track.
3. Inventories **future problems** the current architecture has not yet faced.
4. Specifies **data collection ideas** (maps, intersections, accidents, weather, spacing/headway, heatmaps) as *inputs to agents*, with honesty labels (scraped vs official vs simulated).
5. Converges on an **agentic message + authority design** that survives those futures.

Do **not** write product TraCI code in this session unless a contract row explicitly requires a smoke artifact. Prefer markdown specs under `.scratch/` and updates to `coflow5-define-ideate.md` / Empathize-linked Ideate addendum.

## 3. Output structure (write these sections)

### A. Per-persona ideation matrix (mandatory)

For **each** of the 8 personas, produce:

| Field | Content |
|---|---|
| Need / HMW | From Empathize |
| Insight IDs | I-1…I-10 |
| Brainstorm ideas (8–12) | Crazy included |
| Worst Possible Idea → invert | One line |
| Chosen line for MVP | One sentence |
| Deferred / rejected | Why (safety, honesty, ADR, compute) |
| Agent touch | A1–A5 / Synapse role |
| Data it needs | Sources + honesty label |
| Metric (measurement need) | From Empathize §D–E |
| Future failure if ignored | One concrete failure mode |

### B. Omar / A4 anomaly detection — Ideate on its own (mandatory deep section)

Treat anomaly detection as a **first-class Ideate problem**, not a footnote of A4.

Brainstorm and then choose among:

1. **What is an “anomaly”?** (incident, sensor failure, demand surge, weather regime shift, stale data, message loss, unusual headway, spillback onset)
2. **Detection methods** (EWMA/CUSUM on residuals — Empathize seed; change-point; isolation; weather-conditioned baselines; multi-source fusion)
3. **Evidence Omar needs in an alert:** what / why / confidence / data age / alternate explanations / recommended bounded action
4. **False alarm vs miss trade-off** — FAR and miss rate by severity (Empathize); no universal detection-delay KPI
5. **Degraded vision:** “nothing wrong” vs “we can’t see”
6. **Weather & roads coupling:** rain/fog → friction, speed drop, incident risk — how A4 labels regime without claiming causal weather→crash certainty it doesn’t have
7. **Accident / near-miss signals:** official crash feeds vs OSM hazard tags vs news scrape vs simulated injections — honesty labels
8. **Heatmap products for Omar & Maria:** where anomalies cluster; where emissions/stops proxies rise; school buffers
9. **Rejected ideas:** black-box alert with no reason; silent dashboard; weather scrape as sole crash predictor; LLM inventing incidents

End with: **chosen A4 alert contract** (fields, TTL, confidence, severity, required reason codes) and **what Synapse may explain vs invent**.

### C. Data collection ideation (inputs to agents, not “big data for its own sake”)

For each data class, fill:

| Data class | Example sources | Scrape / official / sim? | Persona served | Agent consumer | Risk if dirty | Honesty label |
|---|---|---|---|---|---|---|
| Road geometry / maps | OSM extract | open map | all | network build | bad lanes/turns | OSM version + hash |
| Intersections / signal plans | OSM + transcribed plans / MEHAT context | mixed | Yuki, Amara | A1 timing envelope | wrong phases | label synthetic vs transcribed |
| Scheduled transit | TRANSTU GTFS CKAN | official scheduled | Chidi, Rosa | A3 | treat as live AVL | **scheduled ≠ live** |
| Accidents / incidents | police/open data / news / sim inject | mixed | Omar, Marcus | A4 | rumor as fact | source class + confidence |
| Weather | Open-Meteo / national meteo | external API | Omar, David, Maria | A4 regime tag | over-causal claims | weather as **context feature**, not crash proof |
| Traffic volumes / speeds | loops / probe / SUMO | often sim | David, Yuki | A1/A4 | calibrated synthetic as observed | label demand source |
| Car distance / spacing / headway | detectors, CV, SUMO | often sim | David, Chidi, Marcus | A1/A3/A4 | unsafe spacing claims | spacing = **metric**, not “AI saw danger” without definition |
| Pedestrian demand | buttons / counts / SUMO | mixed | Amara | A3 | ignore slow walkers | completion + wait metrics |
| Emissions proxies | HBEFA/SUMO | sim proxy | Maria | A5 | call proxy “AQ” | **proxy only** |
| Heatmaps | derived grids | derived | Omar, Maria, Yuki | Synapse views | pretty map ≠ truth | show method + time window |

**Brainstorm explicitly:** scraping maps/intersections; accident feeds; weather-conditioned prevention **alerts** (not “prevent accidents” claims); inter-vehicle distance / time-headway metrics; school-buffer heatmaps; incident recovery heatmaps.

**Forbidden product claims from data ideation:** lives saved; measured Tunis AQ; live Tunis loops unless verified; scraped news as ground truth crashes.

### D. Future problems the architecture has not yet faced (mandatory)

Brainstorm ≥15 future problems, then cluster into:

1. **Data / sensing:** OSM drift, GTFS stale, weather API down, scrape ToS/ethics, no loops, partial cameras
2. **Control / safety:** two writers, preemption thrash, ped truncation under EV pressure, override abuse
3. **Multi-agent coordination:** message storms, TTL expiry storms, conflicting A2/A3 bids, board silence
4. **Anomaly / trust:** alert fatigue, anomaly≠cause, weather false correlation, “frozen dashboard looks healthy”
5. **Equity / politics:** displacement to Maria’s street, bus vs car trade-offs, opaque Synapse text
6. **Ops / adoption:** Yuki switches system off (I-9); Rosa can’t justify TSP deny; audit gaps
7. **Evaluation honesty:** sim success ≠ Tunis deploy; HBEFA misread as AQ; lives-saved creep
8. **Security / misuse:** spoofed EV priority, poisoned scrape, TraCI exposure via Synapse

For each cluster: **which persona feels it first**, **which agent must own mitigation**, **Ideate seed** (not full build).

### E. Architecture convergence (agentic AI — finalize)

Produce a short **chosen architecture card**:

- A1 Coordinator / Light Boss — sole actuator; Max-Pressure; safety mask
- A2 Emergency — corridor pre-clear bids; recovery
- A3 Ped + Transit — clearance + conditional TSP
- A4 Lookout — forecast residuals + anomaly / degradation / weather regime tags
- A5 Green Guardian — stop/emission proxy + displacement checks
- Message board topics: `state/`, `forecast/`, `alerts/`, `eco/`, `priority_request/`
- Synapse: retrieve evidence bundle + explain logs; **no actuation**
- Explicit: what is **agentic** here (typed cooperating specialists + retrieval explainer) vs what is **not** (LLM traffic light boss)

Compare 3 rejected alternatives in one table (why rejected under ADR + personas).

### F. Ideate techniques (run them, don’t only name them)

1. Brainstorm per persona (section A)
2. Worst Possible Idea × 8 → invert to principle
3. SCAMPER on A4 anomaly detection only
4. Morphological chart: Detection × Evidence fields × Action bound × Data honesty
5. Weighted matrix: score ideas on Safety, Honesty, Persona fit, Feasibility, Auditability — pick winners

## 4. Success criteria for this Kiro output

- [ ] Every idea traces to a persona + insight ID
- [ ] Omar/A4 anomaly section can stand alone as an Ideate mini-spec
- [ ] Data collection table exists with honesty labels
- [ ] ≥15 future problems clustered with owners
- [ ] Architecture card matches ADR-0001
- [ ] No new personas; no LLM-in-control; no lives-saved; no AQ-from-HBEFA
- [ ] Next action named: which file to patch (`coflow5-define-ideate.md` addendum or `.scratch/coflow5-ideate-finalize/…`)

## 5. Start now

1. Restate HMW and ADR boundary in 5 lines.
2. Build the **Omar/A4 anomaly Ideate** section first (deepest gap).
3. Fill the 8-persona ideation matrix.
4. Data collection + heatmap/weather/roads table.
5. Future-problems catalog.
6. Architecture card + rejected alternatives.
7. Write results into a new file: `.scratch/coflow5-ideate-finalize/spec.md` (create folder) and append a Decisions pointer to `.scratch/coflow5-empathize/map.md` only if Empathize claims change (they should not).

**Next action after you finish:** one sentence naming the file path of the Ideate finalize artifact and the single highest-risk future problem for Omar/A4.
