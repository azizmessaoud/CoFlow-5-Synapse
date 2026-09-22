from pathlib import Path

from coflow5.evidence.professor_page import generate_evidence_page_artifacts


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    manifest = generate_evidence_page_artifacts(root)
    print(
        "Row 10c evidence page generated "
        f"page_id={manifest['page_id']} "
        f"artifacts={root / 'harness/work/10c-evidence-page/artifacts'}"
    )
