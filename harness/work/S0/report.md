# S0 boundary gate

The canonical persona, J0 topology, incident lifecycle, and claim-flag
boundaries are sealed for downstream implementation.

- Persona aliases resolve through the final alias table.
- J0 is the required controlled benchmark; 4x4 is planned scale-up work.
- Incident transitions are append-only and carry `event_id`, `run_id`, and
  `scenario_hash`.
- Downstream implementation tickets reference the sealed boundary.
- The gate is decided by files and contract assertions, not self-assessment.
