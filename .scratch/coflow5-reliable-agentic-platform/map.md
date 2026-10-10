---
name: coflow5-reliable-agentic-platform-map
description: Implementation-ready specification for completing CoFlow-5 Synapse
labels: [wayfinder:map]
---

## Destination

An implementation-ready revision of the canonical CoFlow-5 Kiro requirements,
design, and tasks, with harness traceability, for a reliable AI decision
platform that can be completed and evaluated honestly.

## Notes

- Tracker: local Markdown under `.scratch/`.
- Domain: urban traffic management with SUMO; consult `CONTEXT.md`,
  `docs/adr/`, the course brief, and the Kiro spec.
- J0 is the required matched-evidence baseline. Tunis OSM/TRANSTU is a
  separately labelled showcase, not a second inference baseline.
- The read-only API/UI/Synapse layer is required downstream of frozen evidence
  bundles and cannot actuate or create a second source of truth.
- Multi-seed evaluation, failure injection, and proxy validation are required
  artifacts; null and negative results are valid outcomes.
- A1 is the sole signal writer; recovery remains cooperative Max-Pressure →
  actuated → fixed-time. DQN is optional and cannot block completion.

## Decisions so far

- Destination: update the canonical Kiro specification in place rather than
  create a parallel implementation specification.
- Scenario boundary: J0 is the required inference baseline; Tunis is a
  labelled showcase.
- [J0 evidence contract](issues/01-j0-evidence-contract.md): completion requires
  a frozen J0 matched-seed matrix (at least five seeds), specialist ablations,
  recovery-ladder failure cases, and honest stakeholder KPIs; Tunis remains a
  labelled showcase and optional RL cannot block completion.
- [Read-only product contract](issues/02-read-only-product-contract.md):
  explanations, audits, and proposals remain beside immutable evidence; every
  response has seven provenance fields, deterministic verified/template/abstain
  states, explicit bounds, idempotency, and first-class fallback metrics.
- [Spec handoff decomposition](issues/03-spec-handoff-decomposition.md):
  gated history remains immutable; remaining rows receive linked task and
  executable contracts, the approved delivery order is retained, and
  HOSTED/LOCAL_RUNNER permissions are explicit and non-actuating.
- [Professor validation package](issues/04-professor-validation-package.md):
  the final handoff requires an offline runnable walkthrough, frozen evidence
  index, evidence-first sequencing, separate Tunis showcase treatment, and
  explicit claim labels and limitations.
- Product boundary: require the read-only API/UI/Synapse layer downstream of
  immutable evidence, with no actuation capability or duplicate source of truth.
- Evaluation posture: require multi-seed, failure-injection, and proxy-validation
  artifacts while accepting null and negative results.

## Not yet specified

None. The route is clear for implementation planning and execution.

## Out of scope

- Making DQN, MAPPO, or another learned controller a completion dependency.
- Multi-junction inference claims, real-world deployment, measured air quality,
  or lives-saved claims.
- Allowing Synapse, A2–A5, API handlers, or the UI to actuate SUMO.
- Implementing product code while charting this map.
