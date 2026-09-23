from __future__ import annotations

import hashlib
import json
from pathlib import Path

from coflow5.api.errors import EvidenceError


_TEXT_SUFFIXES = {".json", ".md", ".txt", ".xml"}


def sha256_file(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() in _TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n")
    return "sha256:" + hashlib.sha256(data).hexdigest()


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceError("corrupt_evidence", f"unreadable json: {path.name}") from exc


def validate_bundle(bundle: Path) -> dict[str, object]:
    gate_path = bundle / "gate.json"
    contract_path = bundle / "contract.json"
    if not gate_path.is_file() or not contract_path.is_file():
        raise EvidenceError("validation", "bundle is missing gate.json or contract.json")
    gate = _load_json(gate_path)
    if not isinstance(gate, dict):
        raise EvidenceError("corrupt_evidence", "gate.json must be an object")
    if gate.get("pass") is not True or gate.get("openDeltas") != 0 or gate.get("decidedBy") != "tests-and-files":
        raise EvidenceError("validation", "gate is not a completed tests-and-files pass")
    expected_contract = gate.get("contractHash")
    if expected_contract != sha256_file(contract_path):
        raise EvidenceError("validation", "contract hash does not match the gate")
    declared = gate.get("artifactHashes")
    if not isinstance(declared, dict) or not declared:
        raise EvidenceError("corrupt_evidence", "artifactHashes must name every served file")
    checked: dict[str, str] = {}
    for relative, expected in declared.items():
        if not isinstance(relative, str) or not isinstance(expected, str):
            raise EvidenceError("corrupt_evidence", "artifact hash entry is not a string")
        path = _safe_relative(bundle, relative)
        if not path.is_file():
            raise EvidenceError("corrupt_evidence", f"missing artifact: {relative}")
        actual = sha256_file(path)
        if actual != expected:
            raise EvidenceError("corrupt_evidence", f"artifact hash mismatch: {relative}")
        checked[relative] = actual
    return {"gate": gate, "artifact_hashes": checked}


def _safe_relative(bundle: Path, relative: str) -> Path:
    if relative.startswith(("/", "\\")) or ".." in Path(relative).parts:
        raise EvidenceError("validation", "artifact path escapes the bundle")
    path = (bundle / relative).resolve()
    if bundle.resolve() not in path.parents and path != bundle.resolve():
        raise EvidenceError("validation", "artifact path escapes the bundle")
    return path
