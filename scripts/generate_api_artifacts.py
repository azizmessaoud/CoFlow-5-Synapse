"""Write the Row 11 catalog from the gated Row 10f and Row 12 bundles."""

from __future__ import annotations

import ast
import json
from pathlib import Path

from coflow5.api.app import create_app
from coflow5.api.store import EvidenceStore

ROOT = Path(__file__).resolve().parents[1]
BUNDLES = ("10f-graph-growth-benchmark", "12-synapse-agents")
OUT = ROOT / "harness" / "work" / "11-api" / "artifacts"
GRAPH_RUN = "0db24e7b-133e-5b79-ba0c-171f1c0aaf34"
KNOWN_EVENT = "9fa9db22-b826-53cc-92eb-319b50688327"


def _dump(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    store = EvidenceStore(ROOT / "harness" / "work", bundle_ids=BUNDLES)
    accepted = []
    for bundle in store._accepted:
        accepted.append({
            "bundle_id": bundle.bundle_id,
            "primary_run_id": bundle.primary_run_id,
            "run_count": len(bundle.runs),
        })
    _dump(OUT / "validated_catalog.json", {
        "accepted_bundles": accepted,
        "rejected_run_count": len(store._rejected_runs),
        "served_run_count": len(store.list_runs()),
    })
    app = create_app(ROOT / "harness" / "work", bundle_ids=BUNDLES)
    routes = sorted(
        route.path for route in app.routes
        if getattr(route, "methods", None) and "GET" in route.methods and route.path.startswith("/")
    )
    _dump(OUT / "api_surface.json", {"methods": ["GET"], "paths": routes})
    found = None
    offset = 0
    while found is None:
        page = store.events(GRAPH_RUN, limit=50, offset=offset)
        found = next((row for row in page["items"] if row["event_id"] == KNOWN_EVENT), None)
        offset += 50
        if offset > page["total"] + 50:
            break
    if found is None:
        raise SystemExit("known graph event was not served")
    explanations = store.explanations(GRAPH_RUN, limit=20, offset=0)
    _dump(OUT / "sample_page.json", {
        "event_id": found["event_id"],
        "graph_hash": found["graph_hash"],
        "message_id": found["message_id"],
        "request_ids": [row["request_id"] for row in explanations["items"]],
        "run_id": found["run_id"],
        "scenario_hash": found["scenario_hash"],
    })
    forbidden = {"traci", "libsumo", "subprocess", "socket", "requests", "urllib", "httpx"}
    violations: list[str] = []
    for path in (ROOT / "src" / "coflow5" / "api").rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        violations.extend(sorted(imported & forbidden))
    _dump(OUT / "non_actuation_audit.json", {
        "actuates": False,
        "forbidden_imports": violations,
        "methods": ["GET"],
        "sumo_launch": False,
    })


if __name__ == "__main__":
    main()
