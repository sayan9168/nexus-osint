"""
NEXUS-OSINT: Semantic Correlation Engine
Uses sentence-transformers + Qdrant for cross-entity identity matching.
"""
import asyncio
from typing import Any, Optional

import numpy as np
import structlog
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

logger = structlog.get_logger(__name__)


class CorrelationEngine:
    """
    Finds hidden links between entities using semantic embeddings.
    E.g., links a Person to a Domain if their metadata is semantically similar.
    """

    COLLECTION = "nexus_correlations"
    VECTOR_SIZE = 384

    def __init__(self, qdrant_host: str = "qdrant", qdrant_port: int = 6333):
        self._client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self._model = None

    def _get_model(self):
        """Lazy-load sentence transformer model."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
        return self._model

    def _encode(self, text: str) -> list[float]:
        """Generate embedding for text."""
        model = self._get_model()
        embedding = model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def _entity_to_text(self, entity: dict[str, Any]) -> str:
        """Convert entity to a text representation for embedding."""
        parts = [
            f"type: {entity.get('label', 'unknown')}",
            f"value: {entity.get('value', '')}",
        ]
        metadata = entity.get("metadata", {})
        for k, v in metadata.items():
            parts.append(f"{k}: {v}")
        return " | ".join(parts)

    async def index_entity(self, entity: dict[str, Any]) -> str:
        """Index an entity's embedding for future correlation searches."""
        text = self._entity_to_text(entity)
        embedding = await asyncio.to_thread(self._encode, text)

        import hashlib
        point_id = hashlib.md5(
            f"{entity.get('label')}:{entity.get('value')}".encode()
        ).hexdigest()

        self._client.upsert(
            collection_name=self.COLLECTION,
            points=[
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload={
                        "entity_type": entity.get("label"),
                        "value": entity.get("value"),
                        "text_repr": text,
                    },
                )
            ],
        )
        return point_id

    async def find_correlations(
        self,
        entity: dict[str, Any],
        exclude_same_type: bool = True,
        threshold: float = 0.72,
        limit: int = 15,
    ) -> list[dict[str, Any]]:
        """
        Find semantically correlated entities across different types.
        Returns entities that are likely related but not obviously connected.
        """
        text = self._entity_to_text(entity)
        embedding = await asyncio.to_thread(self._encode, text)

        results = self._client.search(
            collection_name=self.COLLECTION,
            query_vector=embedding,
            limit=limit + 5,  # Extra to filter
            score_threshold=threshold,
        )

        correlations = []
        entity_type = entity.get("label", "")
        entity_value = entity.get("value", "")

        for r in results:
            r_type = r.payload.get("entity_type", "")
            r_value = r.payload.get("value", "")

            # Skip self
            if r_value == entity_value and r_type == entity_type:
                continue
            # Skip same type if requested
            if exclude_same_type and r_type == entity_type:
                continue

            correlations.append({
                "entity_type": r_type,
                "value": r_value,
                "similarity_score": round(r.score, 4),
                "correlation_type": self._classify_correlation(entity_type, r_type, r.score),
            })

        return sorted(correlations, key=lambda x: x["similarity_score"], reverse=True)[:limit]

    def _classify_correlation(
        self, source_type: str, target_type: str, score: float
    ) -> str:
        """Classify the type of correlation based on entity types and score."""
        if score > 0.90:
            strength = "strong"
        elif score > 0.80:
            strength = "moderate"
        else:
            strength = "weak"

        pair = f"{source_type}→{target_type}"
        return f"{strength}_{pair.lower()}_correlation"

    async def batch_index(self, entities: list[dict[str, Any]]) -> int:
        """Batch index multiple entities."""
        count = 0
        for entity in entities:
            try:
                await self.index_entity(entity)
                count += 1
            except Exception as e:
                logger.warning("correlation.index_error", error=str(e))
        return count
