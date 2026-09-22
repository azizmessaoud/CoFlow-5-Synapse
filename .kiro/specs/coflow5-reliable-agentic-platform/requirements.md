# CoFlow-5 Synapse Requirements

**Status:** Final specification baseline  
**Workflow:** Requirements-first  
**Source authority:** `SUMO_forStudents.docx` and `docs/source/course-brief.md`  
**Decision authority:** `docs/adr/0001-reliable-ai-platform-boundary.md`  
**Detailed source:** `.scratch/coflow5-reliable-ai-platform/spec.md`  
**Design Thinking record:** `.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md`

## Project intent

CoFlow-5 Synapse answers the course challenge:

> How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?

The required project is an agentic system because five domain agents observe, decide, communicate, and cooperate under explicit authority. Reinforcement learning is not required. Cooperation, one-writer authority, evaluation, and failure recovery are the core.

The course requires Design Thinking. Empathize, Define, and Ideate are complete. A working controlled Prototype and partial technical Test evidence now exist through gated Row 10c. Multi-seed inference, realistic A4/A5 value ablations, stakeholder validation, Synapse, API/UI, and Tunis remain incomplete. Spec enhancement shall keep the eight User Personas, the human-centred How-might-we, the chosen five-agent idea, and the rejected LLM-as-controller idea.

## Harness traceability

This table binds every stable requirement ID to sealed queue work and the identifiers its acceptance evidence must carry. `run_id` and `scenario_hash` identify the run context; `event_id` identifies immutable decisions, faults, transitions, and explanation targets; `message_id` identifies advisory messages and dispositions. A dash means the key is not created by that requirement, not that downstream evidence may omit its run context.

| Requirement | Queue row(s) | Required join keys in acceptance evidence |
|---|---|---|
| 0 Design Thinking | 01–09 | `run_id`, `scenario_hash` |
| 1 Course outcome | 01, 02, 04, 09 | `run_id`, `scenario_hash` |
| 2 Reproducible runs | 01, 02 | `run_id`, `scenario_hash`, `event_id`, `message_id` |
| 3 Authority and safety | 03 | `run_id`, `scenario_hash`, `event_id`, `message_id` |
| 4 Cooperative A1 | 05, 06, 07 | `run_id`, `scenario_hash`, `event_id`, `message_id` |
| 5 Communication | 06 | `run_id`, `scenario_hash`, `event_id`, `message_id` |
| 6 Emergency | 07, 08, 09 | `run_id`, `scenario_hash`, `event_id`, `message_id` |
| 7 Pedestrian/transit | 07, 09 | `run_id`, `scenario_hash`, `event_id`, `message_id` |
| 8 Situation/sustainability | 09, 10 | `run_id`, `scenario_hash`, `event_id`, `message_id` |
| 9 Recovery | 03, 05, 06, 08 | `run_id`, `scenario_hash`, `event_id`, `message_id` |
| 10 Evaluation | 04, 08, 09 | `run_id`, `scenario_hash`, `event_id`, `message_id` |
| 11 Data lifecycle | 02, 09, 10, 14 | `run_id`, `scenario_hash`, `event_id`, `message_id` |
| 12 Synapse | 12 | `run_id`, `scenario_hash`, `event_id` |
| 13 API/UI | 11, 13 | `run_id`, `scenario_hash`, `event_id`, `message_id` |
| 14 Observability/security | 02, 06, 09, 11, 12 | `run_id`, `scenario_hash`, `event_id`, `message_id` |
| 15 Delivery | 01–09; optional 15 | `run_id`, `scenario_hash`, `event_id`, `message_id` |

Rows 02–10c are gated evidence on the working TraCI path; Row 01 remains transparently blocked on native libsumo policy. Remaining product rows 12, 11, 13, and 14 do not erase the completed controlled evidence slice. Optional DQN remains blocked and cannot change the completion meaning of the required prototype.

## Requirement 0: Design Thinking traceability

**User story:** As a professor, I want to see Empathize, Define, Ideate, Prototype, and Test in order, so that the technical design is justified by stakeholder needs rather than by a preferred algorithm.

