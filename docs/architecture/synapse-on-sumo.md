# Synapse on this SUMO simulation

Synapse is the language-model layer for CoFlow-5. It reads a finished SUMO run and speaks only about that record. A1 still writes every signal. Synapse never imports TraCI and never reaches `sumo-gui`.

What exists today is the template version: S1 drafts a scenario and waits, S2 explains one decision with a retrieved citation or abstains, S3 passes or abstains. Qwen is named for later. It is not installed or enabled. The sentences you can already open on the evidence page are that template.

## The system we are building

```text
SUMO
  |
  | TraCI, local Windows only
  v
Domain agents A1–A5          Synapse S1 S2 S3
  A1 writes the light          reads frozen files only
  A2–A5 send typed advice      |
  |                            v
  v                         evidence page and later React
Parquet / JSON evidence --------^
```

Two layers, one simulation.

| Layer | Who | What they may do on a SUMO run |
|---|---|---|
| Control plane | A1 Flow, A2 Emergency, A3 Multimodal, A4 Situation, A5 Sustainability | Observe the sim. A1 alone writes a legal phase. The others publish advice. If advice disappears, A1 continues: Max-Pressure, then actuated, then fixed-time. |
| Synapse | S1 Scenario Planner, S2 Decision Explainer, S3 Evidence Auditor | Read the files that run already wrote. Propose a what-if and wait. Explain one event. Audit the explanation. Stop when the citation is missing. |

The shared model, when it is turned on, is one `Qwen/Qwen2.5-1.5B-Instruct` for S1–S3. Retrieval, when it is earned, is `sentence-transformers/all-MiniLM-L6-v2`. Until those are enabled, the same three roles run on the deterministic template. A missing model is a fallback, not a reason to invent a cause.

## What each Synapse role does with a SUMO run

**S1 Scenario Planner.** Input is a written request plus one source `run_id`. Output is a JSON proposal: demand scale, horizon, source hash. Status stays `awaiting-human-approval`. The proposal is not a signal plan and is not executed. A person approves it before any new SUMO run.

**S2 Decision Explainer.** Input is one question about one `event_id`. It loads that immutable decision (action, reason code, run, scenario, graph). It retrieves allow-listed chunks (ADR, course brief, requirements, design). It drafts an answer. A checker confirms the action, the reason, and the citation are actually in those files. One retry if a provider draft fails the check. If the event or the citation is missing, it abstains. It does not write a new decision.

**S3 Evidence Auditor.** Input is a set of claims about that same event. Every claim must match an event field or a hash-bound artifact. All match: pass, with references. Any miss: abstain, with the failed checks. S3 does not repair the text.

Join keys on every trace: `run_id`, `scenario_hash`, `event_id`, `request_id`, `chunk_id`.

## How this uses the SUMO simulation

1. A local Windows run produces the evidence. The classroom picture is `py -3.11 scripts\watch_sumo.py demo`. The four-junction picture is `py -3.11 scripts\watch_sumo.py graph-growth`. The matched comparison the page lists is the saved 80-cell fixture, not a live SUMO window.
2. A1’s reason code is stored on the event. Examples already in the graph fixture: `GRAPH_NEIGHBOUR_USED`, `MAX_PRESSURE_LOCAL_ONLY`, `BASELINE_POLICY`.
3. Synapse is pointed at that frozen event. On the evidence page, open run `0db24e7b-133e-5b79-ba0c-171f1c0aaf34`. Rosa’s card is S2. An abstention is S2 or S3 refusing to guess.
4. The React page only calls the read-only API. Health stays `actuates: false` and `sumo: false`.

SUMO is the world the domain agents act in. Synapse is the witness of the log.

## Five W’s — agentic patterns and system design

### Who

