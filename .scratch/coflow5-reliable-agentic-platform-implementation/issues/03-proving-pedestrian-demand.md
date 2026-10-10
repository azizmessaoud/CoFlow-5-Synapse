# 03: Proving pedestrian demand on J0

**What to build:** A demonstrable J0 pedestrian path in which seeded crossings produce occupancy, clearance, waiting, and truncation evidence that A3 can use without unsafe preemption.

**Blocked by:** D1: Aligning delivery artifacts with canonical truth.

**Status:** resolved

- [x] J0 produces reproducible seeded pedestrian demand and crossing occupancy.
- [x] A3 receives typed crossing state with remaining clearance and relevant timing.
- [x] Pedestrian mean, P95, and maximum wait are reported for the run.
- [x] Active crossings are never truncated, including during competing priority requests.
- [x] The result is independently demoable and traceable to a run, scenario, and event evidence.
