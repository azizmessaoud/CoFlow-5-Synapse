# How the CoFlow-5 harness works

The SUMO system is the product. Everything around the agent is the harness.

Cast:

- **Router** — `AGENT_GUIDE.md`
- **Plan** — sealed `harness/queue.tsv` plus one evidence pack per row
- **Worker** — one agent invocation per row, resume from files
- **Gate** — machine verdict in `gate.json`, not "looks good"
- **Notebook** — `LEARNINGS.md`
- **Loop** — repeat workers until the queue gates or an exit code fires

```text
course brief + Design Thinking 1-3
        ↓
CAPTURE: seal queue + write contract.json
        ↓
BUILD one row
        ↓
GATE vs contract + evidence bundle
        ↓
pass → next row
fail → same row, fresh worker
blocked/stuck/budget → stop
```

Done is not a ticked chat box. Done is:

- contract hash matches
- `gate.json` pass
- required artifacts exist
- named tests passed

Sources: [harness-engineering-playbook](https://github.com/flyrank-bih/harness-engineering-playbook) pattern; CoFlow-5 product rules in ADR-0001.
