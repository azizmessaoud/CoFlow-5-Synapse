# CoFlow-5 Synapse

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
| Delivery | 12 weeks, three critical-path contributors, CPU-first |

ADR: [`docs/adr/0001-reliable-ai-platform-boundary.md`](docs/adr/0001-reliable-ai-platform-boundary.md)

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
| Kiro requirements | [`.kiro/specs/coflow5-reliable-agentic-platform/requirements.md`](.kiro/specs/coflow5-reliable-agentic-platform/requirements.md) |
| Kiro design | [`.kiro/specs/coflow5-reliable-agentic-platform/design.md`](.kiro/specs/coflow5-reliable-agentic-platform/design.md) |
| Kiro tasks | [`.kiro/specs/coflow5-reliable-agentic-platform/tasks.md`](.kiro/specs/coflow5-reliable-agentic-platform/tasks.md) |
| Long-form spec | [`.scratch/coflow5-reliable-ai-platform/spec.md`](.scratch/coflow5-reliable-ai-platform/spec.md) |
| Portfolio / stack | [`docs/architecture/coflow5-synapse-portfolio-design.md`](docs/architecture/coflow5-synapse-portfolio-design.md) |
| Project context | [`coflow5-project-context.md`](coflow5-project-context.md) |

## Implementation status

Not implemented. The first build task is a native SUMO and Python 3.11 smoke test on Windows.
