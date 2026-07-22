"""
NEXUS-OSINT: Transform Execution Endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, Optional

from transforms.registry import TransformRegistry
from db.schemas import TransformRequest, TransformResult
from workers.tasks import execute_transform_task

router = APIRouter()


class TransformExecuteRequest(BaseModel):
    transform_name: str
    entity_type: str
    entity_value: str
    parameters: dict[str, Any] = {}
    async_execution: bool = False


@router.get("/")
async def list_transforms():
    """List all available transforms."""
    return {"transforms": TransformRegistry.list_all()}


@router.post("/execute")
async def execute_transform(req: TransformExecuteRequest):
    """Execute a transform synchronously or asynchronously."""
    transform = TransformRegistry.get(req.transform_name)
    if not transform:
        raise HTTPException(
            status_code=404,
            detail=f"Transform '{req.transform_name}' not found. Available: {[t['name'] for t in TransformRegistry.list_all()]}",
        )

    if req.async_execution:
        # Queue via Celery
        task = execute_transform_task.delay(
            transform_name=req.transform_name,
            entity_value=req.entity_value,
            parameters=req.parameters,
        )
        return {"status": "queued", "task_id": task.id}

    # Synchronous execution
    result = await transform.run(req.entity_value, req.parameters)
    return result.model_dump()


@router.get("/status/{task_id}")
async def get_transform_status(task_id: str):
    """Check status of an async transform execution."""
    from workers.celery_app import celery_app

    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }
