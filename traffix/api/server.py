"""
Backend API for the React frontend. The frontend only talks to this server,
which reads from the supermaster's live run; it never reaches the masters or SUMO.

  GET  /api/scenarios                       list of scenarios
  POST /api/start?scenario=rain&speed=4     start a live run
  POST /api/stop
  GET  /api/state                           full live snapshot
  GET  /api/network                         map geometry
  GET  /api/notifications?persona=bus_driver
  GET  /api/decisions?limit=200&q=ambulance
  GET  /api/places                          trip planner start and end points
  GET  /api/trip?origin=EDGE&destination=EDGE   personal route, delay, alerts, alternative
  POST /api/ask  {"question": "...", "lang": "en|fr|ar"}   explainer agent (Synapse)
  GET  /api/copilot?lang=fr                 operator copilot summary + suggestions
  POST /api/copilot/report?lang=ar          incident report draft
  POST /api/copilot/decision                approve / dismiss a suggestion (recorded only)
  POST /api/synapse/explain {"decision_id": 412, "question": "..."}   CoFlow Synapse: verified/template/abstain
  POST /api/synapse/audit   {"decision_id": 412, "claim": "..."}      + seven-field provenance
  GET  /api/synapse/metrics                 abstention / fallback rates of this run's Synapse
  GET  /api/llm                             is a language model available?
  GET  /api/results                         experiment summary (if available)
  GET  /api/models                          training metrics
"""
import json
import os

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ..agents.network.explainer import ExplainerAgent
from ..core import config
from ..synapse.coflow_bridge import TraffixSynapse
from .live import LiveRun

app = FastAPI(title="TraffiX API")
SETTINGS = {"gui": False}       # set by scripts/run_live.py --gui
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
RUN = {"live": None}


class Question(BaseModel):
    question: str
    lang: str = "en"


class SynapseQuestion(BaseModel):
    decision_id: int
    question: str = "Why was this decision taken?"


class SynapseClaim(BaseModel):
    decision_id: int
    claim: str


class Decision(BaseModel):
    suggestion_id: str
    title: str
    decision: str          # "approve" | "dismiss"


def live():
    if RUN["live"] is None:
        raise HTTPException(409, "No live run. POST /api/start first.")
    return RUN["live"]


@app.get("/api/scenarios")
def scenarios():
    return [{"id": k, "start": v["start"], "description": v.get("description", ""),
             "events": list((v.get("events") or {}).keys())} for k, v in config.scenarios().items()]


LIVE_CONTROLLERS = ["traffix", "traffix_predictive", "traffix_rl", "traffix_rules", "junction_only"]


@app.get("/api/controllers")
def controllers():
    return LIVE_CONTROLLERS


@app.post("/api/start")
def start(scenario: str = "morning_peak", speed: float = 4.0, seed: int = 1, controller: str = "traffix"):
    if scenario not in config.scenarios():
        raise HTTPException(404, f"Unknown scenario {scenario}")
    if controller not in LIVE_CONTROLLERS:
        raise HTTPException(404, f"Unknown controller {controller}")
    if RUN["live"]:
        RUN["live"].stop()
    RUN["live"] = LiveRun(scenario, seed, speed, controller, gui=SETTINGS["gui"])
    RUN["live"].start()
    return {"started": scenario, "speed": speed, "controller": controller}


@app.post("/api/stop")
def stop():
    if RUN["live"]:
        RUN["live"].stop()
    return {"stopped": True}


@app.get("/api/state")
def state():
    return live().state() if RUN["live"] else {"status": "idle"}


@app.get("/api/network")
def network():
    return live().geometry


@app.get("/api/notifications")
def notifications(persona: str = "operator", limit: int = 50):
    items = [n for n in live().state().get("notifications", []) if n["persona"] == persona]
    return items[-limit:][::-1]


@app.get("/api/decisions")
def decisions(limit: int = 200, q: str = ""):
    lv = live()
    entries = lv.narrator.enrich(lv.log.entries) if hasattr(lv, "narrator") else lv.log.entries
    if q:
        entries = [e for e in entries if q.lower() in json.dumps(e, ensure_ascii=False).lower()]
    return entries[-limit:][::-1]


