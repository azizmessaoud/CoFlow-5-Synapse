# Incident Schema v1
**Status:** Draft (S0)
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

## Event Mapping
Incident effects must map to:
- `edge_capacity_multiplier`: Reduction in max flow.
- `speed_multiplier`: Reduction in free-flow speed.
- `lane_closure`: Boolean for absolute closure.
- `priority_request`: Trigger for A2 emergency priority.
