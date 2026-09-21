# CoFlow-5 × SUMO: AI-engineering stack and job-fit research

**Research date / external-source access date:** 20 September 2026  
**Purpose:** evidence for a grilling/design session, not an implementation specification or labor-market census  
**Scope assumption:** one engineer, one Windows/WSL laptop, no required paid cloud, one to three months

## Executive summary

The strongest portfolio version is not “five LLM agents controlling traffic.” It is a compact, reproducible **AI systems laboratory** in which:

1. a deterministic safety envelope and one authorized controller operate SUMO;
2. fixed-time, actuated, and Max-Pressure baselines anchor the evaluation;
3. one shared-policy DQN is the bounded learned component;
4. structured advisory requests, stale-message handling, fallbacks, and fault injection expose real systems judgment;
5. a small retrieval/explanation service turns immutable reason-coded logs into cited operator answers; and
6. every model or prompt change is evaluated against versioned scenarios, paired seeds, latency/cost data, and failure cases.

This shape is aligned with the broad direction of AI-engineering work without pretending that a small posting sample measures the whole market. WEF identifies AI/big data and technological literacy as fast-growing skills, while LinkedIn's January 2026 labor-market update identifies AI Agents as the fastest-growing AI-engineering skill of 2025 and also places LLMOps and LangChain in its top five.[S1][S2] The Stanford AI Index 2026, using Lightcast posting data, separately reports rapid growth in its agentic-AI skill cluster while warning that scaled agent deployment remains early.[S29] In the **six live postings sampled here**, agents/workflows and evaluation appeared in all six; production software/data concerns appeared in all six; RAG/context engineering and observability appeared in most; and classical ML, RL, or model-serving depth appeared selectively rather than universally.[J1]–[J6] These are sample observations, not prevalence estimates.

The default stack should therefore be deliberately small:

- **Control/evaluation:** SUMO + TraCI for debugging, benchmarked libsumo for batches; Python 3.11; PyTorch CPU; typed Pydantic/dataclass messages; Parquet + DuckDB; pytest; a JSON/SQLite run manifest, optionally upgraded to local MLflow.
- **Synapse:** plain typed Python workflow first; local sentence-transformer embeddings; exact cosine search or a small local vector index first; a hosted LLM behind one provider-neutral interface for the polished demo, with template-only fallback; Phoenix only after useful traces exist.
- **Not default:** LangGraph, LlamaIndex, PostgreSQL/pgvector, Pinecone, Redis, a local 7B+ generator, MAPPO, GNNs, LSTMs, Kubernetes, or “multi-agent” LLM autonomy.

The project becomes distinctive through **architectural restraint and evidence**: the LLM is structurally unable to actuate a signal; an explanation must cite both the immutable decision event and retrieved policy text; safety and performance are independently tested; message loss and model outage are first-class scenarios; and every claimed benefit is an ablation against credible baselines. That is more convincing than either an API wrapper or an overbuilt multi-agent demo.

## 1. Project constraints that should govern every stack choice

The supplied project documents impose non-negotiable constraints:

- Only A1 may write signal commands; A2–A5 make requests, bids, alerts, or weight suggestions.
- Conflicting greens and truncated pedestrian clearance are prohibited by deterministic masks.
- The watchdog ladder is learned policy → Max-Pressure → actuated → fixed-time.
- The LLM never writes TraCI, and loss of the LLM must not alter control.
- Reported comparisons include fixed-time, actuated, and Max-Pressure; use common random numbers, explicit seeds, unfinished-trip handling, and failure reporting.
- HBEFA outputs are emission **proxies**, not measured air quality.
- Simulation evidence must not be translated into lives-saved or real deployment claims.

The local feasibility study further narrows the engineering envelope.[P1]

- SUMO simulation and state extraction are likely to dominate; SUMO’s microscopic simulation is effectively single-core, so independent processes—not a GPU—are the main rollout scaling unit.[S3]
- A small parameter-shared MLP DQN is plausible on CPU. MAPPO, graph models, learned forecasting, and large sweeps are earned stretch work.
- On a weak machine, PostgreSQL, Redis, Dockerized development, and a local generator compete with simulation for RAM and setup time.
- A 4-bit model reduces weight memory but still needs runtime buffers, KV cache, tokenizer/application memory, and suitable kernels; quantization does not turn a large local model into a free dependency.[S22]
- The one-day performance smoke test must replace planning assumptions before any training-volume promise.

**Implication:** infrastructure should be added only when it demonstrates a portfolio capability that the current system cannot show more simply. “Enterprise-looking” services are not evidence of engineering judgment by themselves.

## 2. Evidence methodology and limitations

### 2.1 Source hierarchy

This report uses:

1. official product/framework documentation and source repositories for technical behavior;
2. official specifications for protocol claims;
3. official labor/skills reports for broad direction;
4. company-hosted or company-controlled applicant-tracking pages for a bounded posting sample; and
5. the three supplied CoFlow-5 documents for local requirements and compute assumptions.

Product documentation establishes supported behavior, not comparative benchmark superiority. No vendor’s “production-ready” label is treated as independent evidence that its product is required here.

### 2.2 Bounded posting sample

The posting sample is **six roles**, selected purposively on 20 September 2026 to cover a frontier lab, an agent-platform company, finance/enterprise applied AI, and an end-user product company. It is not random, geographically balanced, junior-role representative, or large enough for market-share claims. Senior/staff roles are overrepresented because they expose end-to-end capability expectations clearly. A capability count below means only “observed in this sample.”

