from __future__ import annotations

import ast
import hashlib
import json
import re
from pathlib import Path

import pyarrow.parquet as pq

from coflow5.evidence.schemas import RunManifest

ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS = ROOT / "harness/work/05-max-pressure/artifacts"
HASH = re.compile(r"^sha256:[0-9a-f]{64}$")


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def test_every_decision_resolves_to_one_manifest_identity_and_retains_explanation() -> None:
    manifest = json.loads((ARTIFACTS / "run_manifest.json").read_text(encoding="utf-8"))
    rows = pq.read_table(ARTIFACTS / "decision_events.parquet").to_pylist()
    event_ids = [row["event_id"] for row in rows]
    assert rows and len(event_ids) == len(set(event_ids))
    for row in rows:
        assert (row["run_id"], row["scenario_hash"]) == (
            manifest["run_id"], manifest["scenario_hash"]
        )
        assert row["accepted_action"]
        assert row["rejected_alternatives"] is not None
        assert row["constraints"]
        assert row["reason_code"] in {
            "MAX_PRESSURE_LOCAL_ONLY", "MAX_PRESSURE_WITH_ADVISORY"
        }
        scores = json.loads(row["action_scores_json"])
        assert scores and scores[0]["phase_id"] == row["accepted_action"]
        assert {item["phase_id"] for item in scores[1:]} == set(row["rejected_alternatives"])
        assert {
            "pressure", "phase_timing", "advisory", "total", "downstream_available"
        } <= set(scores[0])


def test_every_considered_message_resolves_in_the_same_run_or_list_is_empty() -> None:
    audit = json.loads((ARTIFACTS / "controller-audit.json").read_text(encoding="utf-8"))
    rows = pq.read_table(ARTIFACTS / "decision_events.parquet").to_pylist()
    catalog = {item["message_id"]: item for item in audit["message_catalog"]}
    assert any(not row["considered_message_ids"] for row in rows)
    assert any(row["considered_message_ids"] for row in rows)
    for row in rows:
        assert len(row["considered_message_ids"]) == len(set(row["considered_message_ids"]))
        for message_id in row["considered_message_ids"]:
            assert message_id in catalog
            assert catalog[message_id]["run_id"] == row["run_id"]
            assert catalog[message_id]["signal_id"] == row["signal_id"]
    assert audit["unresolved_message_ids"] == []
    assert audit["wrong_run_message_ids"] == []


def test_decision_observation_and_command_rows_join_one_to_one() -> None:
    decisions = pq.read_table(ARTIFACTS / "decision_events.parquet").to_pylist()
    observations = pq.read_table(ARTIFACTS / "observations.parquet").to_pylist()
    commands = pq.read_table(ARTIFACTS / "executed_commands.parquet").to_pylist()
    observations_by_event = {row["event_id"]: row for row in observations}
    commands_by_event = {row["event_id"]: row for row in commands}
    assert len(decisions) == len(observations_by_event) == len(commands_by_event)
    for decision in decisions:
        event_id = decision["event_id"]
        observation = observations_by_event[event_id]
        command = commands_by_event[event_id]
        identity = (
            decision["run_id"], decision["scenario_hash"], decision["proposal_id"],
            decision["signal_id"], decision["simulation_time"],
        )
        assert identity == (
            observation["run_id"], observation["scenario_hash"],
            observation["proposal_id"], observation["signal_id"],
            observation["simulation_time"],
        )
        assert identity == (
            command["run_id"], command["scenario_hash"], command["proposal_id"],
            command["signal_id"], command["simulation_time"],
        )
        assert command["phase_id"] == decision["accepted_action"]
        movement_rows = json.loads(observation["movement_inputs_json"])
        assert {item["movement_id"] for item in movement_rows} == {
            "north", "south", "east", "west"
        }


def test_manifest_hash_binds_each_finalized_artifact_and_producing_source() -> None:
    manifest_data = json.loads((ARTIFACTS / "run_manifest.json").read_text(encoding="utf-8"))
    RunManifest.model_validate(manifest_data)
    references = {item["path"]: item for item in manifest_data["artifact_references"]}
    assert set(references) == {
        "decision_events.parquet",
        "observations.parquet",
        "executed_commands.parquet",
        "controller-audit.json",
    }
    for name, reference in references.items():
        path = ARTIFACTS / name
        assert path.exists()
        assert reference["sha256"] == _sha256(path)
        assert reference["bytes"] == path.stat().st_size
    assert manifest_data["sumo_command"][0].lower().endswith("sumo.exe")
    assert manifest_data["source_hashes"]
    for relative, expected in manifest_data["source_hashes"].items():
        assert HASH.fullmatch(expected)
        assert expected == _sha256(ROOT / relative)


def test_required_path_has_no_llm_langgraph_dqn_torch_or_raw_sumo_import() -> None:
    paths = [
        ROOT / "src/coflow5/control/max_pressure.py",
        ROOT / "src/coflow5/control/a1_controller.py",
    ]
    imported: set[str] = set()
    source = ""
    for path in paths:
        text = path.read_text(encoding="utf-8")
        source += text.lower()
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0].lower() for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0].lower())
    assert not ({"traci", "libsumo", "torch", "langgraph", "openai"} & imported)
    assert "trafficlight.set" not in source
    audit = json.loads((ARTIFACTS / "controller-audit.json").read_text(encoding="utf-8"))
    assert audit["dqn_dependency"] is False
    assert audit["torch_dependency"] is False
    assert audit["recovery_ladder"] == [
        "cooperative-max-pressure", "actuated", "fixed-time"
    ]
