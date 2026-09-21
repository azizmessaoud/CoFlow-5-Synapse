Status: ready-for-agent

# CoFlow-5 Synapse — Reliable AI Decision Platform

## Problem Statement

Traffic-control AI projects often demonstrate one learned controller under ideal conditions, report a best reward, and add an LLM explanation without proving whether the explanation is grounded or whether the system remains safe when models, messages, or providers fail.

CoFlow-5 needs to give its User Personas, student team, professor, and portfolio reviewers stronger evidence. The platform must compare learned control with credible deterministic baselines, preserve legal signal behavior under failure, represent emergency and multimodal needs, explain immutable decisions with cited evidence, and expose enough provenance for another engineer to reproduce every claim.

The team has SUMO installed and a 12-week delivery window. Five students are nominally available, but only three contributors may be placed on the critical path. Compute is CPU-first, with no required paid training infrastructure. A low-cost hosted LLM may support the Synapse layer, but it must never become a dependency of the Control plane.

The repository is currently documentation-first and contains no implementation modules. The feature is therefore a greenfield implementation constrained by the accepted domain language, system requirements, feasibility findings, and ADR-0001.

## Solution

Build CoFlow-5 Synapse as a **Reliable AI decision platform** around Eclipse SUMO.

The Control plane will execute a controlled 4×4 benchmark, compare fixed-time, actuated, and Max-Pressure controllers, accept typed advisory messages from A2–A5, apply deterministic safety constraints, and recover safely when a controller, adviser, message, or model fails. Max-Pressure is the required A1 controller. A shared DQN is an optional experiment and cannot block delivery.

Every run will produce one versioned evidence bundle containing its manifest, scenario and configuration hashes, immutable decision events, agent messages, controller actions, faults, KPIs, and evaluation results. This evidence bundle is the primary product and the highest system test seam. The dashboard, reports, and Synapse layer must consume it rather than invent separate sources of truth.

The Synapse layer will answer operator questions by retrieving an immutable decision event and authoritative policy material, generating a cited explanation, deterministically checking factual claims, and either returning the supported answer or abstaining. It will be structurally unable to actuate SUMO. A deterministic template explanation will remain available when retrieval or the hosted model fails.

The system will also provide a Tunis showcase using OSM and official TRANSTU GTFS/CKAN data. Scheduled transit data is real; road demand remains explicitly synthetic or calibrated unless a separately verified observed source is introduced.

### Course Challenge Alignment

The implementation answers the course question, *“How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?”*, without assuming that technological complexity is success. The working prototype, experiments, baseline comparisons, and data-driven strengths and limitations are mandatory. Emergency vehicles, pedestrians, public transport, sustainability, incidents, communication, and prediction are represented only where they can be evaluated.

The core decision is:

> At each decision epoch, which legal signal action should A1 apply, after considering local traffic state and valid advisory requests, to improve mobility and service objectives without violating safety or hiding harm?

A1 cooperates with A2–A5 through typed messages, but remains the sole actuator. The project tests whether this cooperation adds measurable value over simpler control.

### Data Science Lifecycle

#### 1. Problem

The project solves constrained sequential decision-making under changing demand, conflicting stakeholder needs, imperfect forecasts, and communication failures. The primary problem is not simply “reduce average vehicle delay.” It is to select legal, robust signal actions while preserving emergency priority, pedestrian clearance, transit regularity, sustainability evidence, and operator accountability.

The decision hierarchy is:

1. preserve legal and safe signal operation;
2. maintain local control when advisers or models fail;
3. compare traffic efficiency with credible baselines;
4. arbitrate emergency, pedestrian, transit, and sustainability requests;
5. explain and reproduce every evaluated outcome.

#### 2. Success Criteria

The solution is useful when:

- no tested action produces conflicting greens or truncated required clearance;
- identical control inputs produce identical traffic actions whether Synapse is running or stopped;
- A1 continues under missing, stale, duplicate, malformed, or delayed advisory messages;
- fixed-time, actuated, and Max-Pressure are compared on paired scenario seeds; an optional DQN uses the same evaluation contract if implemented;
- emergency delay, pedestrian waits, transit regularity, network delay, queues, throughput, stops, unfinished trips, teleports, and emissions proxies are reported together;
- at least one cooperative adviser demonstrates value through an ablation, or its lack of value is reported honestly;
- every reported result can be traced to a scenario, configuration, controller, model version, seed, and immutable evidence bundle;
- Synapse explanations cite the correct event and policy evidence, abstain when unsupported, and expose latency, cost, and fallback behavior;
- another reviewer can reproduce the controlled benchmark and inspect the strengths and limitations.