Where an applicant-tracking page rendered only a shell to the research client, the indexed posting text and direct live URL were checked. OpenAI’s page rejected automated fetches but remained directly linked from its official careers domain. Postings can disappear or change after the access date.

### 2.3 Claim discipline

- WEF and LinkedIn support broad directional claims only within their stated methodologies.[S1][S2]
- The posting sample supports factual observations about those six listings only.
- No salary, vacancy-volume, geographic, or “percentage of AI jobs” inference is made.
- Technical comparisons below are recommendations for this project’s constraints, not universal product rankings.

## 3. Bounded live job-posting sample

### J1 — Anthropic, Staff Software Engineer, GTM AI Engineering

The role asks for production agents, MCP servers, tool use, evaluation frameworks, SQL, human approval gates, production monitoring, and observability tying model/tool actions to business outcomes. Its representative project explicitly includes seed scenarios, scoring rubrics, and regression runs on every change.[J1]

**Relevant portfolio proof:** one governed advisory tool surface; human approval before a what-if run; seeded scenario suite; trace-to-outcome links; SQL-backed analysis.

### J2 — OpenAI, AI Systems Engineer, Codex Core Agents

The listing spans harnesses, orchestration, evals, safe execution, production reliability, inference/runtime behavior, latency, cost, capacity, observability, profiling, experiments, and ablations.[J2]

**Relevant portfolio proof:** hard separation between harness/control/model failures; reproducible ablations; latency budget; fallback behavior; model-provider interface rather than prompt-only code.

### J3 — Moss, Applied AI Engineer

The posting asks for end-to-end agent features, systematic evaluations, representative datasets, regression tests, human review, latency/cost measurement, observability, RAG/MCP/knowledge graphs, orchestration frameworks, and guardrails.[J3]

**Relevant portfolio proof:** curated operator-question dataset, CI eval gate, retrieval metrics, explicit approval step, and cost/latency report.

### J4 — bunch, Senior Applied AI Engineer, AI Platform

The role emphasizes production agents, test cases built from real documents, expected outputs, CI regression suites, human review for high-stakes outputs, RAG/MCP, tool contracts, memory, authorization boundaries, and measurable accuracy/latency/cost.[J4]

**Relevant portfolio proof:** typed tool contracts; source-level authorization; golden explanation cases; model/provider regression matrix; no autonomous control authority.

### J5 — Riveron, Senior Associate – AI/ML Engineer

The listing covers data preparation, model/prompt workflows, APIs, RAG ingestion/chunking/embeddings/vector search/reranking/citations/access-aware retrieval, reproducible evaluation, monitoring, model/provider selection, REST interfaces, experiment tracking, and prompt/model versioning.[J5]

**Relevant portfolio proof:** chronological data split; versioned embedding/chunk configuration; cited answers; FastAPI boundary; classical ML run tracking next to LLM traces.

### J6 — SOUM, AI / GenAI Solutions Engineer

The role combines Python/FastAPI, React integration, tool-using workflows, RAG, embeddings, hybrid search, reranking, retrieval evaluation, data pipelines, prompt caching, latency budgets, token-cost control, observability, graceful fallback, offline/online evals, PostgreSQL/Redis, and classical ranking/recommendation/anomaly-detection concepts.[J6]

**Relevant portfolio proof:** end-to-end demo, retrieval evaluation, graceful hosted-model outage, measurable latency/cost, and one classical ML component with a real baseline.

### Factual observations within this six-posting sample

- **Agents/workflows:** 6/6 mention agents, harnesses, orchestration, or tool-using workflows.
- **Evaluation:** 6/6 call for eval frameworks, test datasets, regression suites, benchmarks, or ablations.
- **Production engineering/data:** 6/6 require operating systems end to end, APIs, SQL/data pipelines, or production reliability.
- **Observability/monitoring:** 5/6 explicitly name tracing, monitoring, observability, profiling, or production measurement.
- **RAG/context/retrieval:** 4/6 explicitly request RAG, context engineering, embeddings, retrieval, or reranking.
- **Serving/performance:** 4/6 explicitly discuss latency, cost, capacity, inference/runtime behavior, or model-provider trade-offs.
- **Classical ML/statistics/RL:** present, but uneven: Anthropic names experimentation and predictive modeling; OpenAI names ML workflows and ablations; Riveron asks for the ML lifecycle; SOUM asks for ML/NLP fundamentals and ranking/recommendation; the sampled applied-agent roles do not uniformly demand traffic-control RL.

The defensible conclusion is not “every AI role requires LangGraph” or “RAG is universal.” It is that this sample rewards **measurable, production-shaped AI systems**: data contracts, evals, observability, failure handling, cost/latency awareness, and judgment about when to use deterministic workflows, retrieval, agents, or classical models.

## 4. Capability findings and how CoFlow-5 should answer them

### 4.1 Broad trend, supported beyond the posting sample

WEF’s Future of Jobs 2025 employer survey places AI and big data among the fastest-growing skills through 2030 and identifies AI/ML specialists and software/application developers among fast-growing technology roles.[S1] LinkedIn's January 2026 Economic Graph update, based on paid job postings and member data, ranks AI Agents first, LLMOps third, and LangChain fifth among the fastest-growing AI-engineering skills of 2025; it also says demand varied by market rather than rising uniformly.[S2] The Stanford AI Index 2026 labor-market analysis, using Lightcast job-posting data, reports that its agentic-AI skill cluster rose from 0.06% of U.S. postings in 2024 to 0.23% in 2025, while the report's organizational survey evidence says scaled agent use remained in the single digits across nearly all business functions.[S29]