@app.get("/api/places")
def places():
    return live().places


@app.get("/api/trip")
def trip(origin: str, destination: str):
    """Personal trip: fastest route now, delay, alerts on the route, and an alternative."""
    return live().plan_trip(origin, destination)


@app.post("/api/ask")
def ask(body: Question):
    lv = live()
    tools = {"get_live_state": lambda: lv.copilot.context() if hasattr(lv, "copilot") else lv.state(),
             "get_results": lambda measure="": [r for r in results()["summary"]
                                                if measure.lower() in r["measure"].lower()][:120]}
    return ExplainerAgent(list(lv.log.entries), getattr(lv, "narrator", None)).ask(body.question, lang=body.lang,
                                                                                 tools=tools)


def synapse():
    """CoFlow Synapse over a frozen copy of the live decision log (rebuilt when the log grows)."""
    lv = live()
    entries = list(lv.log.entries)
    cached = getattr(lv, "_synapse", None)
    if cached is None:
        lv._synapse = TraffixSynapse(entries, run_id=f"live_{lv.controller}_{lv.scenario}_{lv.seed}",
                                     scenario=lv.meta)
    elif len(cached.entries) != len(entries):
        lv._synapse = cached.refreshed(entries)
    return lv._synapse


@app.post("/api/synapse/explain")
def synapse_explain(body: SynapseQuestion):
    return synapse().explain(body.question, body.decision_id)


@app.post("/api/synapse/audit")
def synapse_audit(body: SynapseClaim):
    return synapse().audit(body.claim, body.decision_id)


@app.get("/api/synapse/metrics")
def synapse_metrics():
    return synapse().metrics()


@app.get("/api/llm")
def llm_status():
    """Is a language model available? (ANTHROPIC_API_KEY set before starting the server)"""
    from ..synapse import llm
    from ..core import config as cfg
    s = cfg.agents()["synapse"]
    lv = RUN["live"]
    return {"available": llm.available(), "provider": llm.provider(), "languages": s["languages"],
            "models": {r: llm.model_for(r) for r in ("explainer", "copilot", "alert")} if llm.available() else {},
            "alerts": getattr(getattr(lv, "alert_writer", None), "stats", None)}


@app.get("/api/copilot")
def copilot(lang: str = "en"):
    return live().copilot.summary(lang)


@app.post("/api/copilot/report")
def copilot_report(lang: str = "en"):
    return live().copilot.report(lang)


@app.post("/api/copilot/decision")
def copilot_decision(body: Decision):
    lv = live()
    entry = lv.copilot.decide(body.suggestion_id, body.title, body.decision, lv.state().get("t", 0))
    return {"recorded": True, "log_id": entry, "applied": False}


@app.get("/api/results")
def results():
    """Experiment results produced by scripts/run_experiments.py + scripts/analyze.py."""
    def csv(name):
        p = config.path("results", name)
        try:
            return pd.read_csv(p).astype(object).where(lambda d: pd.notna(d), None).to_dict("records")
        except (FileNotFoundError, pd.errors.EmptyDataError):
            return []
    summary = csv("summary_by_persona.csv")
    return {"summary": summary, "significance": csv("significance.csv"),
            "has_chart": os.path.exists(config.path("results", "persona_charts.png")),
            "scenarios": list(dict.fromkeys(r["scenario"] for r in summary)),
            "controllers": [c for c in ["fixed", "actuated", "junction_only", "traffix_rules", "traffix",
                                        "traffix_predictive", "traffix_rl"]
                            if any(r["controller"] == c for r in summary)]}


@app.get("/api/results/chart")
def results_chart():
    p = config.path("results", "persona_charts.png")
    if not os.path.exists(p):
        raise HTTPException(404, "Run scripts/analyze.py first")
    return FileResponse(p, media_type="image/png")


@app.get("/api/models")
def models():
    p = config.path("models", "metrics.json")
    return json.load(open(p)) if os.path.exists(p) else {}


dist = config.path("frontend", "dist")
if os.path.isdir(dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist, "assets")), name="assets")

    @app.get("/{page:path}")
    def spa(page: str):
        """Any non-API path returns the React app, which handles the routing."""
        return FileResponse(os.path.join(dist, "index.html"))
