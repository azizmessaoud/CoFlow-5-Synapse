"""
Publishes the trained models (models/) to the Hugging Face Hub with a model card.

  pip install huggingface_hub
  python scripts/push_models_to_hub.py --repo <hf-user>/traffix-models            private repo
  python scripts/push_models_to_hub.py --repo <hf-user>/traffix-models --public
  python scripts/push_models_to_hub.py --card-only     write models/README.md, upload nothing

The token comes from `hf auth login` or HF_TOKEN (also read from the repo's .env).
The card is built from models/metrics.json, so it always matches the uploaded files.
"""
import argparse
import json
import os

import _path  # noqa: F401
from traffix.core import config

MODELS = config.path("models")

# what each file is, which agent uses it, and the rule it must beat
ABOUT = {
    "demand_forecast": ("Network traffic level and inbound share for the next hour", "demand forecast",
                        "2025 average for the same month, weekday and hour"),
    "pedestrian": ("Will this pedestrian wait too long?", "pedestrian (junction)", "wait > 45 s"),
    "ambulance_eta": ("Seconds until an emergency vehicle reaches the stop line", "emergency priority, emergency route",
                      "distance / speed"),
    "bus_eta": ("Seconds until a bus reaches the stop line", "transit priority", "distance / speed"),
    "bus_lateness": ("Gap to the previous bus when this bus reaches the junction", "transit monitor",
                     "the gap now"),
    "edge_travel_time": ("Travel time of a road one minute later", "rerouting", "length / current speed"),
    "rain_speed": ("Speed factor in rain", "weather", "1 - 0.2 x rain intensity"),
    "arrivals": ("Cars arriving at a junction in the next 30 s", "predictive traffic light", "same as the last 30 s"),
    "notification": ("Which persona page shows an alert", "notification", "our own routing rules"),
    "rl_q": ("Q-function of the reinforcement learning traffic light (Fitted Q-Iteration)", "traffic light (option)",
             "max-pressure"),
}


def _row(name, m):
    if "f1" in m:
        return f"F1 {m['f1']} vs rule {m['rule_f1']}"
    if "rule_mae" in m:
        return f"MAE {m['mae']} vs rule {m['rule_mae']}"
    if "mae_level" in m:
        return (f"MAE {m['mae_level']} vs rule {m['mae_level_naive_same_date']}; "
                f"Ramadan {m['mae_level_ramadan']} vs {m['mae_level_ramadan_naive']}")
    if "training_accuracy" in m:
        return f"training accuracy {m['training_accuracy']} ({m.get('note', '')})"
    return ""


def model_card(metrics):
    v = metrics.get("_versions", {})
    rows = []
    for name, (what, agent, rule) in ABOUT.items():
        if not os.path.exists(os.path.join(MODELS, f"{name}.joblib")):
            continue
        result = _row(name, metrics.get(name, {}))
        if name == "rl_q":
            r = {x["round"]: x["wait_car_plus_ped_s"] for x in metrics.get("rl_traffic_light", {}).get("rounds", [])}
            result = f"car + pedestrian wait {r.get('final')} s vs max-pressure {r.get('reference')} s"
        rows.append(f"| `{name}.joblib` | {what} | {agent} | {rule} | {result} |")
    return f"""---
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
{chr(10).join(rows)}

Not shipped: the sensor-health classifier lost to its rule (F1 0.752 vs 0.978) and the incident
classifier had no labelled data, so both agents use their rules.

`traffic_light_params.json` and `predictive_params.json` hold the tuned light-agent settings;
`metrics.json` holds every number above.

## Use

Load with the same versions: scikit-learn {v.get('scikit-learn', '?')}, numpy {v.get('numpy', '?')},
Python {v.get('python', '?')}. The feature order is defined in `traffix/training/` of the project
repository; the models are meant to be used by its agents, not on their own.

```python
import joblib
from huggingface_hub import hf_hub_download
model = joblib.load(hf_hub_download("<repo>", "ambulance_eta.joblib"))
```

`.joblib` files are pickles: load them only from a repository you trust.
"""


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--repo", help="<hf-user>/<name>, e.g. aziz/traffix-models")
    p.add_argument("--public", action="store_true", help="create the repository as public (default: private)")
    p.add_argument("--card-only", action="store_true", help="write models/README.md and stop")
    a = p.parse_args()
    with open(os.path.join(MODELS, "metrics.json")) as f:
        card = model_card(json.load(f))
    with open(os.path.join(MODELS, "README.md"), "w", encoding="utf-8") as f:
        f.write(card.replace("<repo>", a.repo or "<hf-user>/traffix-models"))
    print("Wrote models/README.md")
    if a.card_only:
        raise SystemExit
    if not a.repo:
        p.error("--repo is required to upload")
    from huggingface_hub import HfApi
    api = HfApi()
    api.create_repo(a.repo, private=not a.public, exist_ok=True)
    api.upload_folder(folder_path=MODELS, repo_id=a.repo, commit_message="Upload TraffiX models",
                      allow_patterns=["*.joblib", "*.json", "README.md"])
    print(f"Uploaded: https://huggingface.co/{a.repo}")
