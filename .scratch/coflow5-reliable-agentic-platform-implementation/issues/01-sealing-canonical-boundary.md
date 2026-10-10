# 01: Sealing the canonical persona and honesty boundary

**What to build:** One authoritative project boundary that downstream implementation can use for personas, J0 topology, incident data, and honesty rules without contradictory claims.

**Blocked by:** None (can start immediately).

**Status:** resolved

**Resolution:** The persona alias table is final and authoritative. J0 is the
required controlled benchmark; 4×4 is planned scale-up work. Incident Schema
v1 is final with append-only `detected` → `active` → `resolved`/`cancelled`
lifecycle transitions, join keys, and an explicit prohibition on direct signal
actuation.

- [x] Persona aliases and the canonical roster are consistent across the project artifacts.
- [x] J0 is identified as the controlled demonstration topology and non-J0 topology claims are labelled appropriately.
- [x] Incident data shape and lifecycle are explicit enough for downstream A4/A5 and recovery work.
- [x] Claim flags distinguish measured simulation evidence, assumptions, proxies, and prohibited deployment claims.
- [x] The resulting boundary is referenced by the downstream implementation tickets.
