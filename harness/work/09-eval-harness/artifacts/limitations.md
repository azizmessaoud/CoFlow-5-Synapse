# Row 09 evaluation limitations

- **One common seed:** fixed-time, actuated, and cooperative Max-Pressure share scenario hash and seed 37, but one seed cannot support an inferential confidence interval.
- **Missing Max-Pressure traffic KPIs:** row 05 records native decisions and safety acceptance but no trip/run KPI table. The matched traffic-outcome cell is therefore `invalid` with reason `MISSING_REQUIRED_TRAFFIC_KPIS`.
- **Unexecuted ablations:** row 07 has specialist-on fixtures but no corresponding off runs; A4 and A5 experiments are also absent. Those cells remain visible as reason-coded invalid outcomes.
- **Proxy boundary:** the sustainability row is null-valued and explicitly labelled a SUMO/HBEFA emission proxy. No ambient sensor observations were collected.
- **Simulation boundary:** emergency effects are simulated travel-time and civilian-delay values. They do not establish real-world safety or casualty effects.
- **Scope and tails:** unfinished trips, teleports, standstills, mean, P95, and maximum values are retained where canonical raw evidence exists. Row 07 and row 08 are deterministic acceptance fixtures, not network-scale estimates.
- **Mixed result retained:** actuated improves completion and waiting metrics against fixed-time in the one matched run, while total time loss is higher. Neither side of that result is suppressed.
- **Selection rule:** the headline is the sole paired/matched baseline evidence, not a selected extreme outcome.
