"""
NEXUS-OSINT: Graph Management Endpoints
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from db.memgraph import get_memgraph
from db.schemas import GraphResponse, GraphNodeResponse, GraphEdgeResponse

router = APIRouter()


class CreateNodeRequest(BaseModel):
    label: str
    value: str
    properties: dict = {}


class CreateEdgeRequest(BaseModel):
    source_id: str
    target_id: str
    edge_type: str
    properties: dict = {}


class GraphQueryRequest(BaseModel):
    cypher: str
    parameters: dict = {}


@router.get("/full", response_model=GraphResponse)
async def get_full_graph(limit: int = Query(default=10000, le=100000)):
    """Retrieve the full graph for 3D visualization."""
    memgraph = await get_memgraph()
    data = await memgraph.get_full_graph(limit=limit)

    nodes = [
        GraphNodeResponse(
            id=n["id"],
            label=n["labels"][0] if n["labels"] else "Unknown",
            value=n["props"].get("value", ""),
            properties=n["props"],
        )
        for n in data["nodes"]
    ]
    edges = [
        GraphEdgeResponse(
            source=e["source"],
            target=e["target"],
            type=e["type"],
            properties=e.get("props", {}),
        )
        for e in data["edges"]
    ]

    return GraphResponse(
        nodes=nodes,
        edges=edges,
        total_nodes=len(nodes),
        total_edges=len(edges),
    )


@router.get("/neighbors")
async def get_neighbors(
    entity_value: str = Query(...),
    depth: int = Query(default=2, ge=1, le=5),
    limit: int = Query(default=100, le=1000),
):
    """Get all neighbors of an entity by value."""
    memgraph = await get_memgraph()

    # First find the node
    results = await memgraph.execute_query(
        "MATCH (n) WHERE n.value = $value RETURN elementId(n) AS id LIMIT 1",
        {"value": entity_value},
    )
    if not results:
        raise HTTPException(status_code=404, detail=f"Entity '{entity_value}' not found")

    node_id = results[0]["id"]
    neighbors = await memgraph.get_neighbors(node_id, depth=depth, limit=limit)
    return {"entity": entity_value, "depth": depth, "results": neighbors}


@router.post("/nodes")
async def create_node(req: CreateNodeRequest):
    """Create a new node in the graph."""
    memgraph = await get_memgraph()
    props = {"value": req.value, **req.properties}
    result = await memgraph.create_node(req.label, props)
    return result


@router.post("/edges")
async def create_edge(req: CreateEdgeRequest):
    """Create a new edge between two nodes."""
    memgraph = await get_memgraph()
    await memgraph.create_edge(req.source_id, req.target_id, req.edge_type, req.properties)
    return {"status": "created"}


@router.delete("/nodes/{node_id}")
async def delete_node(node_id: str):
    """Delete a node and all its relationships."""
    memgraph = await get_memgraph()
    await memgraph.execute_write(
        "MATCH (n) WHERE elementId(n) = $node_id DETACH DELETE n",
        {"node_id": node_id},
    )
    return {"status": "deleted", "node_id": node_id}


@router.post("/query")
async def execute_cypher(req: GraphQueryRequest):
    """Execute a raw Cypher query (read-only)."""
    memgraph = await get_memgraph()
    try:
        results = await memgraph.execute_query(req.cypher, req.parameters)
        return {"results": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/summary")
async def get_graph_summary():
    """Get a summary of the current graph state."""
    memgraph = await get_memgraph()

    node_counts = await memgraph.execute_query(
        "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY count DESC"
    )
    edge_counts = await memgraph.execute_query(
        "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY count DESC"
    )
    total = await memgraph.execute_query(
        "MATCH (n) RETURN count(n) AS nodes"
    )

    return {
        "total_nodes": total[0]["nodes"] if total else 0,
        "node_breakdown": node_counts,
        "edge_breakdown": edge_counts,
    }


@router.post("/correlate")
async def correlate_entities(entity_value: str, entity_type: str = "Domain"):
    """Find semantic correlations for an entity using vector search."""
    from db.qdrant_client import get_qdrant

    qdrant = await get_qdrant()

    # Generate a simple embedding (in production, use sentence-transformers)
    # For now, use a hash-based pseudo-embedding for demonstration
    import hashlib
    import struct

    text = f"{entity_type}:{entity_value}"
    hash_bytes = hashlib.sha256(text.encode()).digest()
    # Create a 384-dim vector from hash (simplified)
    embedding = [struct.unpack('f', hash_bytes[i:i+4])[0] for i in range(0, min(len(hash_bytes), 384*4), 4)]
    # Pad to 384
    embedding = (embedding * ((384 // len(embedding)) + 1))[:384]
    # Normalize
    import math
    norm = math.sqrt(sum(x*x for x in embedding)) or 1.0
    embedding = [x / norm for x in embedding]

    correlations = await qdrant.find_correlations(
        embedding=embedding,
        exclude_types=[entity_type],
        limit=15,
    )
    return {"entity": entity_value, "correlations": correlations}
