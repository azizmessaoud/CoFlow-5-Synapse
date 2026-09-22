from __future__ import annotations

import hashlib
import importlib.metadata
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

from coflow5.sumo_adapter.smoke_backends import (
    measure_libsumo,
    measure_traci,
    traci_module_file,
)

FROZEN_SCENARIO_FILES = (
    "scenarios/smoke/smoke.net.xml",
    "scenarios/smoke/smoke.rou.xml",
    "scenarios/smoke/smoke.sumocfg",
)
SEED = 20260922
SUMO_RELEASE = "1.27.1"
PACKAGE_NAMES = ("libsumo", "psutil", "pytest", "sumo-data", "sumolib", "traci")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def scenario_hash(root: Path, files: Iterable[str] = FROZEN_SCENARIO_FILES) -> str:
    digest = hashlib.sha256()
    for relative in files:
        data = (root / relative).read_bytes()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(data)
        digest.update(b"\0")
    return f"sha256:{digest.hexdigest()}"


def file_hash(path: Path) -> str:
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def _version(binary: str) -> tuple[str, str]:
    result = subprocess.run([binary, "--version"], capture_output=True, text=True, check=True)
    output = result.stdout + result.stderr
    match = re.search(r"(?:sumo|GUI)\s+(\d+\.\d+\.\d+)", output)
    if not match:
        raise RuntimeError(f"Could not parse version from {binary}: {output}")
    return match.group(1), output.strip()


