# CoFlow-5 harness CAPTURE report

**Active work:** row `01-smoke-test` of 15, phase `CAPTURE`  
**Scope:** contracts 01–09 and canonical spec/harness consistency only; no SUMO product implementation or experiment execution.

## Highest gaps first

| Rank | Gap | Persona/HMW | Severity | Layer | Cheapest fix captured |
|---|---|---|---|---|---|
| 1 | Contracts 02–09 did not exist; row 01 lacked full machine checks | Professor, Yuki, all HMW | Critical | Harness | Seal contracts 01–09 with dependencies, tests, artifacts, gates, forbidden imports, and join keys |
| 2 | Stable requirements did not name queue rows or evidence identifiers | All eight User Personas | Critical | Spec | Add one requirement-to-row/join-key table without renumbering requirements |
| 3 | `event_id`/`message_id` and cross-layer referential rules were incomplete | Rosa, Yuki, Omar | Critical | Product/integration | Define manifest, message, decision, KPI, and explanation join rules |
| 4 | Capability boundaries were prose, not explicit import/runtime gates | Amara, Yuki; HMW-9 | Critical | Harness/product | Contract forbidden imports plus one-writer and Synapse-kill tests |
| 5 | Older narratives can make RL/MARL look core or imply planned interviews occurred | Professor; honesty constraint | High | Spec history | Record precedence and contradictions without inventing evidence |

## Sealed spine

Rows 01–09 remain ordered as toolchain, evidence, safety, baselines, Max-Pressure, messaging, A2/A3, failure injection, and evaluation. They are never cut. Rows 10–15 remain later/optional work; row 15 remains `blocked`. Scope cuts proceed 15 → 14 → 13 → 12 → 11 → 10.

Every contract 01–09 names `run_id`, `scenario_hash`, `event_id`, and `message_id`. Applicability is enforced by record type: all product rows retain run/scenario identity, immutable events use `event_id`, and messages/dispositions use `message_id`.

## Gate state at CAPTURE

`gate.json` is intentionally absent for rows 01–09. CAPTURE freezes contracts; it does not fabricate passing tests or product artifacts. Therefore row 01 remains `todo`, Prototype/Test remain incomplete, and the next phase after this capture is CONTRADICT/PATCH—not SUMO BUILD in this session.

Claim flags remain binding: no invented interviews, no lives-saved claim, no measured-air-quality claim, no best-episode headline. Reinforcement learning remains optional and cannot alter the required recovery ladder.