These sources justify investing in AI/data and software-engineering evidence. They do **not** establish that a specific framework, vector database, or multi-agent pattern dominates hiring, and growth from a small base should not be confused with universal adoption.

### 4.2 RAG and retrieval

**Capability to show:** source-aware ingestion, deterministic citations, retrieval evaluation, access/source filters, and an abstention path.

For CoFlow-5, the corpus is small and stable: selected SUMO docs, project requirements, traffic guidance, and reason-code definitions. The impressive work is not standing up a vector service; it is proving that:

- a returned explanation cites the exact decision event;
- policy claims cite an authoritative document chunk;
- retrieval configuration is versioned;
- held-out operator questions measure retrieval hit rate and answer support;
- unsupported questions abstain; and
- decision-log facts outrank free-form model invention.

### 4.3 Evals

**Capability to show:** layered evaluation rather than one “LLM-as-judge” score.

Use four layers:

1. **Deterministic control tests:** safety invariants, action masks, one-writer rule, fallback activation.
2. **Simulation evaluation:** paired seeds, baselines, tails, unfinished trips, teleports, robustness sweeps.
3. **Retrieval evaluation:** source hit, citation correctness, context precision/recall on a small labeled set.
4. **Explanation evaluation:** structured fact consistency against the decision event, required reason-code inclusion, abstention, latency, and cost. LLM-as-judge may be a secondary signal, never the sole oracle.

This directly demonstrates the evaluation, regression, and golden-dataset concerns recurring in the sample.[J1]–[J6]

### 4.4 Agents and workflows

Call A1–A5 **domain agents** only if their independent state, goals, messages, and failure modes are concrete. Do not imply that they are five conversational LLMs.

The LLM-facing Synapse should be a bounded workflow:

`operator question → classify intent → fetch immutable event/state → retrieve policy → construct cited answer → deterministic verifier → answer or abstain`

One optional tool can queue a sandboxed what-if scenario after human approval. No open-ended planner is needed. The MCP specification distinguishes user-controlled prompts, application-controlled resources, and model-controlled tools, and recommends human ability to deny tool invocations plus validation, timeouts, and audit logging.[S21] That vocabulary is useful; an MCP server is optional.

### 4.5 Observability

Tracing is valuable only when trace spans answer useful questions:

- Which retrieval chunk supported this sentence?
- Did the model invent a reason code?
- Which provider/model/prompt/embedding version ran?
- What were retrieval, generation, and verifier latencies?
- What did the call cost?
- Did fallback or abstention occur?
- Which simulation event and scenario hash does the answer describe?

Phoenix and LangSmith both support tracing and evaluation. Phoenix is free to self-host, uses OpenTelemetry/OpenInference, and is source-available under the Elastic License 2.0; it accepts traces for model calls, retrieval, tools, and custom logic and supports code-, model-, and human-scored evaluations.[S17] LangSmith provides framework-independent manual instrumentation plus strong LangGraph integration, offline/online evaluation, dashboards, alerts, and trace inspection.[S18]

### 4.6 Serving and production software

Expose only the stable product boundaries:

- `POST /scenarios` to register/run approved simulations;
- `GET /runs/{id}` for status and manifest;
- `GET /runs/{id}/events` for audit data;
- `POST /explanations` for cited advisory answers;
- a WebSocket/SSE stream only if the UI needs progress.

FastAPI, Pydantic schemas, idempotency keys, bounded queues, cancellation, and structured errors demonstrate more than splitting each agent into a service. The local control loop should stay in process.

### 4.7 Data and classical ML/RL

This is the project’s differentiation advantage:

- scenario/config hashes;
- Parquet event logs and DuckDB analysis;
- chronological forecasting splits if A4 is attempted;
- parameter-shared DQN with action masking;
- nonlearned baselines with equal evaluation care;
- paired seeds and confidence intervals;
- optional tabular emissions surrogate only if it answers a real latency/ablation question.

Do not hide a null result. A controller that fails to beat Max-Pressure but has an honest diagnosis, robust harness, and safe fallback can be stronger portfolio evidence than a cherry-picked reward curve.

## 5. Stack trade-offs

### 5.1 LangGraph versus plain typed workflow code

**LangGraph strengths**

- Designed for long-running, stateful agents with persistence, durable execution, streaming, human-in-the-loop, and a mix of deterministic and LLM-driven steps.[S7]
- Checkpointed graph state is useful if a what-if job must pause for approval and resume after process failure.[S8]
- Recognizable in several sampled listings, though usually as one acceptable option rather than a universal requirement.[J3][J4][J6]

**LangGraph costs**

- Adds graph state, checkpointing, serialization, framework versioning, and debugging concepts.
- Can obscure a six-step acyclic workflow that plain functions and typed states express directly.
- Risks making framework usage the demo rather than traffic-system judgment.

**Decision for this project**

Start with typed functions and an explicit `ExplanationState`. Add LangGraph only if the demo truly needs at least one of: resumable long-running execution, persisted approval interrupts, dynamic looping/tool choice, or visualized branching. If added, keep it solely in Synapse and show the same workflow tests independent of LangGraph.

### 5.2 LlamaIndex versus custom ingestion

**LlamaIndex strengths**

- Provides readers/connectors, parsing, chunking, indexes, retrievers, query engines, and ingestion pipelines; it is useful when sources are heterogeneous or synchronization is a product requirement.[S9]
- Integrates with multiple vector stores and observability tools.