### Acceptance criteria

1. THE specification SHALL record Design Thinking Stages 1–3 as completed work, with links to the Empathize pack and the Define/Ideate document.
2. THE specification SHALL keep the eight User Personas Amara, David, Chidi, Rosa, Marcus, Yuki, Maria, and Omar.
3. THE specification SHALL keep the refined How-might-we: serve every person on the network, not only the average car.
4. THE specification SHALL keep the chosen Ideate result: one-writer A1, advisory A2–A5, deterministic safety, and non-actuating Synapse.
5. THE specification SHALL keep rejected ideas rejected, including LLM signal control and five conversational LLM agents.
6. THE Prototype and Test stages SHALL remain incomplete until a SUMO evidence bundle and paired baseline comparison exist.
7. WHEN a requirement is added, THE specification SHALL name the User Persona or How-might-we it serves, or mark it as infrastructure.

## Requirement 1: Course outcome and evidence

**User story:** As a professor, I want a working and reproducible prototype with experiments and honest comparisons, so that I can assess reasoning and evidence instead of technological complexity.

### Acceptance criteria

1. WHEN a reviewer follows the documented local setup, THE SYSTEM SHALL execute at least one controlled SUMO scenario and produce a complete run evidence bundle.
2. WHEN experimental results are reported, THE SYSTEM SHALL compare cooperative A1 against fixed-time and actuated control on matched scenarios and seeds.
3. WHEN a feature or agent is claimed to add value, THE SYSTEM SHALL provide an on/off ablation or state that its value was not established.
4. WHEN an experiment produces a null or negative result, THE SYSTEM SHALL preserve and report that result.
5. THE SYSTEM SHALL distinguish measured results, proposed targets, assumptions, and literature findings.
6. THE SYSTEM SHALL NOT translate simulated emergency delay into lives saved or SUMO/HBEFA values into measured air quality.

## Requirement 2: Reproducible scenario runs

**User story:** As a traffic engineer, I want every run to be reproducible and traceable, so that controller and agent claims can be verified.

### Acceptance criteria

1. WHEN a scenario run is created, THE SYSTEM SHALL assign a unique run identifier.
2. WHEN a run starts, THE SYSTEM SHALL record the SUMO version, source revision when available, scenario hash, configuration hash, controller version, model versions, and all random seeds.
3. WHEN a run completes or fails, THE SYSTEM SHALL produce an immutable status and artifact manifest.
4. WHEN high-volume events are stored, THE SYSTEM SHALL write compact analytical artifacts suitable for Parquet and DuckDB.
5. WHEN the same compatible scenario, configuration, controller, and seed are rerun, THE SYSTEM SHALL reproduce deterministic outputs or document numeric tolerances.
6. IF an artifact is incomplete or corrupted, THEN THE SYSTEM SHALL mark the run invalid rather than silently include it in evaluation.

## Requirement 3: One-writer authority and deterministic safety

**User story:** As Yuki the traffic engineer, I want one clear signal authority and deterministic safety checks, so that cooperation cannot create unsafe signal actions.

### Acceptance criteria

1. THE SYSTEM SHALL permit only A1 Flow to submit signal commands to the SUMO adapter.
2. THE SYSTEM SHALL NOT provide A2, A3, A4, A5, Synapse, API handlers, or the user interface with signal-actuation capability.
3. WHEN any controller proposes an action, THE SYSTEM SHALL validate it through a deterministic legal-action and clearance mask before execution.
4. IF an action would create conflicting greens or truncate required pedestrian clearance, THEN THE SYSTEM SHALL reject it and record a reason code.
5. WHEN multiple junction executors share one controller policy, THE SYSTEM SHALL preserve exactly one writer for each signal.
6. WHEN a human override is requested, THE SYSTEM SHALL apply the same safety mask before execution.

## Requirement 4: Cooperative A1 control

**User story:** As a road user, I want signal decisions to combine current traffic conditions with valid specialist requests, so that one objective does not silently dominate the network.

### Acceptance criteria

