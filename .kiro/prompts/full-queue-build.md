# Kiro prompt — full sealed-queue BUILD (rows 01–09)

You are continuing CoFlow-5 Synapse in `C:\Users\dell\Downloads\sumo`.
GitHub: `https://github.com/azizmessaoud/CoFlow-5-Synapse.git` (branch `main`).

Output style: https://github.com/ayghri/i-have-adhd
Harness pattern: https://github.com/flyrank-bih/harness-engineering-playbook
Do not copy Shopify code.

This session is a **runner**. Build product code. Do not rewrite the professor book.

## Who I am

Junior Data Science student, ESPRIT 4DS. Explain in simple words when you stop or block. Do not invent results. Do not git commit or git push.

## Read first, in this order

1. `AGENT_GUIDE.md`
2. `docs/source/course-brief.md`
3. `.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md`
4. `docs/adr/0001-reliable-ai-platform-boundary.md`
5. `docs/adr/0002-six-builders-one-queue-row.md`
6. `docs/harness/how-it-works.md`
7. `docs/harness/loop-and-exit.md`
8. `docs/harness/contract-and-evidence.md`
9. `.kiro/steering/product.md`
10. `.kiro/steering/harness.md`
11. `.kiro/steering/output-style.md`
12. `CONTEXT.md`
13. `harness/queue.tsv`
14. `harness/BLOCKED` if it exists
15. `harness/work/01-smoke-test/contract.json` then later rows as you reach them
16. `.kiro/specs/coflow5-reliable-agentic-platform/{requirements,design,tasks}.md`

Do not re-read the whole repo. Do not start row 15.

## Already done (do not redo)

CAPTURE / CONTRADICT / PATCH are finished. Contracts 01–09 exist.

Professor-facing docs tickets 01–06 are finished:

- `CoFlow-5_Final_Project_Book.md`
- `docs/adr/0002-six-builders-one-queue-row.md`
- README / Design Thinking record / product steering aligned
- Empathize pack body is frozen

Do not rewrite those. Do not invent interview quotes, lives saved, air-quality measurements, or best-episode headlines.

Design Thinking Stages 1–3 are complete. Prototype and Test are not complete until gates exist.

## Locked product

- Course HMW: How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?
- Eight personas only: Amara, David, Chidi, Rosa, Marcus, Yuki, Maria, Omar.
- Personas are research-informed. No interview quotes. Wednesday work is **proxy validation**, not stakeholder interviews.
- Six builders, one sealed queue: Aziz Messaoud, Eya Laourine, Fares Ben Kacem, Mohamed Aymen Hamzaoui, Oumayma Saddouri, Ranim Ben Salem.
- Pairs: Control Aziz+Fares; Data Aymen+Oumayma; Product Eya+Ranim.
- Five agents. Only A1 writes signals.
- Required A1: cooperative Max-Pressure. DQN is optional row 15 and stays `blocked`.
- Recovery: Max-Pressure → actuated → fixed-time.
- Synapse never reaches TraCI and never actuates. No LLM in the Control plane.
- Join keys: `run_id`, `scenario_hash`, `event_id`, `message_id`.
- Claim flags: no lives saved, no measured air quality, no best-episode headline.
- Native Windows SUMO smoke test before Docker or WSL as a requirement.
- Course success = rows 01–09 gated. Cut from 15, then 14 downward. Never cut 01–09.

## Current state

- **Row 01 of 15, BUILD.** Queue row `01-smoke-test` is `todo`.
- Row `15-optional-dqn` is `blocked`. Leave it blocked.
- No `gate.json` exists. Create one only after named tests and artifacts exist for that row.
- Native SUMO is installed: `SUMO_HOME=C:\Program Files (x86)\Eclipse\Sumo`. `sumo.exe` and `sumo-gui.exe` are on PATH.
- Native Windows Python 3.11.9 is the pin (`Python.Python.3.11` / `py -3.11`). WSL Python cannot satisfy row 01.

## Job this session

Act as the harness runner. Advance the first unfinished row, gate it, then the next, until rows 01–09 have `gate.json` with `pass: true`, `openDeltas: 0`, `decidedBy: tests-and-files`, and a matching contract hash.

1. Every turn restate: `Row NN of 15, BUILD` and whether that row's gate is red.
2. Follow `harness/work/<id>/contract.json` exactly. Do not skip `must_pass`, named tests, artifacts, or `imports_forbidden`.
3. One row at a time. Do not start row N+1 until row N has a passing gate.
4. After 01 gates, continue 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 without waiting for another human prompt.
5. Do not start rows 10–14 in this session unless 01–09 are all gated and you still have context. Prefer stopping after 09 over a half-built API.
6. Never start row 15. Never enable DQN. Never put an LLM in the Control plane. Never let Synapse import `traci` or `libsumo`.
7. Native Windows only for the smoke-test path. Docker/WSL are not required and must not be the only way to run tests.
8. If Python 3.11 is missing, install native Windows Python 3.11.9 with:

   `winget install -e --id Python.Python.3.11 --version 3.11.9 --scope user --accept-package-agreements --accept-source-agreements`

   Then refresh PATH, confirm `py -3.11 --version`, clear `harness/BLOCKED` only after that confirmation, and continue row 01. Do not use WSL Python.
9. If an install needs a human UAC click and you cannot complete it, write `harness/BLOCKED` with one exact next command and stop (exit 3).
10. Do not mark a row done by self-assessment.
11. Do not git commit, git push, amend, or change git config.
12. When you stop, print: which row, gate red/green, files written, and one next action.

## Row map (do not invent extra rows)

| id | work |
|---|---|
| 01-smoke-test | Pin Python 3.11 + SUMO 1.27.x; toolchain.json; headless scenario; gui-diagnosis.md; TraCI vs libsumo throughput; pytest listed in the contract |
| 02-evidence-bundle | run manifest + Parquet + DuckDB join on run_id / scenario_hash |
| 03-safety-mask | one writer; illegal actions rejected |
| 04-baselines | fixed-time and actuated on matched seeds |
| 05-max-pressure | cooperative A1 required controller |
| 06-message-board | TTL, idempotency, A1 continues if empty |
| 07-a2-a3 | rule-based emergency and multimodal requests |
| 08-failure-injection | drop messages; fail controller; kill Synapse; recovery ladder |
| 09-eval-harness | ablations, unfinished trips, no best-episode headline |
| 15-optional-dqn | leave blocked |

## Stop

- Exit 0: rows 01–09 gated.
- Exit 3: `harness/BLOCKED` exists and a human must act.
- Exit 7: context is too long. Stop at the row boundary and say which prompt to paste next.
- Do not keep going after a red gate by weakening the contract.
