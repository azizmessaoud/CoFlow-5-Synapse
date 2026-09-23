# Kiro prompt — Ideate finalization: agentic AI architecture (post-Empathize)

Copy everything below the line into Kiro.

Output style: https://github.com/ayghri/i-have-adhd  
Harness pattern: https://github.com/flyrank-bih/harness-engineering-playbook  
Do not copy Shopify themes. Lift router / evidence / gate discipline only.

---

## CAPTURE answers (use these — do not re-ask)

**1 = d** — Combined: decision matrix as source of truth + concise presentation view.  
**2 = b** — Data-platform roadmap: prototype-safe sources now + connectors designed for later APIs/feeds; do not implement live scrapers or claim live ops.  
**3 = b** — Keep five top-level agents; allow **bounded Synapse sub-agents only** (research / data-quality / explanation workers) with **no control authority**.

Must-haves: anomaly detection Ideate for Omar/A4; every idea traces to a persona + insight; maps / intersections / weather / incidents / spacing / heatmaps with honesty labels; future-problem catalog the five-agent + Synapse boundary has not yet faced.

---

## 0. Read first (order)

1. `AGENT_GUIDE.md`
2. `docs/adr/0001-reliable-ai-platform-boundary.md`  ← **wins on conflict**
3. `docs/source/course-brief.md`
4. `.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md`
5. `CONTEXT.md`
6. `coflow5-empathize-pack.md` (Evidence §A–E) — **working persona set; roster still under evidence check**
7. `.scratch/coflow5-empathize/research/insight-evidence-alignment.md`
8. `.scratch/coflow5-empathize/research/citation-ledger.md`
9. `.scratch/coflow5-empathize/research/tunisia-practice-evidence.md`
10. `.scratch/coflow5-empathize/research/world-truths-and-metrics.md`
11. `coflow5-define-ideate.md` (historical Ideate — mark superseded bits; do not revive MARL-as-required-A1)
12. `.kiro/steering/product.md`
13. `.kiro/steering/output-style.md`

## 1. What is locked vs still under check

### Locked (do not reopen)

**Study setting:** Grand Tunis simulation (OSM + official **scheduled** TRANSTU GTFS + labelled synthetic/calibrated road demand). Not a live cabinet.

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

**Agent ownership already assigned (do not invent new top-level agents):**
- **A4** owns forecasting + transparent anomaly / residual detection (Omar’s primary evaluation agent).
- **A5** owns sustainability / geographic burden **proxies** (optional system KPIs; not an Empathize parent need).
- Synapse investigates, explains, retrieves evidence, proposes what-if — **cannot control signals**.

### Under check (do not treat as Ideate deliverable)

**Persona roster is still being checked against Evidence.**  
Use the **current** `coflow5-empathize-pack.md` table as the working set for ideation. Do **not**:

- make “finalize N personas” or “confirm Maria/Leila” the job of this session;
- invent replacement personas;
- stack IMATM names on top of pack personas;
- spend the session arguing roster count.

If a persona row is weak or contested, mark the idea **Deferred — roster under check** and keep the architecture decision. Ideate owns **ideas ↔ architecture fit**, not Empathize roster closure.

**Working insight map (from pack; adjust only if pack changes):**  
Amara→I-4 · David→I-1,I-2,I-6 · Chidi→I-5 · Rosa→I-8,I-9 (transit) · Marcus→I-3 · Yuki→I-8,I-9 (signals) · Omar→I-10.  
**I-7** (stop/emission proxies) = optional A5 system KPI track — **not** a parent-persona Ideate spine.

## 2. Job for THIS Kiro session

**Focus = Design Thinking Ideate finalization for agentic AI architecture.**  
SUMO is the world/simulator — **not** the problem to solve here.

Open question to answer:

> Which ideas can the settled five-agent + Synapse architecture actually carry, and which **future problems** each persona would hit if we ship that architecture?

Deliver a **persona-led ideation pack** that:

1. Finalizes ideas per **working** persona (Now / Later / Reject) with architecture fit.
2. Deep-dives **Omar / A4 anomaly detection** as its own Ideate track.
3. Inventories **future problems** the current architecture has not yet faced.
4. Specifies **data collection ideas** (maps, intersections, accidents, weather, spacing/headway, heatmaps) as *inputs to agents*, with honesty labels.
5. Converges on an **agentic message + authority design** that survives those futures — **without** adding top-level agents (Synapse sub-agents OK per CAPTURE 3=b).

Do **not** write product TraCI code unless a contract row explicitly requires a smoke artifact. Prefer markdown under `.scratch/` and an Ideate addendum.