Traffic improvement thresholds remain hypotheses until measured. The project does not require DQN. A null or negative optional DQN result does not invalidate the project if the evaluation is credible and Max-Pressure remains active.

#### 3. Data

There is no single universal “row.” Each dataset has one explicit unit of observation:

- **State row:** one junction or controlled movement at one simulation step, containing queues, occupancy, waits, active phase, elapsed phase time, and relevant approaching road users.
- **Decision row:** one A1 decision epoch, containing proposed action, legal-action mask, accepted action, controller health, fallback state, considered requests, and reason code.
- **Message row:** one advisory message or its disposition, containing source, topic, timestamps, TTL, confidence, priority, correlation ID, payload version, and accept/reject reason.
- **Trip row:** one completed or unfinished vehicle/person trip, containing route class and travel, waiting, stop, completion, teleport, and relevant emissions-proxy outcomes.
- **Link-forecast row:** one link and forecast-origin time for one prediction horizon, containing features, target, prediction, residual, model version, and incident label where available.
- **Run-KPI row:** one run, controller, scenario, demand regime, and seed for one named metric.
- **Corpus row:** one authoritative document chunk with source identity, content hash, section, authority metadata, parser version, and embedding version.
- **Golden-evaluation row:** one operator question with expected event facts, acceptable sources, expected answer behavior, and abstention label.

Data sources are:

- SUMO state, trip, person, signal, safety, and HBEFA emissions-proxy outputs;
- generated controlled demand and injected incidents/faults;
- OSM network data for the Tunis showcase;
- official TRANSTU scheduled GTFS obtained through Tunisia’s transport CKAN portal;
- approved SUMO documentation, traffic-engineering guidance, project requirements, reason-code definitions, and operator playbooks;
- human-labelled retrieval and explanation cases produced by the team.

Limitations include simulation-to-reality gaps, generated Tunis road demand, scheduled rather than confirmed real-time transit data, emissions estimates rather than air-quality measurements, imperfect SUMO sensors, limited seeds under local compute, research-informed rather than interview-validated User Personas, and possible document/model/provider drift.

#### 4. Exploratory Data Analysis

EDA must occur before controller or forecasting claims. It will examine:

- demand, queue, wait, speed, stop, and trip-time distributions by scenario, time window, junction, route class, and stakeholder;
- warm-up behavior, gridlock, spillback, unfinished trips, teleports, and outliers;
- phase utilization and whether fixed programs are mismatched to demand;
- emergency arrivals, pedestrian waits, bus lateness/headway variation, and where objectives conflict;
- temporal autocorrelation, seasonality within simulated demand, lag relationships, and forecast horizons;
- class imbalance in incidents and rare safety/failure events;
- missing, stale, duplicated, delayed, and contradictory agent messages;
- feature leakage, especially future traffic values entering A4 inputs;
- emissions-proxy concentration and whether improvements are displaced to residential links;
- whether controller comparisons use genuinely matched seeds and demand.

Initial hypotheses include: Max-Pressure will outperform fixed-time under variable demand; cooperation may improve selected stakeholder outcomes but can create externalities; emergency priority can reduce emergency delay while increasing civilian delay; pedestrian/transit guarantees may trade mean vehicle delay for tail fairness; A4 is valuable only if forecast-informed actions outperform a no-forecast ablation; and cooperation degrades as messages become stale or unreliable. If attempted, DQN is a separate hypothesis and may not beat Max-Pressure.

#### 5. Preparation

Preparation includes:

- validating schemas, units, timestamps, simulation-step alignment, source versions, and referential integrity;
- removing warm-up periods only according to a predeclared rule while retaining failures and unfinished trips;
- deriving queues, elapsed phase time, pressure, waiting-time buckets, approaching emergency distance, pedestrian wait, bus lateness/headway deviation, and recent link-flow lags;
- if optional DQN work is approved, normalizing its continuous inputs with training-only statistics and encoding phases/actions consistently;
- masking illegal actions instead of teaching safety only through reward penalties;
- generating chronological train/validation/test splits for A4;
- fitting all scalers, imputers, and feature selectors on training data only;
- preserving rare incidents rather than balancing them away, while using suitable weights or stratified analysis where needed;
- creating stable scenario/configuration hashes and run identifiers;
- deduplicating documents, assigning stable chunk IDs, recording provenance, and embedding the allow-listed corpus;
- excluding secrets and unnecessary personal information from logs, prompts, and public artifacts.

#### 6. Baseline

The simplest reasonable traffic baseline is fixed-time control. Actuated control is added as a demand-responsive conventional baseline. Max-Pressure is the required cooperative A1 controller and the strong algorithmic comparison point. An optional DQN must earn the right to replace it in any experiment.

Additional baselines are:

