# ADR contradiction log

**Phase:** CAPTURE  
**Authority:** `docs/adr/0001-reliable-ai-platform-boundary.md` overrides older narrative files through `AGENT_GUIDE.md` precedence.

| Source and text | Conflict/risk | Governing interpretation | Cheapest later fix |
|---|---|---|---|
| `coflow5-define-ideate.md`: “F1→A1 core”, “Rules own safety; RL owns efficiency”, and shared-policy MARL wording | Makes learned control appear required before cooperative Max-Pressure | Cooperative Max-Pressure is required A1; DQN is an optional row 15 experiment after feature freeze | In CONTRADICT/PATCH, mark these passages historical ideation superseded by ADR-0001 |
| `CoFlow-5_System_Requirements_Book.md`: “Shared-policy MARL + messages” marked “Core A1” | Conflicts with the canonical required-controller boundary | Canonical requirements 4 and ADR-0001 govern: Max-Pressure is core and RL cannot block delivery | Add a supersession note; do not rewrite Stage 1–3 evidence |
| Older recovery wording: “policy → Max-Pressure → actuated → fixed-time” | A generic policy can be read as the required primary mode | Required path is `cooperative Max-Pressure -> actuated -> fixed-time`; only optional DQN may precede it | Replace generic “policy” in active specifications; preserve as historical text only where labelled |
| `coflow5-define-ideate.md`: “five planned expert interviews replace placeholders with real quotes” | A plan may be misreported as completed interview evidence | Personas remain research-informed and not interview-validated; no quote or interview claim exists | Label interviews as future validation only |
| Legacy LLM/controller alternatives | Brainstorm alternatives may be mistaken for accepted architecture | Synapse is non-actuating and structurally barred from TraCI; A1 is sole writer | Keep rejected alternatives visibly rejected |
| Empathize eight-persona roster including Maria (parent) | Professor: parent persona not evident | Roster is **seven**: Amara, David, Chidi, Rosa, Marcus, Yuki, Omar. Maria/Leila removed; I-7 deferred without persona owner | Update Empathize pack, journeys, presentation validators; do not reintroduce parent under another name |

Professor-directed roster change authorizes removing Maria; it does not authorize product code, Prototype/Test complete, or adding personas.
