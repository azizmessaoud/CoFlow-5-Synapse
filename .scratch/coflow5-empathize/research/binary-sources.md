# Binary sources vs v2 Empathize seed

Question: which User Persona, User Journey, Evidence, or Possible Solution claims in the three binary files are **not** already in `coflow5-personas-journeys.md` (v2)?

Comparison seed: `C:\Users\dell\Downloads\sumo\coflow5-personas-journeys.md` (v2). That file already names eight User Personas (Amara, David, Chidi, Rosa, Marcus, Yuki, Maria, Omar), staged User Journeys, a cited Evidence trail, and Possible Solutions (including the shared ambulance/school/crossing sequence).

Rule used here: a claim is **unique** only if the binary source states it and v2 does not. Overlapping *roles* with different names are unique as names/profiles; the shared need is listed under restatements. Nothing below is invented; every unique claim cites its source. Several IMATM field figures are labelled by that source itself as assumed placeholders — they are recorded as *what the file says*, not as verified field results.

---

## 1. Source extraction log

| Source | On disk | Size | Text extracted? | Method | Failures |
|---|---|---|---|---|---|
| `C:\Users\dell\Downloads\sumo\CoFlow-5_Traffic_Orchestration.pdf` | Yes (18.09.2026) | 14,796,086 bytes | **Yes, via page images** — no selectable PDF text | 15 pages, MediaBox 1376×768. Content streams are only `1376 0 0 768 0 0 cm` plus full-page `/Subtype /Image` (FlateDecode, PNG predictor 15, Columns 1376). Git Perl inflated 45 streams; 15 RGB pages written and read visually. Watermark on every slide: “Gemini Notebook”. | `python` / `python3`: Windows Store stub (`Python est introuvable`). `pandoc`: not installed. `pdftotext`: not installed. Word COM `Documents.Open` on the PDF hung (>2 min) and was killed. A separate Windows.Media.Ocr script failed (`Windows.Globalization.Language` type not loaded). |
| `C:\Users\dell\Downloads\sumo\Intelligent_Multi-Agent_Traffic_Management_Report.docx` | Yes (18.09.2026) | 81,866 bytes | **Yes** | `tar -xf` (OOXML zip) → `word/document.xml` → concatenated `w:t` nodes. ~115,774 characters, 1,513 lines. Title in `docProps/core.xml`: “Intelligent Multi-Agent Traffic Management”; creator “Design Thinking Project Team”; created 2026-09-18. | Python/pandoc unavailable (same as above). Unzip path succeeded. |
| `C:\Users\dell\Downloads\sumo\SUMO_forStudents.docx` | Yes (09.09.2026) | 16,445 bytes | **Yes** | Same OOXML unzip. ~2,124 characters, 46 lines. `core.xml` creator “Akermi Hasni”; `app.xml`: 1 page, 307 words, Word 16. | Python/pandoc unavailable. Unzip path succeeded. |

Working text dumps (not the notes file): `.scratch/coflow5-empathize/research/_extract/imatm.txt` and `_extract/sumo_students.txt`.

---

## 2. Unique claims (not in v2)

### 2.1 Unique User Persona names / profiles

**From `Intelligent_Multi-Agent_Traffic_Management_Report.docx` §3.3** — six named User Personas. None of these names, ages, or local Tunis profiles appear in v2.

| Source ID | Name | Label in source | Unique profile facts (source) |
|---|---|---|---|
| P-1 | Amine Belhaj | “The Commuter” | 34; software developer at a firm in Les Berges du Lac; married, daughter aged 6; Ariana Ville → school drop-off → Les Berges du Lac, ~11 km in a 2015 Renault Clio; leaves at 06:50 rather than 07:30; uses Waze including through narrow residential streets. |
| P-2 | Karim Nasri | “The First Responder” | 38; ambulance driver at a central hospital, 7 years in role; two legs per call (scene, then hospital); uses siren/lights in peak; chooses wider routes; radio + dispatch tablet. |
| P-3 | Nadia Ben Salah | “The Pedestrian with Reduced Mobility” | 62; retired primary-school teacher; osteoarthritis both knees; cane; comfortable speed “approximately 0.8 m/s”; crosses a four-lane central avenue twice daily to market and pharmacy; low digital comfort — “any solution that requires an app excludes her”. |
| P-4 | Hichem Ouali | “The Bus Driver” | 45; public-transport driver, 12 years; high-frequency central line, 10-minute scheduled headway; route ~40 min on schedule / up to 70 min in peak; dwell 12–90 s. **Driver, not passenger** (v2’s Chidi is a bus commuter). |
| P-5 | Emna Jlassi | “The Traffic Operator” | 29; municipal mobility traffic engineer; civil engineering degree; self-taught Python and QGIS; plans in force computed in 2016; most junctions have no permanent detection; manual counts ~once a year; tools: Excel, vendor timing app, self-maintained GIS. |
| P-6 | Leila Mansour | “The Resident on the Junction” | 36; pharmacist; second-floor windows on a saturated junction; son Yassine, 8, diagnosed with asthma; queues ~07:00–09:30 and evening peak; windows closed year-round; child’s bed moved to rear of flat. |

