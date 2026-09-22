from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_ROWS = (
    "01-smoke-test",
    "02-evidence-bundle",
    "03-safety-mask",
    "04-baselines",
    "05-max-pressure",
    "06-message-board",
    "07-a2-a3",
    "08-failure-injection",
    "09-eval-harness",
)


def test_adr_0003_exists_and_keeps_authority_rules() -> None:
    text = (ROOT / "docs" / "adr" / "0003-cicd-devops-mlops.md").read_text(encoding="utf-8")
    assert "Status:** Accepted" in text or "**Status:** Accepted" in text
    assert "never reaches TraCI" in text or "never reach TraCI" in text
    assert "MLflow" in text
    assert "mint a second" in text
    assert "Docker is not a required smoke-test command" in text


def test_rows_01_to_09_have_contracts() -> None:
    missing = [
        row
        for row in CONTRACT_ROWS
        if not (ROOT / "harness" / "work" / row / "contract.json").is_file()
    ]
    assert not missing, f"Missing contracts: {missing}"


def test_pr_workflow_is_sumo_free() -> None:
    text = (ROOT / ".github" / "workflows" / "pr.yml").read_text(encoding="utf-8")
    assert "tests/architecture" in text
    assert "test_native_windows_smoke" not in text
    assert "libsumo" not in text
    assert "eclipse-sumo" not in text


def test_eval_claim_flag_script_ignores_contract_prohibition() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "check_eval_claim_flags.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "No best-episode headline in harness/work" in result.stdout


def test_eval_workflow_does_not_pass_without_libsumo() -> None:
    text = (ROOT / ".github" / "workflows" / "eval.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch" in text
    assert "scripts/require_libsumo.py" in text
    assert "scripts/check_eval_claim_flags.py" in text


def test_hosted_images_do_not_install_sumo() -> None:
    compose = (ROOT / "deploy" / "docker-compose.yml").read_text(encoding="utf-8").lower()
    assert "eclipse-sumo" not in compose
    assert "libsumo" not in compose
    for dockerfile in (ROOT / "deploy").glob("*.Dockerfile"):
        text = dockerfile.read_text(encoding="utf-8").lower()
        assert "eclipse-sumo" not in text
        assert "libsumo" not in text
        assert "sumo" not in text


def test_native_smoke_command_does_not_require_docker() -> None:
    smoke = (ROOT / "scripts" / "run_native_smoke.py").read_text(encoding="utf-8").lower()
    assert "docker" not in smoke
    assert "wsl" not in smoke
    contract = (ROOT / "harness" / "work" / "01-smoke-test" / "contract.json").read_text(
        encoding="utf-8"
    )
    assert "docker -> required smoke-test path" in contract
