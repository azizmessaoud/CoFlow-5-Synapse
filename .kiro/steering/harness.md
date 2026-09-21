---
inclusion: always
---

# Harness engineering

Follow the pattern in [flyrank-bih/harness-engineering-playbook](https://github.com/flyrank-bih/harness-engineering-playbook). Do not copy the Shopify theme.

Router: `AGENT_GUIDE.md`.

Rules:

- Product code is not the harness. Specs, queue, contracts, gates, prompts, and self-tests are the harness.
- One sealed queue. One evidence pack per row. Resume from files.
- A worker cannot declare done. `gate.json` declares done.
- Fresh context per queue row. Do not compact a giant chat and keep going.
- Write `harness/BLOCKED` instead of guessing when a human decision is required.
- Join every layer on `run_id`.
- Add a library only after the typed interface already has a failing-then-passing gate without that library.

When enhancing specs, also specify the harness files Kiro must add or tighten: `harness/queue.tsv`, `harness/work/<id>/contract.json`, gate schema, forbidden imports, and exit codes.
