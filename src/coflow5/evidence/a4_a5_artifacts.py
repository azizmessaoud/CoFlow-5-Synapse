from __future__ import annotations

import hashlib
import importlib.metadata
import json
import shutil
import sys
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from coflow5.a2 import A2EmergencyAgent, EmergencyPriorityPayload, RoadPosition
from coflow5.a4 import (
    A4SituationAgent,
    ForecastPayload,
    SituationClassification,
    SituationEvidence,
    TimeSeriesPoint,
    chronological_split,
    evaluate_forecast_ladder,
)
from coflow5.a5 import (
    PROXY_LABEL,
    A5SustainabilityAgent,
    EmissionProxyObservation,
    SustainabilityAdvicePayload,
    compute_link_displacement,
)
from coflow5.control import (
    A1RequestArbitrator,
    ArbitrationContext,
    DeterministicSafetyMask,
    controlled_cross_plan,
)
from coflow5.control.fallback_probe import run_forecast_fallback_probe
from coflow5.messaging import (
    InProcessMessageBoard,
    MessageDisposition,
    MessageEnvelope,
    thaw_json,
)
CONTRACT_PATH = "harness/work/10-a4-a5/contract.json"
SOURCE_FILES = (
    "scripts/generate_a4_a5_artifacts.py",
    "src/coflow5/a4/situation.py",
    "src/coflow5/a5/sustainability.py",
    "src/coflow5/messaging/a1_forecasts.py",
    "src/coflow5/control/request_arbitration.py",
    "src/coflow5/control/situation_aware.py",
    "src/coflow5/control/fallback_probe.py",
    "src/coflow5/control/max_pressure.py",
    "src/coflow5/control/a1_controller.py",
    "src/coflow5/control/safety.py",
    "src/coflow5/evidence/a4_a5_artifacts.py",
)

MESSAGE_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("scenario_case", pa.string()),
    ("record_kind", pa.string()), ("message_id", pa.string()),
    ("source_agent", pa.string()), ("destination_or_topic", pa.string()),
    ("simulation_time", pa.float64()), ("expires_at", pa.float64()),
    ("priority_class", pa.string()), ("payload_type", pa.string()),
    ("payload_json", pa.string()), ("referenced_message_id", pa.string()),
    ("event_id", pa.string()), ("accepted", pa.bool_()),
    ("reason_code", pa.string()), ("provenance", pa.string()),
])
DECISION_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("scenario_case", pa.string()),
    ("event_id", pa.string()), ("referenced_message_id", pa.string()),
    ("reply_message_id", pa.string()), ("simulation_time", pa.float64()),
    ("source_agent", pa.string()), ("priority_class", pa.string()),
    ("accepted", pa.bool_()), ("selected_action", pa.string()),
    ("reason_code", pa.string()), ("safety_reason_code", pa.string()),
    ("specialist_signal_write", pa.bool_()), ("provenance", pa.string()),
])
FORECAST_EVALUATION_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("record_kind", pa.string()),
    ("split_name", pa.string()), ("split_start_time", pa.float64()),
    ("split_end_time", pa.float64()), ("row_count", pa.int64()),
    ("model_name", pa.string()), ("model_version", pa.string()),
    ("status", pa.string()), ("validation_mae", pa.float64()),
    ("fit_end_time", pa.float64()), ("evaluation_start_time", pa.float64()),
    ("evaluation_end_time", pa.float64()), ("selected_model", pa.bool_()),
    ("classification", pa.string()), ("evidence_basis", pa.string()),
])
SUSTAINABILITY_KPI_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("run_id", pa.string()),
    ("scenario_hash", pa.string()), ("link_id", pa.string()),
    ("receptor_type", pa.string()), ("sensitive", pa.bool_()),
    ("baseline_co2_mg_s", pa.float64()), ("observed_co2_mg_s", pa.float64()),
    ("co2_delta_mg_s", pa.float64()), ("baseline_nox_mg_s", pa.float64()),
    ("observed_nox_mg_s", pa.float64()), ("nox_delta_mg_s", pa.float64()),
    ("stop_delta", pa.float64()), ("classification", pa.string()),
    ("proxy_label", pa.string()), ("claim_boundary", pa.string()),
])


