from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping
from xml.etree import ElementTree


class GraphIdentityError(ValueError):
    """The graph cannot be joined safely to its SUMO network."""


@dataclass(frozen=True)
class JunctionNode:
    signal_id: str
    incoming_lane_ids: tuple[str, ...]
    outgoing_lane_ids: tuple[str, ...]
    legal_phase_ids: tuple[str, ...]
    executor_owner: str = "A1"


@dataclass(frozen=True)
class GraphEdge:
    edge_id: str
    from_signal_id: str
    to_signal_id: str
    connecting_lane_ids: tuple[str, ...]
    storage_capacity_vehicles: float
    free_flow_seconds: float


@dataclass(frozen=True)
class JunctionGraph:
    schema_version: int
    network_sha256: str
    graph_hash: str
    nodes: tuple[JunctionNode, ...]
    edges: tuple[GraphEdge, ...]
    adjacency: Mapping[str, tuple[str, ...]]

    def __post_init__(self) -> None:
        node_ids = tuple(node.signal_id for node in self.nodes)
        if len(node_ids) != 4 or len(set(node_ids)) != 4:
            raise GraphIdentityError("graph benchmark requires exactly four unique signals")
        if any(node.executor_owner != "A1" for node in self.nodes):
            raise GraphIdentityError("A1 must own every signal executor")
        known = set(node_ids)
        edge_ids = [edge.edge_id for edge in self.edges]
        if len(edge_ids) != len(set(edge_ids)):
            raise GraphIdentityError("graph edge ids must be unique")
        if any(edge.from_signal_id not in known or edge.to_signal_id not in known for edge in self.edges):
            raise GraphIdentityError("graph edge references an unknown signal")
        adjacency = {key: tuple(value) for key, value in self.adjacency.items()}
        if set(adjacency) != known or any(not set(values) <= known for values in adjacency.values()):
            raise GraphIdentityError("adjacency references an unknown signal")
        object.__setattr__(self, "adjacency", MappingProxyType(adjacency))

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": self.schema_version,
            "network_sha256": self.network_sha256,
            "graph_hash": self.graph_hash,
            "nodes": [asdict(node) for node in self.nodes],
            "edges": [asdict(edge) for edge in self.edges],
            "adjacency": {key: list(value) for key, value in self.adjacency.items()},
        }


@dataclass(frozen=True)
class NeighbourObservation:
    from_signal_id: str
    to_signal_id: str
    movement_group: str
    observed_at: float
    expires_at: float
    queue_vehicles: float
    occupancy_ratio: float
    predicted_discharge_vehicles: float
    source: str = "observation_adapter"

    def __post_init__(self) -> None:
        values = (
            self.observed_at, self.expires_at, self.queue_vehicles,
            self.occupancy_ratio, self.predicted_discharge_vehicles,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("neighbour values must be finite")
        if self.movement_group not in {"NS", "EW"}:
            raise ValueError("movement_group must be NS or EW")
        if self.observed_at < 0 or self.expires_at < self.observed_at:
            raise ValueError("invalid neighbour freshness interval")
        if self.queue_vehicles < 0 or not 0 <= self.occupancy_ratio <= 1:
            raise ValueError("invalid neighbour queue or occupancy")


def _sha256(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def _canonical_hash(value: object) -> str:
    return _sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def load_junction_graph(network_file: Path, *, expected_graph_hash: str | None = None) -> JunctionGraph:
    """Parse the four-signal benchmark without NetworkX or a mutable graph."""
    network_file = Path(network_file)
    network_bytes = network_file.read_bytes()
    root = ElementTree.fromstring(network_bytes)
    signals = tuple(sorted(
        junction.attrib["id"]
        for junction in root.findall("junction")
        if junction.attrib.get("type") == "traffic_light"
    ))
    if len(signals) != 4:
        raise GraphIdentityError(f"expected four traffic-light junctions, found {signals}")

    lanes_by_edge: dict[str, tuple[str, ...]] = {}
    edge_ends: dict[str, tuple[str, str]] = {}
    lane_metrics: dict[str, tuple[float, float]] = {}
    for edge in root.findall("edge"):
        edge_id = edge.attrib.get("id", "")
        if edge.attrib.get("function") or not edge_id:
            continue
        lane_ids: list[str] = []
        for lane in edge.findall("lane"):
            lane_id = lane.attrib["id"]
            length = float(lane.attrib["length"])
            speed = float(lane.attrib["speed"])
            if length <= 0 or speed <= 0:
                raise GraphIdentityError(f"invalid lane geometry: {lane_id}")
            lane_ids.append(lane_id)
            lane_metrics[lane_id] = (length, speed)
        lanes_by_edge[edge_id] = tuple(sorted(lane_ids))
        edge_ends[edge_id] = (edge.attrib["from"], edge.attrib["to"])

    nodes: list[JunctionNode] = []
    for signal_id in signals:
        incoming = sorted(
            lane for edge_id, (_, target) in edge_ends.items() if target == signal_id
            for lane in lanes_by_edge[edge_id]
        )
        outgoing = sorted(
            lane for edge_id, (source, _) in edge_ends.items() if source == signal_id
            for lane in lanes_by_edge[edge_id]
        )
        if len(incoming) != 4 or len(outgoing) != 4:
            raise GraphIdentityError(f"{signal_id} must have four incoming and outgoing lanes")
        nodes.append(JunctionNode(
            signal_id=signal_id,
            incoming_lane_ids=tuple(incoming),
            outgoing_lane_ids=tuple(outgoing),
            legal_phase_ids=(
                "NS_GREEN", "NS_YELLOW", "ALL_RED_TO_EW",
                "EW_GREEN", "EW_YELLOW", "ALL_RED_TO_NS",
            ),
        ))

    edges: list[GraphEdge] = []
    for edge_id, (source, target) in sorted(edge_ends.items()):
        if source not in signals or target not in signals:
            continue
        lane_ids = lanes_by_edge[edge_id]
        capacity = sum(lane_metrics[lane][0] / 7.5 for lane in lane_ids)
        free_flow = max(lane_metrics[lane][0] / lane_metrics[lane][1] for lane in lane_ids)
        edges.append(GraphEdge(
            edge_id=edge_id,
            from_signal_id=source,
            to_signal_id=target,
            connecting_lane_ids=lane_ids,
            storage_capacity_vehicles=round(capacity, 6),
            free_flow_seconds=round(free_flow, 6),
        ))
    adjacency = {
        signal: tuple(sorted(edge.to_signal_id for edge in edges if edge.from_signal_id == signal))
        for signal in signals
    }
    if any(len(neighbours) != 2 for neighbours in adjacency.values()):
        raise GraphIdentityError("each 2x2 signal must have two directed one-hop neighbours")

    network_sha = _sha256(network_bytes)
    canonical = {
        "schema_version": 1,
        "network_sha256": network_sha,
        "nodes": [asdict(node) for node in nodes],
        "edges": [asdict(edge) for edge in edges],
        "adjacency": {key: list(value) for key, value in adjacency.items()},
    }
    graph_hash = _canonical_hash(canonical)
    if expected_graph_hash is not None and expected_graph_hash != graph_hash:
        raise GraphIdentityError("graph hash does not match the expected immutable identity")
    return JunctionGraph(1, network_sha, graph_hash, tuple(nodes), tuple(edges), adjacency)
