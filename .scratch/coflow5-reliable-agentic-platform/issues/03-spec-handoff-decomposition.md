---
name: spec-handoff-decomposition
description: Decompose the decisions into canonical Kiro and harness work
labels: [wayfinder:resolved]
parent: coflow5-reliable-agentic-platform-map
Type: grilling
Status: resolved
---

## Question

How should the settled evidence and read-only product contracts be represented
in the canonical `requirements.md`, `design.md`, `tasks.md`, and harness queue
so implementation workers have complete acceptance tests, ownership boundaries,
and no contradictory completion claims?

## Answer

The handoff preserves all gated rows 01–09 and 10b/10c unchanged. The
resolved J0 and read-only product contracts are added as explicit acceptance
overlays for the remaining work, rather than rewriting historical evidence
packs.

`tasks.md` remains the human-readable scope and ownership decomposition.
Each remaining queue row also gets one canonical executable contract linking
its requirement IDs, owning workstream, required artifacts, named tests,
provenance joins, forbidden capabilities, and gate condition. The task and
queue contract cross-link each other; neither becomes a duplicate source of
truth.

The delivery order remains `10e -> 12 -> 11 -> 13 -> R -> 14`. Row 15 stays
optional and blocked. A product milestone may be gated independently, but no
partial product milestone may weaken or replace the frozen J0 completion claim.

The canonical specification explicitly documents two deployment profiles:
`HOSTED` is fully read-only, while `LOCAL_RUNNER` may mutate runs and
proposals. Neither profile has a signal surface. This boundary is covered by
requirements, design rules, forbidden-import checks, and runtime capability
tests.
