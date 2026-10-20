# Learn the project: what we built, in simple words

This guide explains the whole TraffiX / CoFlow-5 Synapse project to the team.
Read it from top to bottom once. After that, use it as a reference.

Each part answers three questions: **what is it**, **how does it work**, and **why did we build it this way**.

---

## Part 0. The project in one minute

**The problem.** The traffic lights in Tunis centre-ville work alone. Each light sees only its own queue. An ambulance can arrive at a red light. A late bus waits like everyone else. Green can start while a person is still crossing. No one can say why a light changed.

**Our answer.** A team of software agents controls six real junctions (J1–J6) in a simulation of Tunis centre-ville. Each agent has one small job. A strict hierarchy decides who may change a light. A separate layer, **Synapse**, explains every decision in plain language, or says "I don't know" (abstains).

**Three sentences to remember:**
1. **Agents decide.** Many small agents propose; one master per junction decides.
2. **Synapse explains.** It reads the decisions and explains them with proof. It can never change a light.
3. **Safety is code.** The safety rules are fixed code. No model and no LLM can change them.

---

## Part 1. The basic words

| Word | Simple meaning |
|---|---|
| **SUMO** | A free traffic simulator. It moves every car, bus, ambulance and person, one second at a time. It is our "city". |
| **TraCI / libsumo** | The connection between our Python code and SUMO. We use it to read sensors and to set lights. |
| **OSM (OpenStreetMap)** | A free map of the world, made by volunteers. We took the real streets of Tunis from it. |
| **netconvert** | A SUMO tool. It turns the OSM map into a road network that SUMO can drive on. |
| **Junction / TLS** | A crossroads. TLS = traffic light system, the light at that junction. |
| **Phase** | One light pattern, for example "north–south green, east–west red". |
| **Agent** | A small program with one job. It looks at some data and sends messages. |
| **Rule** | A simple fixed instruction we wrote, for example "if a reading is older than 10 s, it is stale". |
| **Model (ML)** | A program that learned a pattern from examples, for example "how many seconds until this ambulance reaches the light". |
| **LLM** | Large Language Model (Claude, GPT-style). Good at writing and understanding text. We use it only to explain. |
| **Seed** | A number that fixes the random generator. The same seed gives exactly the same traffic, so we can repeat a test. |
| **Actuated** | SUMO's normal "smart" light: green stays while cars keep arriving, and stops at a gap or a time limit. It is our main comparison (baseline). |
| **Scenario** | A situation to test: morning peak, rain, an incident, an emergency, Ramadan before iftar, and so on. We have 12. |
| **Decision log** | A file. Every decision goes into it with a **reason code** (for example `EMERGENCY_GRANTED_HOLD`). |

---

## Part 2. The map: six real junctions

We took the real streets of Tunis centre-ville from OpenStreetMap and cut a box of about 1.4 × 1.4 km.
Six junctions in the box get a traffic light that our agents control. All other junctions have no light (cars give way).

| Light | Real streets |
|---|---|
| J1 | Av. Habib Bourguiba × Place du 14 Janvier 2011 × Av. Mohamed V (a roundabout) |
| J2 | Av. Habib Bourguiba × Av. de France × Rue Jamel Abdel Nasser × Rue de Rome |
| J3 | Rue Saad Zagloul × Av. Moncef Bey |
| J4 | Av. Habib Thameur × Rue de Rome × Rue Mokhtar Attia |
| J5 | Av. Habib Thameur × Rue de Sparte × Rue Salonique × Rue d'Athènes |
| J6 | Av. Habib Bourguiba × Rue d'Alger |

**How the map is built** (`scripts/build_tunis_centre_6j.py`):
1. Cut the box out of the big Tunis OSM file.
2. Remove the light tags from OSM, then tell netconvert to put lights on our six junctions only.
3. Rename the junctions and their lights to J1…J6, and store the street names.
4. Give junction roads without a speed limit the Tunisian urban limit: 50 km/h.
5. Add the real TRANSTU bus lines and their stops.
6. Make the traffic (cars, buses, ambulances, pedestrians) with a fixed seed.
7. Write `junctions.json`: the facts about each junction (phases, neighbours, bus stops).

Result: 1,335 roads, 6 lights, 16 bus stops, 25 bus-line directions.

Files: `scenarios/tunis-centre-6j/`, config in `config/networks/tunis6j.yaml`.

