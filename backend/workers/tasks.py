"""
NEXUS-OSINT: Celery Task Definitions
Async transform execution via task queue.
"""
import asyncio
from typing import Any, Optional

from celery import shared_task
import structlog

logger = structlog.get_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def execute_transform_task(
    self,
    transform_name: str,
    entity_value: str,
    parameters: Optional[dict[str, Any]] = None,
) -> dict:
    """
    Execute an OSINT transform asynchronously via Celery.
    Results are written directly to Memgraph.
    """
    from transforms.registry import TransformRegistry

    logger.info(
        "celery.transform_started",
        task_id=self.request.id,
        transform=transform_name,
        entity=entity_value,
    )

    transform = TransformRegistry.get(transform_name)
    if not transform:
        return {"status": "error", "message": f"Transform '{transform_name}' not found"}

    try:
        # Run async transform in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(transform.run(entity_value, parameters))
        loop.close()

        logger.info(
            "celery.transform_completed",
            task_id=self.request.id,
            transform=transform_name,
            new_nodes=len(result.new_nodes),
            new_edges=len(result.new_edges),
        )

        # Broadcast via WebSocket (fire-and-forget)
        _broadcast_transform_result(result.model_dump())

        return result.model_dump()

    except Exception as exc:
        logger.error("celery.transform_failed", error=str(exc))
        raise self.retry(exc=exc)


def _broadcast_transform_result(result: dict) -> None:
    """Send transform result to WebSocket clients (best-effort)."""
    try:
        import redis as redis_lib
        from config import get_settings
        settings = get_settings()
        r = redis_lib.from_url(settings.REDIS_URL)
        r.publish("nexus:ws:broadcast", json.dumps({
            "type": "transform_completed",
            "data": result,
        }))
    except Exception:
        pass  # Non-critical


import json