Stakeholder map unique to this docx (§3.2): TRANSTU named as transit operator; quadrants by influence × exposure; “P-5 represents” high-influence operators; P-3, P-4, P-6 as low-influence / high-exposure.

**From `CoFlow-5_Traffic_Orchestration.pdf` page 11** — no personal names. Six *category* labels in a “STAKEHOLDER” table (source’s word): Drivers; Emergency Services; Pedestrians / Transit (one combined row); Operators in Crisis; Residents; City Engineers. Unique vs v2’s eight named User Personas: the PDF merges pedestrians with transit, and it does not name a depot-controller User Persona (v2 Rosa) as its own row.

**From `SUMO_forStudents.docx`:** no User Persona names.

### 2.2 Unique User Journeys

**IMATM docx** — each User Persona has a “Journey” / working-reality block (§3.3) that v2 does not use:

- **Amine:** trip time “between 22 and 55 minutes with no warning”; waits “up to 90 s at a red light while the conflicting approach is visibly empty”; quoted (interview 3): “I don’t mind driving thirty minutes. I mind not knowing whether it will be thirty or sixty.”
- **Karim:** drivers want to yield but have nowhere to go; local pre-emption “only moves the queue to the next one”; quoted (ride-along): “A green light when I am already at the line is worth nothing.”
- **Nadia:** commits after the signal; if countdown ends mid-crossing she keeps going and raises her hand; 12-second pedestrian green vs 18 seconds she needs; waits “over two minutes”; no refuge island; quoted (interview 8): “The green is made for young legs.”
- **Hichem:** bunching until he is “nose-to-tail with the bus in front while the following gap grows to 25 minutes”; quoted (ride-along): “I carry ninety people. The car in front of me carries one. We wait exactly the same.”
- **Emna:** can change timing in ten minutes but cannot demonstrate effect; vendors offer adaptive systems she cannot inspect; quoted (shadowing / prototype review): “If I cannot explain why the system did that, I will switch it off the first time somebody complains.”
- **Leila:** quoted (interview 11): “The cars pass. We stay.” and “Nobody has ever measured the air on this street. So officially, there is no problem here.”

Consolidated empathy map (docx Table 6) is unique as a packed User Journey synthesis: every User Persona described “variance, exclusion or invisibility”, none “a problem of average speed”.

**PDF page 6 — “System Synergy in Action: The 08:12 Crash”** (unique staged sequence; not v2’s ambulance/school/crossing table):

| Time | What the slide states |
|---|---|
| T=00 | A4 notices speeds collapsing vs forecast; raises confidence alert. |
| T+01 | Neighbouring A1 controllers switch to “protect blocked road” mode to prevent spillback. |
| T+02 | A2 dispatches ambulance via A4 predictions; requests cleared queued queues ahead. |
| T+03 | A1 accepts request, runs safe transition sequence. |
| T+04 | A3 reroutes late buses; A5 tracks emission spike and dynamically adjusts weights (λ). |

**SUMO_forStudents.docx:** no staged User Journey.

### 2.3 Unique Evidence citations / figures

**IMATM docx** states a field protocol and investigation table. **The same file warns these digits are assumed:** §3.1: “Adapt before submission: the numbers in Table 4 describe the protocol this report assumes.” §4.2: figures marked ▲ “come from baseline simulation runs and field sessions” and “replace them with your own numbers before submission — the method is the deliverable, the specific digits are not.” Unique *as claims the file makes*, not as validated Evidence.