**Honest note:** only 3 of the 21 roads that touch J1–J6 have real lane counts in OSM. The other 18 use SUMO's default lane counts. They are listed in `lane_overrides.json` and on a printable `field-survey-sheet.html` for a site visit.

---

## Part 3. The big picture: four levels

Think of a city traffic department:

| Level | In real life | In our code |
|---|---|---|
| 4. Interface | the screens people look at | 7 web pages (React) + an API (FastAPI) |
| 3. Explanation | the press officer who explains what happened | **Synapse** (explainer, copilot, alert writer, CoFlow bridge) |
| 2. City level | the central control room | **Supermaster** + 8 network agents |
| 1. Junction level | the officer at each crossroads, with assistants | **Master** + 5 junction agents, at each of J1–J6 |
| 0. The city | the streets | **SUMO** + sensors + **executor** |

```
  7 web pages (React)
        │  REST only
  FastAPI  (/api/state, /api/ask, /api/synapse/...)
        │  read only
  SYNAPSE ── reads the decision log ── never touches a light
  ─────────────────────────────────────────────────────────
  SUPERMASTER ── 8 network agents ── sends "directives" down
        │
  MASTER J1 … MASTER J6 ── each has 5 junction agents
        │  request()
  EXECUTOR + SAFETY RULES ── the ONLY code that changes a light
        │
  SUMO (the simulated city) ── sensors go back up to the agents
```

**One important idea:** information goes UP through sensors and messages. Only ONE path goes DOWN to the lights: master → safety rules → executor. Everything else can only *ask*.

---

## Part 4. One second of simulation, step by step

The loop is in `traffix/orchestration/system.py`. Every simulated second:

1. **SUMO moves** every vehicle and person one step.
2. **The world** adds scenario events: rain starts, a car breaks down, a sensor freezes. (`simulation/world.py`) Agents are NOT told about these. They must detect them.
3. **Sensors** read the queues, speeds, people waiting and vehicles approaching. Each reading has a time stamp, so an agent can see old (stale) data. (`simulation/sensors.py`)
4. **The supermaster** runs its network agents. Most run every 5 s. Three run every second (incident, transit monitor, emergency route).
5. **Each master** lets its 5 junction agents look and post messages, then decides.
6. **The executor** runs the safe change of the light: clear the crossing → yellow → new green.
7. **The message bus** deletes expired messages.
8. **The decision log** has stored every decision with its reason code.

---

## Part 5. The agents, one by one

### 5.1 How every agent works (`traffix/agents/base.py`)

All agents share the same base class. Each agent:
- reads the **sensors** and the **message bus**;
- writes only **messages** (requests, proposals, directives, publications);
- never touches SUMO and never changes a light.

**Model or rule?** If a trained model file exists in `models/`, the agent uses it. If there is no file, or the file was trained with another scikit-learn version, the agent uses its **rule**. So every agent always works, even with no trained model.

### 5.2 The junction level (six copies: one at each of J1–J6)

#### The Master (`orchestration/master.py`)
- **Job:** the boss of one junction. The only one who decides its light.
- **How:** every second it collects all requests and proposals, then applies a **fixed priority order**:
  **safety > emergency > supermaster directive > late bus > pedestrian > normal traffic.**
- **Model:** none. The order is fixed code.
- **Why no model?** Safety and priority must be the same every day. You must be able to explain them in one sentence.
- **Also:** it chooses a **mode** from data health: `max_pressure` (all data fresh) → `actuated` (exit data stale) → `fixed` (entry data stale). This is "graceful degradation": bad data → a simpler, safer mode.

#### 1. Traffic light agent (`agents/junction/traffic_light.py`)
- **Job:** proposes the next phase for normal traffic.
- **How (max-pressure):** pressure = cars waiting to enter − cars waiting after the junction + waiting pedestrians + a bonus when a platoon comes from a neighbour. The phase with the most pressure wins.
  - Simple picture: open the door where the most people push, but only if the room behind the door is not full.
- **Model:** max-pressure is a proven control algorithm, not machine learning. Its settings were tuned by search.
- **Two other versions** (for experiments):
  - **Predictive** (`predictive_light.py`): simulates the next 60 seconds for a few plans ("keep green", "switch now", "switch in 10 s") and picks the plan with the least waiting. It uses the **arrivals model**.
  - **Reinforcement learning** (`rl_light.py`): learned *when* to switch from experience (see Part 7.4).

