# Implementation tasks

**Spec:** CoFlow-5 Reliable Agentic Platform  
**Goal:** implement the course prototype from `docs/source/course-brief.md` without making reinforcement learning required.

Mark a task complete only when its acceptance checks pass. Keep a working baseline throughout.

Design Thinking Stages 1–3 are already done. Do not re-invent User Personas or replace the chosen architecture. These tasks are Stage 4 Prototype and Stage 5 Test.

- [ ] Keep `design-thinking.md` linked from the README and from reports.
- [ ] Map each implemented feature to a User Persona or How-might-we.
- [ ] Keep rejected ideas rejected: LLM signal control, five chatbots, required RL.
- [ ] Keep `AGENT_GUIDE.md` as the router. Execute work from `harness/queue.tsv`, not from chat memory.
- [ ] Gate each row with `harness/work/<id>/gate.json`. Do not self-assess done.

## 0. Harness

- [ ] Seal `harness/queue.tsv`.
- [ ] Write `contract.json` before product code for that row.
- [ ] Stop on `harness/BLOCKED`, stuck loops, or context blow-up.
- [ ] Join product artifacts on `run_id`.
- [ ] Follow https://github.com/flyrank-bih/harness-engineering-playbook as pattern, not as Shopify code.
- [ ] Follow https://github.com/ayghri/i-have-adhd for operator-facing answers.

## 1. Toolchain and smoke test

- [ ] Pin Python 3.11 and one exact SUMO release.
- [ ] Record `SUMO_HOME`, package versions, and `traci.__file__`.
- [ ] Run one small headless SUMO scenario and one `sumo-gui` diagnosis scenario.
- [ ] Measure TraCI versus libsumo throughput, memory, and artifact size on team hardware.
- [ ] Replace compute estimates with the measured smoke-test numbers.

_Check:_ a reviewer can reproduce the smoke test from the documented command.

## 2. Run evidence bundle

- [ ] Define run, scenario, configuration, and seed identifiers.
- [ ] Write a run manifest with versions, hashes, status, timings, and artifact paths.
- [ ] Store compact Parquet event and KPI artifacts.
- [ ] Add DuckDB queries for run comparison.
- [ ] Invalidate incomplete or corrupted runs.

_Check:_ one frozen scenario produces a complete evidence bundle.

## 3. SUMO adapter and safety mask

- [ ] Isolate TraCI/libsumo behind an observation and command adapter.
- [ ] Give only the signal executor write access to traffic lights.
- [ ] Encode legal phase transitions, minimum green, yellow/all-red, and pedestrian clearance.
- [ ] Reject conflicting greens and truncated clearance with reason codes.

_Check:_ illegal proposed actions never appear as executed commands.

## 4. Baseline controllers

- [ ] Implement fixed-time control.
- [ ] Implement actuated control.
- [ ] Evaluate both on matched scenarios and seeds.
- [ ] Report unfinished trips, teleports, standstills, and tail delay.

_Check:_ baseline comparison exists before any specialist or learned controller claim.

## 5. Cooperative A1 Max-Pressure

- [ ] Implement Max-Pressure using local queues or pressure and legal actions.
- [ ] Include downstream blocking where configured.
- [ ] Record accepted action, rejected alternatives, and reason codes.
- [ ] Keep A1 as the only signal writer.

_Check:_ cooperative Max-Pressure runs without A2–A5 and remains the recovery mode.

## 6. Typed message board

- [ ] Implement the message envelope from the design document.
- [ ] Support topics for state, forecast, alerts, eco, requests, replies, and health.
- [ ] Enforce TTL, idempotency, confidence, and disposition logging.
- [ ] Keep transport behind an interface so Redis can be added later.

_Check:_ duplicate, expired, malformed, and missing messages cannot stop local A1 control.

## 7. A2 emergency specialist

- [ ] Publish expiring corridor-priority requests with ETA, urgency, benefit, and externality.
- [ ] Preserve in-crossing pedestrian clearance.
- [ ] Apply deterministic two-emergency arbitration.
- [ ] Recover after passage instead of an unsafe phase reset.

_Check:_ emergency on/off ablation reports emergency travel and civilian delay separately.

## 8. A3 pedestrian and transit specialist

