# Row 12 report

The Synapse service now resolves bounded explanations and audits against supplied
immutable evidence and an allow-listed policy corpus. Every result carries the
seven required provenance fields. Missing events produce typed abstentions;
missing policy support produces a marked template. The API exposes idempotent
explanation and audit POST operations while preserving the non-actuating
boundary.

Validation: 6 focused tests passed, including the existing non-actuation
contract. Over-limit questions are explicit 422 client errors and abstentions
remain HTTP 200 domain responses. The golden metric pack records citation
validity, event consistency, fallback state, abstention behavior, latency,
cost, and the boundary against TraCI and signal actuation.
