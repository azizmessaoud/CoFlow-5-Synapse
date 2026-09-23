# CoFlow-5 Empathize pack

Label: `wayfinder:map`

## Destination

One canonical Empathize pack with four top-level sections — User Personas, User Journeys, Evidence, and Possible Solution — ready to hand off. Seed from `coflow5-personas-journeys.md`; reconcile the duplicate markdown and the PDF/docx. This map does not produce a built CoFlow-5 system.

## Notes

- Tracker: local markdown under `.scratch/` (`docs/agents/issue-tracker.md`).
- Consult `domain-modeling` and `CONTEXT.md` for Empathize-pack language.
- User Personas are research-informed design artifacts, not interview-validated profiles. Keep the v2 claims note.
- The LLM is structurally barred from actuation; that constraint is out of this map's scope, not a Possible Solution to invent here.
- Skills every session should consult: `wayfinder`, `grilling`, `domain-modeling`; `research` for source tickets.

## Decisions so far

- [Binary sources](issues/04-binary-sources.md): Unique Empathize claims live in the IMATM report (six Tunis User Personas, S-1–S-10); the PDF is architecture slides; `SUMO_forStudents.docx` is a brief with no roster. Notes: [binary-sources.md](research/binary-sources.md).
- **Roster (professor):** seven personas — Maria/parent **removed (not evident)**; Omar = P7; I-7 deferred without persona owner. Ticket: [02-persona-roster.md](issues/02-persona-roster.md).
- Empathize pack filename: [`coflow5-empathize-pack.md`](../../coflow5-empathize-pack.md) — four top-level sections (User Personas, User Journeys, Evidence, Possible Solution). v2 eight User Personas including operators. IMATM names are an alternate roster, not extra people.
- [Tunisia practice Evidence](research/tunisia-practice-evidence.md): Empathize leads with TRANSTU, Décret 2000-149, MEHAT signalisation, ANPE, CODATU–AFD, official GTFS; SCATS/Surtrac/SCOOT are transfer-only; simulation honesty flags kept.
- [World truths + metrics](research/world-truths-and-metrics.md): FHWA ATSPM/ASCT MOEs, reliability indices, TIM, TSP, ped, EVP, operator, emission-proxy families mapped to the eight User Personas; SMART targets stay proposed.
- [Insight → Evidence → Metric](research/insight-evidence-alignment.md): I-1…I-10 checked detail-by-detail; Table 9 ▲ excluded; rejected framings recorded. Evidence bar: [03-evidence-bar.md](issues/03-evidence-bar.md) resolved.
- **Empathize alignment verdict (wayfinder):** conceptual spine passes. Wording refined (I-1 soft WTP; I-3 space; I-4 wait/clearance/completion; I-5 dual mechanisms; I-7 stops lever; I-8≠I-9). Citation precision gate: [06-citation-precision.md](issues/06-citation-precision.md) resolved with [citation-ledger.md](research/citation-ledger.md); human page-verify remains for `from-prior-pack` loci only.

## Not yet specified

- How Possible Solution cites A1–A5 beyond the evaluation-accountability table already in the pack.
- Human verification of remaining `from-prior-pack` page loci in the citation ledger (before professor submission).

## Out of scope

- SUMO/RL implementation and a first running experiment.
- Synapse in the control loop.
- Full Tier 0–2 build.
- Treating the design-patterns paper as the report body.
