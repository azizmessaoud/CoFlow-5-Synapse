from __future__ import annotations

import hashlib
import json
import math
import shutil
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import pyarrow.parquet as pq

MISSING = "not in this run"
CONTRACT_PATH = Path("harness/work/10c-evidence-page/contract.json")
DEFAULT_OUTPUT = Path("harness/work/10c-evidence-page/artifacts")
FROZEN_PACKS = (
    "02-evidence-bundle",
    "03-safety-mask",
    "04-baselines",
    "05-max-pressure",
    "06-message-board",
    "07-a2-a3",
    "08-failure-injection",
    "09-eval-harness",
    "10-a4-a5",
    "10b-max-pressure-trip-kpis",
)
SOURCE_FILES = (
    "scripts/generate_evidence_page.py",
    "scripts/show_evidence_page.py",
    "src/coflow5/evidence/professor_page.py",
)


class EvidencePageError(RuntimeError):
    """Evidence cannot be released as a factual professor page."""


@dataclass(frozen=True)
class ControllerResult:
    run_id: str
    scenario_hash: str
    controller: str
    seed: int
    planned_trips: int
    completed_trips: int
    unfinished_trips: int
    mean_waiting_seconds: float
    p95_waiting_seconds: float
    total_time_loss_seconds: float
    standstill_vehicle_seconds: int
    teleport_events: int


@dataclass(frozen=True)
class TrafficEvidence:
    source_row: str
    run_id: str
    scenario_hash: str
    controller: str
    seed: int
    configured_horizon_seconds: float
    planned_trips: int
    completed_trips: int
    unfinished_trips: int
    mean_waiting_seconds: float
    p95_waiting_seconds: float
    total_time_loss_seconds: float
    standstill_vehicle_seconds: int
    teleport_events: int
    advisory_message_count: int
    same_run_accepted_requests: str
    same_run_rejected_requests: str
    same_run_reason_codes: str
    decisions: int
    safety_events: int
    accepted_commands: int
    illegal_or_conflicting_executed_commands: int
    writer_count_by_signal: Mapping[str, int]
    comparison: tuple[ControllerResult, ...]


@dataclass(frozen=True)
class AdviceEvidence:
    source_row: str
    run_id: str
    scenario_hash: str
    fixture_label: str
    accepted_requests: int
    rejected_requests: int
    reason_codes: tuple[str, ...]
    selected_forecast_model: str
    selected_validation_mae: float
    persistence_validation_mae: float
    lightgbm_status: str
    classifications: tuple[str, ...]
    sustainability_outcomes: tuple[str, ...]
    proxy_label: str
    specialist_signal_writes: int


@dataclass(frozen=True)
class RecoveryEvidence:
    source_row: str
    run_id: str
    scenario_hash: str
    fixture_label: str
    required_ladder: tuple[str, ...]
    observed_transitions: tuple[tuple[str, str], ...]
    unexpected_transitions: tuple[str, ...]
    legal_local_decisions: int
    illegal_decisions: int
    action_sequences_unchanged_when_synapse_fails: bool


@dataclass(frozen=True)
class EvidencePage:
    schema_version: int
    page_id: str
    traffic: TrafficEvidence
    advice: AdviceEvidence
    recovery: RecoveryEvidence
    one_seed_only: bool
    significance_test_performed: bool
    winner_claim: None
    limitations: tuple[str, ...]
    claim_flags: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "page_id": self.page_id,
            "sections": {
                "traffic": {
                    **asdict(self.traffic),
                    "same_run_request_detail": {
                        "accepted_requests": self.traffic.same_run_accepted_requests,
                        "rejected_requests": self.traffic.same_run_rejected_requests,
                        "reason_codes": self.traffic.same_run_reason_codes,
                    },
                },
                "advice_fixture": asdict(self.advice),
                "recovery_fixture": asdict(self.recovery),
            },
            "one_seed_only": self.one_seed_only,
            "significance_test_performed": self.significance_test_performed,
            "winner_claim": self.winner_claim,
            "limitations": list(self.limitations),
            "claim_flags": list(self.claim_flags),
        }


