# CoFlow-5 Synapse — AI agent audit

Read from the repository on 25 September 2026. Claims below name a file or an artifact. Where a measurement is absent, the cell says **not found**.

Glossary constraint from `CONTEXT.md`: **Domain agent** means A1–A5. **Synapse layer** is the only thing this project calls agentic AI. An LLM that writes a signal is outside both terms.

Official Hugging Face leaderboard queries on this date returned an empty list for `open-llm-leaderboard/contents/leaderboard` and for official-benchmark searches of timeseries and retrieval. No benchmark score is invented below. The model already named in `harness/work/12-synapse-agents/contract.json` remains `Qwen/Qwen2.5-1.5B-Instruct`, disabled.

## 1. Agent inventory

| Agent | File path(s) | Observes | Decides | Algorithm actually in the code | Deterministic or learned | Writes SUMO/TraCI | Evidence artifacts |
|---|---|---|---|---|---|---|---|
| A1 | `src/coflow5/control/a1_controller.py`, `control/max_pressure.py`, `control/graph_max_pressure.py`, `control/safety.py`, `control/request_arbitration.py`, `control/recovery.py`, `control/situation_aware.py`. The TraCI write is only in `src/coflow5/sumo_adapter/signal_executor.py` (`trafficlight.setRedYellowGreenState`). | Queues, downstream capacity, neighbour discharge when fresh, advisory requests, pedestrian clearance, forecast messages if present. | One legal phase, or the next rung of the recovery ladder. | Cooperative Max-Pressure: `capacity_weighted_pressure`. Graph-aware adds bounded one-hop discharge, service-age bonus, and a switching penalty (`graph_max_pressure.py`). Safety mask rejects illegal states. | Deterministic rules. `RecoveryMode.OPTIONAL_DQN` exists in `control/recovery.py` and is not a trained model. | **Yes**, only through `SignalExecutor`. `A1FlowController` has no TraCI import. | `harness/work/05-max-pressure/artifacts/decision_events.parquet`, `executed_commands.parquet`. `harness/work/10b-max-pressure-trip-kpis/artifacts/trips.parquet`, `run_kpis.parquet`, `matched-comparison.json`. `harness/work/10f-graph-growth-benchmark/artifacts/decision_events.parquet`, `run_kpis.parquet`, `graph_frames.parquet`. |
| A2 | `src/coflow5/a2/emergency.py` | `RoadPosition` (edge, lane, distance), route, ETA, urgency, downstream capacity, expiry. | A typed `priority_request` on the message board. | Rule checks: finite inputs, authenticated fields, expiry. No route optimizer is implemented in this file. | Deterministic rules. | **No.** | `harness/work/07-a2-a3/artifacts/messages.parquet`, `decision_events.parquet`, `cooperation-kpis.parquet`, `trips.parquet`. |
| A3 | `src/coflow5/a3/multimodal.py` | Crossing state, pedestrian deadline, transit headway / lateness payload. | Pedestrian state and a conditional transit-priority request. An early bus publishes nothing (Row 07 contract, exercised by tests). | Threshold rules. Not a vision model. | Deterministic rules. | **No.** | Same Row 07 artifact set as A2. |
| A4 | `src/coflow5/a4/situation.py` | A chronological series and `SituationEvidence`: residual, EWMA, CUSUM, speed ratio, occupancy, sample age. | A forecast payload and one class: `normal`, `detected_anomaly`, `likely_incident`, `congestion`, `stale_data`, `insufficient_data`. | Persistence and a one-lag autoregression, compared by validation MAE (`evaluate_forecast_ladder`). EWMA/CUSUM thresholds for the class. LightGBM is a slot: if no MAE is passed, the score is `not_available_not_accepted`. | Deterministic given the series. Not a fitted neural model. LightGBM is **not found** as an installed trainer. | **No.** | `harness/work/10-a4-a5/artifacts/forecast-evaluation.parquet`, `decision_events.parquet`, `messages.parquet`, `run_manifest.json`. |
| A5 | `src/coflow5/a5/sustainability.py` | Link-level emission-proxy observations. | Advice: accept, or reject for spillback or a higher-priority request. Label is fixed: `PROXY_LABEL = "SUMO/HBEFA emission proxy — not measured air quality"`. | Arithmetic displacement per link (`compute_link_displacement`). | Deterministic rules. | **No.** | `harness/work/10-a4-a5/artifacts/sustainability-kpis.parquet`. |
| S1 | `src/coflow5/synapse/specialists.py` (`S1ScenarioPlanner`) | A source `run_id` and scenario hash. | A `ScenarioProposal` whose status is only `awaiting-human-approval`, `executed` is `False`, `automatic_approval` is `False`. | Template. `OptionalDraftProvider` exists in `synapse/provider.py` and is not a live model. | Deterministic template. | **No.** | `harness/work/12-synapse-agents/artifacts/scenario_proposals.json`, `synapse_traces.parquet`. |
| S2 | `src/coflow5/synapse/specialists.py` (`S2DecisionExplainer`), `synapse/evidence_reader.py`, `synapse/retrieval.py` | One immutable graph decision and allow-listed text chunks. | A cited answer or an abstention. One retry, then the template. | Exact-token retrieval (`ExactTokenCorpus`). Not MiniLM. Not Qwen. | Deterministic template. | **No.** | `harness/work/12-synapse-agents/artifacts/explanations.json`, `corpus_chunks.parquet`, `corpus_manifest.json`, `golden_results.json`. |
| S3 | `src/coflow5/synapse/specialists.py` (`S3EvidenceAuditor`) | Claims plus event fields or artifact hashes. | `pass` only if every check matches. Otherwise `abstained`. | Field and hash equality. | Deterministic. | **No.** | `harness/work/12-synapse-agents/artifacts/evidence_audits.json`, `golden_cases.json`, `golden_results.json`. |

