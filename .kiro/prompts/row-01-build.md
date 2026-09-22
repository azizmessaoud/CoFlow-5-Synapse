# Kiro prompt — Row 01 BUILD (native Windows smoke test)

Copy everything below the line into a **new** Kiro chat in `C:\Users\dell\Downloads\sumo`.

If you want the old CAPTURE/PATCH chat instead, do not paste this. Resume session `8780be2f-a326-4789-93a0-c898a5ff8891`.

---

You are continuing CoFlow-5 Synapse in `C:\Users\dell\Downloads\sumo`. GitHub: `https://github.com/azizmessaoud/CoFlow-5-Synapse.git` (branch `main`).

Output style: https://github.com/ayghri/i-have-adhd
Harness pattern: https://github.com/flyrank-bih/harness-engineering-playbook
Do not copy Shopify code.

## Who I am

Junior Data Science student, ESPRIT 4DS. Explain in simple words when you stop or block. Do not invent results.

## Read first, in this order

1. `AGENT_GUIDE.md`
2. `docs/source/course-brief.md`
3. `.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md`
4. `docs/adr/0001-reliable-ai-platform-boundary.md`
5. `docs/harness/how-it-works.md`
6. `docs/harness/loop-and-exit.md`
7. `docs/harness/contract-and-evidence.md`
8. `.kiro/steering/product.md`
9. `.kiro/steering/harness.md`
10. `.kiro/steering/output-style.md`
11. `CONTEXT.md`
12. `harness/queue.tsv`
13. `harness/BLOCKED`
14. `harness/work/01-smoke-test/contract.json`
15. `harness/capture-report.md`
16. `harness/contradictions.md`

Do not re-read the whole repo. Do not start rows 02–15.

## Already done (do not redo)

CAPTURE, CONTRADICT, and PATCH finished in a previous Kiro session (`8780be2f-a326-4789-93a0-c898a5ff8891`).

- Contracts 01–09 exist under `harness/work/<id>/contract.json`.
- Canonical specs were updated: `.kiro/specs/coflow5-reliable-agentic-platform/{requirements,design,tasks}.md`.
- Five legacy files have ADR-0001 historical/superseded notes: `coflow5-define-ideate.md`, `CoFlow-5_System_Requirements_Book.md`, `CoFlow-5_System_Requirements.md`, `final.md`, `coflow5-design-patterns.md`.
- Queue SHA-256 at CAPTURE: `b286ff0c3acee5dc0b5f3d215d6f37d6dad80d8a7c7386582254b465f8ca03eb`.
- Design Thinking Stages 1–3 are complete. Prototype and Test are not complete.
- Professor deck: `docs/presentation/CoFlow-5-Synapse-DT-4DS.pptx` (honest: no fake % results).

## Locked product

- Course HMW: How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?
- Eight personas only: Amara, David, Chidi, Rosa, Marcus, Yuki, Maria, Omar.
- Personas are research-informed. Interviews were not completed. No interview quotes.
- Five agents. Only A1 writes signals.
- Required A1: cooperative Max-Pressure. DQN is optional row 15 and stays `blocked`.
- Recovery: Max-Pressure → actuated → fixed-time.
- Synapse never reaches TraCI and never actuates.
- Join keys: `run_id`, `scenario_hash`, `event_id`, `message_id`.
- Claim flags: no lives saved, no measured air quality, no best-episode headline.
- Native Windows SUMO smoke test before Docker or WSL as a requirement.

## Current state

- **Row 01 of 15, BUILD.**
- `harness/queue.tsv` row `01-smoke-test` is `todo`.
- Row `15-optional-dqn` is `blocked`.
- No `gate.json` exists. Do not create one until named tests and artifacts exist.
- `harness/BLOCKED` says: SUMO 1.27.1 is available; native Windows Python 3.11 is missing; the Python 3.11.9 installer was canceled (exit 1602). WSL Python cannot satisfy this contract.

## Job this session

BUILD row `01-smoke-test` only. Follow `harness/work/01-smoke-test/contract.json` exactly.

1. Restate every turn: `Row 01 of 15, BUILD` and whether the gate is red.
2. Check native Windows Python 3.11 with `py -3.11 --version` or equivalent. Do not use WSL Python.
3. If Python 3.11 is still missing, keep `harness/BLOCKED` and give me one exact installer step. Do not invent a workaround.
4. If Python 3.11 is present, produce the contract artifacts and named tests. Do not touch rows 02–15.
5. Do not mark the row done by self-assessment. A pass requires `gate.json` with `pass: true`, `openDeltas: 0`, `decidedBy: tests-and-files`, and a matching contract hash.

## Stop

- Exit 3: human must install Python 3.11. Keep BLOCKED.
- Exit 7: context is too long. Stop and ask for a fresh chat.
- Do not start SUMO product agents, RL, Docker, or WSL to “save time.”