- [ ] Publish crossing state and remaining clearance.
- [ ] Escalate pedestrian wait deadlines.
- [ ] Request transit priority only when lateness or headway evidence supports it.
- [ ] Report pedestrian waits and transit regularity.

_Check:_ A3 cannot truncate an active crossing and cannot preempt for an early bus.

## 9. A4 situation awareness

- [ ] Build chronological train, validation, and test splits.
- [ ] Compare persistence and a simple tree baseline before LightGBM.
- [ ] Add EWMA/CUSUM residual detection.
- [ ] Publish horizon, confidence, source time, expiry, and model version.
- [ ] Continue A1 when A4 is silent or stale.

_Check:_ forecast leakage tests fail if future rows enter training.

## 10. A5 sustainability advice

- [ ] Compute advisory hot-spot or weight messages from SUMO/HBEFA proxies.
- [ ] Label outputs as emission proxies.
- [ ] Report displacement on selected residential or school-sensitive links.
- [ ] Reject advice during spillback or higher-priority conflicts.

_Check:_ A5 cannot override safety, pedestrian clearance, or emergency recovery.

## 11. Evaluation harness

- [ ] Create matched experiment cells for controller, demand, incident, communication fault, and seed.
- [ ] Support agent on/off ablations.
- [ ] Classify requirement, directional, and exploratory metrics.
- [ ] Preserve null and negative results.
- [ ] Never headline a best episode.

_Check:_ a professor can read one evaluation report and see strengths, limitations, and failure classes.

## 12. Failure recovery

- [ ] Implement `Max-Pressure -> actuated -> fixed-time`.
- [ ] Record controller transitions and health evidence.
- [ ] Inject message, adviser, forecast, controller, and Synapse faults.
- [ ] Keep optional DQN off the required path.

_Check:_ the scripted reliability demo passes without a learned controller.

## 13. Retrieval corpus

- [ ] Allow-list SUMO docs, course brief, requirements, reason codes, and operator playbooks.
- [ ] Store source identity, content hash, parser version, and stable chunk IDs.
- [ ] Embed with a recorded sentence-transformer configuration.
- [ ] Start with exact local cosine search.

_Check:_ re-ingestion keeps stable chunk identity for unchanged content.

## 14. Synapse explanations

- [ ] Implement classify, fetch event, retrieve policy, draft, verify, answer or abstain.
- [ ] Add a deterministic template fallback.
- [ ] Verify event facts against immutable fields.
- [ ] Require citations for policy claims.
- [ ] Keep Synapse unable to reach the signal executor.

_Check:_ killing Synapse does not change traffic actions for the same control inputs.

## 15. API and operator view

- [ ] Expose typed run, evidence, cancellation, explanation, and approval operations.
- [ ] Add idempotency keys, bounded queues, and structured errors.
- [ ] Show controller/recovery state, messages, reason codes, citations, and limitations.
- [ ] Serve hosted views from precomputed evidence.

_Check:_ the required prototype remains usable without a hosted LLM.

## 16. Observability and golden evals

- [ ] Trace retrieval, generation, verification, fallback, latency, and cost.
- [ ] Join traces to run, event, scenario, and seed identifiers.
- [ ] Create a versioned golden operator-question set.
- [ ] Gate prompt, model, embedding, and corpus changes on that set.

_Check:_ changing a prompt produces a visible regression report.

## 17. Tunis showcase, after the grid is frozen

- [ ] Import a bounded OSM subnetwork.
- [ ] Import official TRANSTU scheduled GTFS and record source version.
- [ ] Generate labelled synthetic or calibrated road demand.
- [ ] Keep the 4×4 grid as the scientific comparison.

_Check:_ reports distinguish scheduled transit data from synthetic road demand.

## 18. Optional DQN experiment, after feature freeze

- [ ] Implement the same controller interface, safety mask, scenarios, and seeds.
- [ ] Use replay, target network, action masking, and separate train/eval seeds.
- [ ] Fail into Max-Pressure.
- [ ] Publish a comparison or an honest null result.

_Check:_ the course prototype still passes if this task is never started.

## Out of scope unless a later spec change is accepted

- LLM signal control
- five conversational LLM agents
- required MAPPO, GNN, or local LLM serving
- Pinecone, Kafka, or Kubernetes
- lives-saved or measured air-quality claims
- live Tunis road-traffic deployment