Message transport for A2–A5 is `src/coflow5/messaging/board.py` (`InProcessMessageBoard`). Topics are declared in `src/coflow5/messaging/envelope.py`. Redis and Kafka are **not found**.

## 2. Agentic classification

| Agent | Class | Present | Not found in this agent |
|---|---|---|---|
| A1 | Hybrid of reactive control and a fixed recovery policy. Not learning. | Memory of the current phase and service age inside one run. Communication by typed advisories. | Forecasting, counterfactuals, uncertainty intervals, causal inference, multi-step planning, tool use, self-evaluation. |
| A2 | Reactive. | Typed request, expiry. | Path search beyond the payload, forecasting, learning, uncertainty, causal claims, tool use. |
| A3 | Reactive. | Headway rule, crossing state. | Vision, forecasting, learning, uncertainty, counterfactuals. |
| A4 | Predictive plus a reactive classifier. | Chronological split, persistence MAE, autoregression MAE, EWMA/CUSUM class. | A trained forecaster, conformal intervals, causal attribution, vision, tool use. The class does not name a cause. |
| A5 | Reactive proxy arithmetic. | Link displacement and a hard proxy label. | A learned emissions model, measured air, uncertainty, causality. |
| S1 | Deliberative only in the weak sense: it drafts a scenario and stops. | Human gate. | Multi-step search, tool use against SUMO, a language model, self-evaluation beyond the schema. |
| S2 | Explanatory. | Retrieval, citation check, one retry, abstention, trace rows. | A live LLM, embeddings, uncertainty on the sentence, causal what-if. |
| S3 | Explanatory self-check of claims. | Pass or abstain against fields and hashes. | A second model, tool use, planning. |

Communication protocol that does exist: `MessageEnvelope` with topic, TTL, idempotency, and disposition (`messaging/envelope.py`, `messaging/board.py`). Synapse does not publish onto that board as a signal writer. It reads frozen artifacts.

## 3. Evidence and evaluation audit

### KPIs that are recorded

- Smoke throughput, peak memory, artifact bytes: `harness/work/01-smoke-test/artifacts/throughput.json`. Fresh run in this pack: TraCI 102 steps, 9321 artifact bytes, peak memory 57905152 bytes, 119.46 steps/s. libsumo 102 steps, 9268 bytes, peak memory 55693312 bytes, 303.30 steps/s. Same seed `20260922`.
- Trip KPIs on the matched seed: `harness/work/10c-evidence-page/artifacts/evidence-page.txt` and `harness/work/10b-max-pressure-trip-kpis/artifacts/matched-comparison.json`. Fixed-time 71/84, mean wait 13.17 s, P95 33.00 s, time loss 1227.58 s. Actuated 84/84, mean wait 10.35 s, P95 16.00 s, time loss 1370.06 s. Max-Pressure 70/84, mean wait 14.21 s, P95 25.00 s, time loss 1480.47 s. One seed. No winner.
- Graph-growth cells: `harness/work/10f-graph-growth-benchmark/artifacts/run_kpis.parquet`, `matched_growth_comparison.json`, `growth_report.md`. 80 deterministic fixture cells. 4 demand scales, 5 seeds, 4 controllers. `growth_report.md` says graph-aware finished more trips than local Max-Pressure in 8/20 paired groups and fewer in 4/20. No significance claim. `native_smoke.json` is a diagnostic, not a matrix member.
- Forecast MAE: `harness/work/10-a4-a5/artifacts/forecast-evaluation.parquet`. The evidence page (`10c`) records simple autoregression validation MAE 0.00, persistence MAE 2.00, LightGBM `not_available_not_accepted` on that fixture. Those MAE values are fixture scores, not a city forecast.
- Synapse golden metrics: `harness/work/12-synapse-agents/artifacts/golden_results.json`. Seven golden cases. Citation validity recorded there as 15/15 on that set. Estimated cost 0.0 USD. Latency is a local `perf_counter` sample, not a hosted SLA.
- Safety: illegal executed commands 0 on the Row 10b traffic run, stated in `evidence-page.txt`.

