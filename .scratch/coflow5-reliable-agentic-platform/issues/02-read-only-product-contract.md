---
name: read-only-product-contract
description: Define the evidence-backed API, UI, and Synapse contract
labels: [wayfinder:resolved]
parent: coflow5-reliable-agentic-platform-map
Type: grilling
Status: resolved
---

## Question

Given the frozen J0 evidence contract, what read-only API, dashboard, and
Synapse behaviors, provenance fields, abstention rules, and deterministic
fallbacks are required for the final product layer without affecting control or
inventing a second source of truth?

## Answer

The product layer is read-only with respect to domain facts. Explanations,
audits, and what-if proposals are written beside the immutable evidence bundle,
never into it. `HOSTED` has no mutation surface; `LOCAL_RUNNER` may mutate runs
and proposals but never has a signal surface.

The API, dashboard, and Synapse read only frozen evidence bundles and an
allow-listed policy/document corpus. Every typed response carries seven
provenance fields: `run_id`, `scenario_hash`, `event_id`, `message_id`,
`bundle_digest`, `corpus_hash`, and `query_hash`. Non-applicable fields are
explicitly null.

Caching uses `(bundle_digest, endpoint, query_hash)`. Every explanation pins
`corpus_hash` in its provenance. The fallback ladder is:

1. `verified`: cited event and policy support pass deterministic verification;
2. `template`: deterministic structured facts or explanation, including a
   `policy_support_missing` marker when the event exists but policy support is
   incomplete;
3. `abstain`: no event or insufficient support, with a typed reason.

Abstention is an HTTP 200 domain outcome. HTTP 4xx is reserved for malformed
or over-limit requests. `abstention_rate` and `fallback_rate` are first-class
metrics, partitioned by endpoint, fallback state, corpus version, and time
window. `Idempotency-Key` is required on `POST /explanations` and
`POST /audits`. Bounds are explicit and enforced for runs per comparison,
events per page, and question length.

What-if lineage is `proposal -> human approval -> new run_id`. A proposal is
referenced by the new run but never merged into its measured evidence.
