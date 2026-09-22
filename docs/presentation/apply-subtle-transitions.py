from __future__ import annotations

import re
import sys
import tempfile
import zipfile
from pathlib import Path

FADE = '<p:transition spd="slow" advClick="1"><p:fade/></p:transition>'
TRANSITION = re.compile(r'<p:transition\b[^>]*>.*?</p:transition>|<p:transition\b[^>]*/>', re.DOTALL)
SLIDE = re.compile(r'ppt/slides/slide\d+\.xml')


def apply(path: Path) -> int:
    if not path.is_file():
        raise FileNotFoundError(path)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pptx', dir=path.parent) as handle:
        temp = Path(handle.name)
    count = 0
    try:
        with zipfile.ZipFile(path, 'r') as source, zipfile.ZipFile(temp, 'w', zipfile.ZIP_DEFLATED) as target:
            for item in source.infolist():
                data = source.read(item.filename)
                if SLIDE.fullmatch(item.filename):
                    text = data.decode('utf-8')
                    if TRANSITION.search(text):
                        text = TRANSITION.sub(FADE, text, count=1)
                    elif '</p:cSld>' in text:
                        text = text.replace('</p:cSld>', f'</p:cSld>{FADE}', 1)
                    else:
                        raise ValueError(f'cannot place transition in {item.filename}')
                    if 'advTm=' in text:
                        raise ValueError(f'auto-advance timing remains in {item.filename}')
                    data = text.encode('utf-8')
                    count += 1
                target.writestr(item, data)
        temp.replace(path)
    except Exception:
        temp.unlink(missing_ok=True)
        raise
    return count


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('usage: py -3.11 apply-subtle-transitions.py <deck.pptx>', file=sys.stderr)
        raise SystemExit(2)
    deck = Path(sys.argv[1]).resolve()
    transitions = apply(deck)
    print(f'PASS fade transitions deck={deck.name} slides={transitions} click_only=true auto_advance=false')