- no-specialist/no-message ablations for A2–A5;
- persistence and simple tree models before more complex A4 forecasting;
- EWMA/CUSUM without learned forecasts for incident detection;
- deterministic event templates and no-retrieval generation for Synapse;
- exact local vector search before pgvector indexing or managed stores.

#### 7. Model

A1 uses Max-Pressure because it is transparent, CPU-feasible, responsive to changing queues, and compatible with deterministic safety constraints and advisory arbitration. A1 features include observable queue/pressure state, phase and elapsed time, recent arrivals/waits, the legal action mask, and valid summarized adviser requests.

A shared DQN is optional research work after the cooperative Max-Pressure system and evaluation harness are frozen. If attempted, it uses the same observations, legal action contract, scenarios, seeds, and fallback behavior. Safety-critical rules are never learned features; they remain deterministic constraints.

A4 uses LightGBM after persistence and simple baselines because lagged traffic features are tabular, training is CPU-feasible, feature contributions can be inspected, and the model does not require a large time-series corpus. EWMA/CUSUM over residuals supplies transparent incident evidence.

A2, A3, and A5 use deterministic rules in the required slice because their constraints, budgets, and reason codes need auditability more than additional learned-model breadth.

Synapse uses sentence-transformer embeddings for retrieval and a hosted generator behind a provider-neutral interface. Generation is permitted only after immutable event retrieval and must pass deterministic verification. LangGraph is limited to persisted approval/resume and bounded retry in the Synapse layer.

#### 8. Evaluation

Metrics are selected by failure consequence and User Persona need:

- **Safety:** illegal/conflicting action count, clearance violations, emergency conflicts, teleports, and collision/surrogate-safety outputs where configured.
- **Efficiency:** mean and P95 travel time, delay, queue length, throughput, stops, completion rate, and gridlock/standstill indicators.
- **Emergency:** response-vehicle travel and delay plus civilian externality during and after preemption.
- **Pedestrian:** mean, P95, and maximum waiting time plus clearance completion.
- **Transit:** lateness, headway variation, journey time, and general-traffic externality.
- **Sustainability:** SUMO/HBEFA fuel and pollutant proxies, stops, and spatial displacement; never measured air quality.
- **Forecasting/incidents:** MAE/RMSE by horizon and regime, residual behavior, precision, recall, F1, detection delay, and false-alert rate.
- **Robustness:** KPI degradation under message delay/loss, stale sensors, model rejection, and Synapse/provider outage.
- **RAG/explanation:** retrieval recall at `k`, citation validity, event-fact consistency, required reason-code coverage, abstention quality, latency, token use, estimated cost, and fallback rate.
- **Reproducibility:** successful reruns, complete manifests, version coverage, and artifact integrity.

Controllers use common random numbers, paired comparisons, confidence intervals, equal evaluation care, and predeclared stopping rules. Best episodes are never used as headline evidence.

#### 9. Error Analysis

Every failure is assigned to a separate class rather than hidden in aggregate reward:

- illegal or masked control proposal;
- legal action with poor traffic outcome;
- reward gaming, starvation, oscillation, or spillback;
- regime or network generalization failure;
- stale, missing, malformed, duplicate, or contradictory message;
- A4 forecast miss or false incident;
- retrieval miss or wrong-source retrieval;
- unsupported citation or event inconsistency;
- provider timeout, rate limit, malformed output, or excessive cost;
- API, queue, persistence, trace, or UI failure.

Analysis slices errors by controller, demand regime, junction, route/user class, incident type, communication fault, seed, model version, and fallback state. Representative traces and counterexamples accompany aggregate metrics.

#### 10. Iteration

Iteration is evidence-gated:

- if the throughput smoke test cannot support the planned seeds, reduce network size or training volume before reducing baseline rigor;
- if an optional DQN fails to beat Max-Pressure, inspect state/action design and reward failure once, then retain Max-Pressure rather than cherry-pick;
- if an adviser has no ablation value, simplify or remove it from the required slice;
- if A4 does not beat persistence or does not improve downstream decisions, keep transparent residual detection and cut the learned forecast;
- if retrieval misses dominate, improve source coverage, metadata, chunking, or query formulation before changing the generator;
- if explanations contradict events, strengthen deterministic verification and templates before trying a larger model;
- if hosted-model latency or cost violates the demo budget, cache approved evidence, shorten context, or use template fallback;
- if integration slips, cut optional models and infrastructure before safety, baselines, evidence bundles, and traceability.

#### 11. Deployment

Another system or user consumes CoFlow-5 through:

- a reproducible local CPU-first SUMO runner;
- a FastAPI service for idempotent scenario submission, run status, evidence/event access, cancellation, explanations, and approved what-if requests;
- a React/Vite interface for precomputed scenario comparison, controller/fallback state, agent messages, citations, evaluations, and traces;
- Parquet/DuckDB and versioned reports for offline analysis;
- a hosted read-only portfolio deployment over precomputed runs with live bounded Synapse queries.

