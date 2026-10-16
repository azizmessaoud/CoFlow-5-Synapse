# TraffiX hierarchy + CoFlow Synapse on Tunis centre-ville

The traffix3 multi-agent controller ([aymenhamzik/traffix3](https://github.com/aymenhamzik/traffix3)),
running on the real OSM streets of Tunis centre-ville with six signalised
junctions (J1..J6). Decision: [ADR-0004](../adr/0004-traffix-hierarchy-on-tunis6j.md).

> Simulation only. Road demand and bus lines are synthetic. Calendar values are
> project assumptions. No lives saved, no measured air quality, no deployment.

## Run

```powershell
python -m pip install -r requirements-traffix.txt
python scripts/setup.py          # network (if missing), demand for every scenario, models if unusable
python scripts/run_live.py       # open http://localhost:8000, pick a scenario, press Start
```

Add `--gui` to `run_live.py` to also watch the run in SUMO's own window.

Other commands:

```powershell
python scripts/run_experiments.py --scenario morning_peak --seeds 1    # one quick comparison
python scripts/run_experiments.py                                      # 7 controllers x 12 scenarios x 3 seeds
python scripts/analyze.py                                              # tables and charts in results/
python scripts/check_architecture.py                                   # hierarchy rules hold
python scripts/train.py                                                # retrain on the current network
python scripts/ask.py results/logs/decisions_traffix_emergency_1.jsonl "Why did ambulance1 get green at J1?"
python -m pytest tests/traffix tests/scripts/test_tunis_centre_6j.py -q
```

Switch back to traffix3's schematic network with `TRAFFIX_NETWORK=tunis_centre`
(then `python scripts/build_network.py` and `python scripts/build_demand.py`).

## The six junctions

| Light | Streets | Bus lines |
|---|---|---|
| J1 | Av. Habib Bourguiba x Place du 14 Janvier 2011 | L1_west, L1_east |
| J2 | Av. Habib Bourguiba x Av. de France | L1_west, L1_east, L2_south, L3_south |
| J3 | Rue Saad Zagloul x Av. Moncef Bey | L3_south |
| J4 | Av. Habib Thameur x Rue de Rome | L1_east, L2_south, L3_south |
| J5 | Av. Habib Thameur x Rue de Sparte | L2_south |
| J6 | Av. Habib Bourguiba x Rue d'Alger | L1_west |

Details, OSM node ids and signal plans: `scenarios/tunis-centre-6j/junctions.json`.
Bus lines, event places and the demand level for this map: `config/networks/tunis6j.yaml`.

## The hierarchy

| Level | Component | Role |
|---|---|---|
| Junction (x6) | 5 agents | traffic light (max-pressure / predictive / RL), pedestrian, transit priority, emergency priority, sensor health |
| Junction (x6) | Master | resolves requests (safety > emergency > supermaster directive > transit > pedestrian > normal); the only writer of its light |
| Network | Supermaster | runs 8 network agents every 5 s, sends directives, never writes a light |
| Network | 8 agents | demand forecast, incident detection, rerouting, emergency route, corridor, transit monitor, weather, notification |
| Synapse | Explainer, alert writer, operator copilot | traffix3's language layer (EN/FR/AR, optional LLM); no path to the simulation |
| Synapse | **CoFlow Synapse** | `traffix/synapse/coflow_bridge.py`: verified / template / abstain over the decision log, seven-field provenance |

## CoFlow Synapse API

Each decision in the log becomes a CoFlow `EvidenceEvent`. The policy corpus is
the reason-code table in `traffix/core/decision_log.py`.

```text
POST /api/synapse/explain  {"decision_id": 337}
POST /api/synapse/audit    {"decision_id": 337, "claim": "J1 held green for ambulance 2"}
GET  /api/synapse/metrics
```

- `verified`: the decision's reason code is in the corpus and is cited.
- `template`: no citation available; answer built from recorded facts only.
- `abstain`: unknown decision id, or a claim the recorded facts do not support.

The analyst page shows a **Verify with CoFlow Synapse** button under each decision.

## Honest notes

- The real street grid has many unsignalised side streets that yield; car waits
  are higher than on the schematic network. `demand.base_vehicles_per_hour` is
  2400 for this map (`config/networks/tunis6j.yaml`), not 4000.
- Models in `models/` were retrained on this map with
  `python scripts/train.py --skip-tune --skip-rl`. Exceptions, recorded in
  `models/metrics.json`:
  - sensor health: the retrained model scored F1 0.62 against 0.98 for its
    rule, so no model file is shipped and the agent uses the rule;
  - incident detection: too few labelled incidents on this map to retrain, so
    the schematic-network model is still used;
  - tuned traffic-light parameters and the RL policy still come from the
    schematic network. Run the full `python scripts/train.py` (30-60 min) to
    retune them for Tunis.
