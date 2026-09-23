from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEB = ROOT / "web"
SRC = WEB / "src"


def test_package_versions_are_exact() -> None:
    package = json.loads((WEB / "package.json").read_text(encoding="utf-8"))
    for group in ("dependencies", "devDependencies"):
        for name, version in package[group].items():
            assert not version.startswith(("^", "~")), f"{name} is not pinned: {version}"
    assert package["scripts"]["test"] == "node --test src/evidence.test.js"


def test_ui_source_has_no_control_path() -> None:
    forbidden = ("websocket", "traci", "libsumo", "setphase", "manual phase", "readfilesync", "fs.")
    violations: list[str] = []
    for path in SRC.rglob("*"):
        if path.suffix not in {".js", ".jsx", ".css"}:
            continue
        source = path.read_text(encoding="utf-8").lower()
        hits = [token for token in forbidden if token in source]
        if hits:
            violations.append(f"{path.name}: {hits}")
    assert not violations
    app = (SRC / "App.jsx").read_text(encoding="utf-8")
    for label in (
        "Controller comparison",
        "Graph frames",
        "Messages and reasons",
        "Explanations, citations, and abstentions",
        "Limitations",
        "Recovery",
        "Freshness:",
        "Unfinished",
    ):
        assert label in app
    assert "/api/runs/" in app
    assert "open(" not in app
