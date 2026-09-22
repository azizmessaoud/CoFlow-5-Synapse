# Design Thinking record

**Course requirement:** follow Design Thinking to understand the problem, identify stakeholders and needs, explore solutions, build a prototype, and test ideas (`docs/source/course-brief.md`, from `SUMO_forStudents.docx`).

**Framework used:** Interaction Design Foundation stages — Empathize, Define, Ideate, Prototype, Test (Teo Yu Siang and the Interaction Design Foundation). This file records what CoFlow-5 **did**, not a reprint of the teaching article.

**Status**

| Stage | Status | Canonical output |
|---|---|---|
| 1 Empathize | Done | `coflow5-empathize-pack.md` |
| 2 Define | Done | `coflow5-define-ideate.md` Stage 2 |
| 3 Ideate | Done | `coflow5-define-ideate.md` Stage 3 |
| 4 Prototype | Working controlled prototype; product expansion incomplete | Gated Rows 02–10c plus `.kiro/specs/coflow5-reliable-agentic-platform/tasks.md` |
| 5 Test | Technical tests and one-seed matched evidence run; human and multi-seed validation incomplete | Gated evidence packs plus evaluation contract in requirements and design |

Full narrative with requirements IDs: `CoFlow-5_System_Requirements_Book.md`.

Kiro must keep this sequence. Do not skip Empathize/Define/Ideate when enhancing specs. Do not treat the full portfolio, multi-seed inference, or stakeholder validation as complete.

**Proxy validation:** a team or professor walkthrough of research-informed User Personas is not an interview. 23 September 2026 is labelled proxy validation.

---

## Stage 1 — Empathize

**Prompt we executed:** understand who suffers from congestion, what they need, and what sits under a traffic-management product. Consult experts, map journeys, and do not assume “smarter lights for cars” is enough.

**How we Empathized**

| Method | What we did |
|---|---|
| Consult experts | Literature and product docs: DfT TAG, FHWA, SCATS, Surtrac, RESCO, T-REX, CoLLMLight, AgentSUMO |
| Observe | User Journeys for eight User Personas |
| Immerse | SUMO as a stand-in street environment, not a substitute for interviews |
| Set aside assumptions | Evidence trail and Claim flags |

**User Personas (research-informed, not interview-validated)**

| ID | User Persona | Need |
|---|---|---|
| P1 | Amara | Enough time to finish crossing |
| P2 | David | Predictable journeys, not only shorter ones |
| P3 | Chidi | Regular bus arrivals, not bunching |
| P4 | Rosa | See why priority was granted or denied |
| P5 | Marcus | Safe emergency passage and recovery afterwards |
| P6 | Yuki | Automation she can diagnose, override, and disable |
| P7 | Maria | Cleaner arterials that do not dump harm on her street |
| P8 | Omar | Alerts that say what is wrong, why, and how much to trust them |

The IMATM report’s Tunis names (Amine, Karim, Nadia, Hichem, Emna, Leila) are an alternate roster. Map them. Do not stack them as extra people.

**Empathize outputs Kiro must preserve**

- User Personas
- User Journeys
- Evidence
- Possible Solution
- Claim flags: no lives saved from simulation, no measured air quality, no “1.5× perceived wait”, no interview-validated persona claim

---

## Stage 2 — Define

**Prompt we executed:** organise Empathize findings into human-centred problems. The problem is not “cut average vehicle delay.”

**Human-centred problem statement**

Street users — pedestrians, drivers, bus riders, emergency crews, and the people who run the network — need signal control that treats their distinct needs as first-class objectives with visible trade-offs, because today each need is handled by a separate mechanism that optimizes vehicle throughput, hides who pays for whom, and degrades silently when conditions or communications fail.

**Course How-might-we**

> How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?

**Refined How-might-we**

> How might we do that for every person on the network — walker, rider, driver, paramedic, operator, resident — not only the average car?

**Core problems carried into Ideate**

1. Efficiency claims must be earned against Max-Pressure, not asserted.
2. Emergency, pedestrian, transit, emissions, and incidents are not co-arbitrated today.
3. Operators cannot diagnose, override, or audit silent degradation.
4. Mean-delay optimization hides starvation and displacement.
5. Communication, sensors, and agents fail; perfect-data evaluation is not enough.

---

## Stage 3 — Ideate

**Prompt we executed:** generate many ideas, then cut. Techniques used: Brainstorm/Brainwrite, Worst Possible Idea, SCAMPER, morphological comparison, then a chosen architecture.

**Chosen idea**

A five-agent cooperative system:

- A1 Flow is the only signal writer.
- A2 Emergency, A3 Multimodal, A4 Situation, and A5 Sustainability ask through typed messages.
- A deterministic safety mask rejects illegal actions.
- Recovery is `Max-Pressure -> actuated -> fixed-time`.
- Synapse explains immutable decisions and never actuates.
- Required A1 method is cooperative Max-Pressure.
- Reinforcement learning is an optional later experiment.

**Rejected ideas (keep them rejected unless new Evidence overturns them)**

- LLM as traffic-light controller
- Five conversational LLM agents
- Independent learned controllers with no one-writer rule
- Throughput-only optimization
- Best-episode reporting as success
- Required DQN/MAPPO on the critical path

---

## Stage 4 — Prototype

A working controlled prototype now exists through gated Row 10c. It includes safe A1 control, specialist requests, failure recovery, A4/A5 fixtures, matched trip evidence, and a deterministic professor page. Synapse agents, API gating, React, Tunis, and optional DQN remain later work in `.kiro/specs/coflow5-reliable-agentic-platform/tasks.md`.

Minimum prototype that still satisfies the course:

1. Reproducible controlled SUMO scenario
2. Fixed-time and actuated baselines
3. Cooperative Max-Pressure A1 with safety mask
4. Typed A2/A3 requests
5. Run evidence bundle
6. Failure recovery demonstration

---

## Stage 5 — Test

Technical tests, failure injection, and a one-seed matched controller comparison have run. Test remains incomplete for multi-seed inference, realistic A4/A5 value ablations, and stakeholder validation. The continuing evaluation contract requires:

- matched scenarios and seeds
- stakeholder KPIs, not mean delay alone
- agent on/off ablations
- message and controller failure injection
- honest null and negative results
- no best-episode headline

---

## Data Science loop inside Prototype/Test

The course also asks for this reasoning chain. Keep it visible in specs and reports:

1. Problem
2. Success criteria
3. Data
4. EDA
5. Preparation
6. Baseline
7. Model
8. Evaluation
9. Error analysis
10. Iteration
11. Deployment
12. Monitoring

Root-cause analysis uses the Fishbone in `.scratch/coflow5-reliable-ai-platform/spec.md`.
