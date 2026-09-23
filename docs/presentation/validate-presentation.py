from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
PPTX = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "CoFlow-5-Synapse-DT-4DS.pptx"
SOURCE = ROOT / "build-professor-pptx.js"
LEDGER = ROOT / "presentation-claim-ledger.json"
PERSONAS = ("Amara", "David", "Chidi", "Rosa", "Marcus", "Yuki", "Omar")
REQUIRED_TEXT = (
    "32-row mixed-source evidence register",
    "cooperative Max-Pressure",
    "Only A1 writes signals",
    "Synapse never actuates",
    "Max-Pressure",
    "actuated",
    "fixed-time",
    "run_id",
    "scenario_hash",
    "event_id",
    "message_id",
    "6.4 million",
    "12.5%",
    "7% lower adjusted odds",
    "scheduled TRANSTU",
    "synthetic or calibrated",
    "Rows 07 and 08 are verified",
    "Row 09 is not verified",
)


def fail(message: str) -> None:
    raise AssertionError(message)


def xml_text(data: bytes) -> str:
    root = ET.fromstring(data)
    return " ".join(
        (node.text or "").strip()
        for node in root.iter()
        if node.tag.endswith("}t") and (node.text or "").strip()
    )


def numbered(names: list[str], prefix: str, suffix: str) -> list[str]:
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+){re.escape(suffix)}$")
    matched = []
    for name in names:
        match = pattern.match(name)
        if match:
            matched.append((int(match.group(1)), name))
    return [name for _, name in sorted(matched)]


def main() -> int:
    if not SOURCE.is_file() or not LEDGER.is_file() or not PPTX.is_file():
        fail("presentation source, ledger, or PPTX is missing")
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    source = SOURCE.read_text(encoding="utf-8")
    if len(ledger.get("claims", [])) < 17:
        fail("claim ledger is incomplete")
    claim_ids = {item["id"] for item in ledger["claims"]}
    if len(claim_ids) != len(ledger["claims"]):
        fail("claim ledger contains duplicate IDs")
    for item in ledger["claims"]:
        if not all(str(item.get(key, "")).strip() for key in ("id", "classification", "safe_wording", "source")):
            fail(f"claim ledger entry is incomplete: {item.get('id')}")
    for forbidden in ledger["forbidden_patterns"]:
        if forbidden.lower() in source.lower():
            fail(f"forbidden stale wording in source: {forbidden}")
    for persona in PERSONAS:
        if f"name: '{persona}'" not in source:
            fail(f"missing full persona data: {persona}")

    with zipfile.ZipFile(PPTX) as archive:
        names = archive.namelist()
        slides = numbered(names, "ppt/slides/slide", ".xml")
        notes = numbered(names, "ppt/notesSlides/notesSlide", ".xml")
        if len(slides) < 30:
            fail(f"expected at least 30 slides, found {len(slides)}")
        if len(notes) != len(slides):
            fail(f"speaker-note count {len(notes)} does not equal slide count {len(slides)}")
        slide_texts = [xml_text(archive.read(name)) for name in slides]
        note_texts = [xml_text(archive.read(name)) for name in notes]
        if any(not text.strip() for text in slide_texts):
            fail("one or more slides has no text")
        if any(len(text.strip()) < 20 for text in note_texts):
            fail("one or more speaker notes is missing or too short")
        if max(map(len, slide_texts)) > 3800:
            fail("a slide exceeds the deterministic text-density budget")
        deck_text = "\n".join(slide_texts)
        for required in REQUIRED_TEXT:
            if required.lower() not in deck_text.lower():
                fail(f"required presentation text is missing: {required}")
        for index, persona in enumerate(PERSONAS, start=1):
            title = f"Persona {index} — {persona}"
            if sum(title in text for text in slide_texts) != 1:
                fail(f"expected exactly one full card title: {title}")
        used_claim_ids = set(re.findall(r"\[(C\d{2})\]", deck_text))
        if used_claim_ids != claim_ids:
            fail(f"citation mismatch; missing={sorted(claim_ids-used_claim_ids)}, unknown={sorted(used_claim_ids-claim_ids)}")
        for forbidden in ledger["forbidden_patterns"]:
            if forbidden.lower() in deck_text.lower():
                fail(f"forbidden stale wording in deck: {forbidden}")
        positive_claim_patterns = (
            r"\b(?:we|coflow-5|the system) (?:save|saves|saved) lives\b",
            r"(?<!no )(?<!not )measured air quality",
            r"(?<!not )interview-validated personas",
            r"\bbest episode proves\b",
            r"\bdeployed in tunis\b",
        )
        for pattern in positive_claim_patterns:
            if re.search(pattern, deck_text, flags=re.IGNORECASE):
                fail(f"prohibited positive claim matched: {pattern}")
        presentation = ET.fromstring(archive.read("ppt/presentation.xml"))
        size = next((node for node in presentation.iter() if node.tag.endswith("}sldSz")), None)
        if size is None:
            fail("PPTX slide size is missing")
        ratio = int(size.attrib["cx"]) / int(size.attrib["cy"])
        if abs(ratio - 16 / 9) > 0.01:
            fail(f"slide ratio is not 16:9: {ratio}")

    print(
        "PASS presentation validation "
        f"slides={len(slides)} notes={len(notes)} personas=7 citations={len(claim_ids)} "
        f"max_slide_chars={max(map(len, slide_texts))} bytes={PPTX.stat().st_size}"
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f"FAIL presentation validation: {exc}", file=sys.stderr)
        raise SystemExit(1)
