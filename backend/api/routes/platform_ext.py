from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from osint_core.audit import list_events, record
from osint_core.jobs import enqueue, list_jobs, status
from osint_core.models import EntityType
from osint_core.plugins import list_plugins
from osint_core.rbac import allowed

router = APIRouter()


class JobRequest(BaseModel):
    case_id: str
    target: str = Field(min_length=1, max_length=2048)
    target_type: EntityType
    authorized: bool = False


@router.get("/plugins")
def plugins() -> dict:
    return {"plugins": list_plugins()}


@router.get("/rbac/{role}")
def rbac(role: str) -> dict:
    return {"role": role, "permissions": [p for p in ("case:read", "case:write", "scan:run", "report:read", "graph:read", "job:run", "audit:read", "source:manage") if allowed(role, p)]}


@router.post("/jobs")
def create_job(request: JobRequest) -> dict:
    if not request.authorized:
        raise HTTPException(status_code=403, detail="Explicit authorization is required")
    job = enqueue(request.case_id, request.target, request.target_type)
    record("job.enqueue", "api", request.case_id, request.target)
    return job


@router.get("/jobs")
def jobs() -> dict:
    return {"jobs": list_jobs()}


@router.get("/jobs/{job_id}")
def job(job_id: str) -> dict:
    result = status(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    return result


@router.get("/audit")
def audit(limit: int = 100) -> dict:
    return {"events": list_events(limit)}