Protocol the file assumes (Table 4): 12 semi-structured interviews (4 commuters, 2 emergency staff, 2 transit staff, 2 municipal engineers, 2 residents); 1 ambulance + 2 bus ride-alongs; 4 observation sessions of 45 min at 2 junctions; 1 half-day engineer shadowing; 61 questionnaire responses; 214 coded notes; walking-speed sample n = 84 (Appendix A.5).

Investigation figures the file prints (Table 9), all marked ▲ in the source:

| ID | Figure the docx states |
|---|---|
| I-1 | Mean route time 27.4 min; 90th percentile 46.1 min; buffer time index 0.68; 74% of questionnaire respondents leave ≥15 min earlier than necessary. |
| I-2 | 21.3% of green seconds network-wide served to an empty approach; three worst junctions >30%. |
| I-3 | Local pre-emption reduced EV travel time by only 8.1%; in 63% of runs the EV still stopped because the downstream link was full. |
| I-4 | Median walking speed 1.24 m/s; 15th percentile 0.79 m/s; 19% of observed crossings not completed before conflicting green. “Standard design speed of 1.2 m/s is itself the median.” |
| I-5 | Bus delay per vehicle 1.12× cars; headway CV 0.18 at first stop → 0.57 by eighth. |
| I-6 | Greedy local controller: +11% own-junction throughput, +34% network blocked-junction events, +26% flow on two residential streets. |
| I-7 | Per-cell CO₂ correlated with stops r = 0.81 vs vehicle-kilometres r = 0.46. |
| I-10 | Incident-affected periods 7% of simulated time but 31% of total network delay; recovery 18–26 min after clearance. |

Also unique to this docx: Karim “loses an estimated 4–8 minutes per peak-hour run” (§3.3); study area Tunis city centre corridor, ~2.4 km², 18 signalised junctions, 4 unsignalised, 2 roundabouts (§2.1); WHO air-quality guideline values listed as secondary data (Table 4); I-9 flagged by the source as weakest (single operator session).

Rejected hypotheses unique to the docx (§4.3.1): “drivers are the obstacle to emergency vehicles” rejected in favour of a capacity/space problem; “congestion is the main driver of local emissions” partially rejected in favour of stop-start behaviour.

References in the docx that are **not** in v2’s §9 Evidence trail: Brown (2008) Design Thinking; Chen et al. (2020) “thousand lights”; Geroliminis & Daganzo (2008) MFD; Lopez et al. (2018) SUMO; Lowe et al. (2017); Mnih et al. (2015); Ng et al. (1999) reward shaping; Schulman et al. (2017) PPO; Van Hasselt et al. (2016); Varaiya (2013) max pressure; Wang et al. (2016) dueling; Wei et al. (2018) IntelliLight; Zheng et al. (2019) PressLight; Alegre SUMO-RL. (Daganzo 2009 bunching *is* already in v2 — restatement.)

**PDF** — slides cite almost no primary sources. Unique *slide-stated* figures / named systems (architecture Evidence, not interview Evidence):

- Page 2: Classical Max-Pressure “blind to spillback”; Learning-based (RESCO, MPLight) “synthetic 4x4 grids”, “Zero deployments”; LLMLight “high latency” unfit for “second-by-second control loops”; siloed optimisation studies “EVs, pedestrians, and emissions one at a time”.
- Page 8: “Standard SUMO ‘blue lights’ ignore red lights (unsafe upper bound)”.
- Page 8: pedestrian max-wait “60-90s” (v2’s proposed cap is 40 s).
- Page 12: “11 specific scenarios”; H1 “MARL beats Max-Pressure by ≥5% under non-stationary demand”; H6 “30% packet loss and 500ms latency degrade performance by ≤10%”; H7 transfer from 4×4 “to realistic region with bounded loss”; scenario dots S0–S10.
- Page 14: emulators test “up to 30% loss”; “GDPR-compliant anonymization of probe/Wi-Fi data”.

**SUMO_forStudents.docx:** no Evidence citations.

### 2.4 Unique Possible Solutions

**IMATM docx §6** — ten numbered Possible Solutions (S-1…S-10) with owning “agent” names **Junction / Emergency Corridor / Transit Priority and Regularity / Vulnerable Road User / Network Supervisor** (not v2’s A1–A5 labels), plus targets the seed does not use:

| ID | Unique mechanism / target the docx states |
|---|---|
| S-1 | 15-min GNN+LSTM forecast; DE-CONGESTION when forecast v/c > 0.85; target buffer time index **−30%**. |
| S-2 | Pressure-based RL every 5 s; empty-green target **< 5%**; mean delay **−20%** vs fixed-time. |
| S-3 | Rolling corridor 3–4 junctions; lead 60–120 s; max pre-emption 45 s/junction; cross-street cap **100 s**; EV time **−35%**, **≤ 1 stop**. |
| S-4 | Speed bands 0.6 / 0.8 / 1.0 / 1.2 m/s; long-press push-button fallback; right-turn suppression; clearance from 15th-percentile of those present; pedestrian max wait **≤ 60 s**; 100% completion before conflicting green. |
| S-5 | Priority only if headway deviation > 1.3× and occupancy > 20; holding the leader (max 45 s); optional stop-skipping; headway CV **−40%**. |
| S-6 | Spillback penalty at 80% downstream occupancy; perimeter gating at 85% critical accumulation, max 30% inflow cut, max 15 min; blocked-junction events **−60%**. |
| S-7 | AIR-QUALITY regime 07:00–10:00 and 16:00–19:00; HBEFA3 hotspots on **50 m cells**; emission weight 0.1 → 0.35; hotspot CO₂ **−12%**; delay penalty cap **8%**. |
| S-8 | **Shadow baseline** (parallel fixed-time simulation of the same demand); “why did junction 12 do that at 08:14?”; 90-day explanation retention. |
| S-9 | Forecast-residual detection; confirm over two 120 s windows; detect **≤ 120 s**; false-positive **< 1 per hour per zone**; recovery regime held 10 min after flow resumes. |
| S-10 | Hard max wait **120 s** per approach (**90 s** if a pedestrian crossing); Jain index **≥ 0.85** — “no persona asked for this”; predicted harm of the optimiser. |

Fail-safe unique vs v2’s fallback ladder: on detection/comms/confidence loss, “reverts to the **existing fixed-time plan**” (docx §5.6). v2’s ladder is watchdog → Max-Pressure → actuated → fixed-time.

Arbitration order unique wording (docx §5.4.1): safety shell → pedestrian already in crossing (outranks emergency) → emergency → VRU max-wait → fairness cap → conditional transit → learned policy last.

**PDF Possible Solutions not in v2 (or named differently):**

- Page 3: “City as a Hospital Ward”; only one entity “has the authority to press the light buttons” (Central Actuator).
- Page 4 agent nicknames/timescales: A1 FLOW “Sole Actuator” 5–10s; A2 EMERGENCY “Navigator” 1–2s; A3 MULTIMODAL “Voice of the People” 5–10s (pedestrian wait bounds **and** transit TSP bids in one specialist); A4 SITUATION “Radar” 60s–5m; A5 SUSTAINABILITY “Environmental Officer” 5m, dynamic eco-weighting λ.
- Page 5: Layer 2 “Sensor & Channel Emulators” inject range limits, noise, dropout, and latency (not in v2).
- Page 7: watchdog — if learned policy fails or inputs invalid, “A1 instantly falls back to **provable Max-Pressure**” (not v2’s four-rung ladder).
- Page 8: A2 “time-dependent shortest path on predicted times”; A3 bids = **occupancy × expected seconds saved**; KPI “EV benefit per civilian delay”.
- Page 9: forecast stack “ARIMA → LightGBM → LSTM”; “If prediction variance is too high, A4 **stays silent**”; λ “rises when delay slack exists, and falls when travel-time budgets are exceeded”.
- Page 10: “Priority Auction” with Layer 3 **Net-Benefit Auction** `Bid = (Benefit − Externality)` and Layer 4 **Anti-Thrash** cooldowns. Priority order on the slide: **EV > Incident Protection > Pedestrian Deadline > Conditional Transit > General Flow > Eco** (differs from IMATM’s “in-crossing pedestrian outranks EV”, and from v2’s narrative that pedestrian clearance is preserved before conflicting release).
- Page 6 T+04: “A3 **reroutes** late buses” (v2 Possible Solution is conditional priority / holding, not reroute).
- Page 13: 14-week tiers — Tier 0 week 6, Tier 1 week 10 (A2, A3, A5 + message bus), Tier 2 week 12 (learned A4, comms-failure sweeps, **scale to 200+**). “If a tier slips, features are cut, not statistical rigor.”
- Page 14 Breaker 4: GDPR / probe / Wi-Fi anonymisation as a Possible Solution constraint.

