from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "harness/work/10f-graph-growth-benchmark/artifacts"


def _hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def test_required_artifacts_are_manifest_bound_and_exact() -> None:
    manifest = json.loads((ARTIFACTS / "run_manifest.json").read_text(encoding="utf-8"))
    expected = {
        "graph.json", "demand_cells.json", "junction_states.parquet",
        "graph_frames.parquet", "decision_events.parquet", "trips.parquet",
        "run_kpis.parquet", "matched_growth_comparison.json", "growth_report.md",
        "native_smoke.json", "input_audit.json",
    }
    references = {row["path"]: row for row in manifest["artifact_references"]}
    assert set(references) == expected
    assert all(_hash(ARTIFACTS / name) == references[name]["sha256"] for name in expected)
    assert manifest["matrix_run_count"] == 80
    assert manifest["native_matrix_run_count"] == 0
    assert manifest["contract_hash"] == _hash(ROOT / "harness/work/10f-graph-growth-benchmark/contract.json")


def test_every_parquet_row_resolves_manifest_and_graph_identity() -> None:
    manifest = json.loads((ARTIFACTS / "run_manifest.json").read_text(encoding="utf-8"))
    identities = {row["run_id"]: row for row in manifest["runs"]}
    for name in ("junction_states.parquet", "graph_frames.parquet", "decision_events.parquet", "trips.parquet", "run_kpis.parquet"):
        rows = pq.read_table(ARTIFACTS / name).to_pylist()
        assert rows
        for row in rows:
            identity = identities[row["run_id"]]
            assert row["scenario_hash"] == identity["scenario_hash"] == manifest["scenario_hash"]
            assert row["graph_hash"] == identity["graph_hash"] == manifest["graph_hash"]
            assert row["seed"] == identity["seed"]
            assert row["controller"] == identity["controller"]
    decisions = pq.read_table(ARTIFACTS / "decision_events.parquet").to_pylist()
    assert len({row["event_id"] for row in decisions}) == len(decisions)
    assert all(row["message_id"] is None and json.loads(row["message_ids_json"]) == [] for row in decisions)


def test_graph_frames_are_five_second_read_only_snapshots() -> None:
    frames = pq.read_table(ARTIFACTS / "graph_frames.parquet").to_pylist()
    by_run = {}
    for row in frames:
        by_run.setdefault(row["run_id"], []).append(row)
        assert row["simulation_time"] % 5 == 0
        assert len(json.loads(row["nodes_json"])) == 4
        assert json.loads(row["messages_json"]) == [] and json.loads(row["faults_json"]) == []
        assert "read-only; cannot actuate SUMO" in json.loads(row["limitations_json"])
    assert len(by_run) == 80
    assert all(sorted(row["simulation_time"] for row in group) == list(range(0, 91, 5)) for group in by_run.values())


def test_fallback_probes_and_report_preserve_negative_results_and_claim_flags() -> None:
    graph = json.loads((ARTIFACTS / "graph.json").read_text(encoding="utf-8"))
    probes = {row["case"]: row for row in graph["fallback_probes"]}
    assert set(probes) == {"fresh", "stale", "missing", "identity-mismatch"}
    assert probes["stale"]["reason_code"] == "GRAPH_NEIGHBOUR_STALE_LOCAL_ONLY"
    assert probes["missing"]["reason_code"] == "GRAPH_NEIGHBOUR_UNAVAILABLE_LOCAL_ONLY"
    assert probes["identity-mismatch"]["reason_code"] == "GRAPH_IDENTITY_MISMATCH_LOCAL_ONLY"
    assert len({probes[name]["accepted_action"] for name in ("stale", "missing", "identity-mismatch")}) == 1
    comparison = json.loads((ARTIFACTS / "matched_growth_comparison.json").read_text(encoding="utf-8"))
    assert comparison["paired_group_count"] == 20
    assert comparison["winner_claim"] is None and comparison["significance_test_performed"] is False
    assert comparison["graph_completed_more_groups"] > 0
    assert comparison["graph_completed_fewer_groups"] > 0
    report = (ARTIFACTS / "growth_report.md").read_text(encoding="utf-8").lower()
    assert "not represented as 80 native sumo runs" in report
    assert "no winner" in report and "no lives saved" in report and "no" in report and "measured air quality" in report


def test_locked_rows_remain_hash_stable() -> None:
    audit = json.loads((ARTIFACTS / "input_audit.json").read_text(encoding="utf-8"))
    assert audit["locked_inputs_unchanged"] is True
    expected = {
        "harness/work/05-max-pressure/contract.json": "sha256:59f1fed8b3cb1dfc3629d9c3df666c3041712fbd4cde496a7eaa1f6e041b8f89",
        "harness/work/05-max-pressure/gate.json": "sha256:8d01e405301400506915e8b0c347818235364e5ec486bf9f340f1f8e3734e5ec",
        "harness/work/10b-max-pressure-trip-kpis/contract.json": "sha256:ae1a6cdab0642d4b54c6ab8f1649d2abf25a497df587b04a70c123e807757c4c",
        "harness/work/10b-max-pressure-trip-kpis/gate.json": "sha256:68e28b5aa5f25dc4c4efeee9446c3d4a3e3bcf66a9668773d5a6a9e584cbe9fa",
    }
    assert all(audit["locked_input_hashes"][path] == value == _hash(ROOT / path) for path, value in expected.items())