#### 2. Pedestrian agent (`pedestrian.py`)
- **Job:** asks for a walk signal when people wait too long.
- **Model:** a classifier that predicts "this person will wait too long". Rule: wait > threshold.
- **Also:** asks the safety rules to hold the crossing while someone is still on it.

#### 3. Transit priority agent (`transit_priority.py`)
- **Job:** asks for priority for a bus, but **only if the bus is late**. A bus on time gets nothing (reason `BUS_NOT_LATE`).
- **Model:** bus ETA regressor (seconds until the bus reaches the light).
- **Why only late buses?** Priority for every bus would hurt everyone else. Late buses cause bunching.

#### 4. Emergency priority agent (`emergency_priority.py`)
- **Job:** asks for green for an ambulance, police car or fire truck before it arrives.
- **Model:** ambulance ETA regressor. Rule: distance ÷ speed.

#### 5. Sensor health agent (`sensor_health.py`)
- **Job:** finds frozen detectors and publishes `DATA_STALE`. The master then drops to a safer mode.
- **Model:** a classifier exists, but on the test data the **rule is better** (F1 0.98 vs 0.75). So the model file was deleted and the agent uses its rule (no update for 10 s → stale).

### 5.3 The city level: the Supermaster and 8 network agents

The **supermaster** (`orchestration/supermaster.py`) runs these agents. It never changes a light. It sends **directives** that the masters weigh in their priority order.

| Agent | Job (simple) | Model | What it sends |
|---|---|---|---|
| **Demand forecast** | "How busy will it be in the next hour?" | 2 regressors, trained on calendar features (hour, day, Ramadan, minutes to sunset, holidays) | a forecast |
| **Incident detection** | "Is a lane blocked?" (a car stopped in the middle of a road, not at a light) | classifier; rule: stopped mid-block for N seconds | `INCIDENT`, `CONGESTION` |
| **Rerouting** | "Is there a faster Route B?" | travel-time regressor + shortest path (Dijkstra) | advice to drivers only |
| **Emergency route** | "An ambulance is coming: warn the next junctions" | arrival-time regressor | `EMERGENCY_PREPARE` directive |
| **Corridor** | "A group of cars leaves J6 towards J1: give them a green wave" | tuned weight | `CORRIDOR_BIAS` directive |
| **Transit monitor** | "Which buses are late?" | lateness regressor | `LATE` bus publication |
| **Weather** | "It rains: longer yellow and crossing time. A road floods: avoid it." | rain-speed regressor | `WEATHER_TIMING`, `FLOOD` |
| **Notification** | "Who must see this alert?" (driver, pedestrian, operator…) | decision tree that copies our rules | alerts for the 7 pages |

**Why a network level?** One junction cannot see an ambulance two junctions away, a blocked road, the rain or a whole bus line. The supermaster sees the whole network.

### 5.4 The Synapse level: explaining, never deciding

| Agent | Job | Model | Tools |
|---|---|---|---|
| **Explainer** (`agents/network/explainer.py`) | answers "why did this happen?" with proof | an LLM (Claude Sonnet, or Groq `gpt-oss-120b`); templates without a key | `search_log`, `get_live_state`, `get_results` |
| **Operator copilot** (`synapse/copilot.py`) | summary of the situation and suggested actions for the operator | LLM; rules + templates without a key | `context()`, `summary()`, `report()`, `decide()` (only records approve / reject) |
| **Alert writer** (`synapse/alert_writer.py`) | writes alerts in English, French and Arabic | small fast LLM (Claude Haiku or Groq `gpt-oss-20b`); built-in texts without a key | templates; a rewrite that changes a number is rejected |
| **CoFlow Synapse bridge** (`synapse/coflow_bridge.py`) | checks a decision or a claim: **verified**, **template**, or **abstain** | **no LLM**, deterministic | the reason-code table, the decision log, CoFlow `SynapseService`, 7 provenance hashes |

**Why can't Synapse change a light?** Because an LLM can make mistakes. So Synapse has no code path to SUMO or the executor. `scripts/check_architecture.py` fails the build if someone adds one.

---

## Part 6. How the agents talk: the message bus

File: `traffix/core/messages.py`. Agents never call each other. They post messages on a shared board.