The local verification path works without a hosted LLM through frozen evidence bundles and deterministic template explanations. Continuous cloud training and real signal deployment are not promised.

#### 12. Monitoring

The platform monitors:

- simulation throughput, job queue depth, run failures, artifact volume, and resource use;
- controller health, action rejection, fallback transitions, safety invariants, unfinished trips, teleports, and KPI drift by scenario regime;
- message volume, age, expiry, duplication, schema rejection, and adviser silence;
- A4 residual and error drift by horizon and demand regime;
- corpus, parser, embedding, prompt, model, provider, and evaluator versions;
- retrieval misses, citation failures, event inconsistencies, abstentions, provider errors, p50/p95 latency, token use, estimated cost, and template fallback;
- golden-evaluation regression results for every approved model, prompt, embedding, or corpus change.

Monitoring in this project establishes simulation and software health. It does not claim field-model drift detection without real deployment data.

### Fishbone Diagram — Root Cause Analysis

**Effect under investigation:** unsafe, ineffective, unfair, or non-reproducible traffic-management decisions.

```text
  DATA / MEASUREMENT                    MODEL / METHOD
  - synthetic demand                    - reward misalignment
  - stale or missing sensors            - overfitting to one regime
  - forecast leakage                    - optional DQN instability
  - weak incident labels                - invalid action proposal
  - proxy emissions                     - unfair objective weighting
                 \                      /
                  \                    /
                   \                  /
                    \                /
                     >===============>  UNSAFE / INEFFECTIVE /
                    /                \   UNFAIR / UNREPRODUCIBLE
                   /                  \  DECISIONS
                  /                    \
  AGENT COMMUNICATION                   ENVIRONMENT / SCENARIO
  - delayed or lost messages            - demand shift and incidents
  - duplicate requests                  - spillback and gridlock
  - conflicting priorities              - limited network diversity
  - unclear TTL/ownership                - simulation-to-reality gap
  - backpressure                         - rare edge cases

  PEOPLE / PROCESS                     PLATFORM / INFRASTRUCTURE
  - unclear success criteria            - SUMO throughput bottleneck
  - cherry-picked episodes              - version mismatch
  - weak integration ownership          - provider outage/rate limit
  - insufficient seeds                  - corrupted/incomplete artifacts
  - targets reported as results         - trace or queue failure
```

The root-cause response is architectural as well as statistical: deterministic safety masks address invalid actions; baselines and paired seeds address weak comparisons; versioned evidence bundles address reproducibility; TTLs and failure injection address communication; fallbacks address model/provider failure; and explicit limitations address simulation and proxy-data gaps.

## User Stories

