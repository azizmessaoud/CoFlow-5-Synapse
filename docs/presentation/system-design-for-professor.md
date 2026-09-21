# CoFlow-5 — system design for the professor (simple English)

This page is what to **verify**. Personas tell *who* we design for. This tells *how many agents*, *how they talk*, and *the safest way to build* so the project is honest.

**Status:** Empathize is done. The software is **not** built yet. This is the architecture we will implement unless you reject a choice.

---

## How many agents?

**Five control/advisory agents** (CoFlow-5). Plus an optional **explain layer** that is **not** a sixth traffic controller.

| # | Short name | Job in one sentence | Can it change a traffic light? |
|---|---|---|---|
| **A1 Flow** | Boss of the lights | Picks the phase at each junction and decides whose request wins | **Yes — only A1** |
| **A2 Emergency** | Ambulance helper | Plans a corridor and *asks* A1 to clear queues ahead | No — request only |
| **A3 Multimodal** | People + buses | Asks for slower walkers and for late buses (not every bus) | No — bid only |
| **A4 Situation** | Radar | Forecasts traffic and flags “this does not match the forecast” | No — alert only |
| **A5 Sustainability** | Environment officer | Asks A1 to care more about emission hot-spots when delay allows | No — weight only |
| **Synapse (LLM)** | Explainer | Reads the decision log and explains it in words; RAG over docs | **Never** |

**Three rules the professor can quote:**

1. **Safety first** — no two greens that fight; a pedestrian already crossing finishes.
2. **The boss is boss** — only A1 writes to SUMO/TraCI.
3. **Backup plans** — if messages die, A1 still runs locally; if the learned policy dies, fall back: Max-Pressure → actuated → fixed-time.

**Why not let the LLM drive?** One-second control needs a reliable, fast loop. LLM delay and failure are wrong for that (CoLLMLight needs tricks to stay real-time; production systems like SCATS keep a human/deterministic override). If the LLM process dies, **lights must not notice**.

---

## How will they communicate?

Not “everyone shouts at SUMO”. Two mechanisms:

### 1. Shared noticeboard (pub/sub)

Agents **post** and **read**. They do not call each other in a tangle.

| Channel (topic) | Typical content | Who writes | Who reads |
|---|---|---|---|
| `state/` | Local queues, occupancy, mode, data age | A1 (and sensors) | A2–A5, logs |
| `forecast/` | Near-term arrivals and link forecasts | A4 | A1, A2, A5 |
| `alerts/` | Incident / degradation / stale data | A4, watchdog | A1, Omar/Yuki views |
| `eco/` | Hot-spot weights, emission proxies | A5 | A1 |

Every message has an **expiry (TTL)** and a **heartbeat**. Old messages are discounted or ignored. If A4 is silent, A1 does **not** freeze: it uses local rules.

**Implementation (proposed):** in-process asyncio pub/sub first (one process, easy to test). Redis Streams only if we must demo two machines. Kafka is overkill for a student prototype.

### 2. Formal ask (contract-net), one round per decision window

For ambulance and bus/pedestrian claims, A2/A3 send a **request** to A1 inside a 5–10 s decision epoch:

**request → A1 accept or reject + reason code** (example: “pedestrian still on crossing”, “downstream lane full”).

A1 compares requests with a **net-benefit bid** (benefit minus harm to others), but **priority tiers** sit above the auction:

**Safety / person already crossing → emergency → pedestrian deadline → late bus (conditional) → general flow → eco.**

One negotiation round only (no long bargaining in 5 seconds).

```
A4 posts forecast/alerts
A5 posts eco weights
A2/A3 send one-shot requests
        |
        v
A1 reads board + requests
        |
        v
Safety mask (illegal greens removed)
        |
        v
Pick phase  -->  SUMO (TraCI / libsumo)
        |
        v
Log (reason codes)  -->  LLM may *read* this later, never write lights
```

**If the board is empty or stale:** A1 still acts. That is how we survive packet loss (we will *test* loss; literature almost never does).

---

## Best way to build it (so you can verify the plan)

**Principle:** earn every extra agent with an ablation. A small honest system beats a five-agent demo that cannot be compared.

### Step 0 — simulation spine (week 1)

- Pin **SUMO ≥ 1.24** + Python, git hash in every log.
- One **4×4 grid** (or small real snippet later).
- Two dumb baselines: **fixed-time** and **actuated**.
- Measure run speed (how many seeds we can afford).

**Professor check:** can we run SUMO and print delay / stops without any “AI”?

### Step 1 — Tier 0 / MVP (satisfies the brief alone)

- **Only A1** vs fixed-time, actuated, and **Max-Pressure**.
- Hard **safety mask** (no conflicting greens).
- Watchdog: bad input → Max-Pressure, not “hope the neural net recovers”.
- Honest stats: **common random numbers**, no “best episode” tables, unfinished trips count as failures.

**Professor check:** is A1 better *or honestly not better* than Max-Pressure on a stated test? A negative result is allowed.

### Step 2 — Tier 1 (add talking agents)

- Message bus + **A2, A3, A5**.
- Arbitration + reason codes (Rosa can read them).
- Ablations: turn one agent **off** and show the delta.

**Professor check:** does each extra agent earn its keep, or only add complexity?

### Step 3 — Tier 2 (situation + stress)

- Learned **A4**, incident flags, **communication-failure** sweeps (drop messages on purpose).
- Larger / more realistic network only after the grid is solid.

**Professor check:** when 30% of messages are lost, does the system degrade, not collapse?

### Parallel, never on the critical path — Synapse

- RAG + explanations **from the log**.
- If this slips, **cut the LLM**, not the evaluation.

### Stack (why these tools)

| Piece | Choice | Why (one line) |
|---|---|---|
| World | SUMO + TraCI/libsumo | Pedestrians, buses, EVs, emissions exist in the model |
| Lights (A1) | Shared-policy DQN first, MAPPO as comparator | RESCO: fancy RL often loses to a simple DQN on realistic nets |
| Bus | asyncio pub/sub | Testable; Redis only if we split processes |
| Explain | LangGraph + RAG **off** the control path | Words for humans, not 1 Hz control |
| Eval | Baselines + paired tests + MLflow gates | The spine of a defensible report |

### What we will **not** do (please reject us if we slip)

- LLM sets a phase.
- Report best training episode as the result.
- Translate simulated ambulance seconds into “lives saved”.
- Call HBEFA/SUMO numbers “air quality”.
- Add A2–A5 before A1 vs Max-Pressure is running.

---

## One paragraph you can read aloud

We propose **five agents**. Only **A1** is allowed to change lights. A2–A5 **publish** on a shared board (`state`, `forecast`, `alerts`, `eco`) and **ask** A1 in one short request round; old messages expire. A talking LLM may **explain the log** but is **outside** the control loop. We build **A1 + baselines first**, then add specialists one by one with ablations, then break the radio on purpose. That is the plan to verify.
