from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pyarrow.parquet as pq
import pytest

from coflow5.evidence.graph_growth_artifacts import generate_graph_growth_artifacts

ROOT = Path(__file__).resolve().parents[2]
PACK = ROOT / "harness/work/10f-graph-growth-benchmark"


@pytest.fixture(scope="module")
def artifacts(tmp_path_factory: pytest.TempPathFactory) -> Path:
    output = tmp_path_factory.mktemp("graph-growth") / "artifacts"
    generate_graph_growth_artifacts(ROOT, output)
    return output


def test_scenario_has_four_signals_and_straight_controlled_movements() -> None:
    network = ET.parse(ROOT / "scenarios/graph-growth/graph-growth.net.xml").getroot()
    signals = sorted(j.get("id") for j in network.findall("junction") if j.get("type") == "traffic_light")
    assert signals == ["J0", "J1", "J2", "J3"]
    for signal in signals:
        connections = [row for row in network.findall("connection") if row.get("tl") == signal]
        assert len(connections) == 4
        assert sorted(int(row.get("linkIndex")) for row in connections) == [0, 1, 2, 3]
    tls = ET.parse(ROOT / "scenarios/graph-growth/graph-growth.tls.xml").getroot()
    assert {row.get("id") for row in tls.findall("tlLogic")} == set(signals)
    assert all(len(row.find("phase").get("state")) == 4 for row in tls.findall("tlLogic"))


def test_exact_80_cell_fixture_matrix_is_paired_and_accounted(artifacts: Path) -> None:
    document = json.loads((artifacts / "demand_cells.json").read_text(encoding="utf-8"))
    cells = document["cells"]
    assert document["matrix_evidence"] == "deterministic-fixture"
    assert document["native_run_count_claimed"] == 0
    assert len(cells) == 80
    assert len({row["run_id"] for row in cells}) == 80
    grouped = {}
    for row in cells:
        grouped.setdefault((row["demand_scale"], row["seed"]), set()).add(row["controller"])
    assert len(grouped) == 20
    assert all(controllers == set(document["controllers"]) for controllers in grouped.values())
    kpis = pq.read_table(artifacts / "run_kpis.parquet").to_pylist()
    assert len(kpis) == 80
    assert all(row["planned_trips"] == row["completed_trips"] + row["unfinished_trips"] for row in kpis)
    assert all(row["safety_violations"] == row["writer_violations"] == row["illegal_transitions"] == 0 for row in kpis)
    assert any(row["unfinished_trips"] > 0 for row in kpis)


def test_native_smoke_is_diagnostic_and_never_fabricated(artifacts: Path) -> None:
    smoke = json.loads((artifacts / "native_smoke.json").read_text(encoding="utf-8"))
    assert smoke["evidence_kind"] == "native-traci-smoke"
    assert smoke["matrix_member"] is False
    assert smoke["status"] in {"completed", "failed", "unavailable"}
    assert smoke["actual_traci_execution"] is (smoke["status"] == "completed")
    if smoke["status"] == "completed":
        assert smoke["writer_count_by_signal"] == {signal: 1 for signal in ("J0", "J1", "J2", "J3")}
        assert smoke["accepted_command_count"] == smoke["decision_count"] == smoke["safety_event_count"]
        assert smoke["rejected_event_count"] == 0
    else:
        assert smoke["failure_reason"]


def test_generator_refuses_frozen_row_destinations(tmp_path: Path) -> None:
    for relative in ("harness/work/05-max-pressure", "harness/work/10b-max-pressure-trip-kpis"):
        before = {path: path.read_bytes() for path in (ROOT / relative).rglob("*") if path.is_file()}
        with pytest.raises(ValueError):
            generate_graph_growth_artifacts(ROOT, ROOT / relative / "row10f-attempt")
        assert before == {path: path.read_bytes() for path in before}