| Person | Agent they meet | What they are allowed to trust |
|---|---|---|
| Amara | A3 asks for the crossing. A1 keeps it. S2 may read that reason later. | Clearance was not cut. No interview, no crash prevented. |
| David | A1 on the road graph. | Unfinished trips and the tail, not a winner. |
| Chidi | A3 bus request after a gap. | Early bus gets nothing. A timetable is not a live bus. |
| Rosa | S2 and S3. | One cited grant or denial, or an abstention. She does not change the light. |
| Marcus | A2 request. A1 checks the exit. | His time and civilian delay, kept separate. No lives saved. |
| Yuki | A1 health and fallback. | The ladder that actually ran. A frozen screen is not health. |
| Omar | A4 class. S2 may repeat the class and must stop. | Normal, anomaly, likely incident, congestion, stale, or insufficient. The class does not name rain or a crash. |

The builders: Control (Aziz, Fares) own A1. Data (Aymen, Oumayma) own the files. Product (Eya, Ranim) own the page. Synapse is the product layer’s reader, not a seventh signal writer.

### What

Agentic here means cooperation under explicit authority.

Patterns we use:

- **Typed specialists.** A2–A5 and S1–S3 each have one job and one message shape. They do not share a tool that sets a phase.
- **One writer.** Only A1 executes a signal, behind the safety mask.
- **Retrieve, then speak.** S2 may quote a chunk it retrieved. It may not quote a policy that was not retrieved.
- **Check, then release.** A draft that disagrees with the event is not shown. One retry, then the template, then abstain.
- **Human approval.** S1 stops at `awaiting-human-approval`. Approval is a person, not the model.
- **Abstain.** Missing event, missing citation, or a failed audit ends in abstention. Empty fields stay empty.
- **Fallback ladder.** Max-Pressure, then actuated, then fixed-time. Synapse explains that ladder. It does not choose the rung.
- **Trace.** Every stage writes `request_id`, latency, token counts, and cost. Cost stays zero while the template runs.

Patterns we do not use:

- A ReAct loop that calls TraCI.
- Five chatbots debating the phase.
- A central language model as the controller.
- LangSmith, LangGraph, or a hosted model as a required part of the SUMO run. A trace viewer can be added later beside S2. It is not the design of the controller.

### Where

| Piece | Place in the repo | Reaches SUMO? |
|---|---|---|
| A1–A5 and the mask | `src/coflow5/control`, `sumo_adapter` | Yes. Local Windows TraCI only. |
| Evidence files | `harness/work/*/artifacts` | No. They are the log. |
| S1 S2 S3 | `src/coflow5/synapse` | No. |
| Read-only API | `src/coflow5/api` | No. |
| React page | `web/src` | No. It calls `/api`. |
| Later host | `deploy/docker-compose.yml` | No. Images must not install SUMO. |
| Pull-request check | `.github/workflows/pr.yml` | No. SUMO-free on purpose. |

The seam between the two layers is the evidence file, joined on `run_id`. Callers of Synapse need to know only: which run, which event, and that the answer is either cited or an abstention.

### When

| Moment | What runs |
|---|---|
| Now | Domain agents and the template Synapse. The page can show a reason, a citation, or an abstention from files already written. |
| After a person approves an S1 proposal | A new local SUMO run may be started by the existing runner. Synapse still does not start it. |
| When the template gate stays green | One shared Qwen model may draft S1–S3 text. MiniLM may retrieve. The checker stays in front of the draft. |
| Later, optional | A trace viewer such as LangSmith, only as a notebook of those drafts. The pull-request job must not need its key. |
| Not in this design | Row 15 deep Q-learning as the required controller. Weather as a model input. A crash map. Measured air. |

### Why

The professor asked for evidence of who is affected and for decisions that can be checked. A language model is useful only where the record is already true: explaining a reason code, refusing a missing citation, and holding a what-if until a person says yes.

If Synapse wrote the light, Amara’s crossing and Yuki’s recovery would depend on a sentence. The control plane stays deterministic so those guarantees stay testable. Synapse stays read-only so a wrong sentence cannot become a green light.

## Claim flags

No lives saved. No measured air quality. No deployment claim. No winner. No best-episode headline. Personas are research-informed design profiles, not interviews.