## 3. Output structure (write these sections)

### A. Decision matrix — source of truth (mandatory)

One row per idea. Columns:

| idea_id | persona | pain / HMW | insight | data needed | honesty label | agent (A1–A5 / Synapse±sub) | evidence / metric | architecture fit (Carry / Stretch / Break) | future risk if shipped | Now / Later / Reject | reason |

Rules:
- Every idea maps to one primary persona from the **working pack**.
- **Carry** = fits ADR-0001 with existing agent roles.  
- **Stretch** = needs Synapse sub-agent, deferred data connector, or optional A5 proxy — still no TraCI from Synapse.  
- **Break** = Reject (second writer, LLM-as-controller, scrape-as-truth, lives-saved, AQ-from-HBEFA, accident-prevention claim from sim).

Also produce a **one-page presentation view** (CAPTURE 1=d): persona → chosen Now idea → agent → metric → one future risk. No dashboard fluff.

### B. Per-persona ideation (mandatory — architecture lens)

For **each working persona** in the Empathize pack:

| Field | Content |
|---|---|
| Need / HMW | From Empathize |
| Insight IDs | I-1…I-10 (I-7 only if A5 proxy track) |
| Brainstorm (8–12) | Crazy included; still agent-tagged |
| Worst Possible Idea → invert | One line |
| Chosen Now line | One sentence + agent |
| Later / Reject | Why (safety, honesty, ADR, compute, roster-under-check) |
| Data it needs | Sources + honesty label |
| Metric | Empathize §D–E |
| Future problem they hit first | Concrete failure under current architecture |

Do not invent a parent/school persona to carry emissions. If geographic burden appears, put it on **A5 proxy + Yuki/David spillback (I-6)** or Later roadmap — not a new Empathize person.

### C. Omar / A4 anomaly detection — Ideate on its own (mandatory deep section)

Treat anomaly detection as a **first-class Ideate problem**, not a footnote of A4.

Brainstorm then choose:

1. **What is an “anomaly”?** (incident, sensor failure, demand surge, weather regime shift, stale data, message loss, unusual headway, spillback onset)
2. **Detection methods** (EWMA/CUSUM on residuals — Empathize seed; change-point; isolation; weather-conditioned baselines; multi-source fusion)
3. **Evidence Omar needs in an alert:** what / why / confidence / data age / alternate explanations / recommended **bounded** action
4. **FAR vs miss** by severity — no universal detection-delay KPI
5. **Degraded vision:** “nothing wrong” vs “we can’t see”
6. **Weather & roads:** rain/fog as **regime context**, not causal crash proof
7. **Accident / near-miss signals:** official crash feeds vs OSM hazard tags vs news scrape vs **simulated injections** — honesty labels; **no “accident prevention” claim from simulation** — use risk indicators, conflict proxies, detection, response support
8. **Heatmap products:** anomaly clusters; recovery; spillback burden — method + time window required
9. **Rejected:** black-box alert; silent healthy-looking dashboard; weather scrape as sole crash predictor; LLM inventing incidents

End with: **chosen A4 alert contract** (fields, TTL, confidence, severity, reason codes) and **what Synapse may explain vs invent**.

### D. Data collection ideation (CAPTURE 2=b)

**Now (prototype-safe):** OSM roads/intersections, TRANSTU GTFS (scheduled), archived weather, documented public incident datasets, SUMO injects — with provenance, timestamps, licensing, uncertainty, stale-data handling.

**Later (connectors designed, not built):** traffic APIs, collision records, road works, weather alerts, sensor feeds.

**Not Now:** fragile scraping, live operational claims, near-real-time alerting as shipped product.

Fill for each class:

| Data class | Now source | Later connector | Scrape/official/sim? | Persona | Agent | Dirty-data risk | Honesty label |
|---|---|---|---|---|---|---|---|
| Road geometry / maps | OSM extract | — | open map | all | network build | bad lanes/turns | OSM version + hash |
| Intersections / plans | OSM + labelled synthetic | MEHAT/municipal | mixed | Yuki, Amara | A1 envelope | wrong phases | synthetic vs transcribed |
| Scheduled transit | TRANSTU GTFS | live AVL later | official scheduled | Chidi, Rosa | A3 | treat as live | **scheduled ≠ live** |
| Accidents / incidents | public archive + sim inject | police/open APIs | mixed | Omar, Marcus | A4 | rumor as fact | source class + confidence |
| Weather | archived Open-Meteo / national | alerts API | external | Omar, David | A4 regime tag | over-causal | **context feature**, not crash proof |
| Volumes / speeds | SUMO / calibrated | probe/loops | often sim | David, Yuki | A1/A4 | synthetic as observed | label demand source |
| Spacing / headway | SUMO / detectors | CV later | often sim | David, Chidi, Marcus | A1/A3/A4 | “AI saw danger” without definition | spacing = **metric** |
| Pedestrian demand | buttons / SUMO | counts | mixed | Amara | A3 | ignore slow walkers | completion + wait |
| Emission proxies | HBEFA/SUMO | — | sim proxy | *(system KPI)* | A5 | call proxy “AQ” | **proxy only** |
| Heatmaps | derived grids | — | derived | Omar, Yuki | Synapse views | pretty ≠ truth | method + window |

