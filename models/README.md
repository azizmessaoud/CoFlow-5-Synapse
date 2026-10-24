---
library_name: sklearn
tags:
- tabular-regression
- tabular-classification
- reinforcement-learning
- traffic
- sumo
- multi-agent
---

# TraffiX models (CoFlow-5 Synapse)

Models used by the agents of TraffiX, a multi-agent traffic-signal controller for six junctions of
Tunis centre-ville, simulated in SUMO. They estimate things (arrival times, lateness, demand);
they never change a light. Each model is used only if it beats a simple rule on held-out data,
otherwise the agent keeps the rule.

**Simulation only.** Training data comes from SUMO runs with synthetic demand dated 2025; tests use
scenarios dated 2026, so a model cannot memorise holiday dates. Nothing here is measured in Tunis.

| File | Predicts | Used by agent | Rule it must beat | Held-out result |
|---|---|---|---|---|
| `demand_forecast.joblib` | Network traffic level and inbound share for the next hour | demand forecast | 2025 average for the same month, weekday and hour | MAE 0.023 vs rule 0.044; Ramadan 0.026 vs 0.103 |
| `pedestrian.joblib` | Will this pedestrian wait too long? | pedestrian (junction) | wait > 45 s | F1 0.443 vs rule 0.0 |
| `ambulance_eta.joblib` | Seconds until an emergency vehicle reaches the stop line | emergency priority, emergency route | distance / speed | MAE 43.65 vs rule 92.63 |
| `bus_eta.joblib` | Seconds until a bus reaches the stop line | transit priority | distance / speed | MAE 139.69 vs rule 285.81 |
| `bus_lateness.joblib` | Gap to the previous bus when this bus reaches the junction | transit monitor | the gap now | MAE 158.94 vs rule 212.25 |
| `edge_travel_time.joblib` | Travel time of a road one minute later | rerouting | length / current speed | MAE 0.53 vs rule 2.5 |
| `rain_speed.joblib` | Speed factor in rain | weather | 1 - 0.2 x rain intensity | MAE 0.15 vs rule 0.38 |
| `arrivals.joblib` | Cars arriving at a junction in the next 30 s | predictive traffic light | same as the last 30 s | MAE 0.69 vs rule 0.69 |
| `notification.joblib` | Which persona page shows an alert | notification | our own routing rules | training accuracy 1.0 (labels are our own rules; the model reproduces them) |
| `rl_q.joblib` | Q-function of the reinforcement learning traffic light (Fitted Q-Iteration) | traffic light (option) | max-pressure | car + pedestrian wait 231.39 s vs max-pressure 221.86 s |

Not shipped: the sensor-health classifier lost to its rule (F1 0.752 vs 0.978) and the incident
classifier had no labelled data, so both agents use their rules.

`traffic_light_params.json` and `predictive_params.json` hold the tuned light-agent settings;
`metrics.json` holds every number above.

## Use

Load with the same versions: scikit-learn 1.9.1, numpy 2.4.6,
Python 3.11.9. The feature order is defined in `traffix/training/` of the project
repository; the models are meant to be used by its agents, not on their own.

```python
import joblib
from huggingface_hub import hf_hub_download
model = joblib.load(hf_hub_download("<hf-user>/traffix-models", "ambulance_eta.joblib"))
```

`.joblib` files are pickles: load them only from a repository you trust.