**LlamaIndex costs**

- A small, curated corpus does not need a generalized document framework.
- Default abstractions can hide document identity, chunk provenance, and update semantics—the exact details the portfolio should expose.
- Version churn and transitive dependencies add reproducibility risk.

**Decision for this project**

Use custom ingestion first: a source manifest, parser per allowed format, deterministic chunk IDs, content hashes, metadata schema, and embedding version. Add a LlamaIndex connector only if one genuinely difficult source—such as frequently changing web docs or complex PDFs—earns it. Keep the custom evaluation and provenance schema either way.

### 5.3 pgvector versus Pinecone

**pgvector strengths**

- Keeps relational metadata, access filters, source records, and vectors in PostgreSQL.
- Exact nearest-neighbor search is the default; HNSW and IVFFlat add approximate search. Its own documentation says HNSW offers a better speed/recall trade-off but slower builds and more memory, while IVFFlat builds faster and uses less memory.[S10]
- Open source and locally inspectable.

**pgvector costs**

- Requires operating PostgreSQL, extension installation, schema/migrations, backups, and memory tuning.
- Is unnecessary when the corpus is small enough for exact local search.

**Pinecone strengths**

- Managed serverless operations, namespaces, metadata filters, and straightforward scaling.
- Namespaces isolate tenant data and reduce scanned data; query cost scales with targeted namespace size under Pinecone’s documented serverless RU model.[S11][S12]

**Pinecone costs**

- External service, credentials, network dependency, usage limits/cost model, and weaker offline reproducibility.
- Solves scale and tenancy problems this one-user portfolio does not have.

**Decision for this project**

Month 1: exact local cosine search over a serialized embedding matrix. Month 2–3, only if SQL-backed provenance is already needed: PostgreSQL + pgvector. Pinecone is a portability adapter or deployment comparison, not the default. Demonstrating that the retrieval interface can switch stores is more useful than operating both.

### 5.4 Local open-weights model versus hosted API

**Local open weights**

- Advantages: offline operation, direct model/version control, no per-call provider dependency, and a visible serving/quantization story.
- Costs: model-specific license review, downloads, RAM/VRAM contention, lower laptop throughput, serving/driver/kernel maintenance, and generally weaker output at a fixed laptop envelope.
- Hugging Face documents 4-bit/8-bit loading to reduce model memory, while serving engines such as vLLM add continuous batching and an OpenAI-compatible API; these are useful capabilities but real operational work. Hugging Face now marks TGI as maintenance-only and recommends engines including vLLM and SGLang for new work.[S22][S23]

**Hosted API**

- Advantages: strongest demo quality with minimal local compute, rapid model comparison, structured/tool outputs, and no local serving stack.
- Costs: variable token cost, rate limits, network/provider outages, behavior changes unless a snapshot is available, and external data-handling constraints. Anthropic documents standard commercial retention and separately eligible zero-data-retention arrangements, illustrating why provider policy must be checked rather than assumed.[S24]

**Decision for this project**

Use a provider-neutral interface with three implementations:

1. deterministic template explainer (mandatory fallback);
2. one hosted model for the polished demo and eval matrix;
3. an optional small local quantized model only if the machine passes a measured RAM/latency gate.

Do not fine-tune an LLM. Do not run a local generator concurrently with SUMO training on a constrained laptop. Record provider, model snapshot/identifier, prompt hash, latency, token usage, and estimated cost.

### 5.5 LangSmith versus Phoenix

**LangSmith**

- Strong integrated experience for LangGraph/LangChain, tracing, datasets, offline and online evals, dashboards, alerts, and production feedback loops.[S18]
- Managed platform is fast to demonstrate; self-host/hybrid options exist in current documentation.
- Creates a commercial platform dependency and can make the portfolio look tied to one ecosystem.

**Phoenix**

- Free to self-host and framework-agnostic, with an OpenTelemetry/OpenInference foundation; traces retrieval, model, tool, and custom spans; supports datasets, experiments, prompt iteration, and multiple evaluator types. Its ELv2 license is source-available but not OSI-approved.[S17]
- Better fit for a local-first, vendor-neutral portfolio and exposes transferable telemetry concepts.
- Requires running and maintaining another local service, and its UI/workflows may be less seamless than a fully managed integrated stack.

**Decision for this project**

Default to structured JSON traces and OpenTelemetry span names first. Add Phoenix in month 2 if Synapse exists. Choose LangSmith instead only if LangGraph becomes a core, demonstrable requirement or setup time is worth more than vendor neutrality. Never run both.

### 5.6 MLflow versus lightweight experiment tracking

**MLflow**

- Logs run parameters, code versions, metrics, and artifacts and provides run search/comparison and a UI.[S19]
- Official docs support a local SQLite backend without a separate database server.[S20]
- Recognizable MLOps evidence and useful once dozens of training/evaluation runs exist.

**Lightweight tracking**

- A versioned run manifest plus Parquet KPI rows and DuckDB queries is transparent, scriptable, and easy to keep consistent with simulation output.
- Requires custom comparison/report generation and artifact conventions.

**Decision for this project**

Build the manifest as the source of truth:

`run_id, git_sha, config_hash, scenario_hash, SUMO_version, controller_version, seed, status, timings, artifact_paths`

Add local MLflow only when it imports/references this manifest rather than duplicating identity. Its first earned use should be comparing DQN/baseline runs and storing selected checkpoints—not tracking every SUMO step.