| Message kind | From → to | Example |
|---|---|---|
| **Request** | junction agent → its master | "green for link 7, ambulance coming" |
| **Proposal** | traffic light agent → master | "switch to phase 2" |
| **Directive** | supermaster → master | "ambulance at J1 in 30 s, prepare" |
| **Publication** | anyone → everyone | "lane X data is stale", "incident on road Y" |
| **Status** | master → neighbours and supermaster | my queues, my mode, my green |
| **Notification** | notification agent → web pages | "Flood alert: road Z is closed" |

**Every message has an expiry time.** An old request disappears by itself. So a request for an ambulance that already passed cannot block the junction.

**Neighbours cooperate:** a master publishes its queues. The neighbouring traffic light agent reads them to know if the road after its junction has room.

---

## Part 7. The models: what they learned and how

### 7.1 Where the training data comes from

We have no real traffic counts for these junctions. So **SUMO is our teacher**:
1. We run 20 simulations (10 scenarios × 2 seeds) with **2025 dates**.
2. A recorder writes, at each moment, **what an agent saw** (the input) and later **what really happened** (the answer, the "label").
   - Example: "the ambulance was 300 m away at 12 m/s" → "it really arrived 27 s later".
3. This gives about 850,000 rows without any manual labelling.

Agents never see the scenario events or the calendar settings. Otherwise their good results would be fake.

### 7.2 The model family: gradient-boosted trees

Almost all models are **HistGradientBoosting** (scikit-learn), the same family as XGBoost and LightGBM.

- **Simple idea:** a decision tree asks questions ("queue > 8 cars?", "raining?"). Boosting builds hundreds of small trees; each new tree corrects the errors of the previous ones.
- **Classifier** = answers a yes/no question ("will this person wait too long?").
- **Regressor** = answers a number ("how many seconds until the bus arrives?").

**Why this family?**
- Our data is tables of numbers. Boosted trees are the strongest standard choice for tables.
- They learn thresholds and combinations (rain × queue).
- They train in seconds on a laptop CPU.
- We can compare them with a simple rule on the same test data.

**Why not deep learning?** Little data, decisions every second, and every decision must be explained.

### 7.3 How we test a model: "beat the rule"

1. Split the rows: 75% to learn, 25% to test.
2. Measure the model AND the old rule on the same 25%.
3. **We use a model only if it beats its rule.** Otherwise we keep the rule.

**Demand forecast:** we train on 2025 and test on 2026. Ramadan moves about 11 days each year. A model that learned "March is quiet" fails in 2026. Ours learned "Ramadan is quiet": error 0.026 vs 0.103 for the naive method.

**Results from the latest full training** (`models/metrics.json`). MAE: lower is better. F1: higher is better.

| Model | Predicts | Model | Rule | Verdict |
|---|---|---|---|---|
| demand forecast | traffic level (2026) | 0.023 | 0.044 | model wins |
| pedestrian | someone will wait too long | F1 0.443 | F1 0.0 | model wins, but still weak |
| ambulance ETA | seconds to the light | 43.7 s | 92.6 s | model wins |
| bus ETA | seconds to the light | 139.7 s | 285.8 s | model wins |
| bus lateness | gap to the previous bus | 158.9 s | 212.3 s | model wins (only 270 rows) |
| edge travel time | road travel time | 0.53 | 2.5 | model wins |
| rain speed | slowdown in rain | 0.15 | 0.38 | model wins |
| arrivals | cars in the next 30 s | 0.69 | 0.69 | equal |
| sensor health | frozen detector | F1 0.752 | F1 0.978 | **rule wins** |
| incident | blocked lane | — | — | not trained: the training incidents were on roads without a detector (now fixed); the agent uses its rule |
| notification | who sees an alert | 100% | — | copies our own rules; proves nothing |

**7 of 11 models beat their rule.**

### 7.4 Tuning and reinforcement learning

**Tuning** (`training/tune.py`): we tried 8 random settings for the light agents in simulation.
Score = car wait + pedestrian wait (lower is better). No setting beat the defaults, so the defaults stay.

