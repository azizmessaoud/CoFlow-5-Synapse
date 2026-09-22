"""Fail CI when evaluation outputs make prohibited headline or outcome claims."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "harness" / "work"
ROW09_REPORT = WORK / "09-eval-harness" / "artifacts" / "evaluation-report.json"


def _positive_claim_violation(text: str) -> bool:
    lowered = text.lower()
    forbidden = (
        "best episode:", "lives saved:", "saved lives:",
        "measured air quality improved", "measured-air-quality improved",
    )
    return any(item in lowered for item in forbidden)


def main() -> int:
    hits: list[str] = []
    if WORK.is_dir():
        for path in WORK.rglob("*"):
            if path.name == "contract.json" or path.suffix.lower() not in {".md", ".json", ".txt", ".log"}:
                continue
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if _positive_claim_violation(text):
                hits.append(str(path.relative_to(ROOT)))
    if ROW09_REPORT.is_file():
        report = json.loads(ROW09_REPORT.read_text(encoding="utf-8"))
        headline = json.dumps(report.get("headline", {}), sort_keys=True)
        if "paired/matched canonical evidence only" not in headline:
            hits.append("row09 headline is not paired/matched evidence")
        if _positive_claim_violation(headline):
            hits.append("row09 headline contains a prohibited claim")
        for claim in report.get("claims", []):
            if _positive_claim_violation(str(claim.get("text", ""))):
                hits.append(f"row09 claim {claim.get('claim_id', '<unknown>')}")
    if hits:
        print("Claim flag: prohibited evaluation claim")
        print("\n".join(sorted(set(hits))))
        return 1
    print("No best-episode headline in harness/work")
    print("Row 09 claim boundaries pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
