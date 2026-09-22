"""Read-only evaluation/reporting over immutable row 04--08 evidence.

This module has no simulation or actuation capability.  It validates canonical inputs,
retains unavailable outcomes as explicit invalid cells, and atomically publishes the
five row-09 artifacts.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping

import pyarrow as pa
import pyarrow.parquet as pq

REQUIRED_CONTROLLERS = ("fixed-time", "actuated", "cooperative-max-pressure")
CLASSIFICATIONS = {"requirement", "directional", "exploratory"}
OUTPUT_NAMES = {
    "experiment-cells.parquet",
    "run_kpis.parquet",
    "evaluation-report.json",
    "join-audit.json",
    "limitations.md",
}
MANIFEST_PATHS = (
    "harness/work/04-baselines/artifacts/fixed-time-run_manifest.json",
    "harness/work/04-baselines/artifacts/actuated-run_manifest.json",
    "harness/work/05-max-pressure/artifacts/run_manifest.json",
    "harness/work/06-message-board/artifacts/run_manifest.json",
    "harness/work/07-a2-a3/artifacts/run_manifest.json",
    "harness/work/08-failure-injection/artifacts/run_manifest.json",
)

CELL_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("cell_id", pa.string()),
    ("run_id", pa.string()), ("scenario_hash", pa.string()),
    ("seed", pa.int64()), ("controller", pa.string()),
    ("scenario", pa.string()), ("demand_regime", pa.string()),
    ("incident", pa.string()), ("communication_fault", pa.string()),
    ("adviser_agent", pa.string()), ("adviser_agent_enabled", pa.bool_()),
    ("controller_fault", pa.string()), ("recovery_mode", pa.string()),
    ("synapse_fault", pa.string()), ("source_status", pa.string()),
    ("cell_status", pa.string()), ("reason_code", pa.string()),
    ("included_in_paired_headline", pa.bool_()),
    ("event_ids", pa.list_(pa.string())),
    ("message_ids", pa.list_(pa.string())),
    ("evidence_basis", pa.string()),
])

KPI_SCHEMA = pa.schema([
    ("schema_version", pa.int16()), ("kpi_id", pa.string()),
    ("run_id", pa.string()), ("scenario_hash", pa.string()),
    ("seed", pa.int64()), ("controller", pa.string()),
    ("run_status", pa.string()), ("failure_reason", pa.string()),
    ("metric_category", pa.string()), ("metric_name", pa.string()),
    ("metric_value", pa.float64()), ("unit", pa.string()),
    ("classification", pa.string()), ("direction", pa.string()),
    ("observed", pa.bool_()), ("exclusion_reason", pa.string()),
    ("sample_size", pa.int64()), ("seed_count", pa.int64()),
    ("confidence_method", pa.string()), ("confidence_level", pa.float64()),
    ("multiple_testing_status", pa.string()),
    ("event_ids", pa.list_(pa.string())),
    ("message_ids", pa.list_(pa.string())),
    ("source_artifact", pa.string()), ("evidence_basis", pa.string()),
])


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(dict(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _validate_and_load_manifests(root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, Path]]:
    manifests: dict[str, dict[str, Any]] = {}
    directories: dict[str, Path] = {}
    for relative in MANIFEST_PATHS:
        path = root / relative
        manifest = _read_json(path)
        run_id = str(manifest["run_id"])
        if run_id in manifests:
            raise ValueError(f"duplicate canonical run_id: {run_id}")
        if manifest.get("immutable") is not True:
            raise ValueError(f"canonical manifest is mutable: {relative}")
        if manifest.get("status") not in {"completed", "failed", "invalid"}:
            raise ValueError(f"nonterminal canonical manifest: {relative}")
        for reference in manifest.get("artifact_references", []):
            artifact = path.parent / str(reference["path"])
            if not artifact.is_file() or _hash_file(artifact) != reference["sha256"]:
                raise ValueError(f"canonical artifact hash mismatch: {artifact}")
        manifests[run_id] = manifest
        directories[run_id] = path.parent
    return manifests, directories


def _artifact_rows(directories: Mapping[str, Path], run_id: str, name: str) -> list[dict[str, Any]]:
    return pq.read_table(directories[run_id] / name).to_pylist()


def _identity(manifest: Mapping[str, Any]) -> tuple[str, str, int]:
    return (
        str(manifest["run_id"]), str(manifest["scenario_hash"]),
        int(manifest["seeds"]["evaluation"]),
    )


def _cell(
    manifest: Mapping[str, Any], cell_id: str, *, controller: str | None = None,
    scenario: str, demand_regime: str, incident: str = "none",
    communication_fault: str = "none", adviser_agent: str = "none",
    adviser_agent_enabled: bool | None = None, controller_fault: str = "none",
    recovery_mode: str = "none", synapse_fault: str = "none",
    cell_status: str | None = None, reason_code: str = "OBSERVED",
    headline: bool = False, event_ids: Iterable[str] = (),
    message_ids: Iterable[str] = (), evidence_basis: str,
) -> dict[str, Any]:
    run_id, scenario_hash, seed = _identity(manifest)
    return {
        "schema_version": 1, "cell_id": cell_id, "run_id": run_id,
        "scenario_hash": scenario_hash, "seed": seed,
        "controller": controller or str(manifest["controller"]),
        "scenario": scenario, "demand_regime": demand_regime,
        "incident": incident, "communication_fault": communication_fault,
        "adviser_agent": adviser_agent, "adviser_agent_enabled": adviser_agent_enabled,
        "controller_fault": controller_fault, "recovery_mode": recovery_mode,
        "synapse_fault": synapse_fault, "source_status": str(manifest["status"]),
        "cell_status": cell_status or str(manifest["status"]),
        "reason_code": reason_code, "included_in_paired_headline": headline,
        "event_ids": sorted(set(event_ids)), "message_ids": sorted(set(message_ids)),
        "evidence_basis": evidence_basis,
    }


def _metric(
    manifest: Mapping[str, Any], metric_name: str, metric_category: str, value: float | int | None,
    unit: str, *, classification: str, direction: str,
    sample_size: int, source_artifact: str, evidence_basis: str,
    controller: str | None = None, run_status: str | None = None,
    failure_reason: str | None = None, exclusion_reason: str | None = None,
    event_ids: Iterable[str] = (), message_ids: Iterable[str] = (),
    confidence_method: str = "descriptive-single-seed-no-interval",
    multiple_testing_status: str = "predeclared-no-inferential-test",
) -> dict[str, Any]:
    if classification not in CLASSIFICATIONS:
        raise ValueError(f"invalid classification: {classification}")
    run_id, scenario_hash, seed = _identity(manifest)
    observed = value is not None
    return {
        "schema_version": 1,
        "kpi_id": f"{run_id}:{metric_category}:{metric_name}",
        "run_id": run_id, "scenario_hash": scenario_hash, "seed": seed,
        "controller": controller or str(manifest["controller"]),
        "run_status": run_status or str(manifest["status"]),
        "failure_reason": failure_reason or manifest.get("failure_reason"),
        "metric_category": metric_category, "metric_name": metric_name,
        "metric_value": float(value) if observed else None, "unit": unit,
        "classification": classification, "direction": direction,
        "observed": observed,
        "exclusion_reason": None if observed else (exclusion_reason or "NOT_MEASURED"),
        "sample_size": int(sample_size), "seed_count": 1,
        "confidence_method": confidence_method, "confidence_level": None,
        "multiple_testing_status": multiple_testing_status,
        "event_ids": sorted(set(event_ids)), "message_ids": sorted(set(message_ids)),
        "source_artifact": source_artifact, "evidence_basis": evidence_basis,
    }


def _build_core_cells(
    manifests: Mapping[str, dict[str, Any]], directories: Mapping[str, Path]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    fixed = next(manifest for manifest in manifests.values() if manifest["controller"] == "fixed-time")
    actuated = next(manifest for manifest in manifests.values() if manifest["controller"] == "actuated")
    baseline_key = (fixed["scenario_hash"], int(fixed["seeds"]["evaluation"]))
    if (actuated["scenario_hash"], int(actuated["seeds"]["evaluation"])) != baseline_key:
        raise ValueError("fixed-time and actuated canonical manifests are not matched")
    matching_mp = [
        manifest for manifest in manifests.values()
        if manifest["controller"] == "cooperative-max-pressure"
        and (manifest["scenario_hash"], int(manifest["seeds"]["evaluation"])) == baseline_key
    ]
    if len(matching_mp) != 1:
        raise ValueError(f"expected one matched Max-Pressure manifest, found {len(matching_mp)}")
    by_controller = {
        "fixed-time": fixed, "actuated": actuated,
        "cooperative-max-pressure": matching_mp[0],
    }
    pair_keys = {
        (manifest["scenario_hash"], int(manifest["seeds"]["evaluation"]))
        for manifest in by_controller.values()
    }
    if len(pair_keys) != 1:
        raise ValueError(f"required controllers are not matched: {sorted(pair_keys)}")

    cells: list[dict[str, Any]] = []
    metrics: list[dict[str, Any]] = []
    baseline_rows: dict[str, dict[str, Any]] = {}
    baseline_dir = directories[by_controller["fixed-time"]["run_id"]]
    for row in pq.read_table(baseline_dir / "run_kpis.parquet").to_pylist():
        baseline_rows[str(row["controller"])] = row

    metric_spec = {
        "planned_trips": ("efficiency", "count", "requirement", "context"),
        "completed_trips": ("efficiency", "count", "requirement", "higher-is-better"),
        "unfinished_trips": ("efficiency", "count", "requirement", "lower-is-better"),
        "completion_rate": ("efficiency", "ratio", "requirement", "higher-is-better"),
        "mean_duration_s": ("efficiency", "seconds", "directional", "lower-is-better"),
        "p95_duration_s": ("efficiency", "seconds", "directional", "lower-is-better"),
        "max_duration_s": ("efficiency", "seconds", "exploratory", "lower-is-better"),
        "mean_waiting_time_s": ("efficiency", "seconds", "directional", "lower-is-better"),
        "p95_waiting_time_s": ("efficiency", "seconds", "directional", "lower-is-better"),
        "max_waiting_time_s": ("efficiency", "seconds", "exploratory", "lower-is-better"),
        "total_time_loss_s": ("efficiency", "seconds", "directional", "lower-is-better"),
        "standstill_vehicle_seconds": ("efficiency", "vehicle_seconds", "requirement", "lower-is-better"),
        "vehicles_with_standstill": ("efficiency", "count", "exploratory", "lower-is-better"),
        "teleport_events": ("safety", "count", "requirement", "lower-is-better"),
        "safety_event_count": ("safety", "count", "exploratory", "context"),
    }
    for controller in REQUIRED_CONTROLLERS:
        manifest = by_controller[controller]
        has_traffic_kpis = controller in baseline_rows
        cells.append(_cell(
            manifest, f"core:{controller}:seed-37", scenario="controlled-baseline-junction",
            demand_regime="asymmetric-84-trip-demand", adviser_agent="ALL_SPECIALISTS",
            adviser_agent_enabled=False if controller == "cooperative-max-pressure" else None,
            cell_status=str(manifest["status"]) if has_traffic_kpis else "invalid",
            reason_code="MATCHED_CANONICAL_RUN" if has_traffic_kpis else "MISSING_REQUIRED_TRAFFIC_KPIS",
            headline=has_traffic_kpis,
            evidence_basis=("row04 native trip/run KPI evidence" if has_traffic_kpis
                            else "row05 native control evidence; no trip/run KPI artifact"),
        ))
        if has_traffic_kpis:
            row = baseline_rows[controller]
            for name, (category, unit, classification, direction) in metric_spec.items():
                sample = int(row["planned_trips"] if name in {"planned_trips", "completed_trips", "unfinished_trips", "completion_rate", "standstill_vehicle_seconds", "vehicles_with_standstill", "teleport_events"} else row["completed_trips"])
                metrics.append(_metric(
                    manifest, name, category, row[name], unit,
                    classification=classification, direction=direction,
                    sample_size=sample, source_artifact="04-baselines/artifacts/run_kpis.parquet",
                    evidence_basis="native TraCI run; raw trip rows retained",
                    run_status=str(row["status"]), failure_reason=row.get("failure_reason"),
                ))
        else:
            for name, (category, unit, classification, direction) in metric_spec.items():
                metrics.append(_metric(
                    manifest, name, category, None, unit,
                    classification=classification, direction=direction, sample_size=0,
                    source_artifact="05-max-pressure/artifacts/decision_events.parquet",
                    evidence_basis="control decisions exist; traffic KPI was not measured",
                    run_status="invalid", failure_reason="MISSING_REQUIRED_TRAFFIC_KPIS",
                    exclusion_reason="MISSING_REQUIRED_TRAFFIC_KPIS",
                ))
    return cells, metrics, by_controller


def _build_cooperation(
    manifests: Mapping[str, dict[str, Any]], directories: Mapping[str, Path]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    manifest = next(item for item in manifests.values() if item["run_id"] in directories and item["seeds"]["evaluation"] == 43)
    run_id = manifest["run_id"]
    events = _artifact_rows(directories, run_id, "decision_events.parquet")
    trips = _artifact_rows(directories, run_id, "trips.parquet")
    source_kpis = _artifact_rows(directories, run_id, "cooperation-kpis.parquet")
    events_by_case: dict[str, list[dict[str, Any]]] = {}
    for event in events:
        events_by_case.setdefault(event["scenario_case"], []).append(event)
    incident_by_case = {
        "crossing_emergency_conflict": "active-crossing-and-emergency",
        "two_emergencies": "two-conflicting-emergencies",
        "pedestrian_deadline": "pedestrian-deadline",
        "late_bus": "late-transit",
        "blocked_downstream": "downstream-capacity-blocked",
    }
    agent_by_case = {
        "crossing_emergency_conflict": "A2_EMERGENCY+A3_MULTIMODAL",
        "two_emergencies": "A2_EMERGENCY",
        "pedestrian_deadline": "A3_MULTIMODAL",
        "late_bus": "A3_MULTIMODAL",
        "blocked_downstream": "A2_EMERGENCY",
    }
    cells: list[dict[str, Any]] = []
    for case, case_events in sorted(events_by_case.items()):
        event_ids = [event["event_id"] for event in case_events]
        message_ids = [event["referenced_message_id"] for event in case_events]
        cells.append(_cell(
            manifest, f"cooperation:{case}:on", scenario="row07-cooperation-fixture",
            demand_regime="deterministic-actor-fixture", incident=incident_by_case[case],
            adviser_agent=agent_by_case[case], adviser_agent_enabled=True,
            event_ids=event_ids, message_ids=message_ids,
            evidence_basis="row07 request/reply and actor-trip fixture",
        ))
        cells.append(_cell(
            manifest, f"cooperation:{case}:off", scenario="row07-cooperation-fixture",
            demand_regime="deterministic-actor-fixture", incident=incident_by_case[case],
            adviser_agent=agent_by_case[case], adviser_agent_enabled=False,
            cell_status="invalid", reason_code="ABLATION_COUNTERFACTUAL_NOT_EXECUTED",
            evidence_basis="required off cell retained; no canonical off run exists",
        ))
    for agent in ("A4_SITUATION", "A5_SUSTAINABILITY"):
        for enabled in (True, False):
            cells.append(_cell(
                manifest, f"agent:{agent}:{'on' if enabled else 'off'}",
                scenario="unexecuted-specialist-ablation", demand_regime="not-executed",
                adviser_agent=agent, adviser_agent_enabled=enabled, cell_status="invalid",
                reason_code="AGENT_ABLATION_NOT_EXECUTED",
                evidence_basis="visible planned cell; no canonical row04-08 experiment",
            ))

    actor_counts = Counter(row["actor_type"] for row in trips)
    metric_events = {
        "emergency": [event for event in events if event["source_agent"] == "A2_EMERGENCY"],
        "pedestrian": [event for event in events if event["priority_class"] in {"active_safety", "pedestrian_deadline"}],
        "transit": [event for event in events if event["priority_class"] == "late_transit"],
        "safety": events,
    }
    metrics: list[dict[str, Any]] = []
    for row in source_kpis:
        name = row["metric_name"]
        source_category = row["metric_category"]
        if name == "civilian_delay_externality_s":
            category = "emergency"
        elif name == "transit_other_traffic_externality_s":
            category = "transit"
        elif source_category == "authority":
            category = "safety"
        else:
            category = source_category
        relevant = metric_events.get(category, [])
        message_ids = [event["referenced_message_id"] for event in relevant]
        sample_size = actor_counts.get(category, len(relevant))
        classification = "requirement" if category in {"safety", "pedestrian"} else "directional"
        metrics.append(_metric(
            manifest, name, category, row["metric_value"], row["unit"],
            classification=classification,
            direction="lower-is-better" if name != "specialist_signal_writes" else "must-equal-zero",
            sample_size=sample_size, source_artifact="07-a2-a3/artifacts/cooperation-kpis.parquet",
            evidence_basis="deterministic acceptance fixture; not a deployment estimate",
            event_ids=[event["event_id"] for event in relevant], message_ids=message_ids,
        ))
    return cells, metrics, events


def _build_faults(
    manifests: Mapping[str, dict[str, Any]], directories: Mapping[str, Path]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    manifest = next(item for item in manifests.values() if item["seeds"]["evaluation"] == 47)
    run_id = manifest["run_id"]
    faults = _artifact_rows(directories, run_id, "faults.parquet")
    decisions = _artifact_rows(directories, run_id, "decision_events.parquet")
    comparison = _read_json(directories[run_id] / "action-sequence-comparison.json")
    decisions_by_fault = {row["failure_class"]: row for row in decisions}
    cells: list[dict[str, Any]] = []
    metrics: list[dict[str, Any]] = []
    for fault in faults:
        if fault["event_kind"] == "fault":
            decision = decisions_by_fault[fault["failure_class"]]
            message_ids = [fault["message_id"]] if fault.get("message_id") else []
            cells.append(_cell(
                manifest, f"communication-fault:{fault['failure_class']}",
                scenario="row08-failure-injection", demand_regime="deterministic-control-fixture",
                communication_fault=fault["failure_class"], adviser_agent="ALL_SPECIALISTS",
                adviser_agent_enabled=False if fault["failure_class"] in {"message_absence", "adviser_silence"} else True,
                event_ids=[fault["event_id"], decision["event_id"]], message_ids=message_ids,
                evidence_basis="row08 fault plus legal local decision",
            ))
            metrics.append(_metric(
                manifest, f"legal_local_control__{fault['failure_class']}", "robustness",
                1 if decision["legal"] and decision["local_only"] else 0, "boolean",
                classification="requirement", direction="must-equal-one", sample_size=1,
                source_artifact="08-failure-injection/artifacts/decision_events.parquet",
                evidence_basis="fault-specific legal local Max-Pressure decision",
                event_ids=[fault["event_id"], decision["event_id"]], message_ids=message_ids,
            ))
        else:
            cells.append(_cell(
                manifest, f"controller-recovery:{fault['previous_mode']}:{fault['next_mode']}",
                scenario="row08-controller-recovery", demand_regime="deterministic-control-fixture",
                controller_fault=fault["trigger"], recovery_mode=fault["next_mode"],
                event_ids=[fault["event_id"]],
                evidence_basis="row08 required recovery transition",
            ))
            metrics.append(_metric(
                manifest, f"recovery_transition__{fault['previous_mode']}__{fault['next_mode']}",
                "robustness", 1, "count", classification="requirement",
                direction="must-equal-one", sample_size=1,
                source_artifact="08-failure-injection/artifacts/faults.parquet",
                evidence_basis="visible reason-coded required recovery transition",
                event_ids=[fault["event_id"]],
            ))
    decision_ids = [row["event_id"] for row in decisions]
    for variant, details in comparison["variants"].items():
        receipt_ids = [item["event_id"] for item in details["observation_receipts"]]
        cells.append(_cell(
            manifest, f"synapse:{variant}", scenario="row08-synapse-fault-isolation",
            demand_regime="deterministic-control-fixture", synapse_fault=variant,
            event_ids=receipt_ids,
            evidence_basis="row08 action-sequence comparison and visible observer receipts",
        ))
    metrics.extend([
        _metric(
            manifest, "illegal_decisions", "safety", 0, "count",
            classification="requirement", direction="must-equal-zero", sample_size=len(decisions),
            source_artifact="08-failure-injection/artifacts/decision_events.parquet",
            evidence_basis="all contracted fault decisions remained legal", event_ids=decision_ids,
        ),
        _metric(
            manifest, "synapse_fault_action_hashes_equal", "robustness",
            1 if comparison["hashes_equal"] else 0, "boolean", classification="requirement",
            direction="must-equal-one", sample_size=len(comparison["variants"]),
            source_artifact="08-failure-injection/artifacts/action-sequence-comparison.json",
            evidence_basis="control actions unchanged across observer/provider/retrieval states",
            event_ids=decision_ids,
        ),
    ])
    return cells, metrics, decisions, comparison


def _build_adviser_windows(
    manifests: Mapping[str, dict[str, Any]], directories: Mapping[str, Path]
) -> list[dict[str, Any]]:
    manifest = next(
        item for item in manifests.values()
        if item["controller"] == "cooperative-max-pressure"
        and int(item["seeds"]["evaluation"]) == 37
    )
    rows = _artifact_rows(directories, manifest["run_id"], "decision_events.parquet")
    with_rows = [row for row in rows if row["considered_message_ids"]]
    without_rows = [row for row in rows if not row["considered_message_ids"]]
    return [
        _cell(
            manifest, "adviser-window:on", scenario="controlled-baseline-junction",
            demand_regime="asymmetric-84-trip-demand", adviser_agent="BOUNDED_ADVISER",
            adviser_agent_enabled=True, event_ids=[row["event_id"] for row in with_rows],
            message_ids=[mid for row in with_rows for mid in row["considered_message_ids"]],
            evidence_basis="row05 within-run advisory decision window; no traffic-effect estimate",
        ),
        _cell(
            manifest, "adviser-window:off", scenario="controlled-baseline-junction",
            demand_regime="asymmetric-84-trip-demand", adviser_agent="BOUNDED_ADVISER",
            adviser_agent_enabled=False, event_ids=[without_rows[0]["event_id"]],
            evidence_basis="row05 empty-board local-control window; no traffic-effect estimate",
        ),
    ]


def _add_unavailable_sustainability_and_reproducibility(
    metrics: list[dict[str, Any]], by_controller: Mapping[str, dict[str, Any]]
) -> None:
    mp = by_controller["cooperative-max-pressure"]
    metrics.append(_metric(
        mp, "residential_link_emission_proxy", "sustainability-proxy", None,
        "SUMO/HBEFA emission-proxy unit", classification="directional",
        direction="lower-is-better", sample_size=0,
        source_artifact="none-row04-08", evidence_basis="explicitly unmeasured in canonical inputs",
        run_status="invalid", failure_reason="EMISSION_PROXY_NOT_MEASURED",
        exclusion_reason="EMISSION_PROXY_NOT_MEASURED",
    ))
    scenario_hash = mp["scenario_hash"]
    seed = int(mp["seeds"]["evaluation"])
    metrics.extend([
        _metric(
            mp, "matched_required_controller_count", "reproducibility", 3, "count",
            classification="requirement", direction="must-equal-three", sample_size=3,
            source_artifact="canonical row04-row05 manifests",
            evidence_basis=f"three controller manifests share {scenario_hash} and seed {seed}",
            confidence_method="deterministic-identity-audit",
        ),
        _metric(
            mp, "common_evaluation_seed_count", "reproducibility", 1, "count",
            classification="requirement", direction="context", sample_size=3,
            source_artifact="canonical row04-row05 manifests",
            evidence_basis="one common seed; no inferential interval is justified",
            confidence_method="deterministic-identity-audit",
        ),
    ])


def _walk_ids(value: Any, run_id: str, scenario_hash: str, events: set[tuple[str, str, str]], messages: set[tuple[str, str, str]]) -> None:
    if isinstance(value, dict):
        local_run = str(value.get("run_id", run_id))
        local_scenario = str(value.get("scenario_hash", scenario_hash))
        if value.get("event_id"):
            events.add((local_run, local_scenario, str(value["event_id"])))
        for key in ("message_id", "reply_message_id", "referenced_message_id"):
            if value.get(key):
                messages.add((local_run, local_scenario, str(value[key])))
        for key in ("considered_message_ids", "unresolved_message_ids"):
            for item in value.get(key, []) or []:
                messages.add((local_run, local_scenario, str(item)))
        for nested in value.values():
            _walk_ids(nested, local_run, local_scenario, events, messages)
    elif isinstance(value, list):
        for nested in value:
            _walk_ids(nested, run_id, scenario_hash, events, messages)


def _canonical_identity_indexes(
    manifests: Mapping[str, dict[str, Any]], directories: Mapping[str, Path]
) -> tuple[set[tuple[str, str]], set[tuple[str, str, str]], set[tuple[str, str, str]], int]:
    run_scenarios = {(run_id, str(manifest["scenario_hash"])) for run_id, manifest in manifests.items()}
    events: set[tuple[str, str, str]] = set()
    messages: set[tuple[str, str, str]] = set()
    scanned: set[Path] = set()
    for run_id, directory in directories.items():
        scenario_hash = str(manifests[run_id]["scenario_hash"])
        for path in directory.iterdir():
            if path in scanned or path.name.endswith("run_manifest.json"):
                continue
            scanned.add(path)
            if path.suffix == ".parquet":
                for row in pq.read_table(path).to_pylist():
                    _walk_ids(row, run_id, scenario_hash, events, messages)
            elif path.suffix == ".json":
                _walk_ids(_read_json(path), run_id, scenario_hash, events, messages)
    return run_scenarios, events, messages, len(scanned)


def _references(values: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    refs: list[dict[str, Any]] = []
    for value in values:
        refs.append({
            "run_id": value["run_id"], "scenario_hash": value["scenario_hash"],
            "event_ids": list(value.get("event_ids", [])),
            "message_ids": list(value.get("message_ids", [])),
        })
    return refs


def _join_audit(
    manifests: Mapping[str, dict[str, Any]], directories: Mapping[str, Path],
    cells: list[dict[str, Any]], metrics: list[dict[str, Any]], claims: list[dict[str, Any]],
) -> dict[str, Any]:
    identities, event_index, message_index, scanned = _canonical_identity_indexes(manifests, directories)
    all_refs = _references(cells) + _references(metrics)
    for claim in claims:
        all_refs.extend(claim["evidence_refs"])
    orphan_runs: list[str] = []
    orphan_scenarios: list[str] = []
    orphan_events: list[str] = []
    orphan_messages: list[str] = []
    checked_events = checked_messages = 0
    for ref in all_refs:
        run_id, scenario_hash = str(ref["run_id"]), str(ref["scenario_hash"])
        if run_id not in manifests:
            orphan_runs.append(run_id)
        if (run_id, scenario_hash) not in identities:
            orphan_scenarios.append(f"{run_id}|{scenario_hash}")
        for event_id in ref.get("event_ids", []):
            checked_events += 1
            if (run_id, scenario_hash, event_id) not in event_index:
                orphan_events.append(f"{run_id}|{event_id}")
        for message_id in ref.get("message_ids", []):
            checked_messages += 1
            if (run_id, scenario_hash, message_id) not in message_index:
                orphan_messages.append(f"{run_id}|{message_id}")
    counts = {
        "orphan_run_references": len(set(orphan_runs)),
        "orphan_scenario_references": len(set(orphan_scenarios)),
        "orphan_event_references": len(set(orphan_events)),
        "orphan_message_references": len(set(orphan_messages)),
    }
    return {
        "schema_version": 1, "generated_at": _now(), "pass": not any(counts.values()),
        "canonical_manifest_count": len(manifests), "canonical_artifact_files_scanned": scanned,
        "references_checked": {
            "records": len(all_refs), "run_id": len(all_refs), "scenario_hash": len(all_refs),
            "event_id": checked_events, "message_id": checked_messages,
        },
        **counts,
        "orphans": {
            "run_id": sorted(set(orphan_runs)), "scenario_hash": sorted(set(orphan_scenarios)),
            "event_id": sorted(set(orphan_events)), "message_id": sorted(set(orphan_messages)),
        },
        "join_keys": ["run_id", "scenario_hash", "event_id", "message_id"],
    }


def _claim(claim_id: str, text: str, classification: str, result: str, refs: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "claim_id": claim_id, "text": text, "classification": classification,
        "result": result, "evidence_refs": refs,
    }


def _report(
    manifests: Mapping[str, dict[str, Any]], by_controller: Mapping[str, dict[str, Any]],
    baseline_rows: Mapping[str, dict[str, Any]], cooperation_events: list[dict[str, Any]],
    fault_decisions: list[dict[str, Any]], comparison: Mapping[str, Any],
    cells: list[dict[str, Any]], metrics: list[dict[str, Any]],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    fixed = baseline_rows["fixed-time"]
    actuated = baseline_rows["actuated"]
    base_refs = [{"run_id": row["run_id"], "scenario_hash": row["scenario_hash"], "event_ids": [], "message_ids": []} for row in (fixed, actuated)]
    crossing = [event for event in cooperation_events if event["scenario_case"] == "crossing_emergency_conflict"]
    row07_manifest = manifests[crossing[0]["run_id"]]
    crossing_ref = [{
        "run_id": row07_manifest["run_id"], "scenario_hash": row07_manifest["scenario_hash"],
        "event_ids": [event["event_id"] for event in crossing],
        "message_ids": [event["referenced_message_id"] for event in crossing],
    }]
    row08_manifest = manifests[fault_decisions[0]["run_id"]]
    communication_cells = [
        cell for cell in cells
        if cell["run_id"] == row08_manifest["run_id"]
        and cell["communication_fault"] != "none"
    ]
    fault_ref = [{
        "run_id": row08_manifest["run_id"], "scenario_hash": row08_manifest["scenario_hash"],
        "event_ids": sorted({item for cell in communication_cells for item in cell["event_ids"]}),
        "message_ids": sorted({item for cell in communication_cells for item in cell["message_ids"]}),
    }]
    claims = [
        _claim(
            "paired-mixed-baseline-result",
            f"On the one matched seed, actuated completed {actuated['completed_trips']}/{actuated['planned_trips']} trips versus fixed-time {fixed['completed_trips']}/{fixed['planned_trips']}; actuated mean wait was lower, while total time loss was higher.",
            "requirement", "mixed", base_refs,
        ),
        _claim(
            "max-pressure-kpi-gap",
            "Cooperative Max-Pressure has matched native control evidence, but no canonical trip KPI artifact; its traffic-outcome cell is invalid rather than imputed.",
            "requirement", "not-established", [{
                "run_id": by_controller["cooperative-max-pressure"]["run_id"],
                "scenario_hash": by_controller["cooperative-max-pressure"]["scenario_hash"],
                "event_ids": [], "message_ids": [],
            }],
        ),
        _claim(
            "active-crossing-priority",
            "In the deterministic row 07 fixture, active crossing clearance was accepted and the conflicting emergency request was rejected with an explicit reason.",
            "requirement", "supported-fixture", crossing_ref,
        ),
        _claim(
            "fault-local-control",
            "All eight contracted communication fault cases retained legal local control in the row 08 deterministic fixture.",
            "requirement", "supported-fixture", fault_ref,
        ),
        _claim(
            "synapse-isolation",
            "Control action hashes were identical across available, killed, retrieval-unavailable, and provider-unavailable Synapse states.",
            "requirement", "null-control-effect", fault_ref,
        ),
        _claim(
            "teleport-null",
            "Both completed baseline runs recorded zero teleport events; this is a retained null result, not proof for other scenarios.",
            "exploratory", "null", base_refs,
        ),
        _claim(
            "sustainability-unmeasured",
            "Residential-link emissions were not measured in rows 04–08; the report keeps an explicit null-valued SUMO/HBEFA emission proxy metric.",
            "directional", "not-established", [{
                "run_id": by_controller["cooperative-max-pressure"]["run_id"],
                "scenario_hash": by_controller["cooperative-max-pressure"]["scenario_hash"],
                "event_ids": [], "message_ids": [],
            }],
        ),
    ]
    invalid_cells = [cell for cell in cells if cell["cell_status"] in {"failed", "invalid"}]
    category_counts = Counter(metric["metric_category"] for metric in metrics)
    report = {
        "schema_version": 1, "generated_at": _now(),
        "title": "CoFlow-5 matched evaluation evidence report",
        "headline": {
            "claim_id": "paired-mixed-baseline-result",
            "basis": "paired/matched canonical evidence only",
            "scenario_hash": fixed["scenario_hash"], "common_evaluation_seeds": [fixed["seed"]],
            "controller_cells": list(REQUIRED_CONTROLLERS),
            "summary": claims[0]["text"],
        },
        "predeclared_metric_classifications": {
            "allowed": sorted(CLASSIFICATIONS),
            "requirement": "contract invariant or required stakeholder KPI",
            "directional": "direction declared before comparison; descriptive at one seed",
            "exploratory": "reported without confirmatory inference",
        },
        "confidence_inputs": {
            "common_seed_count": 1, "common_seeds": [fixed["seed"]],
            "paired_completed_baseline_runs": 2, "required_controller_cells": 3,
            "method": "descriptive paired evidence; no confidence interval with one common seed",
            "multiple_testing": "no inferential hypothesis tests; exploratory metrics are labelled",
        },
        "experiment_summary": {
            "cell_count": len(cells), "invalid_or_failed_cell_count": len(invalid_cells),
            "invalid_or_failed_reason_counts": dict(sorted(Counter(cell["reason_code"] for cell in invalid_cells).items())),
            "dimensions": ["controller", "scenario", "demand_regime", "incident", "communication_fault", "adviser_agent_enabled", "controller_fault", "recovery_mode", "synapse_fault", "seed"],
        },
        "metric_summary": {"row_count": len(metrics), "category_counts": dict(sorted(category_counts.items()))},
        "claims": claims,
        "null_results": [claims[4], claims[5]],
        "negative_or_mixed_results": [claims[0], claims[1], claims[6]],
        "claim_boundaries": {
            "emissions": "SUMO/HBEFA values are emission proxies only; no ambient sensor observations exist here.",
            "emergency": "Emergency metrics are simulated travel-time effects only and have no casualty interpretation.",
            "selection": "The headline uses the sole matched seed and does not select an extreme training outcome.",
            "scope": "Row 07 domain KPIs and row 08 fault outcomes are deterministic fixtures, not deployment estimates.",
        },
        "source_manifest_ids": sorted(manifests),
        "limitations_artifact": "limitations.md",
    }
    return report, claims


def _limitations() -> str:
    return """# Row 09 evaluation limitations

