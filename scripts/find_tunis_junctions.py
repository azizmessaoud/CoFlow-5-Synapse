from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

try:
    import osmium
except ImportError:  # pragma: no cover - environment dependent
    osmium = None

MAJOR_HIGHWAY_CLASSES = {
    "motorway",
    "trunk",
    "primary",
    "secondary",
    "tertiary",
    "unclassified",
    "residential",
    "living_street",
    "motorway_link",
    "trunk_link",
    "primary_link",
    "secondary_link",
    "tertiary_link",
}
MAJOR_ROADS = {"primary", "secondary", "tertiary"}


class JunctionFinder(osmium.SimpleHandler if osmium else object):  # type: ignore[misc]
    def __init__(self, bbox: tuple[float, ...]) -> None:
        if osmium is None:
            raise RuntimeError(
                "pyosmium is required; install it with "
                "`py -3.11 -m pip install osmium`."
            )
        super().__init__()
        self.node_to_ways: dict[int, set[int]] = defaultdict(set)
        self.way_highway: dict[int, str] = {}
        self.node_tags: dict[int, dict[str, str]] = {}
        self.way_tags: dict[int, dict[str, str]] = {}
        self.bbox = bbox

    def _in_bbox(self, lon: float, lat: float) -> bool:
        left, bottom, right, top = self.bbox
        return left <= lon <= right and bottom <= lat <= top

    def way(self, way: Any) -> None:
        highway = way.tags.get("highway")
        if highway not in MAJOR_HIGHWAY_CLASSES:
            return
        self.way_highway[way.id] = highway
        self.way_tags[way.id] = {tag.k: tag.v for tag in way.tags}
        for node in way.nodes:
            if node.location.valid() and self._in_bbox(node.lon, node.lat):
                self.node_to_ways[node.ref].add(way.id)

    def node(self, node: Any) -> None:
        if node.location.valid() and self._in_bbox(node.lon, node.lat) and node.tags:
            self.node_tags[node.id] = {tag.k: tag.v for tag in node.tags}


def _score(finder: JunctionFinder, node_id: int, way_ids: set[int]) -> tuple[int, list[str]]:
    tags = finder.node_tags.get(node_id, {})
    way_tags = [finder.way_tags.get(way_id, {}) for way_id in way_ids]
    score = 0
    reasons: list[str] = []
    if tags.get("highway") == "traffic_signals":
        score += 100
        reasons.append("traffic_signals")
    if tags.get("highway") == "stop":
        score += 40
        reasons.append("stop")
    if tags.get("highway") == "give_way":
        score += 30
        reasons.append("give_way")
    if tags.get("junction") == "roundabout":
        score += 80
        reasons.append("roundabout_node")
    if any(item.get("junction") == "roundabout" for item in way_tags):
        score += 60
        reasons.append("roundabout_way")
    if tags.get("name"):
        score += 20
        reasons.append("named")
    score += 15 if len(way_ids) >= 4 else 5
    reasons.append(f"degree={len(way_ids)}")
    if any(finder.way_highway.get(way_id) in MAJOR_ROADS for way_id in way_ids):
        score += 10
        reasons.append("major_road")
    return score, reasons


def find_junctions(pbf_path: Path, output_path: Path, bbox: tuple[float, ...]) -> dict[str, object]:
    if len(bbox) != 4:
        raise ValueError("bbox must be left,bottom,right,top")
    finder = JunctionFinder(bbox)
    finder.apply_file(str(pbf_path), locations=True)
    candidates: list[dict[str, object]] = []
    for node_id, way_ids in finder.node_to_ways.items():
        if len(way_ids) < 3:
            continue
        score, reasons = _score(finder, node_id, way_ids)
        tags = finder.node_tags.get(node_id, {})
        candidates.append(
            {
                "node_id": node_id,
                "degree": len(way_ids),
                "score": score,
                "reasons": reasons,
                "tags": tags,
                "way_ids": sorted(way_ids),
                "way_highways": [
                    finder.way_highway.get(way_id) for way_id in sorted(way_ids)
                ],
            }
        )
    candidates.sort(key=lambda item: (-int(item["score"]), int(item["node_id"])))
    selected = candidates[:6]
    if len(selected) != 6:
        raise ValueError(f"expected six junctions, found {len(selected)}")
    result = {
        "aoi": {
            "name": "Tunis centre-ville central corridor",
            "bbox": list(bbox),
            "pbf": str(pbf_path),
            "selection_rule": (
                "degree >= 3, ranked by traffic_signals > roundabout > "
                "stop/give_way > named > degree > major_road, then node_id"
            ),
        },
        "junction_count": len(selected),
        "junctions": selected,
        "all_candidate_count": len(candidates),
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pbf", type=Path, required=True)
    parser.add_argument("--bbox", required=True, help="left,bottom,right,top")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    bbox = tuple(float(value) for value in args.bbox.split(","))
    print(json.dumps(find_junctions(args.pbf, args.output, bbox), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
