# Kiro prompt — continue BUILD from row 04

You are continuing CoFlow-5 Synapse in `C:\Users\dell\Downloads\sumo`.
Do not git commit or git push.

Output style: https://github.com/ayghri/i-have-adhd

## State

- Row 01: ungated. libsumo WDAC-blocked. TraCI works. Keep `harness/BLOCKED`. Do not write `pass: true` for 01.
- Row 02: gated. `harness/work/02-evidence-bundle/gate.json`
- Row 03: gated. `harness/work/03-safety-mask/gate.json`
- Controlled TLS scenario exists under `scenarios/safety-mask/`.
- TraCI-only. Lazy-import libsumo. Only A1 writes signals via `src/coflow5/sumo_adapter/signal_executor.py`.
- Clean leftover `.artifacts.staging-*` dirs if they are not the published artifacts.

## Job

BUILD rows **04 → 09** in order. Gate each row before the next.

1. Restate `Row NN of 15, BUILD` every turn.
2. Follow `harness/work/<id>/contract.json` exactly.
3. Named tests must be run with `py -3.11 -m pytest ...` so they hit Python 3.11.
4. After tests pass and artifacts exist, write `gate.json` with `pass: true`, `openDeltas: 0`, `decidedBy: tests-and-files`, matching contract hash.
5. Update `harness/queue.tsv` status to `gated` for each finished row.
6. No LLM in Control plane. No DQN. Row 15 stays blocked. Synapse never imports traci/libsumo.
7. Claim flags: no lives saved, no measured air quality, no best-episode headline.
8. When you stop: which row, gate status, files, one next action.

## Rows

04 baselines (fixed-time + actuated, matched seeds)
05 cooperative Max-Pressure A1
06 message board (TTL, idempotency, empty board)
07 A2 emergency + A3 multimodal requests
08 failure injection + recovery ladder
09 eval harness (ablations, unfinished trips, honest nulls)
