# Agent authority and module boundaries

Type: grilling
Status: unclaimed
Blocked by: 01, 03

## Question

What are the final responsibilities, inputs, outputs, timescales, and forbidden capabilities of A1–A5, the deterministic safety layer, the simulation adapter, the decision log, operator views, and optional Synapse layer?

Stress-test edge cases: a pedestrian is already crossing when an EV request arrives; two EVs conflict; a late bus competes with a pedestrian deadline; A4 is wrong or silent; A5 requests an eco phase during spillback; a human override conflicts with clearance; and the LLM process dies.

The answer must settle whether “single actuator” means one global A1 process or one A1 executor per junction sharing a policy, while preserving exactly one writer per signal.
