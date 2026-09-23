from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pyarrow.parquet as pq

from coflow5.synapse.retrieval import sha256_file


class EvidenceReadError(ValueError):
    pass


@dataclass(frozen=True)
class EventIdentity:
    run_id: str
    scenario_hash: str
    event_id: str


@dataclass(frozen=True)
class ImmutableGraphDecision:
    run_id: str
    scenario_hash: str
    event_id: str
    graph_hash: str
    controller: str
    simulation_time: float
    signal_id: str
    accepted_action: str
    reason_code: str
    safety_accepted: bool
    downstream_blocked: bool
    evidence_path: str
    evidence_sha256: str

    def facts(self) -> dict[str, object]:
        return {
            "run_id": self.run_id,
            "scenario_hash": self.scenario_hash,
            "event_id": self.event_id,
            "graph_hash": self.graph_hash,
            "controller": self.controller,
            "simulation_time": self.simulation_time,
            "signal_id": self.signal_id,
            "accepted_action": self.accepted_action,
            "reason_code": self.reason_code,
            "safety_accepted": self.safety_accepted,
            "downstream_blocked": self.downstream_blocked,
        }


class ImmutableRow10fReader:
    """Reads exactly one hash-bound completed event and exposes no write methods."""

    def __init__(self, root: Path, contract_path: Path) -> None:
        self._root = root.resolve()
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        self._locked: dict[str, str] = dict(contract["locked_inputs"])
        self._gate_path = "harness/work/10f-graph-growth-benchmark/gate.json"
        self._manifest_path = "harness/work/10f-graph-growth-benchmark/artifacts/run_manifest.json"
        self._events_path = "harness/work/10f-graph-growth-benchmark/artifacts/decision_events.parquet"

    def _validated_json(self, relative: str) -> dict[str, object]:
        expected = self._locked.get(relative)
        if expected is None:
            raise EvidenceReadError(f"artifact is not sealed for Row 12: {relative}")
        path = self._root / relative
        if sha256_file(path) != expected:
            raise EvidenceReadError(f"sealed artifact hash mismatch: {relative}")
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise EvidenceReadError(f"artifact must contain an object: {relative}")
        return value

    def validate(self) -> dict[str, object]:
        gate = self._validated_json(self._gate_path)
        manifest = self._validated_json(self._manifest_path)
        event_expected = self._locked[self._events_path]
        if sha256_file(self._root / self._events_path) != event_expected:
            raise EvidenceReadError("sealed decision event hash mismatch")
        if gate.get("pass") is not True or gate.get("openDeltas") != 0:
            raise EvidenceReadError("Row 10f gate is not green")
        if manifest.get("status") != "completed" or manifest.get("immutable") is not True:
            raise EvidenceReadError("Row 10f manifest is not completed and immutable")
        references = manifest.get("artifact_references")
        if not isinstance(references, list):
            raise EvidenceReadError("Row 10f manifest has no artifact references")
        matches = [ref for ref in references if isinstance(ref, dict) and ref.get("path") == "decision_events.parquet"]
        if len(matches) != 1 or matches[0].get("sha256") != event_expected:
            raise EvidenceReadError("decision events are not hash-bound by Row 10f manifest")
        return manifest

    def read_event(self, identity: EventIdentity) -> ImmutableGraphDecision:
        if not identity.run_id or not identity.scenario_hash or not identity.event_id:
            raise EvidenceReadError("complete run, scenario, and event identity is required")
        manifest = self.validate()
        runs = manifest.get("runs")
        identities = [
            row for row in runs if isinstance(row, dict)
            and row.get("run_id") == identity.run_id
            and row.get("scenario_hash") == identity.scenario_hash
        ] if isinstance(runs, list) else []
        if len(identities) != 1:
            raise EvidenceReadError("run and scenario identity do not resolve exactly once")
        rows = pq.read_table(self._root / self._events_path).to_pylist()
        found = [
            row for row in rows
            if row["run_id"] == identity.run_id
            and row["scenario_hash"] == identity.scenario_hash
            and row["event_id"] == identity.event_id
        ]
        if len(found) != 1:
            raise EvidenceReadError("event identity does not resolve exactly once")
        row = found[0]
        if row["safety_accepted"] is not True:
            raise EvidenceReadError("event is not a completed accepted immutable decision")
        return ImmutableGraphDecision(
            run_id=row["run_id"], scenario_hash=row["scenario_hash"], event_id=row["event_id"],
            graph_hash=row["graph_hash"], controller=row["controller"],
            simulation_time=float(row["simulation_time"]), signal_id=row["signal_id"],
            accepted_action=row["accepted_action"], reason_code=row["reason_code"],
            safety_accepted=bool(row["safety_accepted"]),
            downstream_blocked=bool(row["downstream_blocked"]),
            evidence_path=self._events_path,
            evidence_sha256=self._locked[self._events_path],
        )

    def verify_bound_artifact(self, relative: str, expected_hash: str) -> bool:
        sealed_hash = self._locked.get(relative)
        return sealed_hash is not None and expected_hash == sealed_hash and sha256_file(self._root / relative) == sealed_hash
