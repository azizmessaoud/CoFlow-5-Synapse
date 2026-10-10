# Incident Schema v1
**Status:** Final (S0)
**Scope:** Definitive structure for incidents in the CoFlow-5 Synapse system.

## Core Incident Object
Every incident must carry:
- `incident_id`: Unique identifier.
- `scenario_id`: Link to the scenario.
- `type`: Enum [`flood`, `weather`, `emergency`, `police`, `pothole`, `closure`].
- `location`: SUMO edge/lane IDs affected.
- `start_time`: Simulation time of onset.
- `duration_s`: Expected duration (or `null` for permanent).
- `severity`: Float [0.0, 1.0] representing impact on capacity/speed.
- `confidence`: Float [0.0, 1.0] for detected incidents.
- `source`: Enum [`synthetic_scenario`, `scenario_engine`, `agent_detection`].

## Lifecycle

An incident progresses through these states:

1. `detected`: an incident has been observed or injected but has not yet
   changed control inputs.
2. `active`: the incident is applied to its affected network elements and may
   produce advisory messages.
3. `resolved`: the incident no longer affects the scenario, either because its
   duration elapsed or an explicit resolution event was recorded.
4. `cancelled`: the incident was withdrawn before activation and must not
   affect control or evaluation.

Every state transition must record the incident identifier, previous state,
next state, simulation time, source, reason, immutable `event_id`, `run_id`,
and `scenario_hash`. State transitions are append-only evidence and must
remain joinable to their run and scenario.

## Event Mapping
Incident effects must map to:
- `edge_capacity_multiplier`: Reduction in max flow.
- `speed_multiplier`: Reduction in free-flow speed.
- `lane_closure`: Boolean for absolute closure.
- `priority_request`: Trigger for A2 emergency priority.

Effects must be removed when an incident reaches `resolved` or `cancelled`.
An incident may not directly write traffic signals; any priority request is
advisory input to A1 and remains subject to the deterministic safety mask.
