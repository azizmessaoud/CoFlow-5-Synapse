# Agent notes

Read `AGENT_GUIDE.md` first. That file is the router.

## Harness

Pattern: https://github.com/flyrank-bih/harness-engineering-playbook  
Output style: https://github.com/ayghri/i-have-adhd

- Queue: `harness/queue.tsv`
- Packs: `harness/work/<id>/`
- Loop/exits: `docs/harness/loop-and-exit.md`
- Notebook: `LEARNINGS.md`

## Agent skills

### Issue tracker

Issues and specs live as markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

Canonical roles use the default strings (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`). See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` and `docs/adr/` at the repo root. See `docs/agents/domain.md`.
