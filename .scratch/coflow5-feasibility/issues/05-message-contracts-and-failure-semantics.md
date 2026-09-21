# Message contracts and failure semantics

Type: grilling
Status: unclaimed
Blocked by: 04

## Question

What exact message types and failure semantics make pub/sub plus one-round request/reply testable without overbuilding distributed infrastructure?

Settle topic ownership, schemas, ids, timestamps, TTLs, confidence, priority class, benefit/externality fields, heartbeats, reason codes, duplicate/idempotency behaviour, per-epoch budgets, ordering assumptions, backpressure, stale-message discounts, and local fallback when messages are absent, late, malformed, duplicated, or contradictory.

Decide the in-process interface first and the seam that permits Redis Streams later without changing agent logic.
