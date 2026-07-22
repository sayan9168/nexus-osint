"""
NEXUS-OSINT: Abstract Base Transform
Provides execution logging, rate-limiting, error handling, and auto-persistence.
"""
import asyncio
import time
from abc import ABC, abstractmethod
from typing import Any, Optional
from functools import wraps

import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from db.memgraph import get_memgraph
from db.schemas import (
    BaseNode, EdgeSchema, EdgeType, NodeLabel,
    TransformResult, GraphNodeResponse
)

logger = structlog.get_logger(__name__)


class RateLimiter:
    """Token-bucket rate limiter for API calls."""

    def __init__(self, max_calls: int = 10, period_seconds: float = 60.0):
        self.max_calls = max_calls
        self.period = period_seconds
        self._calls: list[float] = []
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self._lock:
            now = time.monotonic()
            # Remove expired entries
            self._calls = [t for t in self._calls if now - t < self.period]
            if len(self._calls) >= self.max_calls:
                wait_time = self.period - (now - self._calls[0])
                logger.warning("rate_limiter.waiting", wait_seconds=wait_time)
                await asyncio.sleep(wait_time)
            self._calls.append(time.monotonic())


class BaseTransform(ABC):
    """
    Abstract base class for all OSINT transforms.
    Subclasses must implement `execute()` and define `name`, `input_type`, `output_types`.
    """

    name: str = "base_transform"
    description: str = "Base transform"
    input_type: NodeLabel = NodeLabel.DOMAIN
    output_types: list[NodeLabel] = []
    rate_limit: RateLimiter = RateLimiter(max_calls=10, period_seconds=60.0)

    def __init__(self):
        self._log = logger.bind(transform=self.name)

    @abstractmethod
    async def execute(
        self, entity_value: str, parameters: Optional[dict[str, Any]] = None
    ) -> TransformResult:
        """
        Core transform logic. Must be implemented by subclasses.
        Returns discovered nodes and edges.
        """
        ...

    async def run(
        self, entity_value: str, parameters: Optional[dict[str, Any]] = None
    ) -> TransformResult:
        """
        Public entry point with rate-limiting, logging, error handling,
        and automatic persistence to Memgraph.
        """
        start_time = time.perf_counter()
        self._log.info("transform.started", entity=entity_value)

        try:
            # Rate limiting
            await self.rate_limit.acquire()

            # Execute with retry
            result = await self._execute_with_retry(entity_value, parameters)

            # Persist discovered entities to graph DB
            if result.new_nodes or result.new_edges:
                await self._persist_to_graph(result)

            elapsed = (time.perf_counter() - start_time) * 1000
            result.execution_time_ms = elapsed
            result.status = "success"

            self._log.info(
                "transform.completed",
                entity=entity_value,
                new_nodes=len(result.new_nodes),
                new_edges=len(result.new_edges),
                elapsed_ms=round(elapsed, 2),
            )
            return result

        except Exception as exc:
            elapsed = (time.perf_counter() - start_time) * 1000
            self._log.error(
                "transform.failed",
                entity=entity_value,
                error=str(exc),
                elapsed_ms=round(elapsed, 2),
            )
            return TransformResult(
                transform_name=self.name,
                status="error",
                error_message=str(exc),
                execution_time_ms=elapsed,
            )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
    )
    async def _execute_with_retry(
        self, entity_value: str, parameters: Optional[dict[str, Any]] = None
    ) -> TransformResult:
        """Execute with exponential backoff retry."""
        return await self.execute(entity_value, parameters)

    async def _persist_to_graph(self, result: TransformResult) -> None:
        """Write discovered nodes and edges to Memgraph."""
        memgraph = await get_memgraph()

        # Create nodes
        node_id_map: dict[str, str] = {}
        for node_data in result.new_nodes:
            label = node_data.get("label", "Domain")
            value = node_data.get("value", "")
            props = {k: v for k, v in node_data.items() if k not in ("label",)}

            created = await memgraph.create_node(label, props)
            if created:
                node_id_map[value] = created.get("id", "")

        # Create edges
        for edge_data in result.new_edges:
            source_val = edge_data.get("source_value", "")
            target_val = edge_data.get("target_value", "")
            edge_type = edge_data.get("edge_type", "LINKED_TO")
            props = edge_data.get("properties", {})

            source_id = node_id_map.get(source_val, "")
            target_id = node_id_map.get(target_val, "")

            if source_id and target_id:
                await memgraph.create_edge(source_id, target_id, edge_type, props)

        self._log.info(
            "transform.persisted",
            nodes=len(result.new_nodes),
            edges=len(result.new_edges),
        )

    def __repr__(self) -> str:
        return f"<Transform: {self.name} ({self.input_type.value} → {[t.value for t in self.output_types]})>"
