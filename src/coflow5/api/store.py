from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class EvidenceStore:
    """Read-only index of tagged evidence bundles. Never launches SUMO."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def list_runs(self) -> list[dict[str, Any]]:
        runs: list[dict[str, Any]] = []
        if not self.root.is_dir():
            return runs
        for manifest_path in sorted(self.root.glob("**/run_manifest.json")):
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            run_id = str(manifest.get("run_id") or "")
            if not run_id:
                continue
            runs.append(
                {
                    "run_id": run_id,
                    "status": manifest.get("status"),
                    "scenario_hash": manifest.get("scenario_hash"),
                    "bundle": str(manifest_path.parent.relative_to(self.root).as_posix()),
                }
            )
        return runs

    def load_manifest(self, run_id: str) -> dict[str, Any]:
        path = self._bundle_dir(run_id) / "run_manifest.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def load_artifact(self, run_id: str, name: str) -> tuple[bytes, str]:
        if Path(name).name != name or "/" in name or "\\" in name:
            raise FileNotFoundError(name)
        path = self._bundle_dir(run_id) / name
        if not path.is_file():
            raise FileNotFoundError(name)
        return path.read_bytes(), path.suffix.lower()

    def _bundle_dir(self, run_id: str) -> Path:
        for manifest_path in self.root.glob("**/run_manifest.json"):
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if str(manifest.get("run_id") or "") == run_id:
                return manifest_path.parent
        raise FileNotFoundError(run_id)
