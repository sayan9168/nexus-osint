"""
NEXUS-OSINT: Qdrant Vector Database Service
Handles semantic embeddings for entity correlation and identity matching.
"""
import hashlib
from typing import Any, Optional

import structlog
from qdrant_client import QdrantClient as QdrantAsyncClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    Filter, FieldCondition, MatchValue, SearchRequest
)

from config import get_settings

logger = structlog.get_logger(__name__)


class QdrantService:
    """Vector database service for semantic entity matching."""

    COLLECTION_NAME = "nexus_entities"
    VECTOR_SIZE = 384  # sentence-transformers/all-MiniLM-L6-v2

    def __init__(self):
        self._settings = get_settings()
        self._client: Optional[QdrantAsyncClient] = None

    async def connect(self) -> None:
        """Initialize Qdrant connection."""
        self._client = QdrantAsyncClient(
            host=self._settings.QDRANT_HOST,
            port=self._settings.QDRANT_PORT,
            prefer_grpc=True,
        )
        await self._ensure_collection()
        logger.info("qdrant.connected")

    async def _ensure_collection(self) -> None:
        """Create collection if it doesn't exist."""
        collections = await self._client.get_collections()
        existing = [c.name for c in collections.collections]

        if self.COLLECTION_NAME not in existing:
            await self._client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=self.VECTOR_SIZE,
                    distance=Distance.COSINE,
                ),
            )
            logger.info("qdrant.collection_created", name=self.COLLECTION_NAME)

    def _generate_point_id(self, entity_type: str, value: str) -> str:
        """Generate deterministic UUID from entity type + value."""
        raw = f"{entity_type}:{value}"
        return hashlib.md5(raw.encode()).hexdigest()

    async def upsert_entity(
        self,
        entity_type: str,
        value: str,
        embedding: list[float],
        metadata: Optional[dict[str, Any]] = None,
    ) -> str:
        """Insert or update an entity embedding."""
        point_id = self._generate_point_id(entity_type, value)

        await self._client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "entity_type": entity_type,
                        "value": value,
                        **(metadata or {}),
                    },
                )
            ],
        )
        return point_id

    async def search_similar(
        self,
        embedding: list[float],
        entity_type: Optional[str] = None,
        limit: int = 10,
        score_threshold: float = 0.75,
    ) -> list[dict[str, Any]]:
        """Search for semantically similar entities."""
        query_filter = None
        if entity_type:
            query_filter = Filter(
                must=[
                    FieldCondition(
                        key="entity_type",
                        match=MatchValue(value=entity_type),
                    )
                ]
            )

        results = await self._client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=embedding,
            query_filter=query_filter,
            limit=limit,
            score_threshold=score_threshold,
        )

        return [
            {
                "id": str(r.id),
                "score": r.score,
                "entity_type": r.payload.get("entity_type"),
                "value": r.payload.get("value"),
                "metadata": r.payload,
            }
            for r in results
        ]

    async def find_correlations(
        self,
        embedding: list[float],
        exclude_types: Optional[list[str]] = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Find cross-entity-type correlations using vector similarity."""
        results = await self._client.search(
            collection_name=self.COLLECTION_NAME,
            query_vector=embedding,
            limit=limit,
            score_threshold=0.70,
        )

        correlations = []
        for r in results:
            etype = r.payload.get("entity_type", "")
            if exclude_types and etype in exclude_types:
                continue
            correlations.append({
                "id": str(r.id),
                "score": r.score,
                "entity_type": etype,
                "value": r.payload.get("value"),
                "correlation_strength": round(r.score, 4),
            })

        return sorted(correlations, key=lambda x: x["score"], reverse=True)

    async def delete_entity(self, entity_type: str, value: str) -> None:
        """Remove an entity from the vector store."""
        point_id = self._generate_point_id(entity_type, value)
        await self._client.delete(
            collection_name=self.COLLECTION_NAME,
            points_selector=[point_id],
        )


# ─── Singleton ───
_qdrant_instance: Optional[QdrantService] = None


async def get_qdrant() -> QdrantService:
    global _qdrant_instance
    if _qdrant_instance is None:
        _qdrant_instance = QdrantService()
        await _qdrant_instance.connect()
    return _qdrant_instance