**Forbidden claims:** lives saved; measured Tunis AQ; live Tunis loops unless verified; scraped news as ground-truth crashes; “we prevent accidents” from sim.

### E. Future problems architecture has not yet faced (mandatory)

Brainstorm ≥15, then cluster:

1. **Data / sensing:** OSM drift, GTFS stale, weather API down, scrape ethics, no loops, partial cameras, stale-data as “normal”
2. **Control / safety:** two writers, preemption thrash, ped truncation under EV pressure, override abuse
3. **Multi-agent coordination:** message storms, TTL expiry storms, conflicting A2/A3 bids, board silence
4. **Anomaly / trust:** alert fatigue, anomaly≠cause, weather false correlation, frozen dashboard looks healthy
5. **Equity / burden:** spillback displacement (I-6), bus vs car trade-offs, opaque Synapse text, A5 proxy misread as AQ
6. **Ops / adoption:** Yuki switches system off (I-9); Rosa can’t justify TSP deny; audit gaps
7. **Evaluation honesty:** sim ≠ Tunis deploy; HBEFA→AQ creep; lives-saved creep; accident-prevention wording
8. **Security / misuse:** spoofed EV priority, poisoned feeds, TraCI exposure via Synapse

For each cluster: **which persona feels it first**, **which agent owns mitigation**, **Ideate seed** (not full build).

### F. Architecture convergence (finalize)

**Chosen architecture card:**

- A1 — sole actuator; Max-Pressure; safety mask
- A2 — corridor pre-clear bids; recovery
- A3 — pedestrian clearance + conditional TSP
- A4 — forecast residuals + anomaly / degradation / weather regime tags
- A5 — stop/emission **proxy** + geographic burden analysis (optional KPI)
- Message board: `state/`, `forecast/`, `alerts/`, `eco/`, `priority_request/`
- Synapse (+ optional bounded sub-agents): retrieve, explain, data-quality check, what-if — **no actuation**
- Explicit: what is **agentic** (typed cooperating specialists + retrieval explainer) vs **not** (LLM traffic-light boss)

Compare **3 rejected alternatives** (why rejected under ADR + personas).

### G. Ideate techniques (run them)

1. Brainstorm per working persona (B)
2. Worst Possible Idea × N → invert
3. SCAMPER on A4 anomaly only
4. Morphological chart: Detection × Evidence fields × Action bound × Data honesty
5. Weighted matrix: Safety, Honesty, Persona fit, Feasibility, Auditability, Architecture fit → Now/Later/Reject

## 4. Success criteria

- [ ] CAPTURE choices recorded as 1=d, 2=b, 3=b
- [ ] Decision matrix is the source of truth; presentation view is derived
- [ ] Every idea → persona + insight + agent + architecture fit
- [ ] Omar/A4 anomaly section stands alone
- [ ] Data table has Now vs Later + honesty labels
- [ ] ≥15 future problems clustered with owners
- [ ] Architecture card matches ADR-0001; no new top-level agents
- [ ] Roster count is **not** the deliverable; contested persona → Deferred flag only
- [ ] No LLM-in-control; no lives-saved; no AQ-from-HBEFA; no accident-prevention-from-sim
- [ ] Next action names the artifact path

## 5. Start now

1. Paste CAPTURE answers (1=d, 2=b, 3=b) and restate HMW + ADR in 5 lines.
2. Build **Omar/A4 anomaly Ideate** first.
3. Fill per-persona ideation for the **current pack** (do not audit roster length).
4. Decision matrix + presentation view.
5. Data collection Now/Later + heatmaps/weather/roads.
6. Future-problems catalog.
7. Architecture card + rejected alternatives.
8. Write: `.scratch/coflow5-ideate-finalize/spec.md` (create folder). Do not change Empathize roster claims in this session.

**Next action after finish:** one sentence with the Ideate artifact path and the single highest-risk future problem for Omar/A4.