### Joins that exist

`run_id`, `scenario_hash`, `event_id`, `message_id` are on `src/coflow5/evidence/schemas.py`. Synapse traces add `request_id` and `chunk_id` (`synapse/specialists.py` `TraceRow`). Graph rows add `graph_hash` (`evidence/graph_growth_artifacts.py`). The read-only API preserves those keys (`src/coflow5/api/records.py`).

### Baselines that exist

`src/coflow5/control/baselines.py`: `FixedTimeController`, `ActuatedController`. Compared in `harness/work/04-baselines/artifacts/baseline-comparison.json` and again in Row 10b. Graph-aware vs local Max-Pressure is the fourth controller in `harness/work/10f-graph-growth-benchmark/artifacts/demand_cells.json`.

### Failure injection that exists

Eight message faults in `src/coflow5/failures/injection.py`: absence, drop, delay, duplication, expiry, malformed payload, contradiction, adviser silence. Artifacts: `harness/work/08-failure-injection/artifacts/faults.parquet`, `recovery-audit.json`, `action-sequence-comparison.json`.

Synapse outage is separate, in `src/coflow5/evaluation/failure_artifacts.py`: `synapse_available`, `synapse_killed`, `retrieval_unavailable`, `hosted_provider_unavailable`. `src/coflow5/evaluation/harness.py` records that control action hashes stayed equal across those four states.

Controller failure is the recovery ladder in `src/coflow5/control/recovery.py`: Max-Pressure, then actuated, then fixed-time. Stale neighbour data is a reason code in `src/coflow5/control/graph_max_pressure.py`: `GRAPH_NEIGHBOUR_STALE_LOCAL_ONLY` and `GRAPH_NEIGHBOUR_UNAVAILABLE_LOCAL_ONLY`. A1 then uses local Max-Pressure.

### Not found

- Confidence intervals or conformal sets on a forecast. **Not found.**
- A causal test (instrument, counterfactual contrast with a design-based estimand). **Not found.** The 80 cells are paired by demand scale and seed, and `growth_report.md` refuses a significance claim.
- An ablation table that turns graph terms off one at a time and publishes the delta. The code has a local-only reason code. A published one-term ablation table is **not found**.
- Forecast-quality metrics beyond fixture MAE (coverage, interval width, pinball loss). **Not found.**
- Weather, crash, or measured-air tables inside product evidence. **Not found.**

## 4. Ranked proposals

Ranked by whether the idea can be tested on evidence that already exists, whether it keeps “only A1 writes lights,” and whether it needs a new dependency. Leaderboard scores were unavailable, so model names below are the ones already named in contracts, not a score ranking.

