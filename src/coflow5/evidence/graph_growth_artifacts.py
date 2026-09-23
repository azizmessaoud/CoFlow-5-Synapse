from __future__ import annotations

import hashlib
import json
import platform
import random
import shutil
import subprocess
import sys
import uuid
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import pyarrow as pa
import pyarrow.parquet as pq

from coflow5.control.graph_max_pressure import score_graph_actions
from coflow5.control.junction_graph import NeighbourObservation, load_junction_graph
from coflow5.sumo_adapter.graph_growth_runner import generate_od_routes, run_native_graph_growth_smoke

DEMAND_SCALES = (0.75, 1.0, 1.25, 1.5)
SEEDS = (11, 23, 37, 53, 71)
CONTROLLERS = (
    "fixed-time", "actuated", "local-cooperative-max-pressure",
    "graph-aware-cooperative-max-pressure",
)
SIGNALS = ("J0", "J1", "J2", "J3")
HORIZON_SECONDS = 90
FRAME_TIMES = tuple(range(0, HORIZON_SECONDS + 1, 5))
CONTRACT = "harness/work/10f-graph-growth-benchmark/contract.json"
LOCKED = (
    "harness/work/05-max-pressure/contract.json",
    "harness/work/05-max-pressure/gate.json",
    "harness/work/10b-max-pressure-trip-kpis/contract.json",
    "harness/work/10b-max-pressure-trip-kpis/gate.json",
    "harness/work/10e-graph-growth-spec/contract.json",
    "harness/work/10e-graph-growth-spec/gate.json",
)
SCENARIO = (
    "scenarios/graph-growth/graph-growth.net.xml",
    "scenarios/graph-growth/graph-growth.rou.xml",
    "scenarios/graph-growth/graph-growth.tls.xml",
    "scenarios/graph-growth/graph-growth.sumocfg",
)
SOURCES = (
    "src/coflow5/control/junction_graph.py",
    "src/coflow5/control/graph_max_pressure.py",
    "src/coflow5/sumo_adapter/graph_growth_runner.py",
    "src/coflow5/evidence/graph_growth_artifacts.py",
    "scripts/generate_graph_growth_artifacts.py",
)


def _hash_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _hash(path: Path) -> str:
    return _hash_bytes(path.read_bytes())


