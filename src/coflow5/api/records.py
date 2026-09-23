from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from coflow5.api.errors import EvidenceError

IDENTITY = (
    "run_id",
    "scenario_hash",
    "graph_hash",
    "event_id",
    "message_id",
    "request_id",
    "chunk_id",
)
PAGE_LIMIT = 50


def parse_page(limit: int | None, offset: int | None) -> tuple[int, int]:
    resolved_limit = 20 if limit is None else limit
    resolved_offset = 0 if offset is None else offset
    if resolved_limit < 1 or resolved_limit > PAGE_LIMIT or resolved_offset < 0:
        raise EvidenceError("validation", "limit must be 1..50 and offset must be >= 0")
    return resolved_limit, resolved_offset


def slice_page(rows: list[dict[str, Any]], limit: int, offset: int) -> dict[str, Any]:
    return {
        "total": len(rows),
        "limit": limit,
        "offset": offset,
        "items": rows[offset:offset + limit],
    }


def read_rows(bundle: Path, hashes: dict[str, str], filename: str, key: str) -> list[dict[str, Any]] | None:
    relative = f"artifacts/{filename}"
    if relative not in hashes:
        return None
    path = bundle / relative
    if filename.endswith(".json"):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            rows = payload
        elif isinstance(payload, dict) and isinstance(payload.get(key), list):
            rows = payload[key]
        else:
            raise EvidenceError("corrupt_evidence", f"{filename} has no {key} list")
        return [_copy_record(row) for row in rows]
    if filename.endswith(".parquet"):
        import pyarrow.parquet as pq

        table = pq.read_table(path)
        return [_copy_record(row) for row in table.to_pylist()]
    raise EvidenceError("unavailable", f"unsupported evidence file: {filename}")


def _copy_record(row: object) -> dict[str, Any]:
    if not isinstance(row, dict):
        raise EvidenceError("corrupt_evidence", "evidence row is not an object")
    copied = dict(row)
    for field in IDENTITY:
        if field in row:
            copied[field] = row[field]
    return copied


def sort_key(row: dict[str, Any], fields: tuple[str, ...]) -> tuple[str, ...]:
    return tuple("" if row.get(field) is None else str(row.get(field)) for field in fields)


def limitations_from_bundle(bundle: Path, hashes: dict[str, str], manifest: dict[str, Any]) -> list[str]:
    found: list[str] = []
    if "artifacts/limitations.json" in hashes:
        payload = json.loads((bundle / "artifacts" / "limitations.json").read_text(encoding="utf-8"))
        values = payload.get("limitations") if isinstance(payload, dict) else None
        if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
            raise EvidenceError("corrupt_evidence", "limitations.json is not a string list")
        found.extend(values)
    report = bundle / "artifacts" / "growth_report.md"
    if "artifacts/growth_report.md" in hashes and report.is_file():
        lines = report.read_text(encoding="utf-8").splitlines()
        capture = False
        for line in lines:
            if line.startswith("## Limitations"):
                capture = True
                continue
            if capture and line.startswith("## "):
                break
            if capture and line.startswith("- "):
                found.append(line[2:])
    boundary = manifest.get("claim_boundary")
    if isinstance(boundary, str) and boundary not in found:
        found.append(boundary)
    return found