1. THE SYSTEM SHALL use cooperative Max-Pressure as the required A1 control method.
2. WHEN A1 selects an action, THE SYSTEM SHALL consider local queues or pressure, current phase, elapsed phase time, downstream capacity, legal actions, and valid advisory requests.
3. WHEN requests conflict, THE SYSTEM SHALL apply the priority order: active safety or in-crossing pedestrian, emergency, pedestrian deadline, conditional late transit, general flow, then sustainability.
4. WHEN multiple requests exist in the same priority tier, THE SYSTEM SHALL rank feasible requests by documented benefit and externality fields.
5. WHEN A1 accepts or rejects a request, THE SYSTEM SHALL record the request identifier, selected action, constraints, and reason code.
6. THE SYSTEM SHALL operate without reinforcement learning.
7. WHERE an optional DQN experiment is enabled, THE SYSTEM SHALL apply the same safety, scenario, seed, logging, and recovery contracts used by required controllers.

## Requirement 5: Agent communication

**User story:** As a system operator, I want agents to exchange bounded and inspectable messages, so that cooperation remains understandable and testable.

### Acceptance criteria

1. THE SYSTEM SHALL provide a typed in-process message board for state, forecasts, alerts, sustainability advice, and formal requests.
2. WHEN an agent publishes a message, THE SYSTEM SHALL include a message identifier, correlation identifier, source, topic, simulation time, creation time, expiry or TTL, priority, confidence, schema version, payload type, and provenance.
3. WHEN A2 or A3 requests priority, THE SYSTEM SHALL complete one request/reply round per decision window.
4. WHEN a duplicate message identifier is received, THE SYSTEM SHALL process it idempotently.
5. IF a message is expired, malformed, unsupported, contradictory, or out of order, THEN THE SYSTEM SHALL ignore or discount it according to a documented rule and record the disposition.
6. IF the message board is empty or unavailable, THEN A1 SHALL continue with local Max-Pressure control.
7. THE SYSTEM SHALL keep transport details behind a message interface so that a later Redis adapter does not change agent logic.

## Requirement 6: Emergency cooperation

**User story:** As Marcus the emergency responder, I want safe corridor priority with visible externalities and recovery, so that an emergency vehicle gains useful passage without leaving uncontrolled harm.

### Acceptance criteria

1. WHEN an emergency vehicle approaches, A2 SHALL publish its position, route or next controlled junctions, ETA, urgency, and request expiry.
2. WHEN downstream space is blocked, A1 SHALL NOT grant a green that cannot provide useful passage solely because an emergency request exists.
3. WHEN a pedestrian is already in a conflicting crossing, THE SYSTEM SHALL preserve clearance before granting the emergency movement.
4. WHEN two emergency requests conflict, THE SYSTEM SHALL apply a deterministic arbitration rule and record both outcomes.
5. AFTER emergency passage, THE SYSTEM SHALL execute a controlled recovery rather than an immediate unsafe phase reset.
6. THE SYSTEM SHALL report emergency travel effects and civilian delay externalities separately.

## Requirement 7: Pedestrian and transit cooperation

**User story:** As Amara and Chidi, I want pedestrian guarantees and conditional transit priority, so that traffic efficiency does not hide unsafe crossings or bus bunching.

### Acceptance criteria

1. WHEN a pedestrian is detected on a crossing, A3 SHALL publish crossing state and required remaining clearance.
2. WHEN pedestrian waiting approaches a configured deadline, A3 SHALL issue an escalation request with age and priority.
3. WHEN a transit vehicle is early or within acceptable headway, A3 SHALL NOT request priority solely because it is a bus.
4. WHEN a transit vehicle is late or part of a large headway gap, A3 MAY issue a bounded priority request.
5. THE SYSTEM SHALL report pedestrian mean, P95, and maximum wait plus clearance truncations.
6. THE SYSTEM SHALL report transit lateness or headway variation plus the externality to other traffic.

## Requirement 8: Situation awareness and sustainability

**User story:** As Omar and Maria, I want trustworthy incident and sustainability advice, so that stale forecasts or network-wide averages do not hide local harm.

