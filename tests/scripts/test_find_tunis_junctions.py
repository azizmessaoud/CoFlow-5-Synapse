import json

from scripts import find_tunis_junctions


def test_junction_selection_is_deterministic(monkeypatch, tmp_path) -> None:
    class Handler:
        def __init__(self, _bbox):
            self.node_to_ways = {
                20: {1, 2, 3},
                10: {4, 5, 6},
                30: {7, 8, 9},
                40: {10, 11, 12},
                50: {13, 14, 15},
                60: {16, 17, 18},
                70: {19, 20, 21},
            }
            self.node_tags = {20: {"highway": "traffic_signals"}}
            self.node_locations = {
                node_id: (10.18, 36.8) for node_id in self.node_to_ways
            }
            self.way_tags = {}
            self.way_highway = {
                way: "secondary"
                for ways in self.node_to_ways.values()
                for way in ways
            }

        def apply_file(self, *_args, **_kwargs):
            return None

    monkeypatch.setattr(find_tunis_junctions, "JunctionFinder", Handler)
    output = tmp_path / "junctions.json"
    result = find_tunis_junctions.find_junctions(
        tmp_path / "tunis.osm.pbf", output, (10.17, 36.79, 10.19, 36.805)
    )

    assert result["junction_count"] == 6
    assert result["junctions"][0]["node_id"] == 20
    assert [item["node_id"] for item in result["junctions"]] == [20, 10, 30, 40, 50, 60]
    assert json.loads(output.read_text(encoding="utf-8")) == result
