from __future__ import annotations

import json
from pathlib import Path

import pytest

from coflow5.evidence.professor_page import (
    EvidencePageError,
    load_evidence_page,
    render_evidence_page,
    require_green_gate,
    verify_locked_inputs,
)

ROOT = Path(__file__).resolve().parents[2]
TRAFFIC_RUN = "1333dbcd-d653-5e8e-b3d5-94de7967a7c8"
ADVICE_RUN = "693d914d-79c3-5120-8049-aaa77ceef7ff"
RECOVERY_RUN = "7dd9f460-ca50-4c5a-9991-67944a897d35"


def test_page_keeps_traffic_advice_and_recovery_as_separate_evidence() -> None:
    page = load_evidence_page(ROOT)
    assert page.traffic.source_row == "10b-max-pressure-trip-kpis"
    assert page.traffic.run_id == TRAFFIC_RUN
    assert page.traffic.controller == "cooperative-max-pressure"
    assert page.traffic.seed == 37
    assert page.traffic.completed_trips == 70
    assert page.traffic.planned_trips == 84
    assert page.traffic.unfinished_trips == 14
    assert page.traffic.mean_waiting_seconds == pytest.approx(14.214285714285714)
    assert page.traffic.p95_waiting_seconds == 25.0
    assert page.traffic.total_time_loss_seconds == pytest.approx(1480.4722754376853)
    assert page.traffic.same_run_accepted_requests == "not in this run"
    assert page.traffic.same_run_rejected_requests == "not in this run"
    assert page.traffic.same_run_reason_codes == "not in this run"

    assert page.advice.source_row == "10-a4-a5"
    assert page.advice.run_id == ADVICE_RUN
    assert page.advice.run_id != page.traffic.run_id
    assert page.advice.accepted_requests == 1 and page.advice.rejected_requests == 2
    assert set(page.advice.reason_codes) == {
        "ACCEPTED_SUSTAINABILITY_ADVICE",
        "REJECTED_DOWNSTREAM_BLOCKED",
        "REJECTED_HIGHER_PRIORITY_REQUEST",
    }
    assert page.advice.selected_forecast_model == "simple_autoregression"
    assert page.advice.lightgbm_status == "not_available_not_accepted"
    assert set(page.advice.sustainability_outcomes) == {"improved", "worsened"}

    assert page.recovery.source_row == "08-failure-injection"
    assert page.recovery.run_id == RECOVERY_RUN
    assert page.recovery.run_id not in {page.traffic.run_id, page.advice.run_id}
    assert page.recovery.required_ladder == (
        "COOPERATIVE_MAX_PRESSURE", "ACTUATED", "FIXED_TIME"
    )
    assert page.recovery.unexpected_transitions == ()


def test_render_is_deterministic_honest_and_professor_readable() -> None:
    page = load_evidence_page(ROOT)
    first = render_evidence_page(page)
    second = render_evidence_page(page)
    assert first == second
    required = (
        "=== CoFlow-5 professor evidence page ===",
        "70 / 84",
        "Mean waiting seconds: 14.21",
        "P95 waiting seconds: 25.00",
        "Accepted requests: not in this run",
        "Related A4/A5 fixture — separate run",
        "ACCEPTED_SUSTAINABILITY_ADVICE",
        "COOPERATIVE_MAX_PRESSURE -> ACTUATED -> FIXED_TIME",
        "One matched seed is insufficient for a winner or significance claim.",
        "No lives saved.",
        "No measured air quality.",
        "No deployment claim.",
    )
    assert all(value in first for value in required)
    assert "Max-Pressure won" not in first and "best controller" not in first
    assert "Qwen" not in first and "LangGraph" not in first


def test_locked_input_and_green_gate_checks_fail_closed(tmp_path: Path) -> None:
    source = tmp_path / "source.json"
    source.write_text('{"value": 1}\n', encoding="utf-8")
    import hashlib
    expected = "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest()
    verify_locked_inputs(tmp_path, {"source.json": expected})
    source.write_text('{"value": 2}\n', encoding="utf-8")
    with pytest.raises(EvidencePageError, match="locked input hash mismatch"):
        verify_locked_inputs(tmp_path, {"source.json": expected})

    contract = tmp_path / "contract.json"
    contract.write_text('{"id":"source-row"}\n', encoding="utf-8")
    contract_hash = "sha256:" + hashlib.sha256(contract.read_bytes()).hexdigest()
    gate = tmp_path / "gate.json"
    gate.write_text(json.dumps({
        "id": "source-row", "pass": False, "openDeltas": 1,
        "decidedBy": "tests-and-files", "contractHash": contract_hash,
    }), encoding="utf-8")
    with pytest.raises(EvidencePageError, match="source gate is not green"):
        require_green_gate(gate, contract)
