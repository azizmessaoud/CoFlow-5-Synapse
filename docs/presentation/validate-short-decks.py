from __future__ import annotations

import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parent
MAIN = ROOT / 'CoFlow-5-Synapse-TALK.pptx'
PERSONAS = ROOT / 'CoFlow-5-Persona-Cards.pptx'
LEDGER = ROOT / 'presentation-claim-ledger.json'
NAMES = ('Amara', 'David', 'Chidi', 'Rosa', 'Marcus', 'Yuki', 'Omar')


def text(data: bytes) -> str:
    root = ET.fromstring(data)
    return ' '.join((n.text or '').strip() for n in root.iter() if n.tag.endswith('}t') and (n.text or '').strip())


def inspect(deck: Path) -> dict:
    with zipfile.ZipFile(deck) as z:
        names = z.namelist()
        slides = sorted(
            (n for n in names if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)),
            key=lambda n: int(re.search(r'(\d+)', n).group(1)),
        )
        notes = [n for n in names if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', n)]
        slide_xml = [z.read(n).decode('utf-8') for n in slides]
        slide_text = [text(x.encode('utf-8')) for x in slide_xml]
        transitions = [x for x in slide_xml if '<p:transition' in x and '<p:fade' in x]
        if any('advTm=' in x for x in slide_xml):
            raise AssertionError(f'{deck.name}: auto-advance timing is forbidden')
        if any('advClick="1"' not in x for x in transitions):
            raise AssertionError(f'{deck.name}: transitions must remain click-only')
        return {
            'slides': len(slides), 'notes': len(notes), 'texts': slide_text,
            'all': '\n'.join(slide_text), 'transitions': len(transitions),
            'max_chars': max(map(len, slide_text)), 'bytes': deck.stat().st_size,
        }


def main() -> int:
    ledger = json.loads(LEDGER.read_text(encoding='utf-8'))
    forbidden = tuple(ledger['forbidden_patterns'])
    main = inspect(MAIN)
    cards = inspect(PERSONAS)
    assert main['slides'] == main['notes'] == main['transitions'] == 14, main
    assert cards['slides'] == cards['notes'] == cards['transitions'] == 8, cards
    assert main['max_chars'] <= 520, main['max_chars']
    assert cards['max_chars'] <= 1050, cards['max_chars']
    required_main = (
        'Design Thinking', 'Empathize', 'Define', 'Ideate',
        'cooperative Max-Pressure', 'Only A1', 'Synapse never actuates',
        'Rows 07, 08 and 09', 'Tunis', 'run_id', 'scenario_hash',
        'synthetic or calibrated', '32-row mixed-source evidence register',
    )
    for value in required_main:
        assert value.lower() in main['all'].lower(), f'main deck missing: {value}'
    for name in NAMES:
        assert name in main['all'], f'main deck missing persona: {name}'
        assert sum(f'Persona {i + 1} — {name}' in t for i, t in enumerate(cards['texts'])) == 1, f'card missing: {name}'
    required_card_fields = ('DESIGN STATEMENT', 'NEED', 'FEAR', 'USES', 'REJECTS', 'EVIDENCE', 'MEASURE')
    for slide, name in zip(cards['texts'], NAMES):
        for field in required_card_fields:
            assert field in slide, f'{name} card missing {field}'
        assert 'not an interviewed person' in slide.lower(), f'{name} disclaimer missing'
    combined = main['all'] + '\n' + cards['all']
    for value in forbidden:
        assert value.lower() not in combined.lower(), f'forbidden stale wording: {value}'
    positive_claims = (
        r'\b(?:we|coflow-5|the system) (?:save|saves|saved) lives\b',
        r'\bdeployed in tunis\b',
        r'\bmeasured air quality\b',
        r'\bbest episode proves\b',
    )
    for pattern in positive_claims:
        assert not re.search(pattern, combined, re.I), f'prohibited claim: {pattern}'
    print(
        'PASS short presentation validation '
        f'main_slides={main["slides"]} main_max_chars={main["max_chars"]} '
        f'persona_slides={cards["slides"]} persona_max_chars={cards["max_chars"]} '
        f'notes={main["notes"] + cards["notes"]} fades={main["transitions"] + cards["transitions"]} '
        f'bytes={main["bytes"] + cards["bytes"]}'
    )
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(f'FAIL short presentation validation: {exc}', file=sys.stderr)
        raise SystemExit(1)
