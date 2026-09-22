from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from coflow5.evidence import BundleValidationError, validate_bundle
from coflow5.evidence.schemas import (
    DecisionEvent,
    FaultEvent,
    MessageRecord,
    RunKpiRecord,
    StateRecord,
    TransitionEvent,
    TripRecord,
)

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "harness" / "work" / "02-evidence-bundle" / "artifacts"


def _copy_bundle(tmp_path: Path) -> Path:
    destination = tmp_path / "bundle"
    shutil.copytree(ARTIFACTS, destination)
    return destination


def _sha256(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def test_all_six_evidence_schema_families_carry_run_and_scenario_identity() -> None:
    models = [StateRecord, MessageRecord, DecisionEvent, FaultEvent, TransitionEvent, TripRecord, RunKpiRecord]
    for model in models:
        assert {"run_id", "scenario_hash"} <= set(model.model_fields)
    assert "event_id" in DecisionEvent.model_fields
    assert "event_id" in FaultEvent.model_fields
    assert "event_id" in TransitionEvent.model_fields
    assert "message_id" in MessageRecord.model_fields


def test_duckdb_audit_joins_every_parquet_row_to_one_manifest() -> None:
    audit = validate_bundle(ARTIFACTS)
    assert audit["valid"] is True
    assert audit["join_checks"] == {
        "missing": 0,
        "duplicate": 0,
        "cross_scenario": 0,
        "orphan": 0,
    }
    assert audit["row_counts"]["state.parquet"] > 0
    assert audit["row_counts"]["messages.parquet"] == 2
    assert audit["row_counts"]["decision_events.parquet"] == 2
    assert audit["row_counts"]["trips.parquet"] == 20
    assert audit["row_counts"]["run_kpis.parquet"] == 1


def test_incomplete_bundle_is_invalidated(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    (bundle / "trips.parquet").unlink()
    with pytest.raises(BundleValidationError) as caught:
        validate_bundle(bundle)
    assert caught.value.audit["valid"] is False
    assert caught.value.audit["artifact_checks"]["missing"] > 0


def test_corrupt_finalized_artifact_is_invalidated_by_manifest_hash(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    state = bundle / "state.parquet"
    state.write_bytes(state.read_bytes()[:64])
    with pytest.raises(BundleValidationError) as caught:
        validate_bundle(bundle)
    assert caught.value.audit["valid"] is False
    assert caught.value.audit["artifact_checks"]["corrupt"] > 0


def test_cross_scenario_row_is_rejected_even_with_a_matching_artifact_hash(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    state_path = bundle / "state.parquet"
    table = pq.read_table(state_path)
    rows = table.to_pylist()
    rows[0]["scenario_hash"] = "sha256:" + "0" * 64
    pq.write_table(pa.Table.from_pylist(rows, schema=table.schema), state_path, compression="zstd", version="2.6")

    manifest_path = bundle / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for ref in manifest["artifact_references"]:
        if ref["path"] == "state.parquet":
            ref["sha256"] = _sha256(state_path)
            ref["bytes"] = state_path.stat().st_size
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with pytest.raises(BundleValidationError) as caught:
        validate_bundle(bundle)
    assert caught.value.audit["valid"] is False
    assert caught.value.audit["join_checks"]["cross_scenario"] > 0


def test_nonterminal_manifest_cannot_enter_evaluation(tmp_path: Path) -> None:
    bundle = _copy_bundle(tmp_path)
    manifest_path = bundle / "run_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["status"] = "invalid"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with pytest.raises(BundleValidationError) as caught:
        validate_bundle(bundle)
    assert caught.value.audit["valid"] is False
    assert caught.value.audit["manifest_status"] == "invalid"
