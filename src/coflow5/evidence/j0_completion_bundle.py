from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq

from coflow5.evaluation.j0_completion import audit_j0_completion


def assemble_j0_completion_bundle(root: Path) -> dict[str, Any]:
    """Join captured native rows with existing recovery and advisory evidence."""
    root = root.resolve()
    artifacts = root / "harness/work/10e/artifacts"
    matched = json.loads((artifacts / "matched-runs.json").read_text(encoding="utf-8"))
    ablations = json.loads((artifacts / "j0-ablations.json").read_text(encoding="utf-8"))
    recovery = json.loads(
        (root / "harness/work/08-failure-injection/artifacts/recovery-audit.json")
        .read_text(encoding="utf-8")
    )
    action_comparison = json.loads(
        (
            root
            / "harness/work/08-failure-injection/artifacts/action-sequence-comparison.json"
        ).read_text(encoding="utf-8")
    )
    advisory = json.loads(
        (root / "harness/work/10d/artifacts/j0-advisory-loop.json").read_text(
            encoding="utf-8"
        )
    )
    row07_manifest = json.loads(
        (root / "harness/work/07-a2-a3/artifacts/run_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    fault_rows = pq.read_table(
        root / "harness/work/08-failure-injection/artifacts/faults.parquet"
    ).to_pylist()
    decision_rows = pq.read_table(
        root / "harness/work/07-a2-a3/artifacts/decision_events.parquet"
    ).to_pylist()
    transition_rows = [
        row for row in fault_rows if row["event_kind"] == "transition"
    ]
    specialist_event = decision_rows[0]
    transition_by_trigger = {row["trigger"]: row for row in transition_rows}
    synapse_event = json.loads(
        (
            root
            / "harness/work/08-failure-injection/artifacts/action-sequence-comparison.json"
        ).read_text(encoding="utf-8")
    )["variants"]["hosted_provider_unavailable"]["observation_receipts"][0]
    source_rows = {
        "controller": (
            recovery["run_id"],
            recovery["scenario_hash"],
            transition_by_trigger["injected_max_pressure_unavailable"]["event_id"],
        ),
        "communication": (
            recovery["run_id"],
            recovery["scenario_hash"],
            fault_rows[0]["event_id"],
        ),
        "synapse": (
            recovery["run_id"],
            recovery["scenario_hash"],
            synapse_event["event_id"],
        ),
        "specialist": (
            row07_manifest["run_id"],
            row07_manifest["scenario_hash"],
            specialist_event["event_id"],
        ),
        "forecast": (
            advisory["run_id"],
            advisory["scenario_hash"],
            advisory["incident"]["event_id"],
        ),
    }

    recovery_specs = (
        (
            "COOPERATIVE_MAX_PRESSURE",
            "ACTUATED",
            "controller",
            "native-row-08",
            transition_by_trigger["injected_max_pressure_unavailable"]["event_id"],
        ),
        (
            "ACTUATED",
            "FIXED_TIME",
            "controller",
            "native-row-08",
            transition_by_trigger["injected_actuated_invalid_output"]["event_id"],
        ),
        ("COOPERATIVE_MAX_PRESSURE", "ACTUATED", "communication", "native-row-08", None),
        ("COOPERATIVE_MAX_PRESSURE", "ACTUATED", "synapse", "native-row-08", None),
        ("COOPERATIVE_MAX_PRESSURE", "ACTUATED", "specialist", "row-07-fixture", None),
        ("COOPERATIVE_MAX_PRESSURE", "ACTUATED", "forecast", "row-10d-fixture", None),
    )
    recovery_rows = [
        {
            "previous_mode": previous,
            "next_mode": next_mode,
            "failure_kind": failure_kind,
            "run_id": source_rows[failure_kind][0],
            "scenario_hash": source_rows[failure_kind][1],
            "event_id": event_id or source_rows[failure_kind][2],
            "evidence_basis": evidence_basis,
            "message_id": (
                advisory["advice"]["message_id"]
                if failure_kind == "forecast"
                else None
            ),
        }
        for previous, next_mode, failure_kind, evidence_basis, event_id in recovery_specs
    ]
    runs = matched["runs"]
    ablation_rows = ablations["rows"]
    audit = audit_j0_completion(
        runs,
        ablation_rows,
        recovery_rows,
        repeat_checks=[
            {
                "compatible": bool(action_comparison["control_inputs_hash"]),
                "action_hash_equal": action_comparison["hashes_equal"],
                "within_tolerance": action_comparison["hashes_equal"],
                "run_id": action_comparison["run_id"],
                "scenario_hash": action_comparison["scenario_hash"],
            }
        ],
    )
    bundle = {
        "schema_version": 1,
        "bundle_id": str(uuid.uuid4()),
        "status": "pass" if audit.pass_gate else "blocked",
        "audit": {
            "pass_gate": audit.pass_gate,
            "matched_seeds": list(audit.matched_seeds),
            "findings": [
                {"code": finding.code, "detail": finding.detail}
                for finding in audit.findings
            ],
        },
        "sources": {
            "matched_runs": "artifacts/matched-runs.json",
            "ablations": "artifacts/j0-ablations.json",
            "recovery": "08-failure-injection/artifacts/recovery-audit.json",
            "action_comparison": "08-failure-injection/artifacts/action-sequence-comparison.json",
            "advisory_loop": "10d/artifacts/j0-advisory-loop.json",
        },
        "recovery_events": recovery_rows,
        "forecast_provenance": {
            "run_id": advisory["run_id"],
            "scenario_hash": advisory["scenario_hash"],
            "event_id": advisory["incident"]["event_id"],
            "message_id": advisory["advice"]["message_id"],
            "evidence_basis": "row-10d-fixture",
        },
        "claim_boundary": (
            "Controlled J0 evidence only; native observations and labelled "
            "deterministic fixtures. No deployment, lives-saved, or measured "
            "air-quality claim."
        ),
    }
    destination = artifacts / "j0-completion-bundle.json"
    staging = destination.with_name(f".{destination.name}.staging-{uuid.uuid4()}")
    staging.write_text(json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    staging.replace(destination)
    return bundle
