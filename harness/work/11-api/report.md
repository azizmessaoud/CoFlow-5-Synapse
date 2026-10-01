# Row 11 — read-only evidence API

The API serves a bundle only when its gate passes, `openDeltas` is 0, `decidedBy` is `tests-and-files`, the contract hash matches, and every declared artifact hash matches. Run, scenario, graph, event, message, request, and chunk identities are copied from those files.

GET routes cover health, the run list, one run, events, KPIs, graph frames, explanations, audits, citations, golden metrics, and limitations. Pages are ordered by identity or time and capped at 50 rows. A missing evidence class returns `unavailable`. A bad gate returns `validation`. A hash mismatch returns `corrupt_evidence`. An unknown run returns `not_found`.

There is no POST, PUT, PATCH, or DELETE route, no SUMO launch, and no TraCI import. Rows 10f and 12 were read and not rewritten. No winner is claimed.
