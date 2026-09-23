from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient

from coflow5.api.app import create_app
from coflow5.api.store import EvidenceStore

ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "11111111-1111-4111-8111-111111111111"
EVENT_ID = "22222222-2222-4222-8222-222222222222"
REQUEST_ID = "golden-s2-cited"
CHUNK_ID = "chunk-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
GRAPH_HASH = "sha256:graph"
SCENARIO_HASH = "sha256:scenario"


def _sha(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def seal_bundle(root: Path, bundle_id: str, artifacts: dict[str, object], *, gate_patch: dict | None = None) -> Path:
    bundle = root / bundle_id
    written: dict[str, str] = {}
    for name, payload in artifacts.items():
        path = bundle / name
        _write(path, payload)
        written[name.replace("\\", "/")] = _sha(path)
    contract = {"id": bundle_id, "serves": "frozen-evidence"}
    contract_path = bundle / "contract.json"
    _write(contract_path, contract)
    gate = {
        "pass": True,
        "openDeltas": 0,
        "decidedBy": "tests-and-files",
        "contractHash": _sha(contract_path),
        "artifactHashes": written,
    }
    if gate_patch:
        gate.update(gate_patch)
    _write(bundle / "gate.json", gate)
    return bundle


def valid_artifacts() -> dict[str, object]:
    return {
        "artifacts/run_manifest.json": {
            "run_id": RUN_ID,
            "scenario_hash": SCENARIO_HASH,
            "graph_hash": GRAPH_HASH,
            "claim_boundary": "fixture boundary",
            "runs": [
                {"run_id": "33333333-3333-4333-8333-333333333333", "scenario_hash": SCENARIO_HASH, "graph_hash": GRAPH_HASH}
            ],
        },
        "artifacts/events.json": {
            "events": [
                {
                    "run_id": RUN_ID,
                    "scenario_hash": SCENARIO_HASH,
                    "graph_hash": GRAPH_HASH,
                    "event_id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
                    "message_id": None,
                    "simulation_time": 5.0,
                },
                {
                    "run_id": RUN_ID,
                    "scenario_hash": SCENARIO_HASH,
                    "graph_hash": GRAPH_HASH,
                    "event_id": EVENT_ID,
                    "message_id": "message-kept",
                    "simulation_time": 0.0,
                },
            ]
        },
        "artifacts/run_kpis.json": {
            "kpis": [
                {"run_id": RUN_ID, "scenario_hash": SCENARIO_HASH, "graph_hash": GRAPH_HASH, "seed": 23, "controller": "fixed-time"},
                {"run_id": RUN_ID, "scenario_hash": SCENARIO_HASH, "graph_hash": GRAPH_HASH, "seed": 11, "controller": "actuated"},
            ]
        },
        "artifacts/graph_frames.json": {
            "frames": [
                {"run_id": RUN_ID, "scenario_hash": SCENARIO_HASH, "graph_hash": GRAPH_HASH, "simulation_time": 5.0, "seed": 1},
                {"run_id": RUN_ID, "scenario_hash": SCENARIO_HASH, "graph_hash": GRAPH_HASH, "simulation_time": 0.0, "seed": 1},
            ]
        },
        "artifacts/explanations.json": {
            "explanations": [
                {
                    "request_id": "golden-s2-abstain",
                    "run_id": RUN_ID,
                    "event_facts": {"run_id": RUN_ID, "event_id": EVENT_ID, "scenario_hash": SCENARIO_HASH, "graph_hash": GRAPH_HASH},
                    "citations": [],
                    "status": "abstained",
                },
                {
                    "request_id": REQUEST_ID,
                    "run_id": RUN_ID,
                    "event_facts": {"run_id": RUN_ID, "event_id": EVENT_ID, "scenario_hash": SCENARIO_HASH, "graph_hash": GRAPH_HASH},
                    "citations": [
                        {"chunk_id": CHUNK_ID, "request_id": REQUEST_ID, "source_id": "adr-0001"},
                        {"chunk_id": "chunk-0000000000000000000000000000000000000000000000000000000000000000", "request_id": REQUEST_ID, "source_id": "brief"},
                    ],
                    "status": "answered",
                },
            ]
        },
        "artifacts/evidence_audits.json": {
            "audits": [
                {"request_id": "golden-s3-pass", "status": "pass", "references": [{"event_id": EVENT_ID}]},
                {"request_id": "golden-s3-abstain", "status": "abstained", "references": []},
            ]
        },
        "artifacts/golden_results.json": {
            "all_passed": True,
            "metrics": {"citation_validity": {"rate": 1.0}},
        },
        "artifacts/limitations.json": {"limitations": ["fixture limit", "no lives saved"]},
    }


def client_for(root: Path) -> TestClient:
    return TestClient(create_app(root))


def test_health_declares_no_sumo_and_no_actuation(tmp_path: Path) -> None:
    body = client_for(tmp_path).get("/health").json()
    assert body["status"] == "ok"
    assert body["actuates"] is False
    assert body["sumo"] is False
    assert "no lives saved" in body["claim_flags"]


def test_valid_hash_bound_bundle_is_listed_and_typed(tmp_path: Path) -> None:
    seal_bundle(tmp_path, "fixture-green", valid_artifacts())
    client = client_for(tmp_path)
    runs = client.get("/runs").json()["runs"]
    assert [row["run_id"] for row in runs] == [
        RUN_ID,
        "33333333-3333-4333-8333-333333333333",
    ]
    manifest = client.get(f"/runs/{RUN_ID}").json()
    assert manifest["run_id"] == RUN_ID
    assert manifest["scenario_hash"] == SCENARIO_HASH
    assert manifest["graph_hash"] == GRAPH_HASH
    events = client.get(f"/runs/{RUN_ID}/events").json()
    assert [row["event_id"] for row in events["items"]] == [
        EVENT_ID,
        "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
    ]
    assert events["items"][0]["message_id"] == "message-kept"
    assert events["items"][1]["message_id"] is None
    kpis = client.get(f"/runs/{RUN_ID}/kpis").json()["items"]
    assert [row["seed"] for row in kpis] == [11, 23]
    frames = client.get(f"/runs/{RUN_ID}/graph-frames").json()["items"]
    assert [row["simulation_time"] for row in frames] == [0.0, 5.0]
    explanations = client.get(f"/runs/{RUN_ID}/explanations").json()["items"]
    assert [row["request_id"] for row in explanations] == ["golden-s2-abstain", REQUEST_ID]
    audits = client.get(f"/runs/{RUN_ID}/audits").json()["items"]
    assert [row["request_id"] for row in audits] == ["golden-s3-abstain", "golden-s3-pass"]
    citations = client.get(f"/runs/{RUN_ID}/citations").json()["items"]
    assert [row["chunk_id"] for row in citations][0] == "chunk-0000000000000000000000000000000000000000000000000000000000000000"
    assert citations[1]["chunk_id"] == CHUNK_ID
    golden = client.get(f"/runs/{RUN_ID}/golden").json()
    assert golden["metrics"]["citation_validity"]["rate"] == 1.0
    limits = client.get(f"/runs/{RUN_ID}/limitations").json()
    assert limits["limitations"] == ["fixture limit", "no lives saved", "fixture boundary"]


def test_pagination_is_bounded_and_stable(tmp_path: Path) -> None:
    seal_bundle(tmp_path, "fixture-green", valid_artifacts())
    client = client_for(tmp_path)
    page = client.get(f"/runs/{RUN_ID}/events?limit=1&offset=1").json()
    assert page["total"] == 2
    assert page["limit"] == 1
    assert page["offset"] == 1
    assert page["items"][0]["event_id"] == "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
    rejected = client.get(f"/runs/{RUN_ID}/events?limit=51")
    assert rejected.status_code == 422
    assert rejected.json()["error"] == "validation"


def test_arbitrary_manifest_bad_gate_and_corrupt_bytes_are_rejected(tmp_path: Path) -> None:
    loose = tmp_path / "loose"
    _write(loose / "run_manifest.json", {"run_id": "loose-run", "secret_marker": "do-not-serve"})
    seal_bundle(
        tmp_path,
        "red-gate",
        {"artifacts/run_manifest.json": {"run_id": "red-run", "scenario_hash": SCENARIO_HASH, "secret_marker": "hidden"}},
        gate_patch={"pass": False},
    )
    seal_bundle(
        tmp_path,
        "bad-contract",
        {"artifacts/run_manifest.json": {"run_id": "bad-contract-run", "scenario_hash": SCENARIO_HASH}},
        gate_patch={"contractHash": "sha256:" + "0" * 64},
    )
    bundle = seal_bundle(
        tmp_path,
        "corrupt",
        {"artifacts/run_manifest.json": {"run_id": "corrupt-run", "scenario_hash": SCENARIO_HASH, "secret_marker": "hidden"}},
    )
    events = bundle / "artifacts" / "events.json"
    _write(events, {"events": [{"event_id": "tampered", "secret_marker": "hidden"}]})
    gate = json.loads((bundle / "gate.json").read_text(encoding="utf-8"))
    gate["artifactHashes"]["artifacts/events.json"] = "sha256:" + "ab" * 32
    _write(bundle / "gate.json", gate)

    client = client_for(tmp_path)
    listed = [row["run_id"] for row in client.get("/runs").json()["runs"]]
    assert "loose-run" not in listed
    assert "red-run" not in listed
    assert "bad-contract-run" not in listed
    assert "corrupt-run" not in listed
    assert client.get("/runs/loose-run").status_code == 404
    assert client.get("/runs/loose-run").json()["error"] == "not_found"
    assert client.get("/runs/red-run").json()["error"] == "validation"
    assert client.get("/runs/bad-contract-run").json()["error"] == "validation"
    corrupt = client.get("/runs/corrupt-run")
    assert corrupt.status_code == 409
    assert corrupt.json()["error"] == "corrupt_evidence"
    assert "secret_marker" not in corrupt.text


def test_path_traversal_and_mutation_routes_are_rejected(tmp_path: Path) -> None:
    seal_bundle(tmp_path, "fixture-green", valid_artifacts())
    client = client_for(tmp_path)
    escaped = client.get(f"/runs/{RUN_ID}/artifacts/../contract.json")
    assert escaped.status_code == 404
    assert client.get("/runs/../contract.json").status_code == 404
    for method in ("post", "put", "patch", "delete"):
        response = getattr(client, method)("/runs")
        assert response.status_code == 405
    surface = {route.path: sorted(route.methods) for route in client.app.routes if hasattr(route, "methods")}
    assert all(methods == ["GET", "HEAD"] or "POST" not in methods for methods in surface.values())


def test_missing_evidence_class_is_unavailable(tmp_path: Path) -> None:
    seal_bundle(
        tmp_path,
        "partial",
        {"artifacts/run_manifest.json": {"run_id": "partial-run", "scenario_hash": SCENARIO_HASH, "graph_hash": GRAPH_HASH}},
    )
    response = client_for(tmp_path).get("/runs/partial-run/graph-frames")
    assert response.status_code == 503
    assert response.json()["error"] == "unavailable"


def test_api_source_has_no_actuation_or_sumo_binding() -> None:
    forbidden = {"traci", "libsumo", "subprocess", "socket", "requests", "urllib", "httpx", "openai"}
    api = ROOT / "src" / "coflow5" / "api"
    for path in api.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        assert not (imported & forbidden)
        source = path.read_text(encoding="utf-8").lower()
        assert "setphase" not in source
        assert "signal_executor" not in source
        assert "sumo_adapter" not in source


def test_gated_graph_and_synapse_bundles_keep_real_identities() -> None:
    store = EvidenceStore(
        ROOT / "harness" / "work",
        bundle_ids=("10f-graph-growth-benchmark", "12-synapse-agents"),
    )
    runs = {row["run_id"] for row in store.list_runs()}
    assert "a995c95e-340e-5610-893a-6aef391551b1" in runs
    assert "015ad194-355a-5ef2-bef6-420ee5fa764f" in runs
    found = None
    offset = 0
    while found is None:
        page = store.events("0db24e7b-133e-5b79-ba0c-171f1c0aaf34", limit=50, offset=offset)
        found = next((row for row in page["items"] if row["event_id"] == "9fa9db22-b826-53cc-92eb-319b50688327"), None)
        offset += 50
        assert offset <= page["total"] + 50
    assert found["run_id"] == "0db24e7b-133e-5b79-ba0c-171f1c0aaf34"
    assert found["message_id"] is None
    explained = store.explanations("0db24e7b-133e-5b79-ba0c-171f1c0aaf34", limit=5, offset=0)
    assert explained["items"][0]["request_id"] == "golden-s2-abstain"
    assert explained["items"][0]["event_facts"]["event_id"] == "9fa9db22-b826-53cc-92eb-319b50688327"
