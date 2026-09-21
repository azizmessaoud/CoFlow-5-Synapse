# For the supervisor — where we are (simple English)

**Project:** CoFlow-5 — how intelligent agents could help city traffic (SUMO simulation).

**Design Thinking stage now: Empathize** = understand people before we code.

We have **not** built the traffic-light software yet. We have decided **who** we design for, **what hurts them**, **what research says**, and **which ideas** to test next.

| Supervisor question | Short answer |
|---|---|
| What did we deliver? | 8 persona sheets (same canvas as the course), journeys, evidence, solution ideas |
| Is the system built? | No. These are **ideas** to prototype in SUMO later |
| Who controls the lights? | One “boss of the lights” (A1). Everyone else **asks**. The talking AI (LLM) **never** presses a light |
| Numbers (40 s, −25%, …) | **Targets to test**, not results we already measured |
| Did we invent evidence? | Literature claims are sourced (e.g. wait *feels* 2× longer). IMATM Tunis survey digits are **placeholders** — we do not present them as real |

**How many agents?** Five (A1–A5). Only A1 changes lights. A2–A5 ask. An LLM may explain the log; it is **not** a sixth controller.

**How they talk:** a shared noticeboard (`state/`, `forecast/`, `alerts/`, `eco/`) plus one-round requests from A2/A3 to A1 with a written reason if rejected. Old messages expire. If the board is silent, A1 still runs.

**How we will build (verify this):** SUMO + dumb baselines first → A1 vs Max-Pressure (MVP) → then A2/A3/A5 + bus → then A4 and radio-loss tests. Cut the LLM before we cut statistics.

Full page for the professor: [docs/presentation/system-design-for-professor.md](docs/presentation/system-design-for-professor.md)

**System requirements book (DT prompt + evidence-why + shalls):** [CoFlow-5_System_Requirements_Book.md](CoFlow-5_System_Requirements_Book.md)

Printable persona sheets: [docs/presentation/personas-canvas.html](docs/presentation/personas-canvas.html) (open in the browser, then Print).