1. As Rosa the city operator, I want to see the active controller and its health, so that I know whether learned or fallback control is running.
2. As Rosa the city operator, I want every signal decision to include a reason code, so that I can audit why the decision was made.
3. As Rosa the city operator, I want to ask why a request was accepted or rejected, so that I can explain the outcome to stakeholders.
4. As Rosa the city operator, I want explanations to cite the exact decision event, so that generated prose cannot replace operational evidence.
5. As Rosa the city operator, I want policy statements to cite authoritative source chunks, so that I can verify the rule behind an explanation.
6. As Rosa the city operator, I want unsupported questions to produce an abstention, so that uncertainty is visible rather than fabricated.
7. As Rosa the city operator, I want a structured event view when the LLM is unavailable, so that core oversight continues during provider failure.
8. As Rosa the city operator, I want a human approval step before any what-if simulation is queued, so that advisory tools cannot consume resources or imply authority without review.
9. As Omar the incident manager, I want incident alerts to include confidence, source time, and expiry, so that stale alerts are not treated as current.
10. As Omar the incident manager, I want to see whether an alert changed an A1 decision, so that forecast value can be tested rather than assumed.
11. As Omar the incident manager, I want the system to continue local control when A4 is silent or wrong, so that forecasting is advisory rather than a single point of failure.
12. As Marcus the emergency responder, I want A2 to request corridor priority with explicit urgency and expected benefit, so that emergency needs can be arbitrated consistently.
13. As Marcus the emergency responder, I want conflicting emergency requests to receive deterministic outcomes and reason codes, so that priority handling remains explainable.
14. As David the driver, I want traffic performance compared across the same scenarios and seeds, so that claimed improvements are not caused by easier demand.
15. As Chidi the transit rider, I want late transit vehicles represented in A3 requests, so that average car delay does not hide service reliability.
16. As Amara the pedestrian, I want crossing clearance protected even when an emergency request arrives, so that optimization cannot truncate a legal crossing.
17. As Amara the pedestrian, I want excessive waits visible as a reported KPI, so that pedestrian harm is not averaged away.
18. As Maria the resident, I want emissions displacement and local delay displacement reported, so that benefits are not silently moved to another street.
19. As Yuki the traffic engineer, I want fixed-time and actuated baselines compared with cooperative Max-Pressure, so that system value is judged against credible alternatives.
20. As Yuki the traffic engineer, I want controller parameters, code version, SUMO version, scenario hash, configuration hash, and seed recorded, so that every result can be reproduced.
21. As Yuki the traffic engineer, I want unfinished trips, teleports, standstills, and tail delays included, so that failures cannot disappear from mean metrics.
22. As Yuki the traffic engineer, I want common random numbers and paired comparisons, so that controller differences are measured with less scenario noise.
23. As Yuki the traffic engineer, I want negative and null results retained, so that the evaluation remains scientifically honest.
24. As Yuki the traffic engineer, I want every optional learned-controller action constrained by the same legal action contract as deterministic controllers, so that safety comparisons are meaningful.
25. As a professor, I want a one-command controlled demonstration, so that I can verify the architecture without reconstructing the environment manually.
26. As a professor, I want the Control plane and Synapse layer visibly separated, so that I can verify that the LLM cannot operate traffic lights.
27. As a professor, I want to kill Synapse without changing traffic actions for identical control inputs, so that the authority boundary is demonstrated rather than merely documented.
28. As a professor, I want to drop, delay, duplicate, expire, and corrupt advisory messages, so that failure semantics can be observed.
29. As a professor, I want primary-controller, adviser, message, forecast, and Synapse failures to activate documented recovery behavior, so that graceful degradation is testable.
30. As a professor, I want every requirement claim linked to a planned or completed test, so that feasibility can be verified in one pass.
31. As an AI-engineering recruiter, I want to inspect typed tool and message contracts, so that the project demonstrates production software boundaries.
32. As an AI-engineering recruiter, I want to inspect a golden retrieval and explanation dataset, so that model quality is supported by repeatable evidence.
33. As an AI-engineering recruiter, I want to see retrieval, generation, verification, and fallback as separate trace spans, so that failure classes are observable.
34. As an AI-engineering recruiter, I want latency, token use, estimated cost, and fallback rates reported, so that LLMOps trade-offs are explicit.
35. As an AI-engineering recruiter, I want prompt, provider, model, embedding, and corpus versions recorded, so that regressions can be attributed.
36. As an AI-engineering recruiter, I want a provider-neutral LLM interface, so that the product is not inseparable from one vendor.
37. As an AI-engineering recruiter, I want the retrieval store to be replaceable behind one contract, so that local exact search and pgvector can be compared without changing application logic.
38. As an AI-engineering recruiter, I want CI to evaluate changed prompts and models against golden cases, so that quality changes are visible before release.
39. As a software engineer, I want idempotent scenario submissions, so that retries do not create duplicate expensive runs.
40. As a software engineer, I want bounded run queues and cancellation, so that one request cannot monopolize local resources.
41. As a software engineer, I want structured API errors, so that the React client can distinguish invalid input, capacity limits, provider failure, and missing evidence.
42. As a software engineer, I want run status and progress events, so that the UI can report work without polling every simulation step.
43. As a software engineer, I want immutable event identifiers and correlation identifiers, so that API responses, traces, logs, and evaluation records can be joined.
44. As a software engineer, I want secrets excluded from logs and artifacts, so that a public portfolio does not expose provider credentials.
45. As a data engineer, I want compact Parquet event and KPI data, so that many runs can be compared efficiently with DuckDB.
46. As a data engineer, I want a stable run manifest as the source of truth, so that MLflow or another UI cannot create conflicting run identities.
47. As a data engineer, I want source documents to have content hashes and stable chunk identifiers, so that citations remain traceable across ingestion runs.
48. As a data engineer, I want chronological splits for A4 forecasting, so that future information does not leak into training.
49. As a data engineer, I want real TRANSTU schedule data distinguished from generated road demand, so that the Tunis showcase is not misrepresented.
50. As a model engineer, I want A4 compared with persistence and simple tree baselines, so that model complexity must earn its place.
51. As a model engineer, I want any optional DQN checkpoint selection separated from final test scenarios, so that learned-controller results are not selected on the test set.
52. As a model engineer, I want training and evaluation seeds recorded separately, so that policy learning and policy comparison can be reproduced.
53. As a model engineer, I want safety violations counted independently from reward, so that reward improvements cannot compensate for illegal actions.
54. As a team lead, I want a working Tier 0 baseline preserved throughout development, so that optional AI work cannot leave the project without a demonstrable core.
55. As a team lead, I want control, data/evaluation, and API/Synapse/evaluation to have explicit owners, so that three dependable contributors can work in parallel.
56. As a team lead, I want optional contributors assigned only removable work, so that their unavailability cannot block the reliability slice.
57. As a team lead, I want LangGraph and pgvector introduced only after their entry gates pass, so that framework setup does not replace product progress.
58. As a portfolio owner, I want team outcomes separated from my API/Synapse/evaluation contribution, so that my resume claims are defensible.
59. As a portfolio owner, I want measured placeholders replaced only after evaluation, so that resume bullets never present targets as results.
60. As a portfolio reviewer, I want a short reliability demonstration, architecture explanation, reproduction instructions, selected artifacts, and a failure analysis, so that the project can be assessed quickly and deeply.
61. As a professor, I want each dataset’s row meaning, source, preparation, and limitation stated explicitly, so that I can verify the Data Science reasoning.
62. As a professor, I want EDA findings to produce testable hypotheses before model selection, so that algorithms are justified by evidence.
63. As a professor, I want error analysis to distinguish data, model, communication, scenario, process, and infrastructure causes, so that iteration addresses root causes.
64. As a professor, I want a Fishbone Diagram connected to concrete mitigations and tests, so that Root Cause Analysis changes the prototype plan.

