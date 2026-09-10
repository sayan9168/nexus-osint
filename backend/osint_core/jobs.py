"""Bounded background investigation runner for single-process deployments.

The queue is intentionally local and in-process. It never bypasses the service's
explicit authorization requirement and is not presented as a durable distributed queue.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from .cases import store
from .collectors import collect, normalize_target
from .models import EntityType

_MAX_WORKERS = 2
_executor = ThreadPoolExecutor(max_workers=_MAX_WORKERS, thread_name_prefix="nexus-osint")
_jobs: dict[str, dict] = {}
_lock = Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def status(job_id: str) -> dict | None:
    with _lock:
        job = _jobs.get(job_id)
        return dict(job) if job else None


def list_jobs() -> list[dict]:
    with _lock:
        return [dict(job) for job in sorted(_jobs.values(), key=lambda x: x["created_at"], reverse=True)]


def _update(job_id: str, **changes: object) -> None:
    with _lock:
        if job_id in _jobs:
            _jobs[job_id].update(changes)


def _run(job_id: str, case_id: str, target: str, target_type: EntityType) -> None:
    _update(job_id, status="running", started_at=_now())
    try:
        evidence = collect(target, target_type)
        for item in evidence:
            store.add_evidence(case_id, item)
        _update(job_id, status="completed", evidence_count=len(evidence), finished_at=_now())
    except Exception as exc:  # keep worker state inspectable
        _update(job_id, status="failed", error=f"{type(exc).__name__}: {exc}", finished_at=_now())


def enqueue(case_id: str, target: str, target_type: EntityType) -> dict:
    if not store.get(case_id):
        raise ValueError("case not found")
    normalized = normalize_target(target, target_type)
    job_id = str(uuid4())
    job = {
        "id": job_id,
        "case_id": case_id,
        "target": normalized,
        "target_type": target_type.value,
        "status": "queued",
        "created_at": _now(),
    }
    with _lock:
        _jobs[job_id] = job
    try:
        _executor.submit(_run, job_id, case_id, normalized, target_type)
    except Exception as exc:
        _update(job_id, status="failed", error=f"queue error: {type(exc).__name__}: {exc}", finished_at=_now())
    return dict(job)
