# Kiro prompt — student continue (after Cursor)

Paste everything below the line into **one** new `kiro-cli chat` in `C:\Users\dell\Downloads\sumo`.
One Kiro session only. Do not start a second chat while another Kiro is writing this repo.

---

You are continuing CoFlow-5 Synapse in `C:\Users\dell\Downloads\sumo`.
GitHub: `https://github.com/azizmessaoud/CoFlow-5-Synapse.git` (branch `main`).

I am a junior Data Science student. Explain in simple words. Do not invent results. Do not git commit or push unless I ask.

Output style: https://github.com/ayghri/i-have-adhd
Harness: https://github.com/flyrank-bih/harness-engineering-playbook
Do not copy Shopify code.

## How I want to work

I will finish this project in **Kiro CLI** when Cursor credit ends. I need:

1. A SUMO window I can watch (`sumo-gui`) so I understand the map and cars.
2. Tests I can run, with a plain-language meaning for pass/fail.
3. One sealed queue row at a time. Teach me what that row built before you start the next row.

## Read first

1. `AGENT_GUIDE.md`
2. `docs/adr/0001-reliable-ai-platform-boundary.md`
3. `docs/adr/0002-six-builders-one-queue-row.md`
4. `docs/harness/loop-and-exit.md`
5. `harness/queue.tsv`
6. `harness/BLOCKED` if it exists
7. the first unfinished row's `harness/work/<id>/contract.json`

## Locked product

- Five agents. Only A1 writes lights. Required A1 = cooperative Max-Pressure.
- Recovery: Max-Pressure → actuated → fixed-time.
- Synapse never reaches TraCI. No LLM in the Control plane.
- Join keys: `run_id`, `scenario_hash`, `event_id`, `message_id`.
- Claim flags: no lives saved, no measured air quality, no best-episode headline.
- Native Windows. Do not make Docker/WSL the required path.
- Course success = rows 01–09. Row 15 stays blocked.

## Already true (do not redo)

- Python 3.11.9: `py -3.11 --version`
- SUMO 1.27.1: `SUMO_HOME=C:\Program Files (x86)\Eclipse\Sumo`
- TraCI from `SUMO_HOME\tools` works. Headless `sumo.exe` works. `sumo-gui.exe` exists.
- Rows **02–09 are gated**. First unfinished product row is **10-a4-a5**.
- `import libsumo` is blocked by Windows application control (`geos_c.dll` / `jupedsim.dll`). Keep `harness/BLOCKED`. Do not invent libsumo numbers. Do not weaken the row-01 contract. You may keep building later rows on the **TraCI** path.
- Professor book + ADR-0002 + ADR-0003 exist. Do not rewrite them.
- How to run SUMO: `docs/how-to-run-sumo.md`

## Job

1. Every turn: `Row NN of 15, PHASE` and gate red/green.
2. Start at the first unfinished row, which should be **row 10** unless `harness/queue.tsv` says otherwise. Do not rebuild 02–09.
3. If a row already has passing named tests, write `gate.json` only from tests-and-files.
4. Then stop and explain in 5 lines: what I can click, what test to run, what the test means.
5. Give me one `py -3.11 scripts\\watch_sumo.py …` command for the scenario that row used.
6. Then wait for me unless I said continue.
7. After I say continue, take the next unfinished row only.

## SUMO window (teach me)

The basics I should see first:

```powershell
$env:SUMO_HOME = "C:\Program Files (x86)\Eclipse\Sumo"
cd C:\Users\dell\Downloads\sumo
py -3.11 scripts\watch_sumo.py smoke
```

Press the green Play button. Tiny grid, a few cars, ~180 seconds. That is the frozen smoke network, not Tunis, not a deployed city. Live A1: `py -3.11 scripts\watch_sumo.py a1`.

## Stop

- Exit 3 if a human must allow libsumo DLLs and the current row truly cannot proceed without it.
- Exit 7 if context is long. Tell me to paste this prompt in a fresh chat.
- Do not start row 15. Do not put an LLM on the lights.
