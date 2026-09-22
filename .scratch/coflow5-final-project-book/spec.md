Status: ready-for-agent

# CoFlow-5 — Professor-facing Final Project Book and six-person delivery envelope

## Problem Statement

The team must show a professor a Design Thinking project tomorrow and then build a Reliable AI decision platform over 12 weeks. A long Final Project Book already exists, but it still talks like “Member 1–6” and “after tomorrow’s workshop,” and it can be misread as if stakeholder interviews or a SUMO prototype already happened.

Six ESPRIT 4DS students will do the work. They are the only people in the Wednesday session. The glossary says a User Persona is research-informed, not an interviewed person. ADR-0001 still describes three dependable contributors. Native Windows Python 3.11 is missing, so row 01 cannot gate.

The users need one honest professor-facing book, named pairs, a labelled proxy validation, and a delivery rule that extra people do not skip the Control plane.

## Solution

Treat the Final Project Book as the single human-facing contract for Wednesday and for the 12-week build. It must agree with the Empathize pack, ADR-0001, the sealed queue, and the glossary.

Wednesday is **proxy validation**: the six builders walk User Personas, User Journeys, and Possible Solutions. They do not interview Amara. They do not run SUMO. They do not upgrade Empathize to interview-validated.

After the walkthrough they fill dated correction cards and a proxy-validation summary. They do not rewrite Evidence-backed Empathize pack sentences the same night.

Delivery is six named people in three pairs, **one sealed queue row at a time**. Course/reliability success is rows 01–09. Cuts go 15 → 10. DQN stays optional and blocked. A short ADR-0002 records the six-person envelope without rewriting ADR-0001.

A later agent may then edit the book, add ADR-0002, and name the pairs. This spec does not start SUMO product code.

## User Stories

