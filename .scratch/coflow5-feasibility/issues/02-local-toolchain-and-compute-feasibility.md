# Local toolchain and compute feasibility

Type: research
Status: resolved
Blocked by:

## Question

What can a 2–3 student team credibly build and evaluate in approximately 12 weeks using local Windows/WSL machines?

Use official SUMO and framework documentation plus reproducible benchmark evidence to assess: SUMO/libsumo/TraCI installation and supported Python versions; Windows/WSL trade-offs; libsumo versus TraCI throughput; multiprocessing constraints; PyTorch CPU/GPU needs for shared-policy DQN and MAPPO; realistic seed/scenario counts; storage/log volume; Docker feasibility; and whether Redis, PostgreSQL/pgvector, MLflow, LangGraph, and an open-weights LLM are required, optional, or scope risks.

Return a resource envelope with low/base/high estimates, a Tier 0 smoke-test procedure that will replace estimates with measurements, and explicit cut-lines for a no-GPU or weak-laptop case.

## Answer

Local delivery is feasible if Tier 0 remains deliberately small:

- Start on **native Windows**, pin one exact SUMO release and **64-bit Python 3.11**, use TraCI + `sumo-gui` for diagnosis, and benchmark libsumo for headless batches.
- Use one simulator process per worker; SUMO microscopic simulation is effectively single-core, so useful scaling comes from independent processes.
- Use cooperative **Max-Pressure** as the required A1 controller. A parameter-shared CPU DQN and MAPPO are optional experiments only after the cooperative core freezes.
- Redis, PostgreSQL/pgvector, LangGraph, and a local open-weights LLM are not Tier 0 dependencies. MLflow is optional and may use local SQLite.
- No GPU: retain Max-Pressure and A4’s CPU models; cut DQN/MAPPO and the local LLM first. Weak laptop: reduce to 2×2/3×3 networks, one worker, compact logs, and five exploratory evaluation seeds.
- The first implementation ticket must benchmark TraCI versus libsumo, worker scaling, decision latency, memory, storage, and achievable seeds before any training or schedule estimate becomes a commitment.

The feasibility conclusion is conditional: protect SUMO, cooperation, one-writer authority, safety baselines, paired evaluation, and failure recovery; treat DQN/MAPPO, distribution, RAG, and presentation infrastructure as scope risks.

**Decision update (20 September 2026):** ADR-0001 supersedes the report’s earlier recommendation to protect DQN as part of Tier 0. The underlying compute findings remain valid, but RL is no longer on the critical path.

Full cited report: [local-toolchain-and-compute-feasibility.md](../research/local-toolchain-and-compute-feasibility.md).
