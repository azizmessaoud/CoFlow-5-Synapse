# Kiro prompt — continue BUILD (TraCI path, rows 02–09)

You are continuing CoFlow-5 Synapse in `C:\Users\dell\Downloads\sumo`.
Do not git commit or git push.

Output style: https://github.com/ayghri/i-have-adhd
Harness pattern: https://github.com/flyrank-bih/harness-engineering-playbook

## Who I am

Junior Data Science student, ESPRIT 4DS. Do not invent results.

## Read first

1. `AGENT_GUIDE.md`
2. `docs/adr/0001-reliable-ai-platform-boundary.md`
3. `docs/harness/loop-and-exit.md`
4. `harness/queue.tsv`
5. `harness/BLOCKED`
6. `harness/work/01-smoke-test/contract.json`
7. `harness/work/01-smoke-test/artifacts/throughput.json`
8. `src/coflow5/sumo_adapter/smoke_backends.py`
9. `src/coflow5/smoke.py`
10. `LEARNINGS.md`
11. each `harness/work/<id>/contract.json` when you reach that row
12. `.kiro/specs/coflow5-reliable-agentic-platform/{requirements,design,tasks}.md`

## Already proven on this machine

- Native Python 3.11.9: `py -3.11 --version`
- Native SUMO 1.27.1: `SUMO_HOME=C:\Program Files (x86)\Eclipse\Sumo`
- Headless `sumo.exe` exits 0 on `scenarios/smoke/smoke.sumocfg` (20 vehicles).
- TraCI from `SUMO_HOME\tools` ran 102 steps. `traci.__file__` is under SUMO_HOME.
- Row 01 artifacts exist under `harness/work/01-smoke-test/artifacts/` including TraCI throughput. Manifest status is `blocked-libsumo`.
- **libsumo is blocked by Windows Code Integrity** policy `{0283ac0f-fff1-49ae-ada1-8a933130cad6}` (events 3033/3077) on `geos_c.dll` / `jupedsim.dll`. Keep `harness/BLOCKED`. Do not invent libsumo numbers. Do not write `gate.json` with `pass: true` for row 01.

## Job this session

Implement the product for rows **02–09** on the native TraCI path. Row 01 stays ungated until an administrator allows libsumo.

1. Every turn restate `Row NN of 15, BUILD` and gate red/green for that row.
2. Follow each `contract.json` exactly. Named tests, artifacts, join keys, forbidden imports.
3. Use TraCI via `src/coflow5/sumo_adapter/` only. Never import `traci` or `libsumo` from synapse, api, ui, a2, a3, a4, a5.
4. Never import `libsumo` at module load. If you need it, lazy-import and tolerate WDAC failure.
5. Only A1 writes signals. Recovery: Max-Pressure → actuated → fixed-time.
6. Synapse never reaches TraCI. No LLM in the Control plane. Row 15 stays blocked. No DQN.
7. Join keys: `run_id`, `scenario_hash`, `event_id`, `message_id`.
8. Claim flags: no lives saved, no measured air quality, no best-episode headline.
9. Native Windows only. Docker/WSL are not required.
10. After a row's named tests pass and artifacts exist, write `harness/work/<id>/gate.json` with `pass: true`, `openDeltas: 0`, `decidedBy: tests-and-files`, and a matching contract hash. Do not self-assess.
11. Do not rewrite the Final Project Book or Empathize pack.
12. When you stop, print which row, gate status, files written, and one next action.

## Row map

| id | work |
|---|---|
| 02-evidence-bundle | run manifest + Parquet + DuckDB joins |
| 03-safety-mask | one writer; illegal actions rejected |
| 04-baselines | fixed-time and actuated, matched seeds |
| 05-max-pressure | cooperative A1 |
| 06-message-board | TTL, idempotency, empty board |
| 07-a2-a3 | emergency + multimodal requests |
| 08-failure-injection | drop messages; fail controller; kill Synapse |
| 09-eval-harness | ablations, unfinished trips, honest nulls |
| 15-optional-dqn | leave blocked |

## Stop

- Exit 0: rows 02–09 gated (01 remains blocked on libsumo).
- Exit 3: a new human blocker besides known libsumo WDAC.
- Exit 7: context too long; stop at a row boundary.