1. As a professor, I want the opening of the book to say **proxy validation**, so that I do not think interviews already happened.
2. As a professor, I want Design Thinking Stages 1–3 marked complete as research-informed work, so that I can see Empathize, Define, and Ideate without a fake Prototype.
3. As a professor, I want Prototype and Test marked planned, so that I do not grade invented % gains.
4. As a professor, I want the course How-might-we visible, so that the project answers `SUMO_forStudents`.
5. As a professor, I want Claim flags on the validation chapter, so that I do not hear lives saved or measured air quality.
6. As Aziz, I want my name and email in the team table, so that the book matches who actually builds.
7. As Eya, I want my name in the team table, so that ownership is not “Member 2.”
8. As Fares, I want my name in the team table, so that Control-pair work is attributable.
9. As Aymen, I want my name in the team table, so that evaluation work is attributable.
10. As Oumayma, I want my name in the team table, so that product/architecture cards have an owner.
11. As Ranim, I want my name in the team table, so that persona-card presentation has an owner.
12. As the team, I want six emails listed once, so that duplicate paste errors do not create a seventh person.
13. As a User Persona (Amara), I want to remain a research-informed profile, so that a student walkthrough does not become my interview.
14. As a User Persona (David), I want journey reliability kept as a need, so that mean delay is not the only story.
15. As a User Persona (Chidi), I want regularity kept distinct from “faster buses,” so that Possible Solutions stay honest.
16. As a User Persona (Rosa), I want unexplained refusals to stay a need, so that reason codes stay in scope.
17. As a User Persona (Marcus), I want passage and recovery kept together, so that emergency greens are not sold as lives saved.
18. As a User Persona (Yuki), I want diagnose/override/disable kept, so that the Control plane stays overridable.
19. As a User Persona (Maria), I want local emission-proxy harm kept, so that a city average cannot hide her street.
20. As a User Persona (Omar), I want “what is wrong, why, and how much to trust” kept, so that a frozen dashboard is a failure mode.
21. As the Empathize pack, I want my four sections left intact tonight, so that Evidence citations are not rewritten by a team vote.
22. As the note-taker, I want Appendix A sheets, so that corrections are dated and anonymous-coded.
23. As the facilitator, I want a two-hour script that starts with “we are testing assumptions,” so that the session is not a sales pitch.
24. As the skeptic, I want a Claim-flag checklist in the room, so that I can stop leading questions.
25. As the storyboard operator, I want Possible Solution cards and an architecture diagram only, so that I am not asked to demo SUMO.
26. As the synthesis recorder, I want keep/revise/remove/test-later, so that we do not take a majority vote as Evidence.
27. As a participant-who-is-also-a-builder, I want the session labelled proxy validation, so that I am not recorded as V-PED-01 the pedestrian.
28. As the team, I want unprompted “recent traffic experience” first, so that cards do not prime every answer.
29. As the team, I want all eight personas available as cards, so that the roster is not shrunk to five invented names.
30. As the team, I want a 30-minute fallback agenda, so that a late professor still sees experience, one persona, shared conflict, failure, ranking.
31. As Pair A, I want Control ownership of rows 01, 03, 04, 05, so that native Windows SUMO stays one pair’s job.
32. As Pair B, I want Data/Evaluation ownership of rows 02, 08, 09, so that the evidence bundle is not invented by the UI.
33. As Pair C, I want Cooperation/Product ownership of rows 06, 07 and later 11–13, so that messages exist before Synapse.
34. As Pair A, I want row 01 blocked until native Windows Python 3.11 exists, so that WSL cannot fake the smoke test.
35. As Pair B, I want no evaluation claims before a valid evidence bundle, so that Wednesday cannot produce throughput tables.
36. As Pair C, I want A2/A3 after Max-Pressure, so that specialists cannot write lights.
37. As the queue, I want one active row, so that six people do not merge Synapse before safety.
38. As the queue, I want rows 01–09 uncuttable, so that course success is still a working, compared, failure-tested prototype.
39. As the queue, I want cuts 15 then 14 then 13 then 12 then 11 then 10, so that optional product dies before rigor.
40. As ADR-0001, I want my three-contributor sizing not silently overwritten, so that a new ADR records six people + one row.
41. As the Control plane, I want only A1 to write signals, so that the book cannot make Synapse the coordinator of PHASE_COMMAND.
42. As the Synapse layer, I want “reads evidence, never TraCI” in the professor chapter, so that LLM-as-controller stays rejected.
43. As cooperative Max-Pressure, I want to remain the required A1 controller, so that MARL is not the Ideate headline.
44. As optional DQN, I want to stay blocked at row 15, so that training risk cannot stop delivery.
45. As recovery, I want Max-Pressure → actuated → fixed-time, so that “policy → …” does not return.
46. As join keys, I want run_id, scenario_hash, event_id, and message_id named in the book’s evidence chapter, so that later tests have one identity language.
47. As a later worker, I want machine gates, not chat memory, so that a pair cannot mark a row done by self-assessment.
48. As a reviewer, I want a dated proxy-validation summary after Wednesday, so that limitations are listed.
49. As a reviewer, I want Green/Amber/Red/Not-tested to stay qualitative, so that six students are not a population sample.
50. As a builder, I want 6–8 hours per person per week treated as an assumption to confirm, so that the 12-week table can shrink to 01–09.
51. As a builder, I want GitHub `azizmessaoud/CoFlow-5-Synapse` to remain the shared copy, so that the six can read the same book on a phone.
52. As the course, I want a path to a working prototype, experiments, baseline comparison, and honest limits, so that proxy validation is not the final deliverable.

## Implementation Decisions

