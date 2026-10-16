from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_readme_keeps_adr_0003_authority_rules() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Status:** Accepted" in text or "**Status:** Accepted" in text
    assert "never reaches TraCI" in text or "never reach TraCI" in text
    assert "MLflow" in text
    assert "mint a second" in text
    assert "Docker is not a required smoke-test command" in text


def test_pr_workflow_is_sumo_free() -> None:
    text = (ROOT / ".github" / "workflows" / "pr.yml").read_text(encoding="utf-8")
    assert "tests/architecture" in text
    assert "test_native_windows_smoke" not in text
    assert "libsumo" not in text
    assert "eclipse-sumo" not in text


def test_eval_workflow_does_not_pass_without_libsumo() -> None:
    text = (ROOT / ".github" / "workflows" / "eval.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch" in text
    assert "scripts/require_libsumo.py" in text


def test_hosted_images_do_not_install_sumo() -> None:
    compose = (ROOT / "deploy" / "docker-compose.yml").read_text(encoding="utf-8").lower()
    assert "eclipse-sumo" not in compose
    assert "libsumo" not in compose
    for dockerfile in (ROOT / "deploy").glob("*.Dockerfile"):
        text = dockerfile.read_text(encoding="utf-8").lower()
        assert "eclipse-sumo" not in text
        assert "libsumo" not in text
        assert "sumo" not in text
