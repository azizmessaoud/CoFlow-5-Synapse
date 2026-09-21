# MVP and success boundary

Type: grilling
Status: resolved
Blocked by:

## Question

What is the smallest CoFlow-5 result that counts as a successful academic project under the course brief, and what evidence must exist before A2–A5 or Synapse are allowed into that claim?

Resolve the mandatory demo, mandatory report evidence, Tier 0 exit criteria, whether a negative A1-versus-Max-Pressure result can still pass, which personas must be represented in the MVP, and which features are explicitly “advanced/future work.” Separate course success, research success, and portfolio polish so they cannot silently expand one another.

## Answer

The accepted boundary is recorded in [`docs/architecture/coflow5-synapse-portfolio-design.md`](../../../docs/architecture/coflow5-synapse-portfolio-design.md) and [ADR-0001](../../../docs/adr/0001-reliable-ai-platform-boundary.md).

### Course success

- Reproducible controlled SUMO scenario.
- Fixed-time, actuated, and Max-Pressure baselines.
- One A1 signal writer, deterministic safety mask, watchdog fallback, and reason-coded log.
- At least A2 emergency and A3 pedestrian/transit requests as testable rules.
- Paired-seed evaluation that counts unfinished trips, teleports, and safety failures.
- Cooperative Max-Pressure is the required A1 controller. DQN is optional and cannot block course success.

### Research success

- Cooperation evaluated through adviser on/off ablations against fixed-time, actuated, and non-cooperative Max-Pressure comparisons.
- Message loss/delay plus controller, adviser, forecast, and Synapse failure sweeps.
- A4 LightGBM-versus-simple-baseline forecast plus EWMA/CUSUM residual incident detection.
- Ablations that isolate specialist value; no best-episode headline.

### Portfolio polish

- Bounded Synapse retrieval/explanation flow, golden evaluation set, deterministic verifier, traces, and template fallback.
- FastAPI plus React/Vite view over precomputed runs.
- Tunis OSM plus official TRANSTU GTFS showcase, with synthetic/calibrated road demand labelled explicitly.
- PostgreSQL/pgvector, Phoenix, and LangGraph are staged integrations, not Tier 0 dependencies.

### Advanced or future work

DQN, MAPPO, LSTM/PatchTST, GNN control/forecasting, learned A5 surrogate, Redis, local LLM serving, Pinecone, and civic infrastructure comparisons are outside the success boundary unless the required cooperative reliability slice is frozen first.