**Reinforcement learning (RL)** (`training/rl.py`, method: Fitted Q-Iteration):
- **Simple idea:** the agent tries actions, sees the result, and learns which action pays off later, not only now.
- **State:** 36 numbers (own queues, cars arriving, room after the junction, neighbours' queues, pedestrians, forecast, rain).
- **Action:** keep the green, or switch (max-pressure gives the candidate phase).
- **Reward:** less waiting here **and** at the neighbours (cooperation), and a small penalty for each switch.
- **Safety:** a 60 s guard prevents one direction from waiting forever. It still only *proposes*.

Result of the latest training:

| Test | Car + pedestrian wait |
|---|---|
| RL, round 3 (with exploration) | 208.9 s |
| **RL, final test (no exploration)** | **231.4 s** |
| **Max-pressure alone** | **221.9 s** |

The RL agent learned something, but in the fair test it is about 4% worse than max-pressure. So **max-pressure stays the default**. RL is an option for experiments (`traffix_rl`). This is an honest result: say it.

### 7.5 The LLMs

We do **not** train the LLMs. We call them through an API (`traffix/synapse/llm.py`):
- **Anthropic** (Claude) if `ANTHROPIC_API_KEY` is set, or **Groq** if `GROQ_API_KEY` is set. Config: `config/agents.yaml`.
- Strong model for explaining (explainer, copilot). Small fast model for short alerts.
- **No key or API error → templates.** The demo works offline. The control loop never waits for an LLM.

---

## Part 8. The AI agent with tools (the explainer)

This is the "agentic AI" part: an LLM that **chooses tools** and **uses them** before it answers.

```
Analyst: "Why did the ambulance get green at J1?"
     │
     ▼
LLM reads the question and the 3 tool descriptions
     │  chooses: search_log("ambulance J1")
     ▼
Python runs the function ──► returns log lines: #336, #337, #341
     │
LLM may call more tools (up to 5 rounds): get_live_state(), get_results("ambulance trip")
     │
LLM writes an answer that cites [#337]
     │
Python checks every [#id]: does it exist in the log?
     ├── yes → answer shown with its citations
     └── no  → rejected → "ABSTAIN"
```

| Tool | What the Python function returns |
|---|---|
| `search_log(query)` | matching decisions as plain sentences, each with its id |
| `get_live_state()` | clock, junction modes and queues, incidents, congestion, weather |
| `get_results(measure)` | experiment results for a measure, by scenario and controller |

- A **tool** = a description the LLM reads (name, purpose, inputs).
- A **function** = the Python code that does the work.
- The LLM never runs code itself. It only asks; Python runs.
- No tool can change a light, call SUMO or open the internet.

The **CoFlow Synapse bridge** adds a second check without any LLM. It turns each log line into evidence and returns:
- **verified**: the reason code is known and is cited;
- **template**: no citation; the answer is built only from the recorded facts;
- **abstain**: unknown decision, or a claim the facts do not support.

API: `POST /api/synapse/explain`, `POST /api/synapse/audit`, `GET /api/synapse/metrics`.

---

## Part 9. The agentic design patterns we used

| Pattern | Simple meaning | Where | Why |
|---|---|---|---|
| **Hierarchical supervisor** | a boss above bosses | supermaster → masters → agents | city problems need a wide view; local decisions stay fast |
| **Single writer** | only one person holds the pen | master + executor | no two agents can give a light opposite orders |
| **Propose → arbitrate** | agents ask, the boss decides | `master.py` | many opinions, one clear decision with a reason |
| **Publish / subscribe (blackboard)** | a shared notice board | `core/messages.py` | agents share facts without knowing each other |
| **Expiring messages** | every note has a "valid until" time | message bus | old requests cannot block the system |
| **Rule + model hybrid** | a model is used only if it beats the rule; the rule is the backup | `agents/base.py` | the system always works, and every model must prove itself |
| **Graceful degradation** | bad data → a simpler, safer mode | master modes | max-pressure → actuated → fixed |
| **Guardrails / safety layer** | hard rules that nothing can bypass | `safety_rules.py`, `executor.py` | minimum green, yellow, pedestrian clearance, exit check |
| **Tool-using LLM agent (ReAct-style)** | the LLM thinks, calls a tool, reads the result, repeats | explainer | answers come from real data, not from the LLM's memory |
| **Verify or abstain** | check the answer; if unsure, say so | explainer + CoFlow bridge | an invented explanation is worse than no explanation |
| **Human in the loop** | the AI suggests; a person decides | operator copilot | "approve" is recorded, never applied automatically |
| **Separation of concerns (read-only AI)** | the AI that talks cannot act | Synapse layer | an LLM mistake can never change a light |

---

## Part 10. Safety: the rules nothing can bypass

File: `traffix/orchestration/safety_rules.py`. Only the executor (`traffix/simulation/executor.py`) writes a light.

1. **Pedestrian clearance:** the walk signal ends, then the system waits until the crossing is empty before the conflicting green starts. In rain the wait is longer. There is a maximum hold, and it is logged.
2. **Exit check:** no green for an ambulance or a bus if the road after the junction is full. Green would only move the queue into the junction.
3. **Stale data:** stale sensor data → a simpler mode that does not need that data.
4. **Minimum green and yellow:** a green lasts at least 5 s (an emergency may cut it short), and yellow is 3 s (longer in rain). Other values: exit is "full" at 85%, data is stale after 10 s, clearance hold is at most 30 s. All in `config/agents.yaml`.

**Every change of light:** green → clearance (walk off, cars still green) → yellow → new green.

`scripts/check_architecture.py` runs in GitHub CI and fails if:
- another file writes a light;
- Synapse imports SUMO, the sensors, the executor or a master;
- agents can read the scenario events or the calendar settings.

---

## Part 11. The web app and API

- **Backend:** FastAPI (`traffix/api/server.py`, `live.py`). It runs the simulation and publishes a snapshot. The pages never touch SUMO.
- **Frontend:** React + Vite (`frontend/src/pages/`). One page per persona:

| Page | Who | What they see |
|---|---|---|
| Pedestrian | Ferjani | walk signals, waiting time |
| CarDriver | Faycel | trip planner, Route B, alerts |
| BusPassenger | Mamadou | next buses at a stop |
| BusDriver | Hédi | gap to the bus ahead, priority |
| EmergencyCrew | Touhami | green ahead, route |
| Operator | Kamel | live map, modes, copilot, alerts |
| Analyst | Tahani | decision log, "ask why", **Verify with CoFlow Synapse** |
| Results | everyone | experiment charts |

Run it: `py -3.11 scripts\run_live.py` → http://localhost:8000 (add `--gui` to also open sumo-gui).
The select at the right of the top bar switches alerts, copilot and answers to French or Arabic.

---

## Part 12. A full example: an ambulance at J1

Real sequence from our emergency run on the Tunis map:

| Step | Who | What happens | Log |
|---|---|---|---|
| 1 | Emergency route agent (network) | sees the ambulance's route; warns J1 about 38 s before | `#336 EMERGENCY_PREPARE` |
| 2 | Emergency priority agent (J1) | asks for green, with the arrival time its model predicts | request |
| 3 | Master J1 | emergency is first after safety; checks the exit road has room | decision |
| 4 | Executor | the light is already green → hold it | `#337 EMERGENCY_GRANTED_HOLD` |
| 5 | Master J1 | the request expires; normal control comes back | `#341 RECOVERY_STARTED` |
| 6 | Notification + Synapse | alerts on the pages; the analyst clicks "Verify" → **verified**, citation #337 | — |

---

## Part 13. How we compare controllers (experiments)

`scripts/run_experiments.py` runs the same scenario and seed with different controllers:

| Controller | What it is |
|---|---|
| `fixed` | SUMO fixed-time plan |
| `actuated` | SUMO detector plan (baseline) |
| `junction_only` | masters + junction agents, no supermaster |
| `traffix_rules` | full hierarchy, rules only (no models) |
| `traffix` | full hierarchy with models (max-pressure light) — **our main system** |
| `traffix_predictive` | same, with the predictive light |
| `traffix_rl` | same, with the RL light |

**Why this list?** Each step adds one thing, so we can measure what each part brings: the hierarchy, the supermaster, the models.

Results on the Tunis map (mean of 3 seeds, 20 Oct 2026, `results/results.csv`):

| Scenario | Measure | Fixed | Actuated | traffix rules | traffix |
|---|---|---|---|---|---|
| morning peak | mean car wait | 123 s | 118 s | **102 s** | 106 s (−11%) |
| emergency | mean car wait | **62 s** | 66 s | 69 s | 79 s (+20%) |
| incident | mean car wait | **69 s** | 96 s | 98 s | 74 s (−24%) |
| morning peak | mean pedestrian wait | 140 s | 144 s | 128 s | **116 s** (−19%) |
| emergency | emergency vehicle trip | **197 s** | 213 s | 232 s | 240 s (+13%) |
| all three | car green started while people crossed (per run) | 239–281 | 331–405 | 16–19 | 17–19 (−95%) |

What to say: traffix protects pedestrians much better; for cars it is mixed; ambulances are slower
than with SUMO's plans (to investigate); with 3 seeds no difference is significant yet. Older
one-seed numbers (−41%, ambulance 487 → 241 s) came before the lane fixes: don't use them.

`scripts/analyze.py` then makes tables, charts and paired t-tests (is the difference real, or luck?).

---

## Part 14. The older part: the J0 platform (`src/coflow5`)

Before traffix, the team built a **single-junction** test platform called J0. It is the scientific benchmark:
- 5 agents: A1 Flow (the only signal writer, max-pressure), A2 Emergency, A3 Multimodal (pedestrians, buses), A4 Situation (forecast, incidents), A5 Sustainability (emissions).
- Synapse service: explanations and audits, read only.
- Evidence bundles, baselines, failure tests, and a read-only API and dashboard (`web/`).

The six-junction Tunis system reuses its ideas (one writer, read-only Synapse) and its `SynapseService` through the CoFlow bridge.

---

## Part 15. Map of the code

```
config/                  every assumption in YAML (agents, scenarios, networks, calendar)
scenarios/tunis-centre-6j/   the real Tunis map, traffic, bus lines, junctions.json
models/                  trained models + metrics.json
traffix/
  simulation/   SUMO connection, sensors, world events, EXECUTOR (the only light writer)
  orchestration/ master, supermaster, safety rules, system (one controller)
  agents/junction/  traffic light (3 versions), pedestrian, transit, emergency, sensor health
  agents/network/   forecast, incident, rerouting, emergency route, corridor, transit monitor,
                    weather, notification, explainer
  core/         config, message bus, decision log + 49 reason codes, narrator
  demand/       traffic generator, calendar (Ramadan, Eid, sunset)
  training/     data generation, model training, tuning, RL
  evaluation/   experiment runner, monitor (measures), analysis
  synapse/      LLM client, copilot, alert writer, translations, CoFlow bridge
  api/          FastAPI server + live runner
frontend/       React pages
src/coflow5/    the earlier J0 platform
scripts/        commands: setup, run_live, train, run_experiments, analyze, check_architecture, build map
tests/          automated tests
```

---

## Part 16. Honest limits (say them before the professor asks)

- **Synthetic traffic.** Real streets, generated traffic. The results come from simulation, not from Tunis measurements.
- **Three seeds, three scenarios** for the controller results: no significant difference yet.
- **Ambulances are slower** with traffix than with SUMO's plans (240 s vs 213 s). Not explained yet.
- **Lanes:** 18 of 21 junction roads use default lane counts.
- **Bus data** comes from community data, not an official feed. Headways (15 min) are assumed.
- **Calendar factors** (how much Ramadan reduces traffic) are our own assumptions.
- **Weak models:** arrivals equals its rule; sensor health loses to its rule; incident is not trained; bus lateness has few rows.
- **RL** is 4% worse than max-pressure.
- **No real weather or accident history** yet (proposed as a next step).

---

## Part 17. Questions the professor may ask

| Question | Answer |
|---|---|
| Why many small agents and not one big AI? | Each small agent is easy to test and explain. One big model cannot be checked for safety. |
| Who decides the light? | Only the master of that junction, through the safety rules and the executor. |
| Can the LLM change a light? | No. Synapse has no code path to the simulation. The CI check fails if one is added. |
| What if the LLM invents something? | Python checks every citation. One false citation → ABSTAIN. |
| What if a model is wrong or missing? | Every agent falls back to its rule. A model is used only if it beat its rule. |
| Why gradient-boosted trees? | Tables of numbers, little data, fast on a CPU, easy to compare with a rule. |
| Where does the training data come from? | From SUMO: what the agent saw, and what really happened later. |
| Why train on 2025 and test on 2026? | Ramadan moves each year, so the model must learn the event, not the date. |
| Why is RL not the default? | In the fair test it was 4% worse than max-pressure. |
| What is a seed? | A number that makes the random traffic repeatable. |
| What is actuated? | SUMO's detector-based light; our baseline and a fallback mode. |
| How do agents communicate? | A message bus with 6 kinds of message, each with an expiry time. |
