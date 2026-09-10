"""Durable bounded jobs with optional Redis/Celery execution and local fallback."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from datetime import datetime, timezone
from uuid import uuid4
import os
from .cases import store
from .collectors import collect, normalize_target
from .models import EntityType
from .persistence import db

MAX_ATTEMPTS = 3
MAX_WORKERS = max(1, min(int(os.getenv("NEXUS_JOB_CONCURRENCY", "2")), 16))
JOB_TIMEOUT_SECONDS = max(10, min(int(os.getenv("NEXUS_JOB_TIMEOUT_SECONDS", "300")), 900))
_worker_executor = ThreadPoolExecutor(max_workers=MAX_WORKERS, thread_name_prefix="nexus-job")
_collect_executor = ThreadPoolExecutor(max_workers=MAX_WORKERS, thread_name_prefix="nexus-collect")

def _now():
    return datetime.now(timezone.utc).isoformat()

def _row(job_id):
    rows = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,))
    return dict(rows[0]) if rows else None

def status(job_id):
    return _row(job_id)

def list_jobs():
    return [dict(r) for r in db.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 500")]

def _set(job_id, **changes):
    if changes:
        db.insert(f"UPDATE jobs SET {', '.join(f'{k}=?' for k in changes)} WHERE id=?", tuple(changes.values()) + (job_id,))

def _collect_with_timeout(target, target_type):
    future = _collect_executor.submit(collect, target, target_type)
    return future.result(timeout=JOB_TIMEOUT_SECONDS)

def _run(job_id, case_id, target, target_type):
    current = _row(job_id)
    if not current or current["status"] == "cancelled":
        return
    attempt = max(1, int(current.get("attempts") or 0))
    _set(job_id, status="running", started_at=_now(), attempts=attempt, error=None)
    try:
        evidence = _collect_with_timeout(target, target_type)
        if (_row(job_id) or {}).get("status") == "cancelled":
            return
        for item in evidence:
            if (_row(job_id) or {}).get("status") == "cancelled":
                return
            store.add_evidence(case_id, item)
        _set(job_id, status="completed", finished_at=_now())
    except FutureTimeout:
        _retry_or_fail(job_id, case_id, target, target_type, "job timeout")
    except Exception as exc:
        _retry_or_fail(job_id, case_id, target, target_type, f"{type(exc).__name__}: {exc}")

def _retry_or_fail(job_id, case_id, target, target_type, error):
    current = _row(job_id)
    if not current or current["status"] == "cancelled":
        return
    attempt = int(current.get("attempts") or 0)
    if attempt < MAX_ATTEMPTS:
        next_attempt = attempt + 1
        _set(job_id, status="queued", attempts=next_attempt, error=f"retry {next_attempt}/{MAX_ATTEMPTS}: {error}")
        _worker_executor.submit(_run, job_id, case_id, target, target_type)
    else:
        _set(job_id, status="failed", error=error, finished_at=_now())

def _celery_task():
    try:
        from celery import Celery
        app = Celery("nexus_osint", broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1"), backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2"))
        app.conf.update(task_acks_late=True, worker_prefetch_multiplier=1, task_time_limit=JOB_TIMEOUT_SECONDS, task_soft_time_limit=max(5, JOB_TIMEOUT_SECONDS - 30), task_track_started=True, result_expires=86400)
        @app.task(bind=True, max_retries=MAX_ATTEMPTS - 1)
        def run_job(self, job_id, case_id, target, target_type):
            try:
                _run(job_id, case_id, target, EntityType(target_type))
            except Exception as exc:
                self.retry(exc=exc, countdown=min(60, 2 ** self.request.retries))
        return app, run_job
    except ImportError:
        return None, None

celery_app, _celery_run = _celery_task()

def recover_stale_jobs():
    rows = db.execute("SELECT id FROM jobs WHERE status='running'")
    for row in rows:
        _set(row["id"], status="queued", error="recovered after worker restart")
    if os.getenv("NEXUS_USE_CELERY", "false").lower() != "true":
        for row in db.execute("SELECT id,case_id,target,target_type FROM jobs WHERE status='queued' AND attempts<?", (MAX_ATTEMPTS,)):
            _worker_executor.submit(_run, row["id"], row["case_id"], row["target"], EntityType(row["target_type"]))

def enqueue(case_id, target, target_type):
    if not store.get(case_id):
        raise ValueError("case not found")
    normalized = normalize_target(target, target_type)
    job_id = str(uuid4())
    db.insert("INSERT INTO jobs(id,case_id,target,target_type,status,created_at,attempts) VALUES(?,?,?,?,?,?,?)", (job_id, case_id, normalized, target_type.value, "queued", _now(), 1))
    if os.getenv("NEXUS_USE_CELERY", "false").lower() == "true" and _celery_run:
        try:
            _celery_run.apply_async(args=[job_id, case_id, normalized, target_type.value], task_id=job_id)
        except Exception as exc:
            _set(job_id, status="failed", error=f"celery unavailable: {type(exc).__name__}: {exc}", finished_at=_now())
    else:
        _worker_executor.submit(_run, job_id, case_id, normalized, target_type)
    return _row(job_id)

def cancel(job_id):
    job = _row(job_id)
    if not job:
        return None
    if job["status"] in {"queued", "running"}:
        _set(job_id, status="cancelled", finished_at=_now())
    if celery_app:
        try:
            celery_app.control.revoke(job_id, terminate=False)
        except Exception:
            pass
    return _row(job_id)

recover_stale_jobs()