## Implementation Decisions

- The implementation must respect ADR-0001 and the domain meanings of **Reliable AI decision platform**, **Control plane**, and **Synapse layer**.
- The highest acceptance seam is a versioned **run evidence bundle**. A scenario request and approved configuration produce a manifest, immutable messages and decision events, controller actions, fault events, KPI outputs, and evaluation results. Synapse queries and UI views consume that bundle.
- The system is greenfield. Modules will be organized by stable responsibility rather than by framework: scenario execution, SUMO adaptation, control, safety, domain advisers, messaging, evidence storage, evaluation, retrieval, Synapse, API, and presentation.
- One A1 executor owns each signal’s write capability. A parameter-shared policy may be reused across junction executors, but no signal may have multiple writers.
- The SUMO adapter is the only module that can reach TraCI or libsumo actuation APIs. Synapse, retrieval, API handlers, and A2–A5 will not receive that capability.
- A1 accepts current observable state and valid advisory messages, proposes an action through the selected controller, applies deterministic safety and clearance constraints, and records the accepted or rejected outcome with a reason code.
- The required recovery ladder is cooperative Max-Pressure, actuated control, then fixed-time control. If an optional learned policy is enabled for an experiment, it is placed before Max-Pressure. Controller health and recovery cause are part of the decision event.
- Fixed-time, actuated, and cooperative Max-Pressure are mandatory. DQN is optional and can start only after the required evaluation harness is frozen.
- A2, A3, and A5 are deterministic advisers in the required slice. A4 uses a simple forecasting ladder ending at LightGBM plus EWMA/CUSUM residual detection. More learned specialists are not required.
- Advisory messages use a versioned envelope with message identifier, correlation identifier, source agent, destination or topic, creation time, effective simulation time, expiry/TTL, priority class, confidence, payload type, payload version, and provenance.
- Message handling is idempotent by message identifier. Duplicate messages cannot consume budget twice. Expired, malformed, unsupported-version, contradictory, and out-of-order messages produce explicit reason-coded outcomes.
- The initial message transport is in process. Agent logic depends on a publish/read contract rather than transport details so Redis Streams can be introduced later without changing domain behavior.
- Backpressure is bounded. When capacity is exceeded, the system rejects or coalesces advisory work according to a documented policy; it does not block signal control.
- The run manifest is the canonical run identity. It includes run ID, git revision when available, scenario and configuration hashes, SUMO version, controller version, model versions, seeds, status, timing, and artifact references.
- High-volume events and KPI rows use Parquet. DuckDB is the default local analytical interface. A lightweight JSON or SQLite registry records run lifecycle and artifact locations.
- MLflow is optional and may index or reference the canonical manifest; it must not create a second run identity.
- The controlled 4×4 network is the scientific comparison environment. The scenario ladder may begin with one junction and a corridor for smoke tests, but portfolio claims use the frozen controlled benchmark.
- The Tunis showcase imports a selected OSM subnetwork and official TRANSTU scheduled GTFS through the official CKAN source. Imported source versions and hashes are recorded.
- Tunis road demand is generated or calibrated synthetic demand until an observed road-traffic source is separately verified. The API, UI, reports, and portfolio language expose that limitation.
- A4 training uses chronological train/validation/test splits and compares against persistence and simple supervised baselines before any neural forecaster.
- Optional DQN work uses a parameter-shared CPU-first PyTorch implementation and legal action masking. DQN, MAPPO, GNNs, LSTMs, and transformer forecasting are outside the required slice.
- The retrieval corpus is allow-listed and source aware. Initial sources include approved SUMO documentation, traffic-engineering guidance, project requirements, reason-code definitions, and operator playbooks.
- Ingestion records source identity, authority, retrieval date, content hash, parser version, stable chunk ID, section metadata, embedding model, pooling/normalization choice, and vector dimension.
- Development retrieval starts with exact local cosine search behind a retrieval contract. PostgreSQL with pgvector is introduced after provenance and filtering requirements are validated and the hosted read-only product needs durable SQL-backed retrieval.
- Pinecone is not a default dependency. LlamaIndex may supply a connector only if a difficult changing source demonstrates that custom ingestion is insufficient.
- The hosted LLM is accessed through one provider-neutral interface that records provider, model identifier or snapshot, prompt version, latency, token usage, estimated cost, and terminal outcome.
- A deterministic template explainer is mandatory and consumes the same immutable event fields as the generative explainer.
- The bounded Synapse state flow is: classify intent, fetch immutable event/state, retrieve policy evidence, construct a cited answer, verify deterministic claims, and return the answer or abstain.
- LangGraph is limited to the Synapse layer. It is introduced when persisted approval/resume or bounded verify/retry branching is implemented; typed state and domain tests remain independent of LangGraph.
- A what-if scenario tool can only create an approved simulation request. It cannot directly invoke signal actuation or alter an active run.
- The deterministic verifier checks referenced event IDs, reason codes, controller/fallback state, numeric fields, required citations, and unsupported claims before an answer is released.
- LLM-as-judge may provide a secondary evaluation signal, but deterministic checks and human-labelled golden cases are authoritative.
- OpenTelemetry/OpenInference-compatible spans cover retrieval, generation, tools, custom verification, and fallback. Phoenix is the selected visualization/evaluation system after a useful golden dataset exists.
- FastAPI exposes stable product boundaries for scenario submission, run status, run evidence/events, explanation requests, and approved what-if requests.
- Scenario submissions accept idempotency keys. Run jobs are bounded and cancellable. Errors distinguish validation, conflict, capacity, dependency, provider, retrieval, and evidence failures.
- Progress is exposed through server-sent events or WebSockets only where the React client needs it; simulation-step streaming is not a requirement.
- React/Vite presents scenario comparisons, current controller/fallback, advisory messages, decision evidence, citations, explanation status, and trace links. UI polish cannot block course success.
- Local simulation is reproducible and CPU-first. The hosted portfolio serves precomputed run evidence plus live Synapse queries; continuous hosted SUMO training is not promised.
- Containers may package stable services after native toolchain smoke tests pass. Docker orchestration is not evidence by itself and must not precede a working native vertical slice.
- The three critical-path owners are Control plane; scenarios/data/evaluation; and API/Synapse/evaluation. Optional contributors receive dashboard polish, documentation, or extra scenarios.
- The 12-week sequence preserves a working baseline: establish toolchain and baseline evidence first, add measured ML and grounded explanations second, then add LangGraph approval/resume, Tunis showcase, robustness sweeps, and presentation polish.
- Feature freeze occurs before final robustness runs and report generation. Optional features are cut in this order: local LLM, Pinecone or alternate stores, learned A5, neural A4, MAPPO/GNN, Redis/distribution, and civic planning analyses.
- Resume and presentation metrics are populated only from produced evidence bundles. Targets and hypotheses remain labelled as such.

