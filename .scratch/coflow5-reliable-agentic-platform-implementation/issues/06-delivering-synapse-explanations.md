# 06: Delivering bounded Synapse explanations and audits

**What to build:** A non-actuating Synapse experience that explains and audits frozen J0 decisions with verified facts, policy citations, explicit provenance, and deterministic fallback.

**Blocked by:** 05: Freezing the J0 completion evidence.

**Status:** ready-for-agent

- [x] Decision questions resolve against immutable evidence and an allow-listed policy corpus.
- [x] Responses carry the seven provenance fields with explicit nulls where not applicable.
- [x] Fallback state is exactly `verified`, `template`, or `abstain`.
- [x] Missing events abstain; missing policy support produces a marked template response.
- [x] Explanations pin the corpus identity and use the approved cache key.
- [x] Audits compare claims with evidence and abstain when support is insufficient.
- [x] Synapse cannot reach signal actuation, active control state, or TraCI.
- [ ] Golden evaluations cover citation validity, event consistency, abstention, latency, cost, and fallback rate.

**Status:** in progress (core service and API seam implemented; golden metric pack remains)
