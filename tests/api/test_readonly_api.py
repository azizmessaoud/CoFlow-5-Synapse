from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from coflow5.api.app import create_app

FIXTURE_RUN = {
    "run_id": "demo-readonly-0001",
    "status": "fixture",
    "scenario_hash": "sha256:not-a-measured-run",
    "note": "Placeholder for hosted read-only demo. Not a SUMO evaluation result.",
}


def write_fixture(root: Path) -> None:
    bundle = root / "demo-readonly-0001"
    bundle.mkdir(parents=True)
    (bundle / "run_manifest.json").write_text(
        json.dumps(FIXTURE_RUN, indent=2) + "\n", encoding="utf-8"
    )
    (bundle / "gui-diagnosis.md").write_text(
        "Fixture note: no sumo-gui was launched for this placeholder.\n",
        encoding="utf-8",
    )


def test_health_declares_no_sumo_and_no_actuation(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["actuates"] is False
    assert body["sumo"] is False
    assert "no lives saved" in body["claim_flags"]


def test_lists_and_reads_tagged_bundle(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    client = TestClient(create_app(tmp_path))
    runs = client.get("/runs").json()["runs"]
    assert runs[0]["run_id"] == "demo-readonly-0001"
    assert runs[0]["scenario_hash"] == FIXTURE_RUN["scenario_hash"]
    manifest = client.get("/runs/demo-readonly-0001").json()
    assert manifest["status"] == "fixture"
    artifact = client.get("/runs/demo-readonly-0001/artifacts/gui-diagnosis.md")
    assert artifact.status_code == 200
    assert "no sumo-gui was launched" in artifact.text


def test_unknown_run_is_404(tmp_path: Path) -> None:
    client = TestClient(create_app(tmp_path))
    assert client.get("/runs/missing").status_code == 404


def test_artifact_name_cannot_escape_bundle(tmp_path: Path) -> None:
    write_fixture(tmp_path)
    client = TestClient(create_app(tmp_path))
    assert client.get("/runs/demo-readonly-0001/artifacts/../run_manifest.json").status_code == 404
