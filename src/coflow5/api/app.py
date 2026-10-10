from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from coflow5.api.store import EvidenceStore
from coflow5.synapse.service import SynapseService

DEFAULT_EVIDENCE_ROOT = Path(__file__).resolve().parents[3] / "deploy" / "evidence"


def create_app(
    evidence_root: Path | None = None,
    synapse_service: SynapseService | None = None,
) -> FastAPI:
    root = Path(evidence_root or os.environ.get("EVIDENCE_ROOT") or DEFAULT_EVIDENCE_ROOT)
    store = EvidenceStore(root)
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

    idempotent_results: dict[tuple[str, str], dict[str, object]] = {}

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

    return app


app = create_app()
