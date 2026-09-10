"""Deterministic investigation graph projection from stored evidence."""
from __future__ import annotations

from pydantic import BaseModel, Field

from .cases import Case


class GraphNode(BaseModel):
    id: str
    label: str
    kind: str


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    confidence: float = Field(ge=0.0, le=1.0)
    provenance_hash: str | None = None


class GraphProjection(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


def project(case: Case) -> GraphProjection:
    nodes: dict[str, GraphNode] = {}
    edges: list[GraphEdge] = []

    def node(identifier: str, label: str, kind: str) -> None:
        nodes.setdefault(identifier, GraphNode(id=identifier, label=label, kind=kind))

    for target in case.targets:
        node("target:" + target, target, "target")

    for ev in case.evidence:
        source_id = "source:" + ev.source
        target_id = "target:" + ev.target
        node(source_id, ev.source, "source")
        node(target_id, ev.target, "target")
        edges.append(GraphEdge(source=source_id, target=target_id, relation="observed",
                               confidence=ev.confidence, provenance_hash=ev.provenance_hash))

    return GraphProjection(nodes=list(nodes.values()), edges=edges)
