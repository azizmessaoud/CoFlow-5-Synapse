from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src" / "coflow5"
FORBIDDEN_FAMILIES = {
    "synapse", "retrieval", "provider", "specialists", "api", "ui",
    "a2", "a3", "a4", "a5",
}
FORBIDDEN_BINDINGS = {"traci", "libsumo"}


def imports_in(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


def test_non_actuating_families_cannot_import_sumo_bindings() -> None:
    violations: list[str] = []
    for path in SRC.rglob("*.py"):
        relative = path.relative_to(SRC)
        family = relative.parts[0] if len(relative.parts) > 1 else relative.stem
        forbidden = imports_in(path) & FORBIDDEN_BINDINGS
        if family in FORBIDDEN_FAMILIES and forbidden:
            violations.append(f"{relative}: {sorted(forbidden)}")
    assert not violations, "Forbidden SUMO imports: " + "; ".join(violations)


def test_sumo_bindings_stay_inside_adapter_boundary() -> None:
    violations: list[str] = []
    for path in SRC.rglob("*.py"):
        relative = path.relative_to(SRC)
        if relative.parts[0] == "sumo_adapter":
            continue
        forbidden = imports_in(path) & FORBIDDEN_BINDINGS
        if forbidden:
            violations.append(f"{relative}: {sorted(forbidden)}")
    assert not violations, "SUMO bindings escaped adapter: " + "; ".join(violations)


def test_roadwayvr_is_not_a_runtime_dependency() -> None:
    dependency_files = [ROOT / "pyproject.toml", ROOT / "requirements-smoke.txt"]
    contents = "\n".join(path.read_text(encoding="utf-8").lower() for path in dependency_files)
    assert "roadwayvr" not in contents



def test_libsumo_is_never_imported_at_adapter_module_load() -> None:
    violations: list[str] = []
    adapter = SRC / "sumo_adapter"
    for path in adapter.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in tree.body:
            if isinstance(node, ast.Import):
                if any(alias.name.split(".")[0] == "libsumo" for alias in node.names):
                    violations.append(str(path.relative_to(SRC)))
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".")[0] == "libsumo":
                    violations.append(str(path.relative_to(SRC)))
    assert not violations, "libsumo imported at module load: " + "; ".join(violations)


def test_evidence_has_no_signal_actuation_or_mlflow_identity_dependency() -> None:
    violations: list[str] = []
    paths = list((SRC / "evidence").rglob("*.py")) + [SRC / "evaluation" / "harness.py"]
    for path in paths:
        source = path.read_text(encoding="utf-8").lower()
        imported = imports_in(path)
        relative = path.relative_to(SRC)
        if "mlflow" in imported:
            violations.append(f"{relative}: mlflow")
        if (
            "trafficlight.set" in source
            or "setredyellowgreenstate" in source
            or "signal_executor" in source
        ):
            violations.append(f"{relative}: signal actuation")
    assert not violations, "Forbidden evidence/evaluation capability: " + "; ".join(violations)



def _raw_signal_write_calls(path: Path) -> list[int]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    lines: list[int] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if not node.func.attr.startswith("set"):
            continue
        owner = node.func.value
        if isinstance(owner, ast.Attribute) and owner.attr == "trafficlight":
            lines.append(node.lineno)
    return lines


def test_only_signal_executor_contains_raw_trafficlight_writes() -> None:
    permitted = Path("sumo_adapter/signal_executor.py")
    violations: list[str] = []
    write_sites: list[str] = []
    for path in SRC.rglob("*.py"):
        relative = path.relative_to(SRC)
        for line in _raw_signal_write_calls(path):
            write_sites.append(f"{relative}:{line}")
            if relative != permitted:
                violations.append(f"{relative}:{line}")
    assert not violations, "Raw signal writes outside executor: " + "; ".join(violations)
    assert len(write_sites) == 1, f"expected one raw signal write site, found {write_sites}"


def test_a1_controller_has_no_raw_connection_or_sumo_binding() -> None:
    controller = SRC / "control" / "a1_controller.py"
    source = controller.read_text(encoding="utf-8").lower()
    assert not (imports_in(controller) & FORBIDDEN_BINDINGS)
    assert "trafficlight" not in source
    assert "setredyellowgreenstate" not in source


def test_non_actuating_families_cannot_import_signal_executor() -> None:
    violations: list[str] = []
    for path in SRC.rglob("*.py"):
        relative = path.relative_to(SRC)
        family = relative.parts[0] if len(relative.parts) > 1 else relative.stem
        source = path.read_text(encoding="utf-8")
        if family in FORBIDDEN_FAMILIES and "signal_executor" in source:
            violations.append(str(relative))
    assert not violations, "Non-actuating family imports executor: " + "; ".join(violations)


def test_a2_a3_have_transport_only_authority_and_no_hosted_agent_runtime() -> None:
    forbidden_imports = {
        "traci", "libsumo", "langgraph", "openai", "anthropic", "signal_executor",
    }
    violations: list[str] = []
    for family in ("a2", "a3"):
        for path in (SRC / family).rglob("*.py"):
            relative = path.relative_to(SRC)
            imported = imports_in(path)
            source = path.read_text(encoding="utf-8").lower()
            forbidden = imported & forbidden_imports
            if forbidden:
                violations.append(f"{relative}: imports {sorted(forbidden)}")
            if any(token in source for token in (
                "trafficlight.set", "setredyellowgreenstate", "signal_executor",
            )):
                violations.append(f"{relative}: signal actuation capability")
    assert not violations, "A2/A3 authority boundary violations: " + "; ".join(violations)