## 6. Precise Hugging Face taxonomy mapping

Hugging Face’s task pages and `pipeline_tag` are a coarse API/discovery taxonomy: the tag describes the shape of a model API and helps determine filtering, widgets, and inference behavior.[S13][S14] Custom model-card tags are allowed, so a phrase visible on the Hub is not automatically an official pipeline category.[S14]

### Reinforcement learning

- **Status:** an official top-level Hugging Face task page/category.[S13][S15]
- **CoFlow-5 mapping:** A1’s DQN/MAPPO policy interacting with SUMO.
- **Precision note:** Hugging Face TRL is a **library for post-training transformer/foundation models** with methods such as SFT, DPO, GRPO, and reward modeling; it is not the appropriate library for traffic-control DQN merely because “RL” appears in its name.[S16] Use PyTorch/Stable-Baselines3-style RL tooling and publish a model card/checkpoint if useful.

### Time-series forecasting

- **Status:** supported by models and prediction classes in Transformers, including `TimeSeriesTransformerForPrediction` and PatchTST prediction classes.[S25]
- **CoFlow-5 mapping:** optional A4 link-flow/arrival forecasts.
- **Precision note:** the current public top-level task index fetched for this report does not list “Time Series Forecasting” alongside NLP/Tabular/RL categories.[S13] Describe it as a supported Transformers/model family and use a precise model-card tag; do not imply every forecasting model has a standard hosted pipeline/widget.

### Graph machine learning

- **Status:** a field/library/model-family concept, not a top-level official task shown on the fetched HF task index.[S13] Graphormer is an official Transformers model family for graph representations and graph-level classification/regression.[S26]
- **CoFlow-5 mapping:** optional movement-graph encoding or GNN comparator.
- **Precision note:** “Graph ML” should be a custom model-card tag or architecture description unless the actual model’s valid pipeline tag is more specific. Do not list it as an official HF pipeline category without checking the chosen library/model integration.

### Tabular regression

- **Status:** an official Hugging Face task page/category.[S13][S27]
- **CoFlow-5 mapping:** optional A5 emissions surrogate predicting a continuous SUMO/HBEFA proxy from traffic/fleet features.
- **Precision note:** this is a classical supervised regression task. LightGBM/CatBoost/scikit-learn with a model card is more defensible than forcing a transformer.

### Feature extraction / embeddings

- **Status:** “Feature Extraction” is an official NLP task on the current task index and inference schemas.[S13][S28]
- **CoFlow-5 mapping:** document/query embeddings for Synapse retrieval.
- **Precision note:** “embedding” is a representation/output and ecosystem term; Sentence Similarity is also a separate official task. Record the actual model, pooling method, normalization, vector dimension, and evaluation rather than calling all embeddings “feature extraction” interchangeably.

### Question answering

- **Status:** an official NLP task/pipeline category.[S13][S28]
- **CoFlow-5 mapping:** operator asks a question grounded in policy documents and decision events.
- **Precision note:** RAG is an **application architecture**, not one HF task. The generator may use text generation; the retriever uses embeddings/similarity; extractive QA models consume supplied context. Label the final system “retrieval-augmented question answering,” not a single QA model unless that is actually used.

### Text generation and summarization

- **Status:** both are official NLP task/pipeline categories.[S13][S28]
- **CoFlow-5 mapping:** cited event explanations use text generation; end-of-shift summaries can use summarization or constrained generation.
- **Precision note:** if the input is structured event records plus retrieved evidence, “text generation” is usually the more exact task. Use “summarization” only where a longer source trace/report is condensed and factual coverage is evaluated.

## 7. Realistic solo scope: one, two, and three months

### One month — credible systems spine

**Core**

- Reproduce the local smoke test: one small deterministic network, fixed-time controller, TraCI/libsumo measurement, compact outputs, version/seed/config hashes.
- Implement actuated and Max-Pressure baselines.
- Implement the sole-writer A1 adapter, deterministic safety mask, watchdog, and typed advisory-message schema with TTL.
- Build a run manifest and DuckDB KPI queries; include unfinished trips, teleports, tails, and paired-seed comparisons.
- Add one fault-injection test: dropped/stale advisory messages must not stop A1.
- Produce one simple operator view from immutable reason-coded events—templates are sufficient.

**Optional**

- Short DQN integration/smoke run; no performance claim.
- Small hosted-model explanation comparison on 20–40 hand-labeled questions, behind a template fallback.
- Local MLflow UI if it consumes the existing manifest cleanly.

**Trap**

- Five learned agents, MAPPO, a realistic city network, GNN, LSTM, local 7B model, LangGraph, PostgreSQL, Pinecone, Redis, Docker Compose, React polish, or live multi-agent chat.

**Portfolio claim at month 1:** “I built a reproducible, safety-constrained traffic-control evaluation harness with deterministic baselines, failure injection, typed advisory agents, and auditable explanations.” Do not claim production RAG or superior RL.

### Two months — differentiated AI-engineering project

**Core**

- Freeze Tier 0 and run the DQN/baseline paired evaluation with honest negative-result handling.
- Add one specialist end to end—prefer A2 emergency requests **or** A3 pedestrian/transit, not both initially—with explicit accept/reject reason codes and ablation.
- Build custom ingestion over a small authoritative corpus with deterministic chunk IDs and provenance.
- Build the bounded explanation workflow with hosted model + template fallback.
- Create a versioned eval dataset covering retrieval, event consistency, citation validity, abstention, latency, and cost.
- Add OpenTelemetry-style spans and Phoenix **or** LangSmith, not both.
- Serve scenario/query endpoints via FastAPI with typed schemas and cancellation.