## Testing Decisions

- Tests assert externally observable behavior and produced evidence, not private class structure, framework nodes, or call counts.
- The primary acceptance seam is the run evidence bundle. A test provides a frozen scenario, configuration, seed, controller selection, advisory inputs, and fault schedule, then verifies the manifest, decision events, actions, KPIs, and evaluation report as one coherent result.
- The same frozen scenario and control inputs run with Synapse enabled and disabled must produce identical traffic actions.
- The same scenario seeds are used across fixed-time, actuated, and cooperative Max-Pressure evaluation. An optional DQN uses those same seeds.
- Safety-contract tests propose conflicting, premature, and clearance-truncating actions through the public controller seam and verify that no illegal action is emitted and that a reason-coded rejection is recorded.
- Property-based tests generate legal and illegal phase proposals, timing boundaries, message orderings, TTL values, and duplicate identifiers to exercise invariant behavior beyond hand-written examples.
- Message-failure acceptance tests inject absent, delayed, duplicated, expired, malformed, out-of-order, contradictory, and unsupported-version messages and verify that A1 continues, budgets remain consistent, and outcomes are recorded.
- Recovery acceptance tests make the primary controller, advisers, forecast, message path, retrieval, and hosted model unavailable or unhealthy and verify the documented transition or degradation behavior. If optional DQN is enabled, its failure must transition to Max-Pressure.
- Scenario-run tests verify idempotent submission, bounded capacity, cancellation, restart-safe status, immutable completed evidence, and structured error categories through the public API.
- Reproduction tests rerun the same frozen scenario with the same compatible versions and seed and compare deterministic artifacts or documented numeric tolerances.
- Baseline evaluation tests verify unfinished trips, teleports, standstills, P95/tail metrics, and safety failures are included rather than dropped.
- Statistical report tests verify pairing by seed, controller labels, confidence-interval inputs, hypothesis classification, and the separation of pass/fail requirements, directional hypotheses, and exploratory metrics.
- A4 tests use chronological splits and verify that future rows cannot enter training features. Persistence and simple-tree results must appear beside LightGBM results.
- Ingestion acceptance tests verify stable source and chunk identities, content hashes, authority metadata, parser/embedding versions, deterministic re-ingestion, and deletion/update behavior.
- Retrieval tests use a versioned human-labelled operator-question set and report source hit/recall at `k`, citation correctness, context precision/recall where labelled, and abstention cases.
- Explanation tests verify that every event claim matches immutable fields, required reason codes appear, citations resolve to the recorded corpus version, and unsupported claims are rejected.
- Provider-failure tests inject timeout, rate limit, malformed output, and network failure and verify deterministic template fallback or an explicit abstention.
- Prompt/model regression tests execute the golden dataset for every approved prompt or model change and publish quality, latency, token, cost, and fallback deltas.
- Trace tests verify that one correlation identifier links API request, retrieval, generation, verification, fallback, decision event, run, scenario, and seed without leaking secrets.
- Tunis data tests verify OSM and GTFS source versions, route/stop referential integrity, and clear labelling of scheduled transit versus synthetic road demand.
- React acceptance tests exercise the public API with representative evidence bundles and verify visible controller/fallback state, decision reason, citations, limitations, and errors rather than component implementation.
- The end-to-end reliability demonstration is an automated acceptance suite where possible and a scripted professor demo otherwise: kill Synapse, drop messages, silence an adviser, fail A4, force the controller recovery ladder, remove retrieval support, and change a prompt/model.
- Performance smoke tests measure SUMO step throughput, libsumo versus TraCI batch behavior, memory, artifact volume, retrieval latency, and explanation latency on actual team hardware. DQN update time is measured only if the optional experiment is approved.
- No prior implementation tests exist in the repository. Prior art is the accepted requirements, feasibility reports, evaluation contract, and ADR; the first implementation must establish reusable frozen scenarios and evidence-bundle fixtures.

