"""Lightweight background investigation queue for a single-process deployment."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from .cases import store
from .collectors import collect, normalize_target
from .models import EntityType

_jobs: dict[str, dict] = {}


def status(job_id: str) -> dict | None:
    return _jobs.get(job_id)


def list_jobs() -> list[dict]:
    return list(_jobs.values())


async def _run(job_id: str, case_id: str, target: str, target_type: EntityType) -> None:
    job = _jobs[job_id]
    job.update(status="running", started_at=datetime.now(timezone.utc).isoformat())
    try:
        for evidence in await asyncio.to_thread(collect, target, target_type):
            store.add_evidence(case_id, evidence)
        job.update(status="completed", finished_at=datetime.now(timezone.utc).isoformat())
    except Exception as exc:  # keep worker state inspectable
        job.update(status="failed", error=str(exc), finished_at=datetime.now(timezone.utc).isoformat())


def enqueue(case_id: str, target: str, target_type: EntityType) -> dict:
    if not store.get(case_id):
        raise ValueError("case not found")
    job_id = str(uuid4())
    normalized = normalize_target(target, target_type)
    job = {"id": job_id, "case_id": case_id, "target": normalized, "target_type": target_type.value,
           "status": "queued", "created_at": datetime.now(timezone.utc).isoformat()}
    _jobs[job_id] = job
    asyncio.create_task(_run(job_id, case_id, normalized, target_type))
    return job