**SUMO_forStudents.docx:** no concrete Possible Solution. Only open questions (“What information should an agent use?” …) and a “Think Beyond Traffic Lights” list.

---

## 3. Claims that only restate the v2 markdown

Same need, restated with other names or architecture labels:

- Slow walker with a cane at ~0.8 m/s who needs enough crossing time (v2 Amara; IMATM Nadia).
- Predictability valued over a faster mean (v2 David; IMATM Amine; PDF page 11 “Drivers / Predictability / P95 travel time”).
- Emergency passage needs space / pre-clearance, not only a green at the stop line (v2 Marcus; IMATM Karim / S-3; PDF A2 queue pre-clearance).
- Bus bunching and person-weighted / conditional priority, not unconditional TSP (v2 Chidi; IMATM Hichem / S-5; PDF A3).
- Operator needs explanations, override, and an audit trail (v2 Yuki / Rosa; IMATM Emna / S-8; PDF “City Engineers / Trust / reason-code coverage”).
- Residents must not absorb displaced queues/emissions; HBEFA outputs are proxies (v2 Maria + flags §8; IMATM Leila / S-7; PDF A5 “emission proxy tracking”, page 11 “Exposure near receptors”).
- Incidents drive a large share of delay; detection must be scored with false alarms (v2 Omar / FHWA 25–30%; IMATM I-10 31% of delay in *their* simulation; PDF A4 detection delay & FAR).
- Pedestrian already in the crossing finishes; conflicting greens forbidden (v2 P1/P5/P6; IMATM safety shell; PDF Layer 1 hard safety).
- Fallback when sensors/comms/policy fail (v2 P6 ladder; IMATM fixed-time revert; PDF Max-Pressure watchdog / neighbor masking).
- Design Thinking Empathize → Define → Ideate → Prototype → Test (all three binaries + v2’s Empathize framing).
- SUMO + TraCI / libsumo, Max-Pressure baseline, multi-specialist cooperation with one actuator (v2 traceability A1–A5; PDF pages 4–5; IMATM five “agents”).
- Daganzo (2009) bunching (IMATM references **and** v2 Evidence trail).

PDF page 11 is a compressed restatement of v2’s eight User Personas into six stakeholder rows (Rosa’s depot-controller User Persona is the one v2 row with no PDF counterpart).

---

## 4. `SUMO_forStudents.docx` — not a SUMO tooling tutorial; almost no Empathize material

The file is a **one-page student project brief**, not Eclipse SUMO documentation.

What it contains: project title “Intelligent Multi-Agent Traffic Management”; urban congestion as a changing problem; Design Thinking (understand the problem, stakeholders and needs, Possible Solutions, prototype, test); challenge quote “How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?”; open design questions; expected outcome (prototype, experiments, baseline comparison, strengths and limitations); a “Think Beyond Traffic Lights” list: “Emergency vehicles • pedestrians • public transportation • sustainability • pollution • accident scenarios • communication between agents • prediction • large-scale urban networks”.

What it does **not** contain: named User Personas; staged User Journeys; Evidence citations; specified Possible Solutions; SUMO install/CLI/netconvert tutorial material.

Empathize yield: only the methodology prompt and that factor list. Safe to treat as **no Empathize roster** for the pack; do not harvest User Personas from it.

---

## 5. Implications for the Empathize pack (not decisions)

- **Roster conflict:** v2 keeps eight named User Personas; IMATM keeps six different names in Tunis. Unique names are real, but they are an alternate roster, not extra people to silently append.
- **Evidence bar:** IMATM’s interview counts and Table 9 digits are self-labelled placeholders. They must not enter Evidence as primary-source findings. PDF slides are Gemini Notebook architecture graphics with almost no citations — treat slide numbers as Possible Solution statements, not Evidence.
- **Possible Solution mismatch to flag if merged:** PDF priority order (EV above pedestrian deadline) vs IMATM/v2 (person already in the crossing outranks EV); PDF pedestrian wait 60–90 s vs v2 proposed 40 s cap; PDF A3 bus reroute vs v2 conditional priority; fallback target (Max-Pressure vs fixed-time vs v2 ladder).
- **Rosa / Omar:** present in v2, absent as named User Personas in all three binaries (PDF only has “Operators in Crisis” + “City Engineers”).
)