### Acceptance criteria

1. A4 SHALL compare persistence and simple supervised baselines before LightGBM is accepted.
2. WHEN A4 publishes a forecast, THE SYSTEM SHALL include horizon, confidence, model version, source time, and expiry.
3. WHEN residual detection indicates an anomaly, A4 SHALL distinguish detected anomaly, likely incident, congestion, stale data, and insufficient data where evidence permits.
4. IF A4 is silent, stale, or unavailable, THEN A1 SHALL continue without forecast input.
5. WHEN A5 publishes sustainability advice, THE SYSTEM SHALL label SUMO/HBEFA values as emission proxies.
6. WHEN sustainability outcomes are evaluated, THE SYSTEM SHALL report link-level displacement near selected residential or school-sensitive links.
7. IF sustainability advice conflicts with spillback or a higher priority tier, THEN A1 SHALL reject or defer it with a reason code.

## Requirement 9: Failure recovery

**User story:** As a professor and operator, I want the system to degrade safely when components fail, so that agentic behavior does not create fragile control.

### Acceptance criteria

1. THE REQUIRED recovery ladder SHALL be cooperative Max-Pressure, actuated control, then fixed-time control.
2. WHERE optional DQN is enabled, its failure SHALL transition to Max-Pressure before the required recovery ladder continues.
3. WHEN a controller transition occurs, THE SYSTEM SHALL record the previous mode, next mode, trigger, simulation time, and health evidence.
4. WHEN advisory messages are absent, delayed, duplicated, expired, malformed, or contradictory, THE SYSTEM SHALL continue legal local control.
5. WHEN A4 fails, THE SYSTEM SHALL mark forecast state unavailable rather than assume normal conditions.
6. WHEN Synapse, retrieval, or the hosted model fails, traffic actions SHALL remain unchanged.
7. WHEN retrieval or generation fails, THE SYSTEM SHALL return a deterministic event explanation or an explicit abstention.

## Requirement 10: Evaluation and error analysis

**User story:** As a data scientist, I want matched experiments and separated failure classes, so that iteration is based on evidence.

### Acceptance criteria

1. THE SYSTEM SHALL evaluate fixed-time, actuated, and cooperative Max-Pressure using common random numbers and paired scenario seeds.
2. THE SYSTEM SHALL report safety, efficiency, emergency, pedestrian, transit, sustainability-proxy, robustness, and reproducibility metrics.
3. THE SYSTEM SHALL include unfinished trips, teleports, standstills, and tail metrics rather than silently remove them.
4. THE SYSTEM SHALL classify failures as control safety, poor traffic outcome, communication, forecast, retrieval, explanation, provider, API, persistence, or presentation failures.
5. THE SYSTEM SHALL support agent on/off ablations and communication loss or delay sweeps.
6. THE SYSTEM SHALL NOT use a best training episode as the headline comparison.
7. WHEN multiple hypotheses are tested, THE SYSTEM SHALL document the correction or exploratory status used.
8. WHEN a proposed feature does not improve its intended outcome, THE SYSTEM SHALL retain the result and permit the feature to be cut.

## Requirement 11: Data lifecycle

**User story:** As a data scientist, I want each dataset to have an explicit unit, source, preparation rule, and limitation, so that model and evaluation leakage can be detected.

### Acceptance criteria

1. THE SYSTEM SHALL define separate schemas for state rows, decision rows, message rows, trip rows, forecast rows, run-KPI rows, corpus chunks, and golden evaluation cases.
2. WHEN A4 data is prepared, THE SYSTEM SHALL use chronological train, validation, and test splits.
3. WHEN scalers, imputers, or feature selectors are fitted, THE SYSTEM SHALL fit them using training data only.
4. WHEN warm-up data is removed, THE SYSTEM SHALL apply a predeclared rule and retain all failures and unfinished trips.
5. WHEN Tunis data is used, THE SYSTEM SHALL distinguish OSM network data, official TRANSTU scheduled GTFS, and synthetic or calibrated road demand.
6. THE SYSTEM SHALL record data source versions, retrieval dates, hashes, transformations, and limitations.

