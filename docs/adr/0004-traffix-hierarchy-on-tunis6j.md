# ADR-0004: Adopt the traffix3 hierarchy, with CoFlow Synapse, on the Tunis six-junction map

**Status:** Accepted
**Date:** 16 October 2026

## Context

The team chose the agentic architecture of
[aymenhamzik/traffix3](https://github.com/aymenhamzik/traffix3) as the
reference: per-junction masters, a supermaster with eight network agents, and a
Synapse language layer with no path to the simulation. traffix3 ran on a
schematic network. CoFlow-5 already had a real OSM map of Tunis centre-ville and
six selected junctions (row 14), but none of them was signalised, and CoFlow's
own Synapse service (verified / template / abstain, seven-field provenance)
was not connected to any multi-junction controller.

## Decision

1. The traffix3 code lives in this repository: `traffix/`, `config/`,
   `models/`, `frontend/`, and its scripts in `scripts/`.
2. The default network is `tunis6j` (`scenarios/tunis-centre-6j/`), built by
   `scripts/build_tunis_centre_6j.py`. Only J1..J6 carry lights, so there is
   exactly one master per light. Node and light ids are both J1..J6.
3. Network-specific facts (folder, bus lines, scenario event places, demand
   level) live in `config/networks/<network>.yaml`. Scenarios refer to places
   as `"@name"`. The schematic `tunis_centre` network still works.
4. CoFlow's `SynapseService` is attached to the traffix decision log by
   `traffix/synapse/coflow_bridge.py` and exposed at `/api/synapse/*` and on
   the analyst page. It is read-only, like the rest of `traffix/synapse/`.

## How the CoFlow rules map

| CoFlow rule (AGENT_GUIDE) | traffix on tunis6j |
|---|---|
| One signal writer: A1 only | Only `simulation/executor.py` writes lights; only masters call it (`scripts/check_architecture.py`) |
| Synapse cannot reach TraCI | `traffix/synapse/` and the explainer may not import the backend, sensors, executor or masters (same check) |
| Recovery Max-Pressure -> actuated -> fixed-time | Master modes `MODE_MAX_PRESSURE` -> `MODE_ACTUATED` -> `MODE_FIXED` on stale data |
| DQN optional | RL light agent is optional (`traffix_rl`); max-pressure is the default |
| Claim flags stay | Demand is synthetic; bus lines are illustrative, not TRANSTU; showcase only |

## Consequences

- `python scripts/run_live.py` runs the full hierarchy on the real Tunis streets.
- Decisions carry real junction ids (J1..J6) and street names end to end:
  decision log, narrator, dashboard and Synapse provenance.
- The models shipped in `models/` must be retrained on the Tunis map
  (`python scripts/train.py`) whenever the network or demand changes.
- traffix3 has no licence file. It is used here at the team's request; add a
  licence or the author's written permission before any public release.
- The `src/coflow5` row 01-14 artefacts are unchanged; the traffix hierarchy
  is the multi-junction controller those rows did not have.