| Rank | Name | Upgrades | New module | Algorithm | Artifact | Evaluation | Risk | Time (estimate, not a measurement) | A1-only / Synapse read-only |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Re-seal stale gates | none new | no new agent | Hash audit | Updated `gate.json` for rows 10, 10b, 10c, 10f, 13 | Contract hash and source hashes match | Low | Days | Yes |
| 2 | Publish the A4 ladder on the page next to Omar | A4, S2 | extend `web/src/evidence.js` to read `forecast-evaluation.parquet` via the API | Persistence vs autoregression MAE already in `a4/situation.py` | A page row citing `forecast-evaluation.parquet` | Omar’s card shows MAE and class, or says the file is absent | Low | One week | Yes. S2 only quotes the file. |
| 3 | Split conformal intervals on A4 residuals | A4 | `src/coflow5/a4/intervals.py` | Split conformal around the persistence residual. No new neural net. | `forecast-intervals.parquet` with coverage on a chronological holdout | Coverage near the nominal rate on the holdout. If coverage misses, the interval is rejected. | Low | Two to three weeks | Yes. Intervals are advice. |
| 4 | Turn S1’s approved JSON into one extra local SUMO cell | S1, A1 | No model. A runner that accepts only `status=approved` proposals. | The existing fixed-time / Max-Pressure runners | A new `run_manifest.json` whose `source_request_id` points at `scenario_proposals.json` | The new cell uses a seed that is not one of the five evaluation seeds. Unapproved proposals produce no run. | Medium | Three weeks | Yes. A person approves. A1 still writes. |
| 5 | Enable the named Qwen draft behind the existing checker | S1, S2, S3 | `synapse/provider.py` implementation, still off in CI | `Qwen/Qwen2.5-1.5B-Instruct` as specified in the Row 12 contract. Retrieval stays exact-token until MiniLM beats it on the golden set. | `golden_results.json` with `generation_version` not equal to the template, plus fallback rows | The seven golden cases still pass. A bad draft is retried once and does not ship. Cost and latency recorded. | Medium | Four to six weeks | Yes. Checker stays in front. |
| 6 | Graph forecaster only if it beats persistence | A4 | `src/coflow5/a4/graph_forecast.py` | Start with the persistence baseline on neighbour links. A GNN (DCRNN or Graph WaveNet) is allowed only as a later candidate. | `forecast-evaluation.parquet` with a third score row | Chronological split. Accept only if validation MAE is lower than persistence. Otherwise `not_accepted`. | High | Six weeks or more | Yes, if it publishes a forecast message and does not set a phase. |
| 7 | Optional trace viewer | S2 | Env-gated sender next to `TraceRow`. Not in `pr.yml`. | LangSmith or any trace sink. Not a model. | The existing `synapse_traces.parquet` remains the source of truth. | CI passes with the key unset. | Low if optional. High if required. | One week once a live draft exists | Yes. |

Rejected for the required path, with the reason:

| Idea | Why it is not next | Keeps the rule? |
|---|---|---|
| MARL / shared DQN / MAPPO on A1 | `RecoveryMode.OPTIONAL_DQN` is unused. Row 15 is blocked. A learned writer needs the mask, the paired seeds, and a Max-Pressure fallback first. | Only if A1 remains the sole writer and DQN can be switched off. Not as the required controller. |
| SHAP for A1 | The score is already `capacity_weighted_pressure` plus three bounded terms in `graph_max_pressure.py`. SHAP would explain a formula that is already printed as a reason code. | Yes, but low value. |
| Causal-inference agent | No design-based contrast exists. S1’s approved scenario is the counterfactual. A new agent that names causes would violate Omar’s rule that a class is not a cause. | Only if it outputs a proposed run, not a cause label. |
| Parallel digital-twin engine | The paired runners already exist (`baseline_runner.py`, `max_pressure_trip_runner.py`, `graph_growth_runner.py`). Another engine is a second writer risk. | Only if it calls those runners. |
| Learned emissions surrogate | Would blur `PROXY_LABEL` in `a5/sustainability.py`. | Only if the artifact keeps the proxy label and cannot override safety. |
| Vision incident detection | **Not found** in A3 or A4. A camera model that raises `likely_incident` would name a cause the class is not allowed to name. | No, unless it is a separate research feed that A4 may ignore. |
| Redis or Kafka | ADR-0003 names them as not the default. The board is in-process (`messaging/board.py`). | A stream does not by itself break the rule, and it is not earned. |
| Bayesian optimization of the 80 cells | The five seeds are evaluation seeds. Tuning on them is forbidden by the Row 10f contract. | Only on a separate design seed. |
| Sim-to-real | Row 14 is not started. No Tunis loop data is in the repo. | The transfer plan must stay labelled synthetic. |

## 5. Three-month roadmap

### Month 1 — seal what is already true

Deliverables: re-gated rows 10, 10b, 10c, 10f, and 13. Omar’s card and the evidence page cite `forecast-evaluation.parquet` when the bundle validates. Native graph smoke rerun recorded in a new `native_smoke.json` without deleting the old failed record.

Gates: those five `gate.json` files show `pass: true`, `openDeltas: 0`, `decidedBy: tests-and-files`, and hashes that match the file bytes on Linux and Windows.

Evidence: updated gates, plus one paragraph in `growth_report.md` that states the new smoke status beside the old WinError 4551 record.