**Optional**

- Add the second specialist.
- Add local MLflow for DQN runs/checkpoints.
- Add PostgreSQL/pgvector if SQL provenance/filtering has become valuable.
- Add one approved what-if tool with human confirmation.

**Trap**

- Calling every service an agent; introducing dynamic multi-agent LLM delegation; optimizing UI before eval coverage; using LLM-as-judge as ground truth; adding a managed vector DB solely for a logo.

**Portfolio claim at month 2:** “I shipped an eval-driven hybrid AI system combining safe RL control, deterministic fallbacks, retrieval-grounded operator explanations, end-to-end tracing, and fault-tested APIs.”

### Three months — polished case study, not a larger feature list

**Core**

- Add the remaining highest-value specialist only after ablation criteria pass.
- Run communication loss/delay and model outage sweeps; publish degradation plots and failure taxonomy.
- Add A4 as **EWMA/CUSUM over residuals or simple supervised forecasting first**; compare against persistence/seasonal/simple tree baselines. A transformer is not required.
- Package one reproducible CPU-first demo; Docker is optional if it reduces setup risk.
- Publish model/system cards, architecture threat/failure analysis, exact reproduction commands, eval dataset, and an interview-ready case study with decisions and rejected alternatives.
- Demonstrate “kill the LLM, lights unchanged.”

**Optional**

- Small local quantized explainer compared with the hosted model on quality/latency/RAM.
- LangGraph only for a persisted approval/resume workflow.
- pgvector portability implementation.
- A5 tabular emissions surrogate if inference latency or counterfactual analysis justifies it.

**Trap**

- MAPPO plus GNN plus LSTM plus local serving plus Kubernetes; full realistic-city generalization; “self-healing” agents; autonomous signal-changing LLM; invented social-impact numbers.

**Portfolio claim at month 3:** “I designed and evaluated a failure-tolerant AI decision system whose learned, deterministic, retrieval, and generative components have separate contracts, metrics, and fallback paths.”

## 8. Differentiation criteria

The project is more than an API wrapper only if a reviewer can inspect evidence for the following.

### 8.1 Hard authority boundary

The LLM and advisory agents cannot call TraCI. This is enforced by module/process capability, not merely a system prompt. A test proves that replacing, timing out, or killing Synapse leaves the action sequence unchanged for the same control inputs.

### 8.2 Counterfactual baselines and ablations

Every “smart” feature has a comparator:

- DQN vs fixed/actuated/Max-Pressure;
- A2/A3/A5 on vs off;
- messages normal vs delayed/dropped;
- RAG vs no retrieval;
- hosted model vs template fallback;
- framework workflow vs plain typed workflow only if LangGraph is added.

### 8.3 One evidence chain

An operator answer should link:

`answer sentence → cited policy chunk → immutable decision event → controller/version/config → scenario/seed`

That chain is uncommon in toy demos and directly combines data engineering, AI evaluation, observability, and domain safety.

### 8.4 Evaluation that separates failure classes

The report must distinguish:

- unsafe/invalid action;
- poor traffic outcome;
- stale or missing message;
- retrieval miss;
- unsupported citation;
- explanation inconsistency;
- provider timeout/rate limit;
- UI/API failure.

An aggregate “accuracy” or reward cannot do this.

### 8.5 Graceful degradation as a demo

Show, do not merely document:

- message bus empty → A1 continues locally;
- learned policy rejected/unhealthy → Max-Pressure;
- LLM unavailable → templates/structured event view;
- retrieval confidence low → abstain;
- stale sensor/alert → mark unknown, not clear.

### 8.6 Honest scientific result

Publish failed hypotheses and confidence intervals. Avoid best-episode reporting. A strong portfolio artifact is the decision record explaining why a feature was cut after an ablation, not the number of frameworks installed.

### 8.7 Transferable engineering artifacts

- typed schemas and state machine;
- reproducible scenario/eval manifests;
- provider/store interfaces;
- trace semantic conventions;
- golden test datasets;
- CI checks;
- concise architecture decision records;
- one-command local demo.

These demonstrate skills that transfer beyond traffic simulation.

## 9. Recommended default stack

### Mandatory core

- **Runtime:** Python 3.11 x64, pinned dependencies.
- **Simulation:** one pinned SUMO release; TraCI for GUI/debugging; libsumo only if the smoke test earns it.
- **Control:** typed Python modules, PyTorch CPU shared DQN, deterministic action mask, Max-Pressure/actuated/fixed fallbacks.
- **Messages:** in-process typed queue/event board with TTL, confidence, source, schema version, and correlation ID.
- **Data:** Parquet + DuckDB; JSON/SQLite run manifest; compact SUMO statistic/tripinfo output.
- **Tests:** pytest property/invariant tests, seeded integration tests, fault injection.
- **API:** FastAPI + Pydantic only after the local core is stable.

### Synapse default

- Custom deterministic ingestion and chunk provenance.
- A small sentence-transformer embedding model; exact local vector search.
- Plain typed workflow.
- One hosted LLM adapter plus deterministic template fallback.
- Structured verifier comparing answer claims to event fields and allowed citations.
- OpenTelemetry-compatible span names; Phoenix only after the eval set exists.

### Earned upgrades

