# CoFlow-5 Empathize

Glossary for the Empathize pack this repo is finding its way to. Implementation and simulation details do not belong here.

## Language

**Empathize pack**:
The canonical four-section document this map is finding its way to.
_Avoid_: spec, README, implementation plan, design-patterns paper

**User Persona**:
A research-informed stakeholder profile in the Empathize pack, not an interview-validated person. Roster is **seven** (Amara, David, Chidi, Rosa, Marcus, Yuki, Omar). Parent/Maria removed — professor: not evident.
_Avoid_: user, role, actor (when meaning this profile); Maria/Leila parent persona

**Proxy validation**:
A walkthrough by the student team or professor of research-informed User Personas, User Journeys, and Possible Solutions. It is not an interview with the person a User Persona describes.
_Avoid_: stakeholder interview, interview-validated Empathize, user testing (when meaning this walkthrough)

**User Journey**:
The staged experience of one User Persona from pain to a Possible Solution.
_Avoid_: flow, story, scenario (when meaning this staged experience)

**Evidence**:
A cited primary-source claim that supports a User Persona, User Journey, or Possible Solution. For this pack, **Tunisia practice** (law, agencies, open data, operator publications) is primary; international ATC is **transfer** Evidence. IMATM placeholders and SMART targets are not Evidence.
_Avoid_: literature, background, bibliography (when meaning these supporting claims)

**Insight**:
A falsifiable mechanism claim from Empathize (I-1…I-10). It must map to Evidence and a metric; it is not itself a measured Tunis field result.
_Avoid_: complaint, anecdote, Table 9 digit (when meaning the mechanism)

**Tunis simulation setting**:
The Empathize study place for the SUMO showcase: Grand Tunis roles and institutions, with OSM + scheduled TRANSTU GTFS + labelled synthetic/calibrated road demand. Not a live signal-cabinet deployment.
_Avoid_: Tunis field trial, live Tunis traffic validation (unless separately verified)

**Possible Solution**:
A design response in the Empathize pack, not a built system.
_Avoid_: feature, implementation, agent (when meaning this design response)

**Claim flag**:
A statement the Empathize pack must not make, taken from the v2 flags list.
_Avoid_: disclaimer, warning, caveat (when meaning these forbidden claims)

**Reliable AI decision platform**:
The portfolio identity for CoFlow-5: a system whose decisions are measurable, constrained, explainable, and robust when models, messages, or data fail.
_Avoid_: AI traffic demo, LLM traffic controller, five-chatbot system

**Control plane**:
The safety-critical part that observes SUMO, selects legal traffic-signal actions, and falls back deterministically when learned control fails.
_Avoid_: Synapse, LLM orchestrator

**Domain agent**:
A cooperating specialist in the Control plane, defined by its role, messages, and permissions. The professor's "intelligent autonomous agent" means this. It is not a language model.
_Avoid_: chatbot, agentic AI, LLM agent

**Synapse layer**:
The non-actuating language-model layer. It retrieves evidence, explains logged decisions, evaluates explanation quality, and supports human-reviewed what-if analysis. In this project, this is what "agentic AI" refers to.
_Avoid_: controller, light boss, control plane, domain agent