def _hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _message_row(message: MessageEnvelope, record_kind: str, scenario_case: str) -> dict[str, Any]:
    payload = thaw_json(message.payload)
    assert isinstance(payload, dict)
    return {
        "schema_version": 1, "run_id": message.run_id,
        "scenario_hash": message.scenario_hash, "scenario_case": scenario_case,
        "record_kind": record_kind, "message_id": message.message_id,
        "source_agent": message.source_agent,
        "destination_or_topic": message.destination_or_topic,
        "simulation_time": message.simulation_time, "expires_at": message.expires_at,
        "priority_class": message.priority_class.value, "payload_type": message.payload_type,
        "payload_json": json.dumps(payload, sort_keys=True, separators=(",", ":")),
        "referenced_message_id": payload.get("referenced_message_id"),
        "event_id": payload.get("event_id"), "accepted": payload.get("accepted"),
        "reason_code": payload.get("reason_code"), "provenance": message.provenance,
    }


def _context(run_id: str, scenario_hash: str, simulation_time: float = 20) -> ArbitrationContext:
    return ArbitrationContext(
        run_id=run_id, scenario_hash=scenario_hash, signal_id="J0",
        simulation_time=simulation_time, current_phase_id="NS_GREEN", phase_entered_at=0,
        flow_requested_phase_id="NS_GREEN",
        downstream_feasible_by_movement={"north": True, "east": True},
    )


def _eco_payload(case: str, message_id: str, *, downstream: bool, north: bool) -> SustainabilityAdvicePayload:
    return SustainabilityAdvicePayload(
        scenario_case=case, signal_id="J0", sensitive_link_id="school-link",
        requested_movement="north" if north else "east",
        requested_phase_id="NS_GREEN" if north else "EW_GREEN",
        co2_proxy_mg_s=1200, nox_proxy_mg_s=18, stop_count=7, queue_length=5,
        expected_benefit_seconds=6, other_traffic_externality_seconds=2,
        downstream_available=downstream, proxy_source="SUMO/HBEFA emission proxy",
        advice_expires_at=25,
    )


class _MalformedForecastTransport:
    def read(self, *args: object, **kwargs: object) -> object:
        return type("MalformedRead", (), {
            "disposition": MessageDisposition.MALFORMED,
            "messages": (),
        })()


