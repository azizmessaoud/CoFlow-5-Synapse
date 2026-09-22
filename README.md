# CoFlow-5 Synapse

> **This branch is the TraCI prototype/scaffold**, parked off `main` so that work is not lost.
> `main` stays the spec and Design Thinking focus. Row 01 (`libsumo`) is still blocked by Windows. Rows 02–09 ran through TraCI.
> Watch the map: `py -3.11 scripts\watch_sumo.py smoke` then press Play. That is SUMO, not yet live A1.

A reliable AI decision platform for urban traffic simulation.

Five domain agents cooperate in Eclipse SUMO. Only **A1 Flow** can change traffic lights. The required controller is cooperative **Max-Pressure**. The **Synapse** layer retrieves evidence and explains immutable decisions. It never actuates signals.

This repository holds the **settled specifications** for Kiro enhancement and later implementation. It is not yet a running simulator.

The course requires **Design Thinking**. Stages 1–3 are complete. Prototype and Test are specified, not executed.

| Stage | Status | Start here |
|---|---|---|
| 1 Empathize | Done | [`coflow5-empathize-pack.md`](coflow5-empathize-pack.md) |
| 2 Define | Done | [`coflow5-define-ideate.md`](coflow5-define-ideate.md) |
| 3 Ideate | Done | [`coflow5-define-ideate.md`](coflow5-define-ideate.md) |
| 4 Prototype | Planned | [`.kiro/specs/coflow5-reliable-agentic-platform/tasks.md`](.kiro/specs/coflow5-reliable-agentic-platform/tasks.md) |
| 5 Test | Planned | evaluation contract in the Kiro requirements |

Kiro record of those steps: [`.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md`](.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md).

Agents read [`AGENT_GUIDE.md`](AGENT_GUIDE.md) first. Harness: [`docs/harness/how-it-works.md`](docs/harness/how-it-works.md). Queue: [`harness/queue.tsv`](harness/queue.tsv).