def _source_revision(root: Path) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_smoke(root: Path) -> dict:
    if platform.system() != "Windows":
        raise RuntimeError("Row 01 requires native Windows execution")
    if sys.version_info[:2] != (3, 11):
        raise RuntimeError(f"Row 01 requires Python 3.11, got {platform.python_version()}")

    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home or not Path(sumo_home).is_dir():
        raise RuntimeError("SUMO_HOME must point to the native Eclipse SUMO installation")
    sumo_binary = shutil.which("sumo")
    gui_binary = shutil.which("sumo-gui")
    if not sumo_binary or not gui_binary:
        raise RuntimeError("sumo.exe and sumo-gui.exe must be on PATH")

    sumo_version, sumo_version_output = _version(sumo_binary)
    gui_version, gui_version_output = _version(gui_binary)
    if sumo_version != SUMO_RELEASE or gui_version != SUMO_RELEASE:
        raise RuntimeError(
            f"Expected SUMO {SUMO_RELEASE}; found sumo={sumo_version}, gui={gui_version}"
        )
    package_versions: dict[str, str | None] = {}
    for name in PACKAGE_NAMES:
        try:
            package_versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            package_versions[name] = None

    artifacts = root / "harness" / "work" / "01-smoke-test" / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    config = root / "scenarios" / "smoke" / "smoke.sumocfg"
    current_scenario_hash = scenario_hash(root)
    run_id = str(uuid.uuid4())
    started_at = utc_now()

    toolchain = {
        "captured_at": started_at,
        "native_os": platform.platform(),
        "python_executable": sys.executable,
        "python_version": platform.python_version(),
        "sumo_home": str(Path(sumo_home).resolve()),
        "sumo_binary": sumo_binary,
        "sumo_gui_binary": gui_binary,
        "sumo_version": sumo_version,
        "sumo_gui_version": gui_version,
        "sumo_version_output": sumo_version_output,
        "sumo_gui_version_output": gui_version_output,
        "source_revision": _source_revision(root),
        "traci_file": traci_module_file(),
        "package_versions": package_versions,
        "libsumo_importable": False,
    }
    _write_json(artifacts / "toolchain.json", toolchain)

    headless_tripinfo = artifacts / "headless-tripinfo.xml"
    headless_command = [
        sumo_binary,
        "-c",
        str(config),
        "--seed",
        str(SEED),
        "--no-step-log",
        "true",
        "--duration-log.statistics",
        "true",
        "--tripinfo-output",
        str(headless_tripinfo),
    ]
    headless = subprocess.run(headless_command, cwd=config.parent, capture_output=True, text=True)
    log = (
        f"run_id={run_id}\n"
        f"scenario_hash={current_scenario_hash}\n"
        f"exit_code={headless.returncode}\n"
        f"command={subprocess.list2cmdline(headless_command)}\n"
        "--- stdout ---\n"
        f"{headless.stdout}"
        "--- stderr ---\n"
        f"{headless.stderr}"
    )
    (artifacts / "headless.log").write_text(log, encoding="utf-8")
    if headless.returncode != 0:
        raise RuntimeError(f"Native headless SUMO failed; see {artifacts / 'headless.log'}")

    traci_measurement = measure_traci(
        sumo_binary, config, artifacts / "traci-tripinfo.xml", SEED
    )
    libsumo_measurement = measure_libsumo(
        sumo_binary, config, artifacts / "libsumo-tripinfo.xml", SEED
    )
    libsumo_blocked = bool(libsumo_measurement.get("blocked"))
    toolchain["libsumo_importable"] = not libsumo_blocked
    _write_json(artifacts / "toolchain.json", toolchain)

    gui_version_proc = subprocess.run(
        [gui_binary, "--version"], capture_output=True, text=True, check=False
    )
    (artifacts / "gui-diagnosis.md").write_text(
        "\n".join(
            [
                "# sumo-gui diagnosis",
                "",
                f"`sumo-gui` binary: `{gui_binary}`",
                f"Version: `{gui_version}`",
                f"Exit code: `{gui_version_proc.returncode}`",
                "",
                "```",
                gui_version_output,
                "```",
                "",
                "This file documents that sumo-gui exists for human diagnosis.",
                "It is **not a batch dependency**. The native smoke-test command",
                "uses headless `sumo.exe` plus TraCI and does not launch the GUI.",
                "",
            ]
        ),
        encoding="utf-8",
    )

    if libsumo_blocked:
        blocked = root / "harness" / "BLOCKED"
        blocked.write_text(
            "BLOCKED: Windows Code Integrity policy "
            "{0283ac0f-fff1-49ae-ada1-8a933130cad6} blocks SUMO 1.27.1 "
            "libsumo dependencies geos_c.dll and jupedsim.dll (events 3033/3077). "
            "TraCI from SUMO_HOME\\tools works on native Windows. "
            "Ask the Windows administrator to allow those Eclipse SUMO DLLs, then run: "
            "py -3.11 -c \"import libsumo; print(libsumo.__file__)\"\n",
            encoding="utf-8",
        )

    throughput = {
        "run_id": run_id,
        "scenario_hash": current_scenario_hash,
        "seed": SEED,
        "measured_at": utc_now(),
        "hardware": {
            "machine": platform.machine(),
            "processor": platform.processor(),
            "logical_cpu_count": os.cpu_count(),
            "platform": platform.platform(),
        },
        "measurements": {
            "traci": traci_measurement,
            "libsumo": libsumo_measurement,
        },
        "comparison": {"same_scenario": True, "same_seed": True},
        "units": {
            "throughput": "simulation_steps/second",
            "peak_memory": "bytes",
            "artifact_size": "bytes",
        },
    }
    _write_json(artifacts / "throughput.json", throughput)

    native_command = [sys.executable, str(root / "scripts" / "run_native_smoke.py")]
    manifest = {
        "run_id": run_id,
        "scenario_hash": current_scenario_hash,
        "scenario_hash_algorithm": "sha256 over ordered relative path, NUL, file bytes, NUL",
        "scenario_files": list(FROZEN_SCENARIO_FILES),
        "configuration_hash": file_hash(config),
        "status": "blocked-libsumo" if libsumo_blocked else "completed",
        "started_at": started_at,
        "finished_at": utc_now(),
        "sumo_version": sumo_version,
        "source_revision": toolchain["source_revision"],
        "seed": SEED,
        "native_command": native_command,
        "sumo_command": headless_command,
        "docker_required": False,
        "wsl_required": False,
        "artifact_references": [
            "toolchain.json",
            "throughput.json",
            "headless.log",
            "headless-tripinfo.xml",
            "gui-diagnosis.md",
        ],
    }
    _write_json(artifacts / "run_manifest.json", manifest)
    return manifest


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    manifest = run_smoke(root)
    print(f"run_id={manifest['run_id']}")
    print(f"scenario_hash={manifest['scenario_hash']}")
    print(f"status={manifest['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
