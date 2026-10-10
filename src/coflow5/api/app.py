from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from coflow5.api.store import EvidenceStore
from coflow5.synapse.service import SynapseService

DEFAULT_EVIDENCE_ROOT = Path(__file__).resolve().parents[3] / "deploy" / "evidence"
MAX_EVENTS_PER_PAGE = 100
MAX_RUNS_PER_COMPARE = 5
EVENT_IDS_QUERY = Query(default=None)
RUN_IDS_QUERY = Query(default=[])


def create_app(
    evidence_root: Path | None = None,
    synapse_service: SynapseService | None = None,
    profile: str | None = None,
) -> FastAPI:
    root = Path(evidence_root or os.environ.get("EVIDENCE_ROOT") or DEFAULT_EVIDENCE_ROOT)
    store = EvidenceStore(root)
    active_profile = profile or os.environ.get("COFLOW5_PROFILE", "HOSTED")
    if active_profile not in {"HOSTED", "LOCAL_RUNNER"}:
        raise ValueError("COFLOW5_PROFILE must be HOSTED or LOCAL_RUNNER")
    app = FastAPI(
        title="CoFlow-5 Synapse read-only API",
        description="Serves tagged evidence bundles. Does not run SUMO or actuate signals.",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict[str, object]:
        return {
            "status": "ok",
            "actuates": False,
            "sumo": False,
            "evidence_root": str(store.root),
            "claim_flags": [
                "simulation is not deployment evidence",
                "no lives saved",
                "no measured air quality",
                "no best-episode headline",
            ],
        }

    @app.get("/metrics")
    def metrics() -> dict[str, object]:
        if synapse_service is None:
            return {
                "request_count": 0,
                "abstention_rate": 0.0,
                "fallback_rate": 0.0,
            }
        return synapse_service.metrics()

    @app.get("/runs")
    def list_runs() -> dict[str, object]:
        return {"runs": store.list_runs()}

    @app.get("/runs/{run_id}")
    def get_run(run_id: str) -> dict[str, object]:
        try:
            return store.load_manifest(run_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail="unknown run_id") from exc

    @app.get("/runs/{run_id}/artifacts/{name}")
    def get_artifact(run_id: str, name: str) -> Response:
        try:
            payload, suffix = store.load_artifact(run_id, name)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail="unknown artifact") from exc
        media = "application/json" if suffix == ".json" else "text/plain; charset=utf-8"
        if suffix == ".md":
            media = "text/markdown; charset=utf-8"
        return Response(content=payload, media_type=media)

    @app.get("/events")
    def list_events(
        event_ids: list[str] | None = EVENT_IDS_QUERY,
    ) -> dict[str, object]:
        if event_ids is None:
            event_ids = []
        if len(event_ids) > MAX_EVENTS_PER_PAGE:
            raise HTTPException(status_code=422, detail="events-per-page limit exceeded")
        if synapse_service is None:
            return {"events": []}
        return {"events": synapse_service.event_summaries(event_ids)}

    @app.get("/comparisons")
    def compare_runs(
        run_ids: list[str] = RUN_IDS_QUERY,
    ) -> dict[str, object]:
        if not run_ids or len(run_ids) > MAX_RUNS_PER_COMPARE:
            raise HTTPException(status_code=422, detail="runs-per-compare limit exceeded")
        runs = []
        for run_id in run_ids:
            try:
                runs.append(store.load_manifest(run_id))
            except FileNotFoundError as exc:
                raise HTTPException(status_code=404, detail="unknown run_id") from exc
        return {"runs": runs}

    idempotent_results: dict[tuple[str, str], dict[str, object]] = {}
    proposals: dict[str, dict[str, object]] = {}

    def product_request(
        payload: dict[str, object],
        idempotency_key: str | None,
        operation: str,
    ) -> dict[str, object]:
        if synapse_service is None:
            raise HTTPException(status_code=503, detail="Synapse service unavailable")
        if not idempotency_key:
            raise HTTPException(status_code=400, detail="Idempotency-Key is required")
        question = payload.get("question", payload.get("claim"))
        event_id = payload.get("event_id")
        if not isinstance(question, str) or not isinstance(event_id, str):
            raise HTTPException(status_code=422, detail="question/claim and event_id are required")
        policy_id = payload.get("policy_id")
        if policy_id is not None and not isinstance(policy_id, str):
            raise HTTPException(status_code=422, detail="policy_id must be a string")
        key = (operation, idempotency_key)
        cached = idempotent_results.get(key)
        if cached is not None:
            return cached
        try:
            if operation == "explanations":
                result = synapse_service.explain(
                    question, event_id=event_id, policy_id=policy_id
                )
            else:
                result = synapse_service.audit(
                    question, event_id=event_id, policy_id=policy_id
                )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        response = {
            "fallback": result.fallback,
            "answer": result.answer,
            "citations": list(result.citations),
            "provenance": result.provenance.as_dict(),
        }
        idempotent_results[key] = response
        return response

    @app.post("/explanations")
    def explain(
        payload: dict[str, object],
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> dict[str, object]:
        return product_request(payload, idempotency_key, "explanations")

    @app.post("/audits")
    def audit(
        payload: dict[str, object],
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> dict[str, object]:
        return product_request(payload, idempotency_key, "audits")

    @app.get("/proposals")
    def list_proposals() -> dict[str, object]:
        return {"proposals": list(proposals.values())}

    @app.post("/proposals", status_code=201)
    def create_proposal(payload: dict[str, object]) -> dict[str, object]:
        if active_profile != "LOCAL_RUNNER":
            raise HTTPException(status_code=405, detail="proposals require LOCAL_RUNNER")
        proposal_id = "proposal-" + uuid4().hex
        proposal = {
            "proposal_id": proposal_id,
            "status": "pending_approval",
            "parent_run_id": payload.get("run_id"),
            "request": payload,
        }
        proposals[proposal_id] = proposal
        return proposal

    @app.post("/proposals/{proposal_id}/approve")
    def approve_proposal(proposal_id: str) -> dict[str, object]:
        if active_profile != "LOCAL_RUNNER":
            raise HTTPException(status_code=405, detail="approvals require LOCAL_RUNNER")
        proposal = proposals.get(proposal_id)
        if proposal is None:
            raise HTTPException(status_code=404, detail="unknown proposal")
        if proposal["status"] != "pending_approval":
            raise HTTPException(status_code=409, detail="proposal is not pending approval")
        proposal["status"] = "approved"
        proposal["approved_run_id"] = "run-" + uuid4().hex
        return proposal

    return app


app = create_app()