def _forecast_fallback_rows(
    run_id: str, scenario_hash: str, created: datetime,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for case in ("silent", "stale", "unavailable", "malformed"):
        transport: Any = InProcessMessageBoard()
        if case == "stale":
            published = A4SituationAgent(transport).publish_forecast(
                run_id=run_id, scenario_hash=scenario_hash,
                message_id="fallback-stale", correlation_id="fallback-stale",
                created_at=created, simulation_time=10,
                payload=ForecastPayload(
                    scenario_case="fallback_stale", signal_id="J0", target="arrivals",
                    source_time=10, horizon_seconds=5, predicted_value=2,
                    confidence=0.5, model_name="persistence",
                    model_version="persistence-v1", expires_at=11,
                    classification=SituationClassification.NORMAL, residual=0,
                    evidence_basis="canonical stale fallback fixture",
                ),
            )
            assert published.accepted
        elif case == "unavailable":
            transport.inject_unavailable()
        elif case == "malformed":
            transport = _MalformedForecastTransport()

        probe = run_forecast_fallback_probe(
            transport=transport, run_id=run_id, scenario_hash=scenario_hash,
        )
        result = probe.result
        assert result.local_only and result.forecast_read.forecasts == ()
        assert result.decision.reason_code == "MAX_PRESSURE_LOCAL_ONLY"
        assert result.decision.safety_reason_code == "ACCEPTED"
        assert result.decision.considered_message_ids == ()
        assert probe.safety_event_count == probe.command_count == 1
        assert probe.a1_signal_write_count == 1 and probe.a4_signal_write_count == 0
        rows.append({
            "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
            "record_kind": "fallback", "split_name": case,
            "split_start_time": None, "split_end_time": None, "row_count": 1,
            "model_name": "cooperative_max_pressure",
            "model_version": result.decision.provenance,
            "status": result.forecast_read.disposition.value,
            "validation_mae": None, "fit_end_time": None,
            "evaluation_start_time": 20.0, "evaluation_end_time": 20.0,
            "selected_model": None, "classification": None,
            "evidence_basis": (
                "forecast_count=0; local_only=true; "
                f"decision_reason={result.decision.reason_code}; "
                f"safety_reason={result.decision.safety_reason_code}; "
                f"a1_signal_writes={probe.a1_signal_write_count}; "
                f"a4_signal_writes={probe.a4_signal_write_count}"
            ),
        })
    return rows

def _publish_atomic(staging: Path, destination: Path) -> None:
    backup = destination.parent / f".{destination.name}.previous-{uuid.uuid4()}"
    moved = False
    try:
        if destination.exists():
            destination.replace(backup)
            moved = True
        staging.replace(destination)
    except Exception:
        if moved and backup.exists() and not destination.exists():
            backup.replace(destination)
        raise
    else:
        if moved:
            shutil.rmtree(backup, ignore_errors=True)


def generate_a4_a5_artifacts(root: Path, output_dir: Path | None = None) -> dict[str, Any]:
    root = root.resolve()
    destination = (output_dir or root / "harness/work/10-a4-a5/artifacts").resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    for pattern in (f".{destination.name}.staging-*", f".{destination.name}.previous-*"):
        for stale in destination.parent.glob(pattern):
            shutil.rmtree(stale, ignore_errors=True)
    staging = destination.parent / f".{destination.name}.staging-{uuid.uuid4()}"
    staging.mkdir()
    contract = root / CONTRACT_PATH
    scenario_hash = _hash(contract)
    run_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"coflow5:{scenario_hash}:row10"))
    created = datetime(2026, 9, 22, 18, 0, tzinfo=timezone.utc)

    try:
        points = tuple(TimeSeriesPoint(simulation_time=float(i), value=2 * i + 3) for i in range(30))
        split = chronological_split(points, train_fraction=0.6, validation_fraction=0.2)
        selection = evaluate_forecast_ladder(split)
        forecast_rows: list[dict[str, Any]] = []
        for name, values in (("train", split.train), ("validation", split.validation), ("test", split.test)):
            forecast_rows.append({
                "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
                "record_kind": "split", "split_name": name,
                "split_start_time": values[0].simulation_time,
                "split_end_time": values[-1].simulation_time, "row_count": len(values),
                "model_name": None, "model_version": None, "status": "chronological",
                "validation_mae": None, "fit_end_time": None,
                "evaluation_start_time": None, "evaluation_end_time": None,
                "selected_model": None, "classification": None,
                "evidence_basis": "sorted unique simulation_time; train before validation before test",
            })
        for score in selection.scores:
            forecast_rows.append({
                "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
                "record_kind": "model_score", "split_name": "validation",
                "split_start_time": None, "split_end_time": None, "row_count": len(split.validation),
                "model_name": score.model_name, "model_version": score.model_version,
                "status": score.status, "validation_mae": score.validation_mae,
                "fit_end_time": score.fit_end_time,
                "evaluation_start_time": score.evaluation_start_time,
                "evaluation_end_time": score.evaluation_end_time,
                "selected_model": score.model_name == selection.selected_model,
                "classification": None,
                "evidence_basis": "fit on train only; score on later validation rows; no test selection",
            })
        classification_examples = (
            SituationEvidence(source_time=10, current_time=20, sample_count=2, residual=0, ewma=0, cusum=0, speed_ratio=1, occupancy=0.2),
            SituationEvidence(source_time=1, current_time=20, sample_count=10, residual=0, ewma=0, cusum=0, speed_ratio=1, occupancy=0.2),
            SituationEvidence(source_time=18, current_time=20, sample_count=10, residual=4, ewma=3, cusum=7, speed_ratio=0.3, occupancy=0.4),
            SituationEvidence(source_time=18, current_time=20, sample_count=10, residual=4, ewma=3, cusum=7, speed_ratio=0.6, occupancy=0.9),
            SituationEvidence(source_time=18, current_time=20, sample_count=10, residual=4, ewma=3, cusum=7, speed_ratio=0.9, occupancy=0.4),
            SituationEvidence(source_time=18, current_time=20, sample_count=10, residual=0.2, ewma=0.1, cusum=0.2, speed_ratio=0.9, occupancy=0.4),
        )
        for evidence in classification_examples:
            classification = A4SituationAgent.classify(evidence)
            forecast_rows.append({
                "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
                "record_kind": "classification", "split_name": None,
                "split_start_time": None, "split_end_time": None, "row_count": evidence.sample_count,
                "model_name": None, "model_version": None, "status": "classified",
                "validation_mae": None, "fit_end_time": None,
                "evaluation_start_time": evidence.source_time,
                "evaluation_end_time": evidence.current_time, "selected_model": None,
                "classification": classification.value,
                "evidence_basis": "transparent residual, EWMA/CUSUM, speed-ratio, occupancy, freshness rules",
            })

        forecast_rows.extend(_forecast_fallback_rows(run_id, scenario_hash, created))

        message_rows: list[dict[str, Any]] = []
        forecast_board = InProcessMessageBoard()
        a4 = A4SituationAgent(forecast_board)
        normal = a4.publish_forecast(
            run_id=run_id, scenario_hash=scenario_hash, message_id="forecast-normal",
            correlation_id="omar-normal", created_at=created, simulation_time=20,
            payload=ForecastPayload(
                scenario_case="omar_normal", signal_id="J0", target="north_arrivals",
                source_time=20, horizon_seconds=30, predicted_value=43, confidence=0.9,
                model_name=selection.selected_model, model_version=selection.selected_model_version,
                expires_at=25, classification=SituationClassification.NORMAL,
                residual=0.2, evidence_basis="chronological validation winner",
            ),
        )
        assert normal.message is not None
        message_rows.append(_message_row(normal.message, "forecast", "omar_normal"))
        incident = a4.publish_alert(
            run_id=run_id, scenario_hash=scenario_hash, message_id="alert-incident",
            correlation_id="omar-incident", created_at=created, simulation_time=20,
            payload=ForecastPayload(
                scenario_case="omar_likely_incident", signal_id="J0", target="north_arrivals",
                source_time=20, horizon_seconds=30, predicted_value=43, confidence=0.75,
                model_name=selection.selected_model, model_version=selection.selected_model_version,
                expires_at=25, classification=SituationClassification.LIKELY_INCIDENT,
                residual=4, evidence_basis="EWMA/CUSUM residual plus speed-ratio evidence",
            ),
        )
        assert incident.message is not None
        message_rows.append(_message_row(incident.message, "alert", "omar_likely_incident"))

        eco_requests: list[MessageEnvelope] = []
        eco_replies: list[MessageEnvelope] = []
        eco_decisions: list[Any] = []

        def eco_round(message_id: str, case: str, *, downstream: bool, with_emergency: bool) -> None:
            board = InProcessMessageBoard()
            a5 = A5SustainabilityAgent(board)
            published = a5.publish_advice(
                run_id=run_id, scenario_hash=scenario_hash, message_id=message_id,
                correlation_id=case, created_at=created, simulation_time=20,
                payload=_eco_payload(case, message_id, downstream=downstream, north=downstream),
            )
            assert published.message is not None
            eco_requests.append(published.message)
            if with_emergency:
                A2EmergencyAgent(board).publish_priority_request(
                    run_id=run_id, scenario_hash=scenario_hash, message_id="emergency-for-eco",
                    correlation_id=case, created_at=created, simulation_time=20,
                    payload=EmergencyPriorityPayload(
                        scenario_case=case, vehicle_id="ambulance", signal_id="J0",
                        position=RoadPosition(edge_id="N", lane_id="N_0", distance_m=20),
                        route=("N", "S"), next_controlled_junctions=("J0",), eta_seconds=3,
                        urgency=1, expected_benefit_seconds=15,
                        civilian_delay_externality_seconds=4, requested_movement="north",
                        requested_phase_id="NS_GREEN", downstream_available=True,
                        request_expires_at=25,
                    ),
                )
            result = A1RequestArbitrator(
                transport=board, safety_mask=DeterministicSafetyMask(controlled_cross_plan())
            ).arbitrate(_context(run_id, scenario_hash))
            decision = next(item for item in result.decisions if item.referenced_message_id == message_id)
            reply = next(item for item in result.replies if item.payload["referenced_message_id"] == message_id)
            eco_decisions.append(decision)
            eco_replies.append(reply)

        eco_round("eco-accepted", "maria_eco_accepted", downstream=True, with_emergency=False)
        eco_round("eco-blocked", "maria_spillback", downstream=False, with_emergency=False)
        eco_round("eco-lower-priority", "maria_emergency_conflict", downstream=True, with_emergency=True)
        for message in eco_requests:
            message_rows.append(_message_row(message, "advice", str(message.payload["scenario_case"])))
        for reply in eco_replies:
            referenced = str(reply.payload["referenced_message_id"])
            case = next(str(message.payload["scenario_case"]) for message in eco_requests if message.message_id == referenced)
            message_rows.append(_message_row(reply, "reply", case))
        decision_rows = []
        for decision in eco_decisions:
            case = next(str(message.payload["scenario_case"]) for message in eco_requests if message.message_id == decision.referenced_message_id)
            decision_rows.append({
                "schema_version": 1, "run_id": decision.run_id,
                "scenario_hash": decision.scenario_hash, "scenario_case": case,
                "event_id": decision.event_id, "referenced_message_id": decision.referenced_message_id,
                "reply_message_id": decision.reply_message_id,
                "simulation_time": decision.simulation_time, "source_agent": decision.source_agent,
                "priority_class": decision.priority_class, "accepted": decision.accepted,
                "selected_action": decision.selected_action, "reason_code": decision.reason_code,
                "safety_reason_code": decision.safety_reason_code,
                "specialist_signal_write": False, "provenance": decision.provenance,
            })

        baseline = (
            EmissionProxyObservation(link_id="school-link", simulation_time=10, co2_proxy_mg_s=1000, nox_proxy_mg_s=10, stop_count=5, sensitive=True, receptor_type="school"),
            EmissionProxyObservation(link_id="residential-link", simulation_time=10, co2_proxy_mg_s=800, nox_proxy_mg_s=8, stop_count=4, sensitive=True, receptor_type="residential"),
        )
        observed = (
            EmissionProxyObservation(link_id="school-link", simulation_time=10, co2_proxy_mg_s=900, nox_proxy_mg_s=9, stop_count=4, sensitive=True, receptor_type="school"),
            EmissionProxyObservation(link_id="residential-link", simulation_time=10, co2_proxy_mg_s=920, nox_proxy_mg_s=9, stop_count=6, sensitive=True, receptor_type="residential"),
        )
        displacement = compute_link_displacement(
            baseline, observed, selected_links={"school-link", "residential-link"}
        )
        sustainability_rows = [{
            "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
            **asdict(row),
            "claim_boundary": "deterministic simulation fixture; emission proxy only; not ambient measurement or deployment evidence",
        } for row in displacement]

        tables = {
            "messages.parquet": pa.Table.from_pylist(message_rows, schema=MESSAGE_SCHEMA),
            "decision_events.parquet": pa.Table.from_pylist(decision_rows, schema=DECISION_SCHEMA),
            "forecast-evaluation.parquet": pa.Table.from_pylist(forecast_rows, schema=FORECAST_EVALUATION_SCHEMA),
            "sustainability-kpis.parquet": pa.Table.from_pylist(sustainability_rows, schema=SUSTAINABILITY_KPI_SCHEMA),
        }
        for name, table in tables.items():
            pq.write_table(table, staging / name, compression="zstd")
        references = [{
            "path": name, "rows": table.num_rows,
            "bytes": (staging / name).stat().st_size, "sha256": _hash(staging / name),
            "schema_name": {
                "messages.parquet": "a4_a5_message",
                "decision_events.parquet": "a5_request_decision",
                "forecast-evaluation.parquet": "a4_forecast_evaluation",
                "sustainability-kpis.parquet": "a5_link_displacement",
            }[name], "schema_version": 1,
        } for name, table in tables.items()]
        manifest = {
            "schema_version": 1, "run_id": run_id, "status": "completed", "immutable": True,
            "backend": "deterministic-fixture",
            "controller": "cooperative-max-pressure-with-a4-a5-advice",
            "scenario_hash": scenario_hash, "scenario_files": [CONTRACT_PATH],
            "configuration_hash": scenario_hash, "seeds": {"evaluation": 53, "sumo": 53},
            "source_revision": None,
            "source_hashes": {relative: _hash(root / relative) for relative in SOURCE_FILES},
            "versions": {
                "python": ".".join(map(str, sys.version_info[:3])),
                "pyarrow": importlib.metadata.version("pyarrow"),
                "pydantic": importlib.metadata.version("pydantic"),
                "coflow5": importlib.metadata.version("coflow5-synapse"),
            },
            "artifact_references": references,
            "finalized_at": "2026-09-22T18:00:00+00:00",
            "claim_boundaries": {
                "forecast": "deterministic chronological fixture; not a deployed incident predictor",
                "sustainability": PROXY_LABEL,
                "authority": "A4/A5 advice only; A1 remains sole signal writer",
            },
        }
        (staging / "run_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        _publish_atomic(staging, destination)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