## Requirement 12: Synapse grounding and evaluation

**User story:** As Rosa the operator, I want supported explanations of immutable decisions, so that generated text remains auditable.

### Acceptance criteria

1. THE Synapse layer SHALL be non-actuating and read only from approved evidence and retrieval interfaces.
2. WHEN an operator asks about a decision, THE SYSTEM SHALL classify intent, fetch the immutable event, retrieve policy evidence, generate or template an answer, verify claims, and answer or abstain.
3. WHEN a generated answer states an event fact, THE SYSTEM SHALL verify it against immutable fields before release.
4. WHEN a generated answer states a policy claim, THE SYSTEM SHALL require a citation to an allow-listed source chunk.
5. WHEN support is insufficient, THE SYSTEM SHALL abstain or return structured event facts.
6. THE SYSTEM SHALL evaluate retrieval recall at k, citation validity, event consistency, reason-code coverage, abstention, latency, token use, estimated cost, and fallback rate.
7. THE SYSTEM SHALL treat LLM-as-judge as a secondary signal, not the sole reference.
8. THE SYSTEM SHALL provide a deterministic template fallback that works without a hosted LLM.

## Requirement 13: API and operator interface

**User story:** As an operator or portfolio reviewer, I want a stable interface for runs and explanations, so that I can inspect the system without reading internal code.

### Acceptance criteria

1. THE SYSTEM SHALL expose typed operations for scenario submission, run status, run evidence, run events, cancellation, explanations, and approved what-if requests.
2. WHEN a scenario is submitted with an idempotency key, THE SYSTEM SHALL avoid duplicate runs.
3. THE SYSTEM SHALL bound concurrent jobs and return a structured capacity error when the queue is full.
4. THE SYSTEM SHALL distinguish validation, conflict, capacity, dependency, provider, retrieval, and evidence errors.
5. THE operator interface SHALL show active controller and recovery state, agent messages, decisions and reason codes, comparisons, citations, and known limitations.
6. THE hosted portfolio SHALL use precomputed SUMO evidence and MAY provide live bounded Synapse queries.
7. THE SYSTEM SHALL NOT promise continuous cloud training.

## Requirement 14: Observability and security

**User story:** As an AI engineer, I want joined traces, versioned configurations, and protected credentials, so that failures and regressions can be diagnosed safely.

### Acceptance criteria

1. WHEN a Synapse request is processed, THE SYSTEM SHALL trace event retrieval, document retrieval, generation, verification, fallback, latency, and terminal outcome.
2. THE SYSTEM SHALL correlate API requests, traces, messages, decisions, runs, scenarios, and seeds.
3. THE SYSTEM SHALL record corpus, parser, embedding, prompt, provider, model, and evaluator versions.
4. THE SYSTEM SHALL NOT write credentials, secrets, or unnecessary personal information to logs, prompts, traces, or public artifacts.
5. WHEN an approved prompt, model, embedding, or corpus changes, THE SYSTEM SHALL execute the golden regression set and report quality, latency, and cost deltas.

## Requirement 15: Delivery boundaries

**User story:** As the team lead, I want the critical path protected from optional complexity, so that three dependable contributors can deliver the course outcome in 12 weeks.

### Acceptance criteria

1. THE critical path SHALL contain three workstreams: Control plane; scenarios/data/evaluation; and API/Synapse/evaluation.
2. THE first implementation task SHALL measure native Windows SUMO/Python compatibility and simulation throughput.
3. THE team SHALL preserve a working fixed-time and actuated baseline while adding cooperation.
4. THE team SHALL freeze the cooperative Max-Pressure evidence slice before adding optional RL.
5. IF schedule or compute capacity is insufficient, THEN THE team SHALL cut optional DQN/MAPPO, local LLM serving, learned A5, neural forecasting, Redis, and civic planning analyses before safety, authority, evaluation, or failure recovery.
6. THE required prototype SHALL remain verifiable without the hosted LLM.

