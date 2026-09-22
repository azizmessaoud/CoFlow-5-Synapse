import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from coflow5.evidence.a4_a5_artifacts import (
    DECISION_SCHEMA,
    FORECAST_EVALUATION_SCHEMA,
    MESSAGE_SCHEMA,
    SUSTAINABILITY_KPI_SCHEMA,
    generate_a4_a5_artifacts,
)

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = {
    "run_manifest.json", "messages.parquet", "decision_events.parquet",
    "forecast-evaluation.parquet", "sustainability-kpis.parquet",
}


@pytest.fixture(scope="module")
def artifacts(tmp_path_factory: pytest.TempPathFactory) -> Path:
    destination = tmp_path_factory.mktemp("row10-a4-a5") / "artifacts"
    generate_a4_a5_artifacts(ROOT, destination)
    return destination


def rows(artifacts: Path, name: str) -> list[dict]:
    return pq.read_table(artifacts / name).to_pylist()


def test_exact_artifacts_are_hash_bound_joined_and_schema_exact(artifacts: Path) -> None:
    assert {p.name for p in artifacts.iterdir()} == REQUIRED
    manifest = json.loads((artifacts / "run_manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "completed" and manifest["immutable"] is True
    assert manifest["backend"] == "deterministic-fixture"
    assert manifest["controller"] == "cooperative-max-pressure-with-a4-a5-advice"
    assert manifest["scenario_hash"] == "sha256:" + hashlib.sha256(
        (ROOT / "harness/work/10-a4-a5/contract.json").read_bytes()
    ).hexdigest()
    refs = {item["path"]: item for item in manifest["artifact_references"]}
    assert set(refs) == REQUIRED - {"run_manifest.json"}
    schemas = {
        "messages.parquet": MESSAGE_SCHEMA,
        "decision_events.parquet": DECISION_SCHEMA,
        "forecast-evaluation.parquet": FORECAST_EVALUATION_SCHEMA,
        "sustainability-kpis.parquet": SUSTAINABILITY_KPI_SCHEMA,
    }
    for name, schema in schemas.items():
        path = artifacts / name
        table = pq.read_table(path)
        assert table.schema == schema
        assert "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest() == refs[name]["sha256"]
        assert table.num_rows == refs[name]["rows"]
        assert set(table["run_id"].to_pylist()) == {manifest["run_id"]}
        assert set(table["scenario_hash"].to_pylist()) == {manifest["scenario_hash"]}


def test_forecast_ladder_and_classifications_are_visible_without_leakage(artifacts: Path) -> None:
    forecast = rows(artifacts, "forecast-evaluation.parquet")
    by_model = {row["model_name"]: row for row in forecast if row["record_kind"] == "model_score"}
    assert set(by_model) == {"persistence", "simple_autoregression", "lightgbm"}
    assert by_model["persistence"]["status"] == "evaluated"
    assert by_model["simple_autoregression"]["status"] == "evaluated"
    assert by_model["lightgbm"]["status"] == "not_available_not_accepted"
    assert by_model["simple_autoregression"]["fit_end_time"] < by_model["simple_autoregression"]["evaluation_start_time"]
    split_rows = [row for row in forecast if row["record_kind"] == "split"]
    assert [row["split_name"] for row in split_rows] == ["train", "validation", "test"]
    assert split_rows[0]["split_end_time"] < split_rows[1]["split_start_time"]
    assert split_rows[1]["split_end_time"] < split_rows[2]["split_start_time"]
    classifications = {row["classification"] for row in forecast if row["record_kind"] == "classification"}
    assert classifications == {
        "normal", "detected_anomaly", "likely_incident", "congestion",
        "stale_data", "insufficient_data",
    }

    fallback = {row["split_name"]: row for row in forecast if row["record_kind"] == "fallback"}
    assert set(fallback) == {"silent", "stale", "unavailable", "malformed"}
    assert fallback["silent"]["status"] == fallback["stale"]["status"] == "empty"
    assert fallback["unavailable"]["status"] == "unavailable"
    assert fallback["malformed"]["status"] == "malformed"
    assert all(row["model_name"] == "cooperative_max_pressure" for row in fallback.values())
    assert all("decision_reason=MAX_PRESSURE_LOCAL_ONLY" in row["evidence_basis"] for row in fallback.values())
    assert all("safety_reason=ACCEPTED" in row["evidence_basis"] for row in fallback.values())
    assert all("a1_signal_writes=1; a4_signal_writes=0" in row["evidence_basis"] for row in fallback.values())


def test_a5_decisions_and_link_kpis_are_honest_and_joined(artifacts: Path) -> None:
    messages = rows(artifacts, "messages.parquet")
    decisions = rows(artifacts, "decision_events.parquet")
    eco = {row["message_id"]: row for row in messages if row["source_agent"] == "A5_SUSTAINABILITY" and row["record_kind"] == "advice"}
    replies = [row for row in messages if row["record_kind"] == "reply"]
    assert len(eco) == len(decisions) == len(replies) == 3
    assert {row["referenced_message_id"] for row in decisions} == set(eco)
    assert {row["referenced_message_id"] for row in replies} == set(eco)
    assert len({row["event_id"] for row in decisions}) == len(decisions)
    by_id = {row["referenced_message_id"]: row for row in decisions}
    assert by_id["eco-accepted"]["accepted"] is True
    assert by_id["eco-blocked"]["reason_code"] == "REJECTED_DOWNSTREAM_BLOCKED"
    assert by_id["eco-lower-priority"]["reason_code"] == "REJECTED_HIGHER_PRIORITY_REQUEST"
    assert all(row["specialist_signal_write"] is False for row in decisions)

    kpis = rows(artifacts, "sustainability-kpis.parquet")
    assert {row["link_id"] for row in kpis} == {"school-link", "residential-link"}
    assert all(row["sensitive"] and row["proxy_label"] == "SUMO/HBEFA emission proxy — not measured air quality" for row in kpis)
    assert {row["classification"] for row in kpis} == {"improved", "worsened"}
    assert any(row["co2_delta_mg_s"] < 0 for row in kpis)
    assert any(row["co2_delta_mg_s"] > 0 for row in kpis)
    assert all("simulation fixture" in row["claim_boundary"] for row in kpis)