Pattern: [harness-engineering-playbook](https://github.com/flyrank-bih/harness-engineering-playbook). Output style: [i-have-adhd](https://github.com/ayghri/i-have-adhd).

## Course brief

Source: `SUMO_forStudents.docx`, transcribed in [`docs/source/course-brief.md`](docs/source/course-brief.md).

Challenge:

> How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?

Required outcomes:

- a working prototype
- experiments under different traffic conditions
- comparison with an appropriate baseline
- data-driven strengths and limitations

Evidence matters more than technological complexity.

## Settled decisions

| Decision | Choice |
|---|---|
| Product | Reliable AI decision platform, not an LLM traffic controller |
| Agents | A1 Flow, A2 Emergency, A3 Multimodal, A4 Situation, A5 Sustainability |
| Authority | Only A1 writes signals; A2–A5 ask; Synapse explains |
| Required control | Cooperative Max-Pressure, with deterministic safety |
| Baselines | Fixed-time and actuated |
| RL | Optional DQN after the cooperative core is frozen |
| Evaluation | Paired seeds, ablations, failure injection, honest null results |
| Data | Controlled 4×4 benchmark plus a Tunis OSM + TRANSTU GTFS showcase |
| Delivery | 12 weeks, six named builders, three pairs, one sealed queue row, CPU-first |

ADRs: [`docs/adr/0001-reliable-ai-platform-boundary.md`](docs/adr/0001-reliable-ai-platform-boundary.md), [`docs/adr/0002-six-builders-one-queue-row.md`](docs/adr/0002-six-builders-one-queue-row.md), [`docs/adr/0003-cicd-devops-mlops.md`](docs/adr/0003-cicd-devops-mlops.md)

Professor-facing book: [`CoFlow-5_Final_Project_Book.md`](CoFlow-5_Final_Project_Book.md). Wednesday 23 September 2026 is **proxy validation**, not stakeholder interviews.

## Use these files in Kiro

Open this repository in Kiro and use the spec at:

```text
.kiro/specs/coflow5-reliable-agentic-platform/
  design-thinking.md
  requirements.md
  design.md
  tasks.md
```

Steering:

```text
.kiro/steering/product.md
CONTEXT.md
```

Ask Kiro to enhance the final specs from this baseline **without dropping Design Thinking Stages 1–3**. Keep these constraints:

1. Do not put an LLM in the Control plane.
2. Do not make reinforcement learning required.
3. Keep one signal writer and the recovery ladder `Max-Pressure -> actuated -> fixed-time`.
4. Keep Claim flags: no lives saved, no measured air quality, no best-episode headlines.
5. Prefer stronger acceptance criteria and smaller tasks over new frameworks.

Copy this prompt into Kiro: [`.kiro/prompts/enhance-specs-trajectory.md`](.kiro/prompts/enhance-specs-trajectory.md).

Kiro must follow the harness (queue, contracts, `gate.json`, exit codes) and the i-have-adhd output rules in `.kiro/steering/output-style.md`.

## Document map

| Need | File |
|---|---|
| Course brief | [`docs/source/course-brief.md`](docs/source/course-brief.md) |
| Design Thinking steps we did | [`.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md`](.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md) |
| Empathize pack | [`coflow5-empathize-pack.md`](coflow5-empathize-pack.md) |
| Define and Ideate | [`coflow5-define-ideate.md`](coflow5-define-ideate.md) |
| Full Stage 1–3 book | [`CoFlow-5_System_Requirements_Book.md`](CoFlow-5_System_Requirements_Book.md) |
| Glossary | [`CONTEXT.md`](CONTEXT.md) |
| Architecture decision | [`docs/adr/0001-reliable-ai-platform-boundary.md`](docs/adr/0001-reliable-ai-platform-boundary.md) |
| Later CI/CD and MLOps | [`docs/adr/0003-cicd-devops-mlops.md`](docs/adr/0003-cicd-devops-mlops.md) |
| How to run SUMO | [`docs/how-to-run-sumo.md`](docs/how-to-run-sumo.md) |
| Kiro requirements | [`.kiro/specs/coflow5-reliable-agentic-platform/requirements.md`](.kiro/specs/coflow5-reliable-agentic-platform/requirements.md) |
| Kiro design | [`.kiro/specs/coflow5-reliable-agentic-platform/design.md`](.kiro/specs/coflow5-reliable-agentic-platform/design.md) |
| Kiro tasks | [`.kiro/specs/coflow5-reliable-agentic-platform/tasks.md`](.kiro/specs/coflow5-reliable-agentic-platform/tasks.md) |
| Long-form spec | [`.scratch/coflow5-reliable-ai-platform/spec.md`](.scratch/coflow5-reliable-ai-platform/spec.md) |
| Portfolio / stack | [`docs/architecture/coflow5-synapse-portfolio-design.md`](docs/architecture/coflow5-synapse-portfolio-design.md) |
| Project context | [`coflow5-project-context.md`](coflow5-project-context.md) |

## Later deploy (not the smoke test)

Hosted product is **read-only FastAPI + React over tagged evidence**. No SUMO in those containers. See [ADR-0003](docs/adr/0003-cicd-devops-mlops.md) and [`deploy/README.md`](deploy/README.md).

- PR CI (no SUMO): `.github/workflows/pr.yml`
- Eval CI (SUMO-capable runner only): `.github/workflows/eval.yml`
- Local read-only demo: `cd deploy && docker compose up --build`

Native Windows smoke remains `py -3.11 scripts\run_native_smoke.py`. Docker is not a row-01 requirement.

## How to run SUMO

See [`docs/how-to-run-sumo.md`](docs/how-to-run-sumo.md). Short version:

```powershell
$env:SUMO_HOME = "C:\Program Files (x86)\Eclipse\Sumo"
$env:Path = "$env:SUMO_HOME\bin;" + $env:Path
cd C:\Users\dell\Downloads\sumo
py -3.11 scripts\watch_sumo.py smoke
```

Press Play. That window is the map, not live A1. Headless A1: `py -3.11 scripts\generate_max_pressure_artifacts.py`. Live A1 window: `py -3.11 scripts\watch_sumo.py a1`.

## Implementation status

Row 01 is still ungated (`libsumo` blocked). Rows **02–09** are gated on TraCI. Rows 10–14 are todo. Row 15 stays blocked. Do not use `scripts\run_native_smoke.py` as the daily demo until an admin allows `libsumo`.
