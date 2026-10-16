from __future__ import annotations

import ast
from pathlib import Path


from coflow5.synapse import (
    ExplanationObserverBoundary,
    ImmutableDecisionView,
    action_sequence_hash,
)

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src/coflow5"
FORBIDDEN_FAMILIES = {"synapse", "retrieval", "provider", "specialists", "a2", "a3", "a4", "a5"}


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    values: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            values.update(alias.name.lower() for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            values.add(node.module.lower())
    return values


def test_synapse_retrieval_provider_and_specialists_have_no_actuation_imports() -> None:
    violations: list[str] = []
    for path in SRC.rglob("*.py"):
        relative = path.relative_to(SRC)
        family = relative.parts[0] if len(relative.parts) > 1 else relative.stem
        if family not in FORBIDDEN_FAMILIES:
            continue
        imported = _imports(path)
        forbidden = {
            name for name in imported
            if name == "traci" or name.startswith("traci.")
            or name == "libsumo" or name.startswith("libsumo.")
            or "signal_executor" in name
        }
        if forbidden:
            violations.append(f"{relative}: {sorted(forbidden)}")
    assert not violations, "non-actuating boundary violation: " + "; ".join(violations)


def test_killed_observer_returns_visible_failure_without_action_callback() -> None:
    view = ImmutableDecisionView(
        run_id="run", scenario_hash="sha256:" + "c" * 64, event_id="event",
        simulation_time=1.0, selected_action="NS_GREEN",
        reason_code="MAX_PRESSURE_LOCAL_ONLY",
    )
    receipt = ExplanationObserverBoundary(None).observe_after_decision(view)
    assert receipt.observer_available is False
    assert receipt.explanation_status == "unavailable"
    assert receipt.failure_type == "ObserverUnavailable"
    assert action_sequence_hash([view.selected_action]) == action_sequence_hash(["NS_GREEN"])
    assert not hasattr(ExplanationObserverBoundary, "propose_phase")
    assert not hasattr(ExplanationObserverBoundary, "execute")