def _json_hash(value: object) -> str:
    return _hash_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _scenario_hash(root: Path) -> str:
    digest = hashlib.sha256()
    for relative in SCENARIO:
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update((root / relative).read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = (len(ordered) - 1) * percentile
    low = int(rank)
    high = min(len(ordered) - 1, low + 1)
    fraction = rank - low
    return ordered[low] * (1 - fraction) + ordered[high] * fraction


def _fixture_completion(scale: float, seed: int, controller: str) -> float:
    overload = scale - 0.75
    if controller == "fixed-time":
        value = 0.96 - overload * 0.28
    elif controller == "actuated":
        value = 0.98 - overload * 0.20
    elif controller == "local-cooperative-max-pressure":
        value = 0.97 - overload * 0.24
    else:
        value = 0.965 - overload * 0.22 + {11: -0.03, 23: 0.02, 37: -0.01, 53: 0.03, 71: 0.0}[seed]
    return max(0.0, min(1.0, value))


def _fallback_probes(graph_hash: str) -> list[dict[str, object]]:
    local = {"EW_GREEN": 4.0, "NS_GREEN": 6.0}
    available = {key: True for key in local}
    ages = {key: 20.0 for key in local}
    fresh = (NeighbourObservation(
        from_signal_id="J0", to_signal_id="J1", movement_group="NS",
        observed_at=10.0, expires_at=15.0, queue_vehicles=2.0,
        occupancy_ratio=0.2, predicted_discharge_vehicles=1.0,
    ),)
    cases = (
        ("fresh", graph_hash, fresh),
        ("stale", graph_hash, (NeighbourObservation(
            from_signal_id="J0", to_signal_id="J1", movement_group="NS",
            observed_at=1.0, expires_at=2.0, queue_vehicles=2.0,
            occupancy_ratio=0.2, predicted_discharge_vehicles=1.0,
        ),)),
        ("missing", graph_hash, None),
        ("identity-mismatch", "sha256:" + "0" * 64, fresh),
    )
    rows = []
    for name, observed_hash, neighbours in cases:
        decision = score_graph_actions(
            expected_graph_hash=graph_hash, observation_graph_hash=observed_hash,
            simulation_time=10.0, current_phase_id="NS_GREEN",
            local_pressures=local, downstream_available=available,
            service_age_seconds=ages, neighbours=neighbours,
        )
        rows.append({
            "case": name, "accepted_action": decision.accepted_action,
            "reason_code": decision.reason_code,
            "used_neighbour_ids": list(decision.used_neighbour_ids),
            "scores": [asdict(score) for score in decision.scores],
        })
    return rows


def _cell_rows(*, scenario_hash: str, graph_hash: str, contract_hash: str,
               scale: float, seed: int, controller: str) -> dict[str, Any]:
    run_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{contract_hash}:{scenario_hash}:{graph_hash}:{scale}:{seed}:{controller}"))
    _, trip_ids = generate_od_routes(demand_scale=scale, seed=seed)
    rng = random.Random(f"coflow5:{scale}:{seed}:{controller}")
    planned = len(trip_ids)
    completed_count = min(planned, int(round(planned * _fixture_completion(scale, seed, controller))))
    completion_order = list(range(planned))
    rng.shuffle(completion_order)
    completed_indexes = set(completion_order[:completed_count])
    trips: list[dict[str, object]] = []
    durations: list[float] = []
    waits: list[float] = []
    losses: list[float] = []
    for index, trip_id in enumerate(trip_ids):
        departed = round(index * 60.0 / planned, 3)
        completed = index in completed_indexes
        controller_cost = {"fixed-time": 7.0, "actuated": 4.0,
                           "local-cooperative-max-pressure": 5.0,
                           "graph-aware-cooperative-max-pressure": 4.5}[controller]
        duration = round(14.0 + scale * 9.0 + controller_cost + rng.random() * 11.0, 3) if completed else None
        arrival = round(departed + duration, 3) if duration is not None else None
        wait = round(max(0.0, (duration or 0.0) - 20.0), 3) if completed else None
        loss = round((wait or 0.0) + scale * 2.0, 3) if completed else None
        if completed:
            durations.append(duration or 0.0)
            waits.append(wait or 0.0)
            losses.append(loss or 0.0)
        trips.append({
            "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
            "graph_hash": graph_hash, "controller": controller, "seed": seed,
            "demand_scale": scale, "trip_id": trip_id,
            "trip_status": "completed" if completed else "active-at-horizon",
            "departed_at_s": departed, "arrived_at_s": arrival,
            "duration_s": duration, "waiting_time_s": wait, "time_loss_s": loss,
            "observed_at_s": float(HORIZON_SECONDS),
        })

    states: list[dict[str, object]] = []
    frames: list[dict[str, object]] = []
    decisions: list[dict[str, object]] = []
    max_queue_ratio = 0.0
    max_service_age = 0.0
    switches = 0
    previous = {signal: "NS_GREEN" for signal in SIGNALS}
    for time_s in FRAME_TIMES:
        node_frame = []
        edge_frame = []
        for signal_index, signal in enumerate(SIGNALS):
            wave = ((time_s // 5 + signal_index + seed) % 7) / 7.0
            controller_relief = {"fixed-time": 0.02, "actuated": 0.08,
                                 "local-cooperative-max-pressure": 0.06,
                                 "graph-aware-cooperative-max-pressure": 0.07}[controller]
            queue_ratio = max(0.0, min(1.0, scale / 1.5 * 0.72 + wave * 0.24 - controller_relief))
            service_age = min(90.0, queue_ratio * 55.0 + (time_s % 15))
            phase = "NS_GREEN" if (time_s // (15 if controller == "fixed-time" else 10) + signal_index) % 2 == 0 else "EW_GREEN"
            switched = phase != previous[signal]
            switches += int(switched)
            previous[signal] = phase
            max_queue_ratio = max(max_queue_ratio, queue_ratio)
            max_service_age = max(max_service_age, service_age)
            states.append({
                "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
                "graph_hash": graph_hash, "controller": controller, "seed": seed,
                "demand_scale": scale, "simulation_time": float(time_s),
                "signal_id": signal, "phase_id": phase,
                "queue_storage_ratio": queue_ratio, "service_age_seconds": service_age,
                "writer_owner": "A1", "writer_count": 1,
            })
            node_frame.append({"signal_id": signal, "phase_id": phase, "queue_storage_ratio": round(queue_ratio, 6), "mode": controller})
            event_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{run_id}:{time_s}:{signal}"))
            graph_enabled = controller == "graph-aware-cooperative-max-pressure"
            one_hop = min(2.0, queue_ratio * 2.2) if graph_enabled else 0.0
            service_bonus = min(2.0, service_age / 30.0) if graph_enabled else 0.0
            switch_penalty = 1.0 if graph_enabled and switched else 0.0
            decisions.append({
                "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
                "graph_hash": graph_hash, "event_id": event_id, "message_id": None,
                "controller": controller, "seed": seed, "demand_scale": scale,
                "simulation_time": float(time_s), "signal_id": signal,
                "accepted_action": phase, "reason_code": "GRAPH_NEIGHBOUR_USED" if graph_enabled else "MAX_PRESSURE_LOCAL_ONLY" if "pressure" in controller else "BASELINE_POLICY",
                "local_pressure": round(queue_ratio * 10.0, 6),
                "one_hop_discharge_bonus": one_hop, "service_age_bonus": service_bonus,
                "switch_penalty": switch_penalty, "downstream_blocked": False,
                "safety_accepted": True, "message_ids_json": "[]",
            })
        for edge_index in range(8):
            edge_frame.append({"edge_id": f"internal-{edge_index}", "occupancy_ratio": round(min(1.0, scale * 0.4 + ((time_s + edge_index) % 10) / 50.0), 6)})
        frames.append({
            "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
            "graph_hash": graph_hash, "controller": controller, "seed": seed,
            "demand_scale": scale, "simulation_time": float(time_s),
            "nodes_json": json.dumps(node_frame, sort_keys=True, separators=(",", ":")),
            "edges_json": json.dumps(edge_frame, sort_keys=True, separators=(",", ":")),
            "messages_json": "[]", "faults_json": "[]", "mode": controller,
            "limitations_json": json.dumps(["deterministic fixture frame", "read-only; cannot actuate SUMO"]),
        })
    kpi = {
        "schema_version": 1, "run_id": run_id, "scenario_hash": scenario_hash,
        "graph_hash": graph_hash, "controller": controller, "seed": seed,
        "demand_scale": scale, "evidence_kind": "deterministic-fixture",
        "planned_trips": planned, "completed_trips": completed_count,
        "unfinished_trips": planned - completed_count,
        "completion_rate": completed_count / planned,
        "mean_duration_s": sum(durations) / len(durations) if durations else 0.0,
        "p95_duration_s": _percentile(durations, 0.95),
        "mean_waiting_time_s": sum(waits) / len(waits) if waits else 0.0,
        "p95_waiting_time_s": _percentile(waits, 0.95),
        "total_time_loss_s": sum(losses), "teleport_events": 0,
        "safety_violations": 0, "illegal_transitions": 0,
        "writer_violations": 0, "decision_count": len(FRAME_TIMES) * 4,
        "switch_count": switches, "max_queue_storage_ratio": max_queue_ratio,
        "max_service_age_seconds": max_service_age,
        "gridlocked": max_queue_ratio >= 1.0, "fixture_operations": len(states) + len(decisions),
    }
    payload_bytes = len(json.dumps({"trips": trips, "states": states, "frames": frames, "decisions": decisions}, sort_keys=True).encode())
    kpi["fixture_payload_bytes"] = payload_bytes
    return {"run_id": run_id, "trip_ids": trip_ids, "trips": trips, "states": states,
            "frames": frames, "decisions": decisions, "kpi": kpi}


def _native_smoke(root: Path, scenario_hash: str, graph_hash: str, contract_hash: str) -> dict[str, object]:
    binary = shutil.which("sumo")
    if binary is None:
        candidate = Path(r"C:\Program Files (x86)\Eclipse\Sumo\bin\sumo.exe")
        binary = str(candidate) if candidate.is_file() else None
    base = {
        "schema_version": 1, "evidence_kind": "native-traci-smoke",
        "run_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{contract_hash}:{scenario_hash}:native-smoke")),
        "scenario_hash": scenario_hash, "graph_hash": graph_hash,
        "seed": 37, "horizon_seconds": 30.0, "matrix_member": False,
        "claim_boundary": "This is one diagnostic native smoke, not the 80-cell evaluation matrix.",
    }
    if binary is None:
        return {**base, "status": "unavailable", "actual_traci_execution": False,
                "failure_reason": "sumo.exe was not found"}
    try:
        result = run_native_graph_growth_smoke(
            sumo_binary=binary, config=root / "scenarios/graph-growth/graph-growth.sumocfg",
            network_file=root / "scenarios/graph-growth/graph-growth.net.xml",
            run_id=str(base["run_id"]), scenario_hash=scenario_hash,
        )
    except BaseException as exc:
        return {**base, "status": "failed", "actual_traci_execution": False,
                "failure_reason": f"{type(exc).__name__}: {exc}", "sumo_binary": binary}
    return {**base, "status": "completed", "actual_traci_execution": True,
            "failure_reason": None, "simulation_steps": result.simulation_steps,
            "decision_count": len(result.decisions), "safety_event_count": result.safety_event_count,
            "accepted_command_count": result.accepted_command_count,
            "rejected_event_count": result.rejected_event_count,
            "writer_count_by_signal": dict(result.writer_count_by_signal),
            "traci_version": result.traci_version, "sumo_command": list(result.command)}


def _reference(path: Path, rows: int, schema: str) -> dict[str, object]:
    return {"path": path.name, "sha256": _hash(path), "bytes": path.stat().st_size,
            "rows": rows, "schema_name": schema, "schema_version": 1}


def generate_graph_growth_artifacts(root: Path, output_dir: Path | None = None) -> dict[str, object]:
    root = root.resolve()
    destination = (output_dir or root / "harness/work/10f-graph-growth-benchmark/artifacts").resolve()
    protected = tuple((root / relative).parent.resolve() for relative in LOCKED[:4])
    if any(destination == path or path in destination.parents for path in protected):
        raise ValueError("Row 10f cannot write to frozen Row 05 or Row 10b")
    contract_path = root / CONTRACT
    contract_hash = _hash(contract_path)
    before = {relative: _hash(root / relative) for relative in LOCKED}
    graph = load_junction_graph(root / SCENARIO[0])
    scenario_hash = _scenario_hash(root)
    staging = destination.parent / f".{destination.name}.staging-{uuid.uuid4()}"
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)
    try:
        graph_doc = graph.to_dict()
        graph_doc.update({
            "scenario_hash": scenario_hash,
            "term_bounds": {"one_hop_discharge_bonus": 2.0, "service_age_bonus": 2.0, "switch_penalty": 1.0},
            "fallback_probes": _fallback_probes(graph.graph_hash),
            "actuation_capability": None,
        })
        _write_json(staging / "graph.json", graph_doc)
        cells: list[dict[str, object]] = []
        trips: list[dict[str, object]] = []
        states: list[dict[str, object]] = []
        frames: list[dict[str, object]] = []
        decisions: list[dict[str, object]] = []
        kpis: list[dict[str, object]] = []
        identities: list[dict[str, object]] = []
        for scale in DEMAND_SCALES:
            for seed in SEEDS:
                for controller in CONTROLLERS:
                    generated = _cell_rows(
                        scenario_hash=scenario_hash, graph_hash=graph.graph_hash,
                        contract_hash=contract_hash, scale=scale, seed=seed, controller=controller,
                    )
                    cell = {"run_id": generated["run_id"], "scenario_hash": scenario_hash,
                            "graph_hash": graph.graph_hash, "demand_scale": scale,
                            "seed": seed, "controller": controller,
                            "planned_trip_count": len(generated["trip_ids"]),
                            "evidence_kind": "deterministic-fixture"}
                    cells.append(cell)
                    identities.append({key: cell[key] for key in ("run_id", "scenario_hash", "graph_hash", "seed", "controller", "demand_scale")})
                    trips.extend(generated["trips"])
                    states.extend(generated["states"])
                    frames.extend(generated["frames"])
                    decisions.extend(generated["decisions"])
                    kpis.append(generated["kpi"])
        _write_json(staging / "demand_cells.json", {
            "schema_version": 1, "matrix_evidence": "deterministic-fixture",
            "native_run_count_claimed": 0, "demand_scales": list(DEMAND_SCALES),
            "seeds": list(SEEDS), "controllers": list(CONTROLLERS), "cells": cells,
        })
        parquet_sets = (
            ("junction_states.parquet", states), ("graph_frames.parquet", frames),
            ("decision_events.parquet", decisions), ("trips.parquet", trips),
            ("run_kpis.parquet", kpis),
        )
        for name, rows in parquet_sets:
            pq.write_table(pa.Table.from_pylist(rows), staging / name, compression="zstd")
        comparison_rows = []
        for scale in DEMAND_SCALES:
            for seed in SEEDS:
                group = [row for row in kpis if row["demand_scale"] == scale and row["seed"] == seed]
                comparison_rows.append({
                    "demand_scale": scale, "seed": seed,
                    "controllers": [{key: row[key] for key in (
                        "run_id", "controller", "planned_trips", "completed_trips",
                        "unfinished_trips", "completion_rate", "p95_waiting_time_s",
                        "max_queue_storage_ratio", "max_service_age_seconds", "gridlocked",
                    )} for row in group],
                })
        graph_better = sum(
            next(row for row in group["controllers"] if row["controller"] == "graph-aware-cooperative-max-pressure")["completed_trips"]
            > next(row for row in group["controllers"] if row["controller"] == "local-cooperative-max-pressure")["completed_trips"]
            for group in comparison_rows
        )
        graph_worse = sum(
            next(row for row in group["controllers"] if row["controller"] == "graph-aware-cooperative-max-pressure")["completed_trips"]
            < next(row for row in group["controllers"] if row["controller"] == "local-cooperative-max-pressure")["completed_trips"]
            for group in comparison_rows
        )
        comparison = {
            "schema_version": 1, "scenario_hash": scenario_hash, "graph_hash": graph.graph_hash,
            "pairing_keys": ["scenario_hash", "graph_hash", "demand_scale", "seed"],
            "paired_groups": comparison_rows, "paired_group_count": len(comparison_rows),
            "graph_completed_more_groups": graph_better, "graph_completed_fewer_groups": graph_worse,
            "winner_claim": None, "significance_test_performed": False,
            "unfinished_and_gridlocked_retained": True,
            "claim_boundary": "Deterministic fixture outcomes show behavior, not native SUMO superiority or deployment performance.",
        }
        _write_json(staging / "matched_growth_comparison.json", comparison)
        native = _native_smoke(root, scenario_hash, graph.graph_hash, contract_hash)
        _write_json(staging / "native_smoke.json", native)
        after = {relative: _hash(root / relative) for relative in LOCKED}
        input_audit = {
            "schema_version": 1, "contract_hash": contract_hash,
            "locked_input_hashes": before, "locked_inputs_unchanged": before == after,
            "row05_and_10b_modified": False, "scenario_files": {relative: _hash(root / relative) for relative in SCENARIO},
            "source_hashes": {relative: _hash(root / relative) for relative in SOURCES},
        }
        _write_json(staging / "input_audit.json", input_audit)
        report = "\n".join((
            "# Row 10f graph-growth benchmark", "",
            "## Evidence boundary", "",
            "The clean 80-cell matrix is deterministic fixture evidence over the immutable four-signal graph and bounded controller contracts. It is not represented as 80 native SUMO runs.", "",
            f"The native Windows TraCI smoke status is **{native['status']}**. Its full failure or execution provenance is retained in `native_smoke.json`.", "",
            "## Observed fixture result", "",
            f"Graph-aware completed more trips than local Max-Pressure in {graph_better}/20 paired groups and fewer in {graph_worse}/20. No winner or statistical significance is claimed.", "",
            "All planned trips, unfinished trips, queue/storage ratios, service ages, switch counts, safety counts, and read-only five-second graph frames are retained.", "",
            "## Limitations and Claim flags", "",
            "- Deterministic fixture outcomes are contract tests, not calibrated traffic or deployment evidence.",
            "- The one native smoke is diagnostic and is not the paired matrix.",
            "- No lives saved, accident prevention, measured air quality, best episode, or graph-aware superiority is claimed.",
        )) + "\n"
        (staging / "growth_report.md").write_text(report, encoding="utf-8")
        references = [
            _reference(staging / "graph.json", 1, "junction_graph"),
            _reference(staging / "demand_cells.json", len(cells), "growth_demand_cells"),
            _reference(staging / "junction_states.parquet", len(states), "junction_state"),
            _reference(staging / "graph_frames.parquet", len(frames), "graph_frame"),
            _reference(staging / "decision_events.parquet", len(decisions), "graph_decision_event"),
            _reference(staging / "trips.parquet", len(trips), "growth_trip"),
            _reference(staging / "run_kpis.parquet", len(kpis), "growth_run_kpi"),
            _reference(staging / "matched_growth_comparison.json", len(comparison_rows), "matched_growth_comparison"),
            _reference(staging / "growth_report.md", 1, "growth_report"),
            _reference(staging / "native_smoke.json", 1, "native_smoke"),
            _reference(staging / "input_audit.json", len(LOCKED), "input_audit"),
        ]
        manifest = {
            "schema_version": 1,
            "run_id": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{contract_hash}:{scenario_hash}:{graph.graph_hash}:suite")),
            "scenario_hash": scenario_hash, "graph_hash": graph.graph_hash,
            "configuration_hash": _json_hash({"scales": DEMAND_SCALES, "seeds": SEEDS, "controllers": CONTROLLERS, "horizon": HORIZON_SECONDS}),
            "contract_hash": contract_hash, "status": "completed",
            "evidence_kind": "deterministic-fixture-matrix-with-native-smoke",
            "matrix_run_count": len(cells), "native_matrix_run_count": 0,
            "native_smoke_status": native["status"], "runs": identities,
            "versions": {"python": platform.python_version(), "pyarrow": pa.__version__},
            "source_revision": subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True).stdout.strip() or None,
            "artifact_references": references,
            "finalized_at": datetime.now(timezone.utc).isoformat(), "immutable": True,
            "claim_boundary": comparison["claim_boundary"],
        }
        _write_json(staging / "run_manifest.json", manifest)
        destination.parent.mkdir(parents=True, exist_ok=True)
        backup = destination.parent / f".{destination.name}.previous-{uuid.uuid4()}"
        if destination.exists():
            destination.replace(backup)
        staging.replace(destination)
        shutil.rmtree(backup, ignore_errors=True)
        return manifest
    except BaseException:
        shutil.rmtree(staging, ignore_errors=True)
        raise
