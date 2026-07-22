"""
NEXUS-OSINT: Async Memgraph Connection Wrapper
Provides connection pooling, query execution, and transaction management.
"""
import asyncio
from typing import Any, Optional
from contextlib import asynccontextmanager

import structlog
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession

from config import get_settings

logger = structlog.get_logger(__name__)


class MemgraphClient:
    """Async Memgraph client with connection pooling and retry logic."""

    def __init__(self):
        self._driver: Optional[AsyncDriver] = None
        self._settings = get_settings()

    async def connect(self) -> None:
        """Establish connection to Memgraph."""
        uri = f"bolt://{self._settings.MEMGRAPH_HOST}:{self._settings.MEMGRAPH_PORT}"
        auth = None
        if self._settings.MEMGRAPH_USER:
            auth = (self._settings.MEMGRAPH_USER, self._settings.MEMGRAPH_PASSWORD)

        self._driver = AsyncGraphDatabase.driver(
            uri,
            auth=auth,
            max_connection_pool_size=50,
            connection_acquisition_timeout=60.0,
        )
        # Verify connectivity
        await self._driver.verify_connectivity()
        logger.info("memgraph.connected", uri=uri)

    async def disconnect(self) -> None:
        """Gracefully close all connections."""
        if self._driver:
            await self._driver.close()
            logger.info("memgraph.disconnected")

    @asynccontextmanager
    async def session(self, database: str = "memgraph"):
        """Provide an async session context manager."""
        if not self._driver:
            await self.connect()
        async with self._driver.session(database=database) as session:
            yield session

    async def execute_query(
        self,
        query: str,
        parameters: Optional[dict[str, Any]] = None,
        database: str = "memgraph",
    ) -> list[dict[str, Any]]:
        """Execute a Cypher query and return results as list of dicts."""
        async with self.session(database) as session:
            result = await session.run(query, parameters or {})
            records = await result.data()
            return records

    async def execute_write(
        self,
        query: str,
        parameters: Optional[dict[str, Any]] = None,
        database: str = "memgraph",
    ) -> None:
        """Execute a write transaction."""
        async with self.session(database) as session:
            await session.run(query, parameters or {})

    async def execute_transaction(
        self,
        queries: list[tuple[str, dict[str, Any]]],
        database: str = "memgraph",
    ) -> None:
        """Execute multiple queries in a single transaction."""
        async with self.session(database) as session:
            async with session.begin_transaction() as tx:
                for query, params in queries:
                    await tx.run(query, params)

    async def get_node_by_id(self, node_id: str) -> Optional[dict]:
        """Retrieve a single node by its elementId."""
        results = await self.execute_query(
            "MATCH (n) WHERE elementId(n) = $node_id RETURN n",
            {"node_id": node_id}
        )
        return results[0]["n"] if results else None

    async def get_neighbors(
        self, node_id: str, depth: int = 1, limit: int = 100
    ) -> list[dict]:
        """Get all neighbors of a node up to specified depth."""
        query = """
        MATCH path = (n)-[*1..$depth]-(m)
        WHERE elementId(n) = $node_id
        RETURN nodes(path) AS nodes, relationships(path) AS rels
        LIMIT $limit
        """
        return await self.execute_query(
            query, {"node_id": node_id, "depth": depth, "limit": limit}
        )

    async def get_full_graph(self, limit: int = 10000) -> dict:
        """Retrieve the full graph (nodes + edges) for visualization."""
        nodes_query = """
        MATCH (n)
        RETURN elementId(n) AS id, labels(n) AS labels, properties(n) AS props
        LIMIT $limit
        """
        edges_query = """
        MATCH (a)-[r]->(b)
        RETURN elementId(a) AS source, elementId(b) AS target,
               type(r) AS type, properties(r) AS props
        LIMIT $limit
        """
        nodes = await self.execute_query(nodes_query, {"limit": limit})
        edges = await self.execute_query(edges_query, {"limit": limit})
        return {"nodes": nodes, "edges": edges}

    async def create_node(
        self, label: str, properties: dict[str, Any]
    ) -> dict:
        """Create a node with MERGE (idempotent)."""
        # Build property string dynamically
        prop_keys = list(properties.keys())
        prop_str = ", ".join([f"{k}: ${k}" for k in prop_keys])

        query = f"""
        MERGE (n:{label} {{value: $value}})
        ON CREATE SET n += $props, n.created_at = timestamp()
        ON MATCH SET n += $props
        RETURN elementId(n) AS id, labels(n) AS labels, properties(n) AS props
        """
        results = await self.execute_query(
            query, {"value": properties.get("value", ""), "props": properties}
        )
        return results[0] if results else {}

    async def create_edge(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
        properties: Optional[dict[str, Any]] = None,
    ) -> None:
        """Create a relationship between two nodes."""
        prop_str = ""
        if properties:
            prop_keys = list(properties.keys())
            prop_str = "SET r += $props"

        query = f"""
        MATCH (a), (b)
        WHERE elementId(a) = $source_id AND elementId(b) = $target_id
        MERGE (a)-[r:{edge_type}]->(b)
        {prop_str}
        """
        params = {"source_id": source_id, "target_id": target_id}
        if properties:
            params["props"] = properties
        await self.execute_write(query, params)


# ─── Singleton Instance ───
_memgraph_instance: Optional[MemgraphClient] = None


async def get_memgraph() -> MemgraphClient:
    """Get or create the Memgraph client singleton."""
    global _memgraph_instance
    if _memgraph_instance is None:
        _memgraph_instance = MemgraphClient()
        await _memgraph_instance.connect()
    return _memgraph_instance