- **One common seed:** fixed-time, actuated, and cooperative Max-Pressure share scenario hash and seed 37, but one seed cannot support an inferential confidence interval.
- **Missing Max-Pressure traffic KPIs:** row 05 records native decisions and safety acceptance but no trip/run KPI table. The matched traffic-outcome cell is therefore `invalid` with reason `MISSING_REQUIRED_TRAFFIC_KPIS`.
- **Unexecuted ablations:** row 07 has specialist-on fixtures but no corresponding off runs; A4 and A5 experiments are also absent. Those cells remain visible as reason-coded invalid outcomes.
- **Proxy boundary:** the sustainability row is null-valued and explicitly labelled a SUMO/HBEFA emission proxy. No ambient sensor observations were collected.
- **Simulation boundary:** emergency effects are simulated travel-time and civilian-delay values. They do not establish real-world safety or casualty effects.
- **Scope and tails:** unfinished trips, teleports, standstills, mean, P95, and maximum values are retained where canonical raw evidence exists. Row 07 and row 08 are deterministic acceptance fixtures, not network-scale estimates.
- **Mixed result retained:** actuated improves completion and waiting metrics against fixed-time in the one matched run, while total time loss is higher. Neither side of that result is suppressed.
- **Selection rule:** the headline is the sole paired/matched baseline evidence, not a selected extreme outcome.
"""


def _publish_directory(staging: Path, destination: Path) -> None:
    backup = destination.parent / f".{destination.name}.previous-{uuid.uuid4()}"
    moved_old = False
    try:
        if destination.exists():
            destination.replace(backup)
            moved_old = True
        staging.replace(destination)
    except Exception:
        if moved_old and backup.exists() and not destination.exists():
            backup.replace(destination)
        raise
    else:
        if moved_old:
            shutil.rmtree(backup, ignore_errors=True)


def generate_evaluation_artifacts(root: Path, output_dir: Path | None = None) -> dict[str, Any]:
    """Validate rows 04--08 and atomically generate exactly five row-09 artifacts."""
    root = root.resolve()
    destination = (output_dir or root / "harness/work/09-eval-harness/artifacts").resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    for parent in (root / "harness/work").iterdir():
        if parent.is_dir():
            for stale in parent.glob(".artifacts.staging-*"):
                shutil.rmtree(stale, ignore_errors=True)
    for pattern in (f".{destination.name}.staging-*", f".{destination.name}.previous-*"):
        for stale in destination.parent.glob(pattern):
            shutil.rmtree(stale, ignore_errors=True)
    staging = destination.parent / f".{destination.name}.staging-{uuid.uuid4()}"
    staging.mkdir()
    try:
        manifests, directories = _validate_and_load_manifests(root)
        core_cells, metrics, by_controller = _build_core_cells(manifests, directories)
        cooperation_cells, cooperation_metrics, cooperation_events = _build_cooperation(manifests, directories)
        fault_cells, fault_metrics, fault_decisions, comparison = _build_faults(manifests, directories)
        cells = core_cells + _build_adviser_windows(manifests, directories) + cooperation_cells + fault_cells
        metrics.extend(cooperation_metrics)
        metrics.extend(fault_metrics)
        _add_unavailable_sustainability_and_reproducibility(metrics, by_controller)

        baseline_rows = {
            row["controller"]: row for row in _artifact_rows(
                directories, by_controller["fixed-time"]["run_id"], "run_kpis.parquet"
            )
        }
        report, claims = _report(
            manifests, by_controller, baseline_rows, cooperation_events,
            fault_decisions, comparison, cells, metrics,
        )
        audit = _join_audit(manifests, directories, cells, metrics, claims)
        if not audit["pass"]:
            raise ValueError(f"evaluation join audit failed: {audit['orphans']}")

        pq.write_table(pa.Table.from_pylist(cells, schema=CELL_SCHEMA), staging / "experiment-cells.parquet", compression="zstd")
        pq.write_table(pa.Table.from_pylist(metrics, schema=KPI_SCHEMA), staging / "run_kpis.parquet", compression="zstd")
        _write_json(staging / "evaluation-report.json", report)
        _write_json(staging / "join-audit.json", audit)
        (staging / "limitations.md").write_text(_limitations(), encoding="utf-8")
        if {path.name for path in staging.iterdir()} != OUTPUT_NAMES:
            raise ValueError("row 09 output set is not exact")
        _publish_directory(staging, destination)
        return report
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
