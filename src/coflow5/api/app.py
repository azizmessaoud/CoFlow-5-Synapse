from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from coflow5.api.errors import STATUS, EvidenceError
from coflow5.api.store import EvidenceStore

DEFAULT_EVIDENCE_ROOT = Path(__file__).resolve().parents[3] / "deploy" / "evidence"


def create_app(evidence_root: Path | None = None, bundle_ids: tuple[str, ...] | None = None) -> FastAPI:
    root = Path(evidence_root or os.environ.get("EVIDENCE_ROOT") or DEFAULT_EVIDENCE_ROOT)
    store = EvidenceStore(root, bundle_ids=bundle_ids)
    app = FastAPI(
        title="CoFlow-5 Synapse read-only API",
        description="Serves hash-bound evidence bundles. Does not run SUMO or actuate signals.",
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.exception_handler(EvidenceError)
    def evidence_error(_request: object, exc: EvidenceError) -> JSONResponse:
        return JSONResponse({"error": exc.code, "detail": exc.detail}, status_code=STATUS[exc.code])

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
        return store.get_run(run_id)

    @app.get("/runs/{run_id}/events")
    def events(run_id: str, limit: int | None = Query(default=None), offset: int | None = Query(default=None)) -> dict[str, object]:
        return store.events(run_id, limit, offset)

    @app.get("/runs/{run_id}/kpis")
    def kpis(run_id: str, limit: int | None = Query(default=None), offset: int | None = Query(default=None)) -> dict[str, object]:
        return store.kpis(run_id, limit, offset)

    @app.get("/runs/{run_id}/graph-frames")
    def graph_frames(run_id: str, limit: int | None = Query(default=None), offset: int | None = Query(default=None)) -> dict[str, object]:
        return store.graph_frames(run_id, limit, offset)

    @app.get("/runs/{run_id}/explanations")
    def explanations(run_id: str, limit: int | None = Query(default=None), offset: int | None = Query(default=None)) -> dict[str, object]:
        return store.explanations(run_id, limit, offset)

    @app.get("/runs/{run_id}/audits")
    def audits(run_id: str, limit: int | None = Query(default=None), offset: int | None = Query(default=None)) -> dict[str, object]:
        return store.audits(run_id, limit, offset)

    @app.get("/runs/{run_id}/citations")
    def citations(run_id: str, limit: int | None = Query(default=None), offset: int | None = Query(default=None)) -> dict[str, object]:
        return store.citations(run_id, limit, offset)

    @app.get("/runs/{run_id}/golden")
    def golden(run_id: str) -> dict[str, object]:
        return store.golden(run_id)

    @app.get("/runs/{run_id}/limitations")
    def limitations(run_id: str) -> dict[str, object]:
        return store.limitations(run_id)

    @app.get("/runs/{run_id}/artifacts/{name}")
    def get_artifact(run_id: str, name: str) -> Response:
        payload, suffix = store.load_artifact(run_id, name)
        media = "application/json" if suffix == ".json" else "text/plain; charset=utf-8"
        if suffix == ".md":
            media = "text/markdown; charset=utf-8"
        if suffix == ".parquet":
            media = "application/vnd.apache.parquet"
        return Response(content=payload, media_type=media)

    return app


app = create_app()
