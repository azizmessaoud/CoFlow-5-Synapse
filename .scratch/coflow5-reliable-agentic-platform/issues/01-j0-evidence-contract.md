---
name: j0-evidence-contract
description: Freeze the required J0 evidence, ablations, and success boundary
labels: [wayfinder:resolved]
parent: coflow5-reliable-agentic-platform-map
Type: grilling
---

## Resolution

The J0 evidence contract defines the "Done" state for the controlled prototype. Completion is achieved when the following evidence bundle is produced for the single-junction (J0) benchmark.

### 1. The Matched-Seed Matrix (Requirement 1, 2, 10)
The system must produce a reproducible dataset across **matched scenarios and seeds** for:
- **Cooperative A1 (Max-Pressure)**: The required agentic control.
- **Actuated Control**: The standard SUMO baseline.
- **Fixed-Time Control**: The static baseline.

**Evidence Requirement:**
- $\ge 5$ distinct random seeds per scenario.
- Immutable `run_id` and `scenario_hash` for every run.
- Deterministic output verification: Rerunning the same seed must produce identical metrics within numeric tolerance.

### 2. Cooperation Ablations (Requirement 1, 4, 6, 7, 8)
To prove the value of the agentic system, the implementation must provide on/off toggles for the advisory specialists:
- **A2 (Emergency)**: Run with and without emergency vehicle priority.
- **A3 (Pedestrian/Transit)**: Run with and without pedestrian deadline and bus priority.
- **A4 (Forecasting)**: Run with and without incident/congestion forecasts.
- **A5 (Sustainability)**: Run with and without emission-proxy advice.

**Evidence Requirement:**
- Pairwise comparison of metrics (e.g., Emergency Delay $\pm$ A2) to establish the specific contribution of each specialist.
- Explicit report of "Null" or "Negative" results where a feature did not improve the outcome.

### 3. Failure-Injection Cases (Requirement 9)
The recovery ladder must be evidenced through forced transitions:
- **Case A: Specialist Failure**: Silence/Malformation of A2–A5 messages $\rightarrow$ System must maintain legal local Max-Pressure.
- **Case B: Controller Failure**: Transition from A1 $\rightarrow$ Actuated $\rightarrow$ Fixed-Time.
- **Case C: Synapse Failure**: LLM/API timeout $\rightarrow$ System must maintain actuation and return deterministic template explanations.

**Evidence Requirement:**
- Transition logs recording `previous_mode`, `next_mode`, `trigger`, and `simulation_time`.

### 4. Stakeholder KPIs (Requirement 1, 10)
Success is measured by the **honest reporting** of these metrics:
- **Safety**: Zero conflicting greens; zero pedestrian clearance truncations.
- **Efficiency**: Mean/P95 wait times, total trip duration, tail metrics (unfinished trips).
- **Specialist Impact**: Emergency passage time, pedestrian max wait, transit headway variation.
- **Sustainability**: Link-level emission proxies (HBEFA) near sensitive areas.

### 5. The Success Boundary
**CoFlow-5 is "Complete" when:**
1. The J0 Evidence Bundle (Matrix + Ablations + Failure Logs) is frozen and immutable.
2. The Tunis OSM/TRANSTU scenario is executed as a **labelled showcase**, demonstrating real-world data ingestion and multi-junction scale, but without the strict matched-seed baseline requirements of J0.
3. A matched-baseline comparison exists, and all failures are classified (Control, Comm, Forecast, etc.).

**Note:** Optional DQN/MAPPO experiments are outside this contract; they may be added but cannot block the completion of the required prototype.
