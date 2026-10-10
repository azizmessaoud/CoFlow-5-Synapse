# 07: Delivering the read-only API boundary

**What to build:** A typed API through which operators can inspect frozen runs, evidence, explanations, audits, and approved what-if lineage without gaining signal authority.

**Blocked by:** 06: Delivering bounded Synapse explanations and audits.

**Status:** ready-for-agent

- [ ] Run, manifest, evidence, event, comparison, explanation, audit, and approval operations are typed and bounded.
- [ ] `HOSTED` has no mutation surface; `LOCAL_RUNNER` may mutate runs and proposals but neither profile can actuate signals.
- [ ] Explanation and audit POST operations require idempotency keys.
- [ ] Bounds exist for runs per comparison, events per page, and question length.
- [ ] Abstention is returned as a typed HTTP 200 domain result; malformed or over-limit requests are explicit errors.
- [ ] What-if lineage is proposal, human approval, then a new run identifier.
- [ ] Responses preserve the seven provenance fields and never create a second evidence source.