Risk: rewriting a hash to hide a real behavior change. Mitigation: if `graph-growth.sumocfg` or `graph-growth.tls.xml` changed the scenario, the 80-cell fixture is regenerated or explicitly marked as not comparable. Do not start Row 14 in this month.

### Month 2 — two upgrades that stay inside the rules

Deliverables: conformal intervals module behind A4. One approved S1 proposal executed as a single extra local SUMO cell.

Gates: interval coverage test. S1 test that an unapproved proposal creates zero SUMO processes.

Evidence: `forecast-intervals.parquet`. One new run manifest whose `source_request_id` points at `scenario_proposals.json`.

Risk: the interval is overfit to the fixture MAE of 0.00. Mitigation: report coverage on the chronological holdout, and reject the interval if coverage fails.

### Month 3 — one live draft, then stop

Deliverables: Qwen draft behind `OptionalDraftProvider`, still checked by S2 and S3. Golden file shows template fallback when the provider is killed. Portfolio page lists the seven people against the artifact that actually contains their record.

Gates: Row 12 golden cases still pass. Architecture tests still forbid Synapse from importing TraCI. Row 15 stays blocked unless explicitly cut in an ADR.

Evidence: `golden_results.json` with cost, latency, retry count, and `generation_version`.

Risk: a fluent wrong reason. Mitigation: the checker already refuses a draft that disagrees with `reason_code`. Keep that check in front of the model.

Row 14 (OSM plus a dated TRANSTU GTFS file, demand labelled synthetic) is a data pack, not an AI upgrade. It waits until Month 1 seals the gates. It does not add weather, crashes, or measured air.

## 6. Resume bullets

Each bullet uses a number that appears in an artifact named here. Otherwise the token is `[PLACEHOLDER]`.

- **AI evaluation.** Compared fixed-time, actuated, and cooperative Max-Pressure on one matched seed in `harness/work/10b-max-pressure-trip-kpis/artifacts/matched-comparison.json`: actuated finished 84/84 trips, fixed-time 71/84, Max-Pressure 70/84. Reported mean wait, P95 wait, and time loss, and did not claim a winner.
- **ML engineering.** Implemented a chronological forecast ladder in `src/coflow5/a4/situation.py` (persistence, simple autoregression, optional LightGBM). On the Row 10 fixture, autoregression validation MAE was 0.00 and persistence MAE was 2.00. LightGBM was `not_available_not_accepted`.
- **Agent / workflow engineering.** Built eight typed roles. Only `SignalExecutor` writes a SUMO phase. Recovery is Max-Pressure, then actuated, then fixed-time (`src/coflow5/control/recovery.py`).
- **RAG / context engineering.** S2 retrieves exact tokens from an allow-listed corpus and abstains when the chunk is missing (`src/coflow5/synapse/retrieval.py`, `harness/work/12-synapse-agents/artifacts/golden_results.json`). Embedding model: `[PLACEHOLDER]`. Fill it only after MiniLM beats exact-token retrieval on the golden set.
- **LLMOps.** Synapse traces record latency, token counts, and cost (`TraceRow` in `specialists.py`). Hosted-provider-off action hashes stayed equal to the healthy run (`src/coflow5/evaluation/harness.py`). Live model id and dollar cost: `[PLACEHOLDER]` until Qwen is enabled. Template cost in `golden_results.json` is 0.0 USD.
- **Production SWE.** Shipped a read-only FastAPI (`src/coflow5/api`) and a React page (`web/src`) over hash-bound bundles. Health reports `actuates: false`. Pull-request CI runs `tests/architecture` and `tests/api` and does not install SUMO (`.github/workflows/pr.yml`). Hosted uptime: `[PLACEHOLDER]`. Fill it only after `deploy/docker-compose.yml` is actually started. It has not been started.

## 7. Open questions

These are the decisions the audit cannot settle from the files.

**Q1. Re-gate or regenerate Row 10f?** The scene files drifted after the 80-cell fixture. Re-binding the old hashes would claim the new roads are the old experiment.

Recommended answer: regenerate the fixture, keep the old `native_smoke.json` failure next to the new smoke, and do not tune on seeds 11, 23, 37, 41, and 53.

**Q2. Is Month 2 the interval, or the approved what-if run?** Both fit the rules. Doing both slips the month.

Recommended answer: ship the conformal interval first. It does not start SUMO.

**Q3. Does “agentic AI” in the portfolio mean Synapse only?** `CONTEXT.md` says yes. The domain agents are not language models.

Recommended answer: keep that sentence. Call A1–A5 domain agents. Call S1–S3 Synapse.
