---
inclusion: always
---

# CoFlow-5 Synapse — product steering

Use this steering file with the course brief, glossary, and ADR.

## Course authority

The course brief is `docs/source/course-brief.md`, transcribed from `SUMO_forStudents.docx`.

Challenge:

> How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?

Required outcomes: a working prototype, experiments under different traffic conditions, a baseline comparison, and data-driven strengths and limitations. Evidence matters more than technological complexity.

## Product identity

CoFlow-5 Synapse is a Reliable AI decision platform for urban traffic simulation.

- Five domain agents cooperate.
- Only A1 Flow can change traffic signals.
- Required A1 method: cooperative Max-Pressure.
- Synapse retrieves evidence and explains immutable decisions. It cannot actuate SUMO.
- Reinforcement learning is optional and cannot block delivery.

## Language

Follow `CONTEXT.md`.

- User Persona, User Journey, Evidence, Possible Solution, and Claim flag belong to the Empathize pack.
- Control plane owns safety-critical signal decisions.
- Synapse layer is non-actuating.
- Do not call this an LLM traffic controller or a five-chatbot system.

## Authority and recovery

Priority when requests conflict:

1. active safety or in-crossing pedestrian
2. emergency
3. pedestrian deadline
4. conditional late transit
5. general flow
6. sustainability

Required recovery ladder:

`cooperative Max-Pressure -> actuated -> fixed-time`

Optional DQN, if enabled later, fails into Max-Pressure first.

## Honesty rules

- Personas are research-informed, not interview-validated.
- Simulation is not deployment evidence.
- HBEFA outputs are emission proxies, not measured air quality.
- Simulated emergency time is not lives saved.
- Never headline a best training episode.
- Resume metrics stay empty until measured.

## Spec enhancement with Kiro

Canonical spec files:

- `.kiro/specs/coflow5-reliable-agentic-platform/requirements.md`
- `.kiro/specs/coflow5-reliable-agentic-platform/design.md`
- `.kiro/specs/coflow5-reliable-agentic-platform/tasks.md`

When enhancing specs, keep ADR-0001. Do not move the LLM into the Control plane. Do not make DQN required. Prefer stronger acceptance tests, clearer interfaces, and smaller implementation tasks over new agents or frameworks.
