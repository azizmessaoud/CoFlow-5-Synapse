# 04: Multi-agent patterns, limits, and trade-offs

**What to build:** The Final Project Book includes the P-1–P-10 inventory as keep / optional / reject, with micro (one junction, one epoch) and macro (network, five-agent society) limitations and trade-offs. A professor can grade why cooperation with one writer was chosen, and what it costs. Source is the existing design-patterns inventory under ADR-0001, not a new architecture.

**Blocked by:** 01 Honest professor book

**Status:** resolved

- [x] P-1 single actuation authority: **keep**. Only A1 writes signals.
- [x] P-2 deterministic safety mask: **keep**.
- [x] P-3 blackboard / pub-sub: **keep** (in-process first).
- [x] P-4 contract-net request/reply: **keep** for A2/A3.
- [x] P-5 bid-based arbitration: **keep** inside priority tiers; not a global optimum claim.
- [x] P-6 shared-policy MARL: **optional** row 15; not Core A1.
- [x] P-7 hierarchical timescales: **keep** (A1 seconds, advisers slower).
- [x] P-8 watchdog ladder: **keep**, required path starts at cooperative Max-Pressure → actuated → fixed-time.
- [x] P-9 heartbeat / TTL / stale handling: **keep**.
- [x] P-10 LLM explainer: **keep as Synapse layer**; reject as controller.
- [x] Each kept pattern names one limitation and one trade-off a Test cell can later falsify.
- [x] Rejected: LLM signal write, five conversational agents, independent RL with no one-writer rule, throughput-only optimization.

## Answer

Section 16.2 in the Final Project Book. Pattern inventory P-8 and macro CTDE row aligned with ADR-0001.
