import sys
from pathlib import Path

from coflow5.evidence.professor_page import (
    EvidencePageError,
    load_evidence_page,
    render_evidence_page,
)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    try:
        page = load_evidence_page(root)
    except EvidencePageError as exc:
        print(f"ABSTAIN: {exc}", file=sys.stderr)
        raise SystemExit(2)
    print(render_evidence_page(page), end="")
