from __future__ import annotations

import json
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    evidence = root / "deploy" / "evidence"
    manifests = sorted(evidence.glob("**/run_manifest.json"))
    if not manifests:
        raise SystemExit("No tagged evidence bundle found")
    rows = []
    for path in manifests:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        rows.append(
            {
                "run_id": manifest.get("run_id"),
                "scenario_hash": manifest.get("scenario_hash"),
                "status": manifest.get("status"),
                "bundle": str(path.parent.relative_to(evidence)),
            }
        )
    print(json.dumps({"offline": True, "runs": rows}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
