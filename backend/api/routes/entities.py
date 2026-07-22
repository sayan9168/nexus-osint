"""
NEXUS-OSINT: Entity CRUD Endpoints
"""
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from db.memgraph import get_memgraph
from db.schemas import NodeLabel

router = APIRouter()


class EntityCreate(BaseModel):
    label: NodeLabel
    value: str
    properties: dict = {}


class EntityUpdate(BaseModel):
    properties: dict = {}


class EntitySearch(BaseModel):
    query: str
    label: Optional[NodeLabel] = None
    limit: int = 50


@router.get("/")
async def list_entities(
    label: Optional[str] = Query(None),
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0),
):
    """List all entities, optionally filtered by label."""
    memgraph = await get_memgraph()

    if label:
        query = f"""
        MATCH (n:{label})
        RETURN elementId(n) AS id, labels(n) AS labels, properties(n) AS props
        ORDER BY n.created_at DESC
        SKIP $offset LIMIT $limit
        """
    else:
        query = """
        MATCH (n)
        RETURN elementId(n) AS id, labels(n) AS labels, properties(n) AS props
        ORDER BY n.created_at DESC
        SKIP $offset LIMIT $limit
        """

    results = await memgraph.execute_query(query, {"offset": offset, "limit": limit})
    return {"entities": results, "count": len(results)}


@router.get("/{entity_id}")
async def get_entity(entity_id: str):
    """Get a single entity by ID."""
    memgraph = await get_memgraph()
    node = await memgraph.get_node_by_id(entity_id)
    if not node:
        raise HTTPException(status_code=404, detail="Entity not found")
    return {"entity": node}


@router.post("/", status_code=201)
async def create_entity(req: EntityCreate):
    """Create a new entity."""
    memgraph = await get_memgraph()
    props = {"value": req.value, **req.properties}
    result = await memgraph.create_node(req.label.value, props)
    return result


@router.put("/{entity_id}")
async def update_entity(entity_id: str, req: EntityUpdate):
    """Update entity properties."""
    memgraph = await get_memgraph()
    await memgraph.execute_write(
        "MATCH (n) WHERE elementId(n) = $id SET n += $props",
        {"id": entity_id, "props": req.properties},
    )
    return {"status": "updated", "id": entity_id}


@router.delete("/{entity_id}")
async def delete_entity(entity_id: str):
    """Delete an entity and all its relationships."""
    memgraph = await get_memgraph()
    await memgraph.execute_write(
        "MATCH (n) WHERE elementId(n) = $id DETACH DELETE n",
        {"id": entity_id},
    )
    return {"status": "deleted", "id": entity_id}


@router.post("/search")
async def search_entities(req: EntitySearch):
    """Full-text search across entity values."""
    memgraph = await get_memgraph()

    if req.label:
        query = f"""
        MATCH (n:{req.label.value})
        WHERE n.value CONTAINS $query OR n.value =~ $regex
        RETURN elementId(n) AS id, labels(n) AS labels, properties(n) AS props
        LIMIT $limit
        """
    else:
        query = """
        MATCH (n)
        WHERE n.value CONTAINS $query OR n.value =~ $regex
        RETURN elementId(n) AS id, labels(n) AS labels, properties(n) AS props
        LIMIT $limit
        """

    results = await memgraph.execute_query(
        query,
        {"query": req.query, "regex": f"(?i).*{req.query}.*", "limit": req.limit},
    )
    return {"results": results, "count": len(results)}