## Out of Scope

- Real-world traffic-signal deployment or safety certification.
- Claims that simulation results establish Tunis-wide or real-city performance.
- Live observed Tunis road traffic unless a verified source is added through a later decision.
- Translating simulated emergency travel time into lives saved.
- Treating HBEFA emissions estimates as measured air quality.
- LLM, A2, A3, A4, or A5 access to signal actuation.
- Five conversational LLM agents or open-ended autonomous planning.
- LLM fine-tuning.
- A learned model for every domain agent.
- MAPPO, GNN control, LSTM/PatchTST forecasting, and a learned A5 surrogate in the required slice.
- Pinecone, Kafka, Kubernetes, or microservice-per-agent architecture.
- Running Phoenix and LangSmith together.
- Continuous cloud SUMO training or a paid-cloud scaling claim.
- Full Tunis network calibration or generalization.
- Bus-lane, bike-lane, traffic-calming, and broader civic investment recommendations.
- Native mobile applications.
- Automatic changes to an active simulation from a Synapse what-if recommendation.
- DQN as a required deliverable or guaranteed DQN improvement over Max-Pressure.
- Resume metrics populated from targets, estimates, or best episodes.

## Further Notes

- The project succeeds academically without DQN when cooperation, authority, evaluation, failure recovery, credible baselines, and honest analysis are complete.
- The project’s strongest portfolio evidence is the joined chain from explanation to policy source, immutable decision event, controller/configuration, scenario, and seed.
- The first implementation task is a one-day native-Windows SUMO/Python compatibility and throughput smoke test. It must replace current compute estimates with measured capacity.
- The current source tree has no application code, so the first vertical slice should remain small: one scenario, one baseline controller, one manifest, one decision event schema, and one end-to-end acceptance fixture.
- The feature’s primary reviewer setup should not require a hosted LLM. Template explanations and frozen evidence bundles must support offline verification.
- `ready-for-agent` means the design is sufficiently specified to decompose and implement. It does not mean every feasibility-map ticket has been resolved or that measured experiment results exist.