- **MLflow + SQLite:** when run comparison/checkpoint management exceeds the lightweight manifest.
- **PostgreSQL + pgvector:** when relational provenance/filtering or multi-user durability is demonstrated.
- **LangGraph:** when persisted approval/resume or dynamic loops exist.
- **LlamaIndex:** when heterogeneous source synchronization/parsing is a demonstrated bottleneck.
- **Local open-weights generator:** after measured RAM/latency/quality comparison.
- **Redis:** only for a real split-process or split-host demo.

### Explicitly reject by default

- Pinecone for the initial corpus.
- Both Phoenix and LangSmith.
- LLM fine-tuning.
- Five LLM agents.
- LLM actuation.
- Kafka/Kubernetes.
- MAPPO/GNN/LSTM before the DQN/baseline result is frozen.

## 10. Major trade-offs to surface in the grilling session

1. **Breadth versus proof:** Is one specialist with a clean ablation more valuable than five named agents with shallow behavior? Recommendation: yes.
2. **Control novelty versus AI-engineering breadth:** The traffic RL core is technically deep; Synapse should amplify its evidence, not consume the schedule.
3. **Framework recognizability versus legibility:** A recruiter may recognize LangGraph/LlamaIndex, but typed code that exposes state, retries, and evidence can show better judgment. Add one framework only where it solves a visible problem.
4. **Local ownership versus demo quality:** A small local model shows serving skill but may weaken answer quality and consume the same hardware as SUMO. Hosted-first plus measured local comparison is the safer portfolio strategy.
5. **Managed services versus reproducibility:** Pinecone/LangSmith reduce setup but add network/account dependencies. A local-first path is more reproducible; one managed adapter can still show portability.
6. **MLOps product versus source of truth:** MLflow is useful only if run identity remains consistent with scenario manifests and SUMO artifacts.
7. **RL ambition versus statistical honesty:** More algorithms with fewer seeds is worse than one learned controller with paired baselines, robustness sweeps, and transparent limitations.
8. **Agent autonomy versus safety:** Human approval and deterministic guards are portfolio strengths, not concessions, in a cyber-physical domain.

## 11. Decision questions for the user

1. Which audience has priority: AI application engineer, ML engineer, or agent-platform/backend engineer?
2. Is the portfolio judged mainly by a live demo, code review, written case study, or benchmark result?
3. What are the actual physical cores, RAM, GPU/VRAM, and free SSD measured by the smoke test?
4. Must the demo run fully offline, or is a low-cost hosted API acceptable?
5. Which single specialist creates the clearest human story: emergency response, pedestrian/transit fairness, or emissions displacement?
6. Is the one-month success condition allowed to be “baselines + safety + evaluation harness” even if DQN is not yet superior?
7. Does the course require exactly five implemented behaviors, or only a five-agent design?
8. Is public deployment required? If not, local pgvector/Phoenix/Docker may be unnecessary.
9. Is showing LangGraph/LlamaIndex by name a hiring-target requirement, or can the project defend custom typed seams?
10. What is the maximum acceptable external service count for a reproducible reviewer setup?
11. Which 20–40 operator questions will form the first golden explanation/retrieval set, and who validates their expected evidence?
12. What result would cause each optional component—MAPPO, A4 forecasting, local LLM, pgvector, LangGraph—to be cut?

## 12. Recommended grilling thesis

The project should be defended with this thesis:

> CoFlow-5 is a controlled experiment in combining learned decision-making with deterministic safety and evidence-grounded explanation. Its novelty is not the number of agents or frameworks. It is the end-to-end proof that each component has bounded authority, measurable value, observable failure modes, and a tested fallback.

The most challenging design questions are therefore:

- Why is this component learned rather than deterministic?
- What independent baseline can falsify its value?
- What authority does it have?
- What happens when its data is stale or absent?
- How is its output evaluated without asking the same model to grade itself?
- Which artifact lets another engineer reproduce the claim?
- What is cut if the laptop or calendar fails the capacity gate?

If those answers are visible in code, traces, manifests, and ablations, CoFlow-5 will read as AI engineering rather than an API wrapper.

## Sources

All external sources were accessed 20 September 2026 unless stated otherwise.

### Supplied project sources

- **[P1]** `local-toolchain-and-compute-feasibility.md`, supplied local feasibility report, 20 September 2026.
- **[P2]** `coflow5-project-context.md`, supplied project context, 20 September 2026.
- **[P3]** `CoFlow-5_System_Requirements_Book.md`, supplied requirements baseline, 20 September 2026.

### Broad skills and labor-direction sources

