# Loop and exit

A loop without exits is a bill, not a harness.

Each worker reads `prompts` or the Kiro spec task, advances the first unfinished row in `harness/queue.tsv`, and writes progress into that row's evidence pack plus git.

## Inner done (per row)

The row is gated only when all are true:

1. `contract.json` exists and is unchanged from its hash in `gate.json`
2. `gate.json` has `"pass": true` and `"openDeltas": 0`
3. named tests in the contract all passed
4. required artifacts listed in the contract exist
5. no agent self-score is used as the verdict

## Outer done (the runner)

Stop in this order:

| # | Condition | Exit | Action |
|---|---|---|---|
| 1 | Queue complete, every row gated | 0 | success |
| 2 | `harness/BLOCKED` exists | 3 | human decision needed |
| 3 | Max iterations | 4 | safety cap |
| 4 | Budget/token cap | 5 | cost cap |
| 5 | No new commit for N loops | 6 | stuck |
| 6 | Context compacted mid-row | 7 | re-narrow the row |
| 7 | Provider/API failure | 8 | resume from files |

Blocked means the work cannot proceed (missing SUMO pin, human architecture choice, secret). Write one line and unblock steps to `harness/BLOCKED`.

Stuck means the worker runs but lands no commits. Re-narrow to one contract check.

Do not run one conversation until compaction to "save" reloads. Recycle context at the row boundary.

Adapted from [loop-and-exit.md](https://github.com/flyrank-bih/harness-engineering-playbook/blob/main/docs/principles/loop-and-exit.md).
