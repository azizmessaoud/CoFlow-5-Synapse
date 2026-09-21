# CoFlow-5 feasibility and build-readiness

Label: `wayfinder:map`

## Destination

A professor-verifiable feasibility package for a 2–3 student, local-compute, approximately 12-week project: an audited Define/Ideate baseline, defensible MVP scope, technical architecture and interfaces, resource/schedule feasibility, risks and fallbacks, Prototype/Test experiment plan, and a handoff-ready implementation decomposition. The map produces decisions and plans, not code or experiment results.

## Notes

- Tracker: local markdown under `.scratch/` (`docs/agents/issue-tracker.md`).
- Source posture: the pasted Define/Ideate draft is the proposed revision. Promote claims, scores, and architectural statements only after auditing them against primary sources and the existing evidence trail.
- Resource envelope: 2–3 students, local Windows/WSL machines, approximately 12 weeks, no assumed paid cloud compute.
- Standing honesty rules: personas are research-informed, not interview-validated; simulation is not deployment evidence; HBEFA outputs are emission proxies; simulated EV time is not lives saved; never headline best episodes.
- Standing architecture constraint: one actuation authority; the LLM is outside the control loop unless a decision ticket explicitly reopens and overturns that constraint with evidence.
- Skills every session should consult: `wayfinder`, `grilling`, `domain-modeling`; use `research` for primary-source fact work and `codebase-design` when settling module boundaries.

## Decisions so far

- Destination: professor-verifiable feasibility package plus build-ready Prototype/Test and implementation decomposition; no execution in this map.
- Resource envelope: 2–3 students, local compute, approximately 12 weeks.
- Source authority: pasted Define/Ideate draft is a proposed revision, not automatically authoritative; evidence audit decides promotion.
- [Evidence and claim audit](issues/01-evidence-and-claim-audit.md): the design direction survives, but the source set is a 32-row mixed-source register, not 33 verified rows; Kingsley is 12.5%, preemption attributions must be separated, T-REX reports a 14× episode budget rather than universal cost, ALS is lower adjusted odds rather than guaranteed survival loss, and all matrix numbers/targets are team judgements. [Cited report](research/evidence-and-claim-audit.md).
- [Local toolchain and compute feasibility](issues/02-local-toolchain-and-compute-feasibility.md): Tier 0 is locally feasible with pinned native-Windows SUMO/Python 3.11, measured libsumo batches, cooperative Max-Pressure, and paired evaluation. DQN/MAPPO, Redis, Postgres/RAG, LangGraph, and a local LLM are optional scope risks; the first build ticket must replace estimates with a throughput/resource smoke test. [Cited report](research/local-toolchain-and-compute-feasibility.md).
- Portfolio identity: **reliable AI decision platform**, not an LLM traffic controller or five-chatbot system. [ADR-0001](../../docs/adr/0001-reliable-ai-platform-boundary.md).
- Capacity plan: five students nominally, but only three are placed on the critical path. Core ownership is control; scenarios/data/evaluation; and API/Synapse/evals. Other contributions must be removable.
- [MVP and success boundary](issues/03-mvp-and-success-boundary.md): course success is cooperation, one-writer authority, safety, baselines, paired evaluation, and tested failure recovery. Max-Pressure is required; DQN is optional and cannot block delivery. A4 and the Synapse portfolio layer are staged additions. [Portfolio design](../../docs/architecture/coflow5-synapse-portfolio-design.md).
- Scenario strategy: controlled 4×4 benchmark for inference and ablation, plus a Tunis OSM and official TRANSTU GTFS showcase. Tunis road demand is synthetic/calibrated unless a verified observed source is added.
- Deployment strategy: reproducible local simulation plus a hosted read-only API/dashboard over precomputed runs; no promise of continuous cloud SUMO training.
- Stack boundary: typed Python for A1–A5; LangGraph only for bounded Synapse approval/resume; exact local retrieval first, then PostgreSQL/pgvector; hosted LLM behind an interface with deterministic fallback; Phoenix after a golden eval set exists.
- Required AI-task target: time-series forecasting/anomaly detection, feature extraction/RAG, and text generation/summarization. Reinforcement learning, tabular regression, and graph ML are extensions.
- Portfolio headline: prove safe degradation, baseline comparison, grounded explanations, and measured latency/cost—not guaranteed traffic improvement.

## Not yet specified

- Exact local hardware throughput and training wall-clock time; this becomes measurable only after the Tier 0 simulation-speed smoke test.
- Exact Tunis subnetwork, OSM extraction boundary, GTFS routes, and synthetic-demand calibration method.
- Whether the React dashboard is required for grading; it is currently portfolio polish and cannot block course success.
- Whether optional civic analyses (bus-lane, bike-lane, traffic-calming candidates) belong in the final demonstration or a future-work appendix.

## Out of scope

- Implementing agents or provisioning SUMO during wayfinding.
- Claiming deployment readiness, measured air quality, or lives saved.
- Letting an LLM, A2, A3, A4, or A5 write traffic-light phases.
- Paid-cloud scale assumed without a separately approved resource decision.