- The feature is documentation and delivery-envelope alignment, not Control plane code.
- One human-facing document is the seam: the Final Project Book must be internally consistent with the Empathize pack, the Design Thinking record, ADR-0001, and the sealed queue.
- Wednesday is proxy validation. Allowed outputs: participant register of the six builders, consent if a professor joins, assumption log, persona/journey correction cards, Possible Solution keep/revise/remove/test-later, dated summary. Forbidden outputs: interview quotes, interview-validated User Personas, simulation KPIs, lives saved, measured air quality, best-episode tables.
- Empathize pack body text is frozen for the night of 22–23 September 2026. Corrections live on cards and in the summary.
- Possible Solutions are shown as cards plus the one-writer architecture diagram. No SUMO execution. No HTML/PPTX presented as a running product.
- Named builders: Aziz Messaoud, Eya Laourine, Fares Ben Kacem, Mohamed Aymen Hamzaoui, Oumayma Saddouri, Ranim Ben Salem, all `@esprit.tn`.
- Recommended pairs until the team overrides in writing: Control = Aziz + Fares; Data/Evaluation = Aymen + Oumayma; Cooperation/Product = Eya + Ranim.
- Recommended Wednesday roles until overridden: Aziz facilitator; Eya notes; Ranim persona cards; Oumayma Possible Solution and architecture cards; Fares skeptic and Claim flags; Aymen keep/revise/remove board.
- Course/reliability success remains queue rows 01–09. Full portfolio is 01–14. Row 15 DQN stays blocked.
- One sealed row is active. Pairs rotate driver / independent tester / explainer. Only tests-and-files may pass a row.
- ADR-0001 stays accepted. A new ADR-0002 records: six named builders, three pairs, one sealed row, success = 01–09, extra people do not authorize skipping the Control plane.
- Architecture locks are not workshop-votable: one writer, non-actuating Synapse, required cooperative Max-Pressure, recovery Max-Pressure → actuated → fixed-time. Changing those requires a new ADR.
- Row 01 remains blocked until native Windows Python 3.11.9 is installed. WSL Python does not satisfy the smoke-test contract.
- Join keys in any evidence chapter: run_id, scenario_hash, event_id, message_id.
- Glossary term Proxy validation already exists and must be used in the book’s Part III title and first paragraph.

## Testing Decisions

- Test the book as an external document, not its Markdown formatting.
- A good test is: a reader who only sees the book cannot honestly conclude that interviews, SUMO experiments, or required RL already happened.
- Checks: the string “proxy validation” appears in Part III; “interview-validated” does not describe the eight User Personas; “Member 1” is replaced by real names; Pair A/B/C names exist; DQN/MARL is optional or historical; Synapse is non-actuating; recovery ladder is Max-Pressure → actuated → fixed-time; Prototype/Test remain planned; Claim flags include no lives saved and no measured air quality.
- Architecture locks in the book must match ADR-0001. A mismatch is a failed spec, not a new product idea.
- After Wednesday, a summary file must exist that lists method = proxy validation, n = team (± professor), and Not-tested for any persona that had no card discussion.
- Do not test SUMO, pytest, or gate.json under this spec. Those belong to queue row 01 after Python 3.11 exists.
- Prior art: honesty notes already in the Empathize pack, Design Thinking record, harness contradiction log, and ADR-0001 superseded-architecture notes.

## Out of Scope

- Installing Python 3.11 or gating row 01.
- Writing SUMO adapters, agents, Parquet, API, UI, or DQN.
- Rewriting the Empathize pack, canonical Kiro requirements, or ADR-0001 body.
- Real stakeholder recruitment for 23 September 2026.
- Changing the eight-person roster or adding IMATM names.
- Inventing interview quotes or experimental results.
- Making reinforcement learning required.
- Putting an LLM in the Control plane.

## Further Notes

Round 3 of grilling offered pair names, workshop roles, and ADR-0002 as recommendations. The team had not answered those four letters when this spec was written. An implementing agent must keep those recommendations unless a later comment on this spec names a different split.

GitHub remote for shared access: azizmessaoud/CoFlow-5-Synapse, branch main.

Seam for this spec: the professor-facing Final Project Book (plus a one-page ADR-0002). If that seam is wrong, stop and say so before editing.
