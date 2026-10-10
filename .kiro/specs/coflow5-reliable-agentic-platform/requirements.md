# CoFlow-5 Synapse Requirements

**Status:** Final specification baseline (S0 Patched)
**Workflow:** Requirements-first
**Source authority:** `SUMO_forStudents.docx` and `docs/source/course-brief.md`
**Decision authority:** `docs/adr/0001-reliable-ai-platform-boundary.md`
**Detailed source:** `.scratch/coflow5-reliable-agentic-platform/spec.md`
**Design Thinking record:** `.kiro/specs/coflow5-reliable-agentic-platform/design-thinking.md`

## Project intent
CoFlow-5 Synapse answers the course challenge:

> How might we use data and intelligent agents to make urban traffic more efficient, adaptive, and sustainable?

The required project is an agentic system because five domain agents observe, decide, communicate, and cooperate under explicit authority. Reinforcement learning is not required. Cooperation, one-writer authority, evaluation, and failure recovery are the core.

## Persona Alias Table (S0)
To resolve conflicts between the professor's finalized deck and the repository's canonical naming, the following table is the sole source of truth.

| Deck Name | Canonical Name | Role | Primary Agent |
|---|---|---|---|
| Ferjani, 74 | Amara | Pedestrian with a cane | A3 asks; A1 holds |
| Faycel, 41 | David | Bus driver | A1 accountable |
| Mamadou, 25 | Chidi | Bus passenger | A3 (late bus) |
| Tahani, 35 | Rosa | Incident-report reader | Synapse S2/S3 |
| Touhami, 50 | Marcus | Ambulance crew | A2 asks; A1 checks |
| Kamel, 55 | Omar | Duty officer | A4 publishes |

*Note: Yuki and Maria are re-tagged as infrastructure/internal personas and are not primary targets for final validation.*

## Harness traceability
This table binds every stable requirement ID to sealed queue work and the identifiers its acceptance evidence must carry.

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

## Requirement 0: Design Thinking traceability
**User story:** As a professor, I want to see Empathize, Define, Ideate, Prototype, and Test in order, so that the technical design is justified by stakeholder needs rather than by a preferred algorithm.

### Acceptance criteria
1. THE specification SHALL record Design Thinking Stages 1–3 as completed work, with links to the Empathize pack and the Define/Ideate document.
2. THE specification SHALL keep the six finalized User Personas (Amara, David, Chidi, Rosa, Marcus, Omar) as described in the Alias Table.
3. THE specification SHALL keep the refined How-might-we: serve every person on the network, not only the average car.
4. THE specification SHALL keep the chosen Ideate result: one-writer A1, advisory A2–A5, deterministic safety, and non-actuating Synapse.
5. THE specification SHALL keep rejected ideas rejected, including LLM signal control and five conversational LLM agents.
6. THE Prototype and Test stages SHALL remain incomplete until a SUMO evidence bundle and paired baseline comparison exist.
7. WHEN a requirement is added, THE specification SHALL name the User Persona or How-might-we it serves, or mark it as infrastructure.

## Requirement 1: Course outcome and evidence
(No changes)

## Requirement 2: Reproducible scenario runs
(No changes)

## Requirement 3: One-writer authority and deterministic safety
(No changes)

## Requirement 4: Cooperative A1 control
(No changes)

## Requirement 5: Agent communication
(No changes)

## Requirement 6: Emergency cooperation
(No changes)

## Requirement 7: Pedestrian and transit cooperation
(No changes)

## Requirement 8: Situation awareness and sustainability
(No changes)

## Requirement 9: Failure recovery
(No changes)

## Requirement 10: Evaluation and error analysis
(No changes)

## Requirement 11: Data lifecycle
(No changes)

## Requirement 12: Synapse grounding and evaluation
(No changes)

## Requirement 13: API and operator interface
(No changes)

## Requirement 14: Observability and security
(No changes)

## Requirement 15: Delivery boundaries
(No changes)
