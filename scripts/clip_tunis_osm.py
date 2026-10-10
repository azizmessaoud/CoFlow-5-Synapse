"""Clip a PBF to the Tunis showcase AOI for SUMO import.

This helper runs in WSL because the local Windows pyosmium DLL is blocked by
application-control policy.
"""

from __future__ import annotations

import argparse
import html
from pathlib import Path
from typing import Any

import osmium


class CollectWays(osmium.SimpleHandler):
    def __init__(self, bbox: tuple[float, float, float, float]) -> None:
        super().__init__()
        self.left, self.bottom, self.right, self.top = bbox
        self.ways: list[tuple[int, list[int], dict[str, str]]] = []
        self.node_ids: set[int] = set()

    def way(self, way: Any) -> None:
        if way.tags.get("highway") not in {
            "motorway", "trunk", "primary", "secondary", "tertiary",
            "unclassified", "residential", "living_street",
        }:
            return
        refs = [node.ref for node in way.nodes]
        inside = any(
            node.location.valid()
            and self.left <= node.lon <= self.right
            and self.bottom <= node.lat <= self.top
            for node in way.nodes
        )
        if inside:
            self.ways.append((way.id, refs, {tag.k: tag.v for tag in way.tags}))
            self.node_ids.update(refs)


class CollectNodes(osmium.SimpleHandler):
    def __init__(self, node_ids: set[int]) -> None:
        super().__init__()
        self.node_ids = node_ids
        self.nodes: dict[int, tuple[float, float, dict[str, str]]] = {}

    def node(self, node: Any) -> None:
        if node.id in self.node_ids and node.location.valid():
            self.nodes[node.id] = (
                node.lon,
                node.lat,
                {tag.k: tag.v for tag in node.tags},
            )


def write_xml(
    output: Path,
    bbox: tuple[float, float, float, float],
    ways: list[tuple[int, list[int], dict[str, str]]],
    nodes: dict[int, tuple[float, float, dict[str, str]]],
) -> None:
    esc = html.escape
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        stream.write('<osm version="0.6" generator="coflow5-tunis-import">\n')
        stream.write(
            f'  <bounds minlat="{bbox[1]}" minlon="{bbox[0]}" '
            f'maxlat="{bbox[3]}" maxlon="{bbox[2]}"/>\n'
        )
        for node_id in sorted(nodes):
            lon, lat, tags = nodes[node_id]
            stream.write(f'  <node id="{node_id}" lat="{lat}" lon="{lon}">\n')
            for key, value in sorted(tags.items()):
                stream.write(f'    <tag k="{esc(key)}" v="{esc(value)}"/>\n')
            stream.write("  </node>\n")
        for way_id, refs, tags in sorted(ways):
            stream.write(f'  <way id="{way_id}">\n')
            for ref in refs:
                stream.write(f'    <nd ref="{ref}"/>\n')
            for key, value in sorted(tags.items()):
                stream.write(f'    <tag k="{esc(key)}" v="{esc(value)}"/>\n')
            stream.write("  </way>\n")
        stream.write("</osm>\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--bbox", nargs=4, type=float, required=True)
    args = parser.parse_args()
    bbox = tuple(args.bbox)
    ways = CollectWays(bbox)
    ways.apply_file(str(args.input), locations=True)
    nodes = CollectNodes(ways.node_ids)
    nodes.apply_file(str(args.input), locations=True)
    write_xml(args.output, bbox, ways.ways, nodes.nodes)
    print(f"ways={len(ways.ways)} nodes={len(nodes.nodes)} output={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
