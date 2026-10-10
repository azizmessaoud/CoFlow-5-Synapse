# Persona Alias Table
**Status:** Final (S0)
**Scope:** Canonical mapping between professor-finalized deck names and system-canonical names.

This table is the sole authority for persona identity across the CoFlow-5 Synapse system. Any evidence bundle or test case referencing a persona must resolve to the Canonical Name.

| Deck Name | Canonical Name | Role | Primary Agent | Metric Goal |
|---|---|---|---|---|
| Ferjani, 74 | Amara | Pedestrian with a cane | A3 asks; A1 holds | Wait time; truncations = 0 |
| Faycel, 41 | David | Bus driver | A1 accountable | Trip completion; P95 stops |
| Mamadou, 25 | Chidi | Bus passenger | A3 (late bus) | Headway variance |
| Tahani, 35 | Rosa | Incident-report reader | Synapse S2/S3 | Reason-code coverage |
| Touhami, 50 | Marcus | Ambulance crew | A2 asks; A1 checks | EV time; civilian delay |
| Kamel, 55 | Omar | Duty officer | A4 publishes | Detection delay; FAR |

## Infrastructure Personas (Internal)
The following are treated as infrastructure needs rather than primary validation personas:
- Yuki
- Maria
