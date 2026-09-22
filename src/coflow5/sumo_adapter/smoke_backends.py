from __future__ import annotations

import os
import sys
import threading
import time
import uuid
from pathlib import Path
from typing import Any, Callable

import psutil

LIBSUMO_WDAC_POLICY = "{0283ac0f-fff1-49ae-ada1-8a933130cad6}"


def ensure_sumo_tools_on_path() -> Path:
    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home:
        raise RuntimeError("SUMO_HOME must point to the native Eclipse SUMO installation")
    tools = Path(sumo_home) / "tools"
    if not tools.is_dir():
        raise RuntimeError(f"SUMO tools directory missing: {tools}")
    tools_str = str(tools)
    if tools_str not in sys.path:
        sys.path.insert(0, tools_str)
    return tools


def load_traci():
    ensure_sumo_tools_on_path()
    import traci

    return traci


def traci_module_file() -> str:
    traci = load_traci()
    return str(Path(traci.__file__).resolve())


def load_libsumo():
    ensure_sumo_tools_on_path()
    import libsumo

    return libsumo


def _peak_process_tree_rss(stop: threading.Event, result: list[int]) -> None:
    process = psutil.Process()
    peak = 0
    while not stop.is_set():
        processes = [process]
        try:
            processes.extend(process.children(recursive=True))
        except (psutil.Error, OSError):
            pass
        total = 0
        for item in processes:
            try:
                total += item.memory_info().rss
            except (psutil.Error, OSError):
                continue
        peak = max(peak, total)
        stop.wait(0.002)
    result.append(peak)


def _measure(run: Callable[[], int], artifact: Path) -> dict[str, Any]:
    stop = threading.Event()
    peaks: list[int] = []
    sampler = threading.Thread(target=_peak_process_tree_rss, args=(stop, peaks), daemon=True)
    sampler.start()
    started = time.perf_counter()
    try:
        steps = run()
    finally:
        wall_seconds = time.perf_counter() - started
        stop.set()
        sampler.join(timeout=2)
    peak = peaks[0] if peaks else psutil.Process().memory_info().rss
    artifact_bytes = artifact.stat().st_size if artifact.exists() else 0
    return {
        "simulation_steps": steps,
        "wall_seconds": wall_seconds,
        "simulation_steps_per_wall_second": steps / wall_seconds if wall_seconds else 0,
        "peak_memory_bytes": peak,
        "artifact_bytes": artifact_bytes,
    }


def _command(sumo_binary: str, config: Path, tripinfo: Path, seed: int) -> list[str]:
    return [
        sumo_binary,
        "-c",
        str(config),
        "--seed",
        str(seed),
        "--no-step-log",
        "true",
        "--tripinfo-output",
        str(tripinfo),
    ]


def measure_traci(sumo_binary: str, config: Path, tripinfo: Path, seed: int) -> dict[str, Any]:
    traci = load_traci()
    label = f"coflow5-smoke-{uuid.uuid4()}"
    command = _command(sumo_binary, config, tripinfo, seed)

    def run() -> int:
        traci.start(command, label=label, stdout=None)
        connection = traci.getConnection(label)
        steps = 0
        try:
            while connection.simulation.getMinExpectedNumber() > 0:
                connection.simulationStep()
                steps += 1
        finally:
            connection.close(False)
        return steps

    result = _measure(run, tripinfo)
    result["command"] = command
    result["backend"] = "traci"
    return result


def measure_libsumo(sumo_binary: str, config: Path, tripinfo: Path, seed: int) -> dict[str, Any]:
    command = _command(sumo_binary, config, tripinfo, seed)
    try:
        libsumo = load_libsumo()
    except Exception as exc:  # noqa: BLE001 — WDAC/DLL failures are the evidence
        return {
            "backend": "libsumo",
            "blocked": True,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "policy_id": LIBSUMO_WDAC_POLICY,
            "command": command,
        }

    def run() -> int:
        libsumo.start(command)
        steps = 0
        try:
            while libsumo.simulation.getMinExpectedNumber() > 0:
                libsumo.simulationStep()
                steps += 1
        finally:
            libsumo.close()
        return steps

    result = _measure(run, tripinfo)
    result["command"] = command
    result["backend"] = "libsumo"
    result["blocked"] = False
    return result