- **[S1]** World Economic Forum, [Future of Jobs Report 2025](https://reports.weforum.org/docs/WEF_Future_of_Jobs_Report_2025.pdf), especially skills and jobs outlook.
- **[S2]** LinkedIn Economic Graph, [AI Labor Market Update, January 2026](https://economicgraph.linkedin.com/content/dam/me/economicgraph/en-us/PDF/ai-labor-market-update-january-2026.pdf). Its methodology defines the LinkedIn paid-job-posting and member-profile signals used.
- **[S29]** Stanford Institute for Human-Centered AI, [AI Index Report 2026](https://hai.stanford.edu/assets/files/ai_index_report_2026.pdf), especially the economy chapter; labor-market posting analysis supplied by Lightcast.

### SUMO, workflow, retrieval, storage, and observability sources

- **[S3]** Eclipse SUMO, [FAQ: parallel execution](https://sumo.dlr.de/docs/FAQ.html#can_sumo_be_run_in_parallel_on_multiple_cores_or_computers).
- **[S4]** Eclipse SUMO, [Libsumo](https://sumo.dlr.de/docs/Libsumo.html).
- **[S5]** Eclipse SUMO, [TraCI performance](https://sumo.dlr.de/docs/TraCI/index.html#performance).
- **[S6]** Eclipse SUMO, [Randomness](https://sumo.dlr.de/docs/Simulation/Randomness.html).
- **[S7]** LangChain, [LangGraph overview](https://docs.langchain.com/oss/python/langgraph/overview).
- **[S8]** LangChain, [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence) and [checkpointers](https://docs.langchain.com/oss/python/langgraph/checkpointers).
- **[S9]** LlamaIndex, [documentation overview](https://docs.llamaindex.ai/en/stable/) and [file-based ingestion pipeline example](https://docs.llamaindex.ai/en/v0.10.23/examples/node_postprocessor/FileNodeProcessors/).
- **[S10]** pgvector, [official README](https://github.com/pgvector/pgvector/blob/master/README.md).
- **[S11]** Pinecone, [indexing overview](https://docs.pinecone.io/guides/index-data/indexing-overview) and [metadata filtering](https://docs.pinecone.io/guides/search/filter-by-metadata).
- **[S12]** Pinecone, [understanding serverless cost](https://docs.pinecone.io/guides/manage-cost/understanding-cost). Pricing rates can change; the recommendation relies on the documented usage model, not a fixed price.
- **[S17]** Arize, [Phoenix documentation](https://arize.com/docs/phoenix), [self-hosting](https://arize.com/docs/phoenix/self-hosting), and [license](https://arize.com/docs/phoenix/self-hosting/license). Phoenix is licensed under ELv2.
- **[S18]** LangChain, [LangSmith observability](https://docs.langchain.com/langsmith/observability) and [evaluation concepts](https://docs.langchain.com/langsmith/evaluation-concepts).
- **[S19]** MLflow, [ML experiment tracking](https://mlflow.org/docs/latest/ml/tracking/).
- **[S20]** MLflow, [tracking experiments with a local SQLite database](https://mlflow.org/docs/latest/ml/tracking/tutorials/local-database/).
- **[S21]** Model Context Protocol, [server primitives](https://modelcontextprotocol.io/specification/2025-11-25/server) and [tool security considerations](https://modelcontextprotocol.io/specification/2025-06-18/server/tools).

### Model execution and Hugging Face taxonomy sources

- **[S13]** Hugging Face, [Tasks index](https://huggingface.co/tasks).
- **[S14]** Hugging Face, [Model cards and `pipeline_tag`](https://huggingface.co/docs/hub/main/en/model-cards) and [Hub tasks/pipeline types](https://huggingface.co/docs/hub/models-tasks).
- **[S15]** Hugging Face, [Reinforcement Learning task](https://huggingface.co/tasks/reinforcement-learning) and [Stable-Baselines3 Hub integration](https://huggingface.co/docs/hub/en/stable-baselines3).
- **[S16]** Hugging Face, [TRL documentation](https://huggingface.co/docs/trl/en/index).
- **[S22]** Hugging Face Transformers, [bitsandbytes quantization](https://huggingface.co/docs/transformers/en/quantization/bitsandbytes).
- **[S23]** Hugging Face, [Text Generation Inference maintenance notice](https://huggingface.co/docs/text-generation-inference/main/en/index); vLLM, [OpenAI-compatible server](https://docs.vllm.ai/en/stable/serving/online_serving/).
- **[S24]** Anthropic, [API and data retention](https://docs.anthropic.com/en/docs/build-with-claude/zero-data-retention) and [commercial data usage](https://docs.anthropic.com/en/docs/claude-code/data-usage).
- **[S25]** Hugging Face Transformers, [Time Series Transformer](https://huggingface.co/docs/transformers/main/en/model_doc/time_series_transformer) and [PatchTST](https://huggingface.co/docs/transformers/main/model_doc/patchtst).
- **[S26]** Hugging Face Transformers, [Graphormer](https://huggingface.co/docs/transformers/main/model_doc/graphormer).
- **[S27]** Hugging Face, [Tabular Regression task](https://huggingface.co/tasks/tabular-regression).
- **[S28]** Hugging Face, [Inference task schemas](https://huggingface.co/docs/huggingface_hub/en/package_reference/inference_types) and [Transformers task summary](https://huggingface.co/docs/transformers/main/task_summary).

### Bounded live job-posting sample

- **[J1]** Anthropic, [Staff Software Engineer, GTM AI Engineering](https://www.anthropic.com/careers/jobs/5390966008).
- **[J2]** OpenAI, [AI Systems Engineer, Codex Core Agents](https://openai.com/careers/ai-systems-engineer-codex-agents-san-francisco/).
- **[J3]** Moss, [Applied AI Engineer](https://jobs.ashbyhq.com/moss/a4cd2807-aabc-4dfb-9256-0b3736582efe).
- **[J4]** bunch, [Senior Applied AI Engineer, AI Platform](https://jobs.ashbyhq.com/bunch/9b5e752a-ddca-4c44-9ab7-7f0c71f37514).
- **[J5]** Riveron, [Senior Associate – AI ML Engineer](https://jobs.ashbyhq.com/riveron/bb55de9a-382f-475e-9578-b6308c045745).
- **[J6]** SOUM, [AI / GenAI Solutions Engineer](https://jobs.lever.co/soum/838e99ac-69e7-40a2-a9b2-fb098194c1a8).
