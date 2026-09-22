from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from coflow5.api.store import EvidenceStore

DEFAULT_EVIDENCE_ROOT = Path(__file__).resolve().parents[3] / "deploy" / "evidence"


def create_app(evidence_root: Path | None = None) -> FastAPI:
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
        allow_methods=["GET"],
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

    return app


app = create_app()