def _hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise EvidencePageError(f"invalid JSON evidence: {path}") from exc
    if not isinstance(value, dict):
        raise EvidencePageError(f"JSON evidence is not an object: {path}")
    return value


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(dict(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _finite(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise EvidencePageError(f"non-numeric evidence field: {field}")
    number = float(value)
    if not math.isfinite(number):
        raise EvidencePageError(f"non-finite evidence field: {field}")
    return number


def _integer(value: Any, field: str) -> int:
    number = _finite(value, field)
    if not number.is_integer():
        raise EvidencePageError(f"non-integer evidence field: {field}")
    return int(number)


def verify_locked_inputs(root: Path, locked_inputs: Mapping[str, str]) -> None:
    mismatches: list[str] = []
    for relative, expected in locked_inputs.items():
        path = root / relative
        if not path.is_file() or _hash(path) != expected:
            mismatches.append(relative)
    if mismatches:
        raise EvidencePageError("locked input hash mismatch: " + ", ".join(sorted(mismatches)))


def require_green_gate(gate_path: Path, contract_path: Path) -> dict[str, Any]:
    gate = _read_json(gate_path)
    contract = _read_json(contract_path)
    expected_hash = _hash(contract_path)
    if gate.get("id") != contract.get("id") or gate.get("contractHash") != expected_hash:
        raise EvidencePageError(f"source gate contract mismatch: {gate_path}")
    if not (
        gate.get("pass") is True
        and gate.get("openDeltas") == 0
        and gate.get("decidedBy") == "tests-and-files"
    ):
        raise EvidencePageError(f"source gate is not green: {gate_path}")
    return gate


def _verify_manifest(root: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = _read_json(manifest_path)
    if manifest.get("status") != "completed" or manifest.get("immutable") is not True:
        raise EvidencePageError(f"source manifest is not completed and immutable: {manifest_path}")
    artifact_dir = manifest_path.parent
    for reference in manifest.get("artifact_references", []):
        if not isinstance(reference, dict) or not isinstance(reference.get("path"), str):
            raise EvidencePageError(f"malformed artifact reference: {manifest_path}")
        artifact = artifact_dir / reference["path"]
        if not artifact.is_file() or _hash(artifact) != reference.get("sha256"):
            raise EvidencePageError(f"manifest artifact hash mismatch: {artifact}")
    for relative, expected in manifest.get("source_hashes", {}).items():
        source = root / relative
        if not source.is_file() or _hash(source) != expected:
            raise EvidencePageError(f"manifest source hash mismatch: {relative}")
    return manifest


def _verify_rows(
    rows: Sequence[Mapping[str, Any]], manifest: Mapping[str, Any], label: str,
) -> None:
    run_id = manifest.get("run_id")
    scenario_hash = manifest.get("scenario_hash")
    if not rows:
        raise EvidencePageError(f"empty evidence table: {label}")
    if any(row.get("run_id") != run_id or row.get("scenario_hash") != scenario_hash for row in rows):
        raise EvidencePageError(f"identity mismatch in {label}")


def _controller_result(row: Mapping[str, Any]) -> ControllerResult:
    return ControllerResult(
        run_id=str(row["run_id"]),
        scenario_hash=str(row["scenario_hash"]),
        controller=str(row["controller"]),
        seed=_integer(row["seed"], "comparison.seed"),
        planned_trips=_integer(row["planned_trips"], "comparison.planned_trips"),
        completed_trips=_integer(row["completed_trips"], "comparison.completed_trips"),
        unfinished_trips=_integer(row["unfinished_trips"], "comparison.unfinished_trips"),
        mean_waiting_seconds=_finite(row["mean_waiting_time_s"], "comparison.mean_waiting"),
        p95_waiting_seconds=_finite(row["p95_waiting_time_s"], "comparison.p95_waiting"),
        total_time_loss_seconds=_finite(row["total_time_loss_s"], "comparison.total_time_loss"),
        standstill_vehicle_seconds=_integer(row["standstill_vehicle_seconds"], "comparison.standstill"),
        teleport_events=_integer(row["teleport_events"], "comparison.teleports"),
    )


def _page_id(contract_hash: str, locked_inputs: Mapping[str, str]) -> str:
    identity = json.dumps(
        {"contract_hash": contract_hash, "locked_inputs": dict(sorted(locked_inputs.items()))},
        sort_keys=True,
        separators=(",", ":"),
    )
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "coflow5:evidence-page:" + identity))


def load_evidence_page(root: Path) -> EvidencePage:
    root = root.resolve()
    contract_path = root / CONTRACT_PATH
    contract = _read_json(contract_path)
    locked_inputs = contract.get("locked_inputs")
    if not isinstance(locked_inputs, dict):
        raise EvidencePageError("Row 10c contract lacks locked inputs")
    verify_locked_inputs(root, locked_inputs)

    source_specs = {
        "traffic": (
            root / "harness/work/10b-max-pressure-trip-kpis/gate.json",
            root / "harness/work/10b-max-pressure-trip-kpis/contract.json",
            root / "harness/work/10b-max-pressure-trip-kpis/artifacts/run_manifest.json",
        ),
        "advice": (
            root / "harness/work/10-a4-a5/gate.json",
            root / "harness/work/10-a4-a5/contract.json",
            root / "harness/work/10-a4-a5/artifacts/run_manifest.json",
        ),
        "recovery": (
            root / "harness/work/08-failure-injection/gate.json",
            root / "harness/work/08-failure-injection/contract.json",
            root / "harness/work/08-failure-injection/artifacts/run_manifest.json",
        ),
    }
    manifests: dict[str, dict[str, Any]] = {}
    for name, (gate_path, source_contract, manifest_path) in source_specs.items():
        require_green_gate(gate_path, source_contract)
        manifests[name] = _verify_manifest(root, manifest_path)

    traffic_manifest = manifests["traffic"]
    traffic_rows = pq.read_table(
        root / "harness/work/10b-max-pressure-trip-kpis/artifacts/run_kpis.parquet"
    ).to_pylist()
    _verify_rows(traffic_rows, traffic_manifest, "Row 10b run KPIs")
    if len(traffic_rows) != 1:
        raise EvidencePageError("Row 10b requires exactly one Max-Pressure KPI row")
    traffic_row = traffic_rows[0]
    comparison_json = _read_json(
        root / "harness/work/10b-max-pressure-trip-kpis/artifacts/matched-comparison.json"
    )
    if not (
        comparison_json.get("parity_pass") is True
        and comparison_json.get("one_seed_only") is True
        and comparison_json.get("significance_test_performed") is False
        and comparison_json.get("winner_claim") is None
    ):
        raise EvidencePageError("matched comparison claim boundary is invalid")
    comparison = tuple(_controller_result(row) for row in comparison_json.get("controller_rows", []))
    if tuple(row.controller for row in comparison) != (
        "fixed-time", "actuated", "cooperative-max-pressure"
    ):
        raise EvidencePageError("matched comparison controller order is invalid")
    max_pressure = comparison[-1]
    if (
        max_pressure.run_id != traffic_manifest.get("run_id")
        or max_pressure.scenario_hash != traffic_manifest.get("scenario_hash")
        or max_pressure.completed_trips != _integer(traffic_row["completed_trips"], "traffic.completed")
    ):
        raise EvidencePageError("Max-Pressure comparison row does not match traffic run")
    runtime = traffic_manifest.get("runtime_audit", {})
    traffic = TrafficEvidence(
        source_row="10b-max-pressure-trip-kpis",
        run_id=str(traffic_manifest["run_id"]),
        scenario_hash=str(traffic_manifest["scenario_hash"]),
        controller=str(traffic_manifest["controller"]),
        seed=_integer(traffic_row["seed"], "traffic.seed"),
        configured_horizon_seconds=_finite(
            traffic_manifest["configured_horizon_seconds"], "traffic.horizon"
        ),
        planned_trips=_integer(traffic_row["planned_trips"], "traffic.planned"),
        completed_trips=_integer(traffic_row["completed_trips"], "traffic.completed"),
        unfinished_trips=_integer(traffic_row["unfinished_trips"], "traffic.unfinished"),
        mean_waiting_seconds=_finite(traffic_row["mean_waiting_time_s"], "traffic.mean_waiting"),
        p95_waiting_seconds=_finite(traffic_row["p95_waiting_time_s"], "traffic.p95_waiting"),
        total_time_loss_seconds=_finite(traffic_row["total_time_loss_s"], "traffic.time_loss"),
        standstill_vehicle_seconds=_integer(
            traffic_row["standstill_vehicle_seconds"], "traffic.standstill"
        ),
        teleport_events=_integer(traffic_row["teleport_events"], "traffic.teleports"),
        advisory_message_count=_integer(
            runtime.get("advisory_message_count"), "traffic.advisory_count"
        ),
        same_run_accepted_requests=MISSING,
        same_run_rejected_requests=MISSING,
        same_run_reason_codes=MISSING,
        decisions=_integer(runtime.get("decision_count"), "traffic.decisions"),
        safety_events=_integer(runtime.get("safety_event_count"), "traffic.safety_events"),
        accepted_commands=_integer(
            runtime.get("accepted_command_count"), "traffic.accepted_commands"
        ),
        illegal_or_conflicting_executed_commands=_integer(
            runtime.get("rejected_or_conflicting_executed_commands"),
            "traffic.illegal_commands",
        ),
        writer_count_by_signal=dict(runtime.get("writer_count_by_signal", {})),
        comparison=comparison,
    )
    if (
        traffic.completed_trips + traffic.unfinished_trips != traffic.planned_trips
        or traffic.writer_count_by_signal != {"J0": 1}
        or traffic.decisions != traffic.safety_events
        or traffic.decisions != traffic.accepted_commands
    ):
        raise EvidencePageError("traffic accounting or safety reconciliation failed")

    advice_manifest = manifests["advice"]
    decision_rows = pq.read_table(
        root / "harness/work/10-a4-a5/artifacts/decision_events.parquet"
    ).to_pylist()
    forecast_rows = pq.read_table(
        root / "harness/work/10-a4-a5/artifacts/forecast-evaluation.parquet"
    ).to_pylist()
    sustainability_rows = pq.read_table(
        root / "harness/work/10-a4-a5/artifacts/sustainability-kpis.parquet"
    ).to_pylist()
    for label, rows in (
        ("Row 10 decisions", decision_rows),
        ("Row 10 forecasts", forecast_rows),
        ("Row 10 sustainability", sustainability_rows),
    ):
        _verify_rows(rows, advice_manifest, label)
    accepted = [row for row in decision_rows if row.get("accepted") is True]
    rejected = [row for row in decision_rows if row.get("accepted") is False]
    reason_codes = tuple(sorted(str(row["reason_code"]) for row in decision_rows))
    model_scores = {
        str(row["model_name"]): row
        for row in forecast_rows
        if row.get("record_kind") == "model_score"
    }
    selected = [row for row in model_scores.values() if row.get("selected_model") is True]
    if len(selected) != 1 or "persistence" not in model_scores or "lightgbm" not in model_scores:
        raise EvidencePageError("forecast model selection evidence is incomplete")
    classifications = tuple(sorted(
        str(row["classification"])
        for row in forecast_rows
        if row.get("record_kind") == "classification"
    ))
    proxy_labels = {str(row.get("proxy_label")) for row in sustainability_rows}
    if proxy_labels != {"SUMO/HBEFA emission proxy — not measured air quality"}:
        raise EvidencePageError("sustainability proxy claim boundary is invalid")
    advice = AdviceEvidence(
        source_row="10-a4-a5",
        run_id=str(advice_manifest["run_id"]),
        scenario_hash=str(advice_manifest["scenario_hash"]),
        fixture_label="deterministic A4/A5 advice fixture — not the traffic KPI run",
        accepted_requests=len(accepted),
        rejected_requests=len(rejected),
        reason_codes=reason_codes,
        selected_forecast_model=str(selected[0]["model_name"]),
        selected_validation_mae=_finite(selected[0]["validation_mae"], "advice.selected_mae"),
        persistence_validation_mae=_finite(
            model_scores["persistence"]["validation_mae"], "advice.persistence_mae"
        ),
        lightgbm_status=str(model_scores["lightgbm"]["status"]),
        classifications=classifications,
        sustainability_outcomes=tuple(sorted(str(row["classification"]) for row in sustainability_rows)),
        proxy_label=next(iter(proxy_labels)),
        specialist_signal_writes=sum(bool(row.get("specialist_signal_write")) for row in decision_rows),
    )
    if advice.accepted_requests != 1 or advice.rejected_requests != 2 or advice.specialist_signal_writes:
        raise EvidencePageError("A4/A5 fixture decision accounting failed")

    recovery_manifest = manifests["recovery"]
    recovery_audit = _read_json(
        root / "harness/work/08-failure-injection/artifacts/recovery-audit.json"
    )
    if (
        recovery_audit.get("run_id") != recovery_manifest.get("run_id")
        or recovery_audit.get("scenario_hash") != recovery_manifest.get("scenario_hash")
        or recovery_audit.get("valid") is not True
    ):
        raise EvidencePageError("recovery fixture identity or validity failed")
    action_comparison = _read_json(
        root / "harness/work/08-failure-injection/artifacts/action-sequence-comparison.json"
    )
    recovery = RecoveryEvidence(
        source_row="08-failure-injection",
        run_id=str(recovery_manifest["run_id"]),
        scenario_hash=str(recovery_manifest["scenario_hash"]),
        fixture_label="failure-injection recovery fixture — not the traffic KPI run",
        required_ladder=tuple(str(value) for value in recovery_audit["required_recovery_ladder"]),
        observed_transitions=tuple(
            (str(pair[0]), str(pair[1])) for pair in recovery_audit["observed_required_transitions"]
        ),
        unexpected_transitions=tuple(str(value) for value in recovery_audit["unexpected_transitions"]),
        legal_local_decisions=_integer(
            recovery_audit["legal_local_decision_count"], "recovery.legal_decisions"
        ),
        illegal_decisions=_integer(
            recovery_audit["illegal_decision_count"], "recovery.illegal_decisions"
        ),
        action_sequences_unchanged_when_synapse_fails=bool(
            action_comparison.get("all_action_sequences_equal")
            or recovery_audit.get("action_sequence_hashes_equal")
        ),
    )
    identities = {
        (traffic.run_id, traffic.scenario_hash),
        (advice.run_id, advice.scenario_hash),
        (recovery.run_id, recovery.scenario_hash),
    }
    if len(identities) != 3:
        raise EvidencePageError("source evidence identities were merged")

    limitations = (
        "One matched seed is insufficient for a winner or significance claim.",
        "Max-Pressure reproduces the bounded Row 05 advisory fixture; baselines have no specialist request.",
        "Same-run accepted/rejected request details were not persisted in the Row 10b traffic KPI run.",
        "A4/A5 outcomes are a separate deterministic fixture, not measured traffic or ambient air quality.",
        "Recovery outcomes are a separate failure-injection fixture, not the matched traffic KPI run.",
    )
    claim_flags = (
        "No lives saved.",
        "No measured air quality.",
        "No deployment claim.",
        "No winner announced.",
        "No best-episode headline.",
    )
    return EvidencePage(
        schema_version=1,
        page_id=_page_id(_hash(contract_path), locked_inputs),
        traffic=traffic,
        advice=advice,
        recovery=recovery,
        one_seed_only=True,
        significance_test_performed=False,
        winner_claim=None,
        limitations=limitations,
        claim_flags=claim_flags,
    )


def render_evidence_page(page: EvidencePage) -> str:
    traffic = page.traffic
    advice = page.advice
    recovery = page.recovery
    lines = [
        "=== CoFlow-5 professor evidence page ===",
        f"Page ID: {page.page_id}",
        "",
        "TRAFFIC OUTCOME — native matched run",
        f"Source: Row {traffic.source_row}",
        f"Run ID: {traffic.run_id}",
        f"Scenario hash: {traffic.scenario_hash}",
        f"Controller: {traffic.controller}",
        f"Seed: {traffic.seed}",
        f"Configured simulation time: 0 to {traffic.configured_horizon_seconds:.0f} seconds",
        f"Trips completed / planned: {traffic.completed_trips} / {traffic.planned_trips}",
        f"Unfinished trips: {traffic.unfinished_trips}",
        f"Mean waiting seconds: {traffic.mean_waiting_seconds:.2f}",
        f"P95 waiting seconds: {traffic.p95_waiting_seconds:.2f}",
        f"Total time loss seconds: {traffic.total_time_loss_seconds:.2f}",
        f"Standstill vehicle-seconds: {traffic.standstill_vehicle_seconds}",
        f"Teleport events: {traffic.teleport_events}",
        "",
        "Matched observed comparison — same scenario and seed",
    ]
    for row in traffic.comparison:
        lines.append(
            f"- {row.controller}: {row.completed_trips}/{row.planned_trips} completed; "
            f"mean wait {row.mean_waiting_seconds:.2f}s; P95 wait {row.p95_waiting_seconds:.2f}s; "
            f"time loss {row.total_time_loss_seconds:.2f}s"
        )
    lines.extend((
        "",
        "Same-run specialist request detail",
        f"Advisory messages observed: {traffic.advisory_message_count}",
        f"Accepted requests: {traffic.same_run_accepted_requests}",
        f"Rejected requests: {traffic.same_run_rejected_requests}",
        f"Reason codes: {traffic.same_run_reason_codes}",
        "",
        "Safety in this traffic run",
        f"A1 decisions / safety events / commands: {traffic.decisions} / {traffic.safety_events} / {traffic.accepted_commands}",
        f"Writer count: {dict(traffic.writer_count_by_signal)}",
        f"Illegal or conflicting executed commands: {traffic.illegal_or_conflicting_executed_commands}",
        "",
        "Related A4/A5 fixture — separate run",
        f"Source: Row {advice.source_row}",
        f"Run ID: {advice.run_id}",
        f"Scenario hash: {advice.scenario_hash}",
        f"Accepted / rejected advice: {advice.accepted_requests} / {advice.rejected_requests}",
        "Reason codes: " + ", ".join(advice.reason_codes),
        f"Forecast model: {advice.selected_forecast_model}; validation MAE {advice.selected_validation_mae:.2f}",
        f"Persistence validation MAE: {advice.persistence_validation_mae:.2f}",
        f"LightGBM: {advice.lightgbm_status}",
        "Classifications: " + ", ".join(advice.classifications),
        "Sensitive-link outcomes: " + ", ".join(advice.sustainability_outcomes),
        f"Proxy label: {advice.proxy_label}",
        f"Specialist signal writes: {advice.specialist_signal_writes}",
        "",
        "Recovery fixture — separate run",
        f"Source: Row {recovery.source_row}",
        f"Run ID: {recovery.run_id}",
        f"Scenario hash: {recovery.scenario_hash}",
        "Required ladder: " + " -> ".join(recovery.required_ladder),
        f"Unexpected transitions: {len(recovery.unexpected_transitions)}",
        f"Legal / illegal local decisions: {recovery.legal_local_decisions} / {recovery.illegal_decisions}",
        "Synapse failure changed traffic actions: "
        + ("no" if recovery.action_sequences_unchanged_when_synapse_fails else "not established"),
        "",
        "Limitations",
    ))
    lines.extend(f"- {value}" for value in page.limitations)
    lines.append("")
    lines.append("Claim flags")
    lines.extend(f"- {value}" for value in page.claim_flags)
    return "\n".join(lines) + "\n"


def forbid_protected_destination(root: Path, destination: Path) -> None:
    work = (root / "harness/work").resolve()
    protected = [(work / name).resolve() for name in FROZEN_PACKS]
    if any(destination == path or path in destination.parents for path in protected):
        raise EvidencePageError("Row 10c cannot write into a frozen evidence pack")


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


def generate_evidence_page_artifacts(
    root: Path, output_dir: Path | None = None,
) -> dict[str, Any]:
    root = root.resolve()
    destination = (output_dir or root / DEFAULT_OUTPUT).resolve()
    forbid_protected_destination(root, destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    for pattern in (f".{destination.name}.staging-*", f".{destination.name}.previous-*"):
        for stale in destination.parent.glob(pattern):
            shutil.rmtree(stale, ignore_errors=True)
    staging = destination.parent / f".{destination.name}.staging-{uuid.uuid4()}"
    staging.mkdir()
    try:
        page = load_evidence_page(root)
        page_dict = page.to_dict()
        _write_json(staging / "evidence-page.json", page_dict)
        (staging / "evidence-page.txt").write_text(
            render_evidence_page(page), encoding="utf-8"
        )
        contract = _read_json(root / CONTRACT_PATH)
        input_audit = {
            "schema_version": 1,
            "page_id": page.page_id,
            "contract_hash": _hash(root / CONTRACT_PATH),
            "locked_input_count": len(contract["locked_inputs"]),
            "locked_input_hashes": dict(sorted(contract["locked_inputs"].items())),
            "locked_input_hash_mismatches": 0,
            "source_gates_green": 3,
            "manifest_artifact_hash_mismatches": 0,
            "identity_errors": 0,
            "source_sections": [
                {
                    "source_row": page.traffic.source_row,
                    "run_id": page.traffic.run_id,
                    "scenario_hash": page.traffic.scenario_hash,
                },
                {
                    "source_row": page.advice.source_row,
                    "run_id": page.advice.run_id,
                    "scenario_hash": page.advice.scenario_hash,
                },
                {
                    "source_row": page.recovery.source_row,
                    "run_id": page.recovery.run_id,
                    "scenario_hash": page.recovery.scenario_hash,
                },
            ],
            "cross_run_merge_count": 0,
            "generated_text_model": None,
            "network_access": False,
        }
        _write_json(staging / "input-audit.json", input_audit)
        references = []
        for name, kind in (
            ("evidence-page.txt", "professor_evidence_page_text"),
            ("evidence-page.json", "professor_evidence_page_model"),
            ("input-audit.json", "professor_evidence_input_audit"),
        ):
            path = staging / name
            references.append({
                "path": name,
                "sha256": _hash(path),
                "bytes": path.stat().st_size,
                "schema_name": kind,
                "schema_version": 1,
            })
        manifest = {
            "schema_version": 1,
            "page_id": page.page_id,
            "status": "completed",
            "immutable": True,
            "generator": "deterministic-template",
            "contract_hash": _hash(root / CONTRACT_PATH),
            "source_hashes": {relative: _hash(root / relative) for relative in SOURCE_FILES},
            "source_run_ids": [page.traffic.run_id, page.advice.run_id, page.recovery.run_id],
            "artifact_references": references,
            "claim_boundary": "Separate immutable evidence slices; no cross-run causal claim and no generated prose.",
        }
        _write_json(staging / "page-manifest.json", manifest)
        _publish_atomic(staging, destination)
        return manifest
    except Exception:
        shutil.rmtree(staging, ignore_errors=True)
        raise
