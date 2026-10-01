from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from coflow5.api.errors import EvidenceError
from coflow5.api.records import (
    limitations_from_bundle,
    parse_page,
    read_rows,
    slice_page,
    sort_key,
)
from coflow5.api.validate import sha256_file, validate_bundle

RUN_FIELDS = ("run_id", "scenario_hash", "graph_hash", "controller", "seed", "demand_scale")


@dataclass
class AcceptedBundle:
    bundle_id: str
    path: Path
    artifact_hashes: dict[str, str]
    manifest: dict[str, Any]
    runs: dict[str, dict[str, Any]]
    primary_run_id: str


@dataclass
class RejectedBundle:
    code: str
    detail: str
    run_ids: tuple[str, ...] = ()


@dataclass
class EvidenceStore:
    """Read-only index of hash-bound evidence bundles. Never launches SUMO."""

    root: Path
    bundle_ids: tuple[str, ...] | None = None
    _accepted: list[AcceptedBundle] = field(default_factory=list)
    _rejected_runs: dict[str, RejectedBundle] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        self._scan()

    def list_runs(self) -> list[dict[str, Any]]:
        rows = [run for bundle in self._accepted for run in bundle.runs.values()]
        return sorted(rows, key=lambda row: str(row["run_id"]))

    def get_run(self, run_id: str) -> dict[str, Any]:
        self._reject_unsafe_id(run_id)
        bundle = self._bundle_for(run_id)
        return dict(bundle.runs[run_id])

    def events(self, run_id: str, limit: int | None, offset: int | None) -> dict[str, Any]:
        return self._page(run_id, "events.json", "decision_events.parquet", "events", ("event_id",), limit, offset)

    def kpis(self, run_id: str, limit: int | None, offset: int | None) -> dict[str, Any]:
        return self._page(run_id, "run_kpis.json", "run_kpis.parquet", "kpis", ("seed", "controller"), limit, offset)

    def graph_frames(self, run_id: str, limit: int | None, offset: int | None) -> dict[str, Any]:
        return self._page(
            run_id, "graph_frames.json", "graph_frames.parquet", "frames",
            ("simulation_time", "seed", "controller"), limit, offset,
        )

    def explanations(self, run_id: str, limit: int | None, offset: int | None) -> dict[str, Any]:
        self._require_known(run_id)
        rows: list[dict[str, Any]] = []
        seen_file = False
        for bundle in self._accepted:
            loaded = self._rows(bundle, "explanations.json", None, "explanations")
            if loaded is None:
                continue
            seen_file = True
            rows.extend(row for row in loaded if _explanation_run_id(row) == run_id)
        if not seen_file:
            raise EvidenceError("unavailable", "explanations are not in this evidence bundle")
        rows.sort(key=lambda row: sort_key(row, ("request_id",)))
        return slice_page(rows, *parse_page(limit, offset))

    def audits(self, run_id: str, limit: int | None, offset: int | None) -> dict[str, Any]:
        self._require_known(run_id)
        try:
            event_ids = {row.get("event_id") for row in self._owned_rows(run_id, "events.json", "decision_events.parquet", "events")}
        except EvidenceError as exc:
            if exc.code != "unavailable":
                raise
            event_ids = set()
        rows: list[dict[str, Any]] = []
        seen_file = False
        for bundle in self._accepted:
            loaded = self._rows(bundle, "evidence_audits.json", None, "audits")
            if loaded is None:
                continue
            seen_file = True
            for audit in loaded:
                references = audit.get("references") if isinstance(audit.get("references"), list) else []
                referenced = {item.get("event_id") for item in references if isinstance(item, dict)}
                if bundle.primary_run_id == run_id or referenced & event_ids:
                    rows.append(audit)
        if not seen_file:
            raise EvidenceError("unavailable", "audits are not in this evidence bundle")
        rows.sort(key=lambda row: sort_key(row, ("request_id",)))
        return slice_page(rows, *parse_page(limit, offset))

    def citations(self, run_id: str, limit: int | None, offset: int | None) -> dict[str, Any]:
        explanations = self.explanations(run_id, limit=50, offset=0)
        extra = explanations["total"]
        if extra > 50:
            gathered: list[dict[str, Any]] = []
            offset_rows = 0
            while offset_rows < extra:
                gathered.extend(self.explanations(run_id, limit=50, offset=offset_rows)["items"])
                offset_rows += 50
        else:
            gathered = explanations["items"]
        rows: list[dict[str, Any]] = []
        for explanation in gathered:
            citations = explanation.get("citations") if isinstance(explanation.get("citations"), list) else []
            for citation in citations:
                if isinstance(citation, dict):
                    copied = dict(citation)
                    if "chunk_id" in citation:
                        copied["chunk_id"] = citation["chunk_id"]
                    if "request_id" not in copied and "request_id" in explanation:
                        copied["request_id"] = explanation["request_id"]
                    rows.append(copied)
        rows.sort(key=lambda row: sort_key(row, ("request_id", "chunk_id", "source_id")))
        return slice_page(rows, *parse_page(limit, offset))

    def golden(self, run_id: str) -> dict[str, Any]:
        bundle = self._require_known(run_id)
        relative = "artifacts/golden_results.json"
        if relative not in bundle.artifact_hashes:
            raise EvidenceError("unavailable", "golden metrics are not in this evidence bundle")
        payload = json.loads((bundle.path / relative).read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise EvidenceError("corrupt_evidence", "golden_results.json must be an object")
        return payload

    def limitations(self, run_id: str) -> dict[str, Any]:
        bundle = self._require_known(run_id)
        values = limitations_from_bundle(bundle.path, bundle.artifact_hashes, bundle.manifest if bundle.primary_run_id == run_id else {})
        if not values:
            raise EvidenceError("unavailable", "limitations are not in this evidence bundle")
        return {"run_id": run_id, "limitations": values}

    def load_artifact(self, run_id: str, name: str) -> tuple[bytes, str]:
        self._reject_unsafe_id(run_id)
        if Path(name).name != name or name in {"", ".", ".."}:
            raise EvidenceError("not_found", "unknown artifact")
        bundle = self._require_known(run_id)
        relative = f"artifacts/{name}"
        if relative not in bundle.artifact_hashes:
            raise EvidenceError("not_found", "unknown artifact")
        path = bundle.path / relative
        return path.read_bytes(), path.suffix.lower()

    def _scan(self) -> None:
        if not self.root.is_dir():
            return
        names = self.bundle_ids if self.bundle_ids is not None else tuple(
            path.name for path in sorted(self.root.iterdir()) if path.is_dir()
        )
        for name in names:
            bundle = self.root / name
            if not bundle.is_dir():
                continue
            if not (bundle / "gate.json").is_file():
                continue
            try:
                validated = validate_bundle(bundle)
                hashes = validated["artifact_hashes"]
                assert isinstance(hashes, dict)
                manifest = _trusted_manifest(bundle, hashes)
                if manifest is None:
                    raise EvidenceError("corrupt_evidence", "run_manifest.json is not a hash-bound artifact")
                accepted = AcceptedBundle(
                    bundle_id=name,
                    path=bundle,
                    artifact_hashes={str(key): str(value) for key, value in hashes.items()},
                    manifest=manifest,
                    runs=_run_index(manifest),
                    primary_run_id=str(manifest["run_id"]),
                )
                self._accepted.append(accepted)
            except EvidenceError as exc:
                for run_id in _rejected_run_ids(bundle):
                    self._rejected_runs[run_id] = RejectedBundle(exc.code, exc.detail, (run_id,))

    def _bundle_for(self, run_id: str) -> AcceptedBundle:
        return self._require_known(run_id)

    def _require_known(self, run_id: str) -> AcceptedBundle:
        self._reject_unsafe_id(run_id)
        matches = [bundle for bundle in self._accepted if run_id in bundle.runs]
        if len(matches) > 1:
            raise EvidenceError("corrupt_evidence", "run_id is claimed by more than one bundle")
        if len(matches) == 1:
            return matches[0]
        rejected = self._rejected_runs.get(run_id)
        if rejected is not None:
            raise EvidenceError(rejected.code, rejected.detail)
        raise EvidenceError("not_found", "unknown run_id")

    def _page(
        self, run_id: str, json_name: str, parquet_name: str, key: str,
        order: tuple[str, ...], limit: int | None, offset: int | None,
    ) -> dict[str, Any]:
        rows = self._owned_rows(run_id, json_name, parquet_name, key)
        rows.sort(key=lambda row: sort_key(row, order))
        return slice_page(rows, *parse_page(limit, offset))

    def _owned_rows(self, run_id: str, json_name: str, parquet_name: str, key: str) -> list[dict[str, Any]]:
        bundle = self._require_known(run_id)
        rows = self._rows(bundle, json_name, parquet_name, key)
        if rows is None:
            raise EvidenceError("unavailable", f"{key} are not in this evidence bundle")
        return [row for row in rows if row.get("run_id") == run_id]

    def _rows(self, bundle: AcceptedBundle, json_name: str, parquet_name: str | None, key: str) -> list[dict[str, Any]] | None:
        for filename in (json_name, parquet_name):
            if filename is None:
                continue
            rows = read_rows(bundle.path, bundle.artifact_hashes, filename, key)
            if rows is not None:
                return rows
        return None

    @staticmethod
    def _reject_unsafe_id(run_id: str) -> None:
        if run_id in {"", ".", ".."} or ".." in Path(run_id).parts or "/" in run_id or "\\" in run_id:
            raise EvidenceError("not_found", "unknown run_id")


def _trusted_manifest(bundle: Path, hashes: dict[str, str]) -> dict[str, Any] | None:
    relative = "artifacts/run_manifest.json"
    if relative not in hashes:
        return None
    payload = json.loads((bundle / relative).read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or not isinstance(payload.get("run_id"), str):
        raise EvidenceError("corrupt_evidence", "run_manifest.json has no run_id")
    return payload


def _rejected_run_ids(bundle: Path) -> tuple[str, ...]:
    gate_path = bundle / "gate.json"
    manifest_path = bundle / "artifacts" / "run_manifest.json"
    try:
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        declared = gate.get("artifactHashes") if isinstance(gate, dict) else None
        expected = declared.get("artifacts/run_manifest.json") if isinstance(declared, dict) else None
        if not isinstance(expected, str) or not manifest_path.is_file():
            return ()
        if sha256_file(manifest_path) != expected:
            return ()
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return ()
    if not isinstance(payload, dict):
        return ()
    return tuple(_run_index(payload).keys())


def _run_index(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    primary_id = manifest.get("run_id")
    if isinstance(primary_id, str):
        rows[primary_id] = _public_run(manifest)
    cells = manifest.get("runs")
    if isinstance(cells, list):
        for cell in cells:
            if isinstance(cell, dict) and isinstance(cell.get("run_id"), str):
                rows[cell["run_id"]] = _public_run(cell)
    return rows


def _public_run(source: dict[str, Any]) -> dict[str, Any]:
    return {field: source[field] for field in RUN_FIELDS if field in source}


def _explanation_run_id(row: dict[str, Any]) -> str | None:
    facts = row.get("event_facts")
    if isinstance(facts, dict) and isinstance(facts.get("run_id"), str):
        return facts["run_id"]
    run_id = row.get("run_id")
    return run_id if isinstance(run_id, str) else None
