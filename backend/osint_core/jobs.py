"""Persistent jobs with optional Redis/Celery execution and safe local fallback."""
from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from uuid import uuid4
import os
from .cases import store
from .collectors import collect,normalize_target
from .models import EntityType
from .persistence import db
_executor=ThreadPoolExecutor(max_workers=2,thread_name_prefix="nexus-osint")
def _now():return datetime.now(timezone.utc).isoformat()
def _row(job_id):
 rows=db.execute("SELECT * FROM jobs WHERE id=?",(job_id,));return dict(rows[0]) if rows else None
def status(job_id):return _row(job_id)
def list_jobs():return [dict(r) for r in db.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 500")]
def _set(job_id,**changes):
 if changes:db.insert(f"UPDATE jobs SET {', '.join(f'{k}=?' for k in changes)} WHERE id=?",tuple(changes.values())+(job_id,))
def _run(job_id,case_id,target,target_type):
 _set(job_id,status="running",started_at=_now(),attempts=1)
 try:
  evidence=collect(target,target_type)
  if (_row(job_id) or {}).get("status")=="cancelled":return
  for item in evidence:store.add_evidence(case_id,item)
  _set(job_id,status="completed",finished_at=_now())
 except Exception as exc:
  current=_row(job_id)
  if current and current["attempts"]<3 and current["status"]!="cancelled":_set(job_id,status="queued",attempts=current["attempts"]+1,error=f"retry: {type(exc).__name__}");_executor.submit(_run,job_id,case_id,target,target_type)
  elif current:_set(job_id,status="failed",error=f"{type(exc).__name__}: {exc}",finished_at=_now())
def _celery_task():
 try:
  from celery import Celery
  app=Celery("nexus_osint",broker=os.getenv("CELERY_BROKER_URL","redis://localhost:6379/1"),backend=os.getenv("CELERY_RESULT_BACKEND","redis://localhost:6379/2"));app.conf.update(task_acks_late=True,worker_prefetch_multiplier=1,task_time_limit=300,task_soft_time_limit=270)
  @app.task(bind=True,max_retries=2)
  def run_job(self,job_id,case_id,target,target_type):
   try:_run(job_id,case_id,target,EntityType(target_type))
   except Exception as exc:self.retry(exc=exc,countdown=3)
  return app,run_job
 except ImportError:return None,None
celery_app,_celery_run=_celery_task()
def enqueue(case_id,target,target_type):
 if not store.get(case_id):raise ValueError("case not found")
 normalized=normalize_target(target,target_type);job_id=str(uuid4());db.insert("INSERT INTO jobs(id,case_id,target,target_type,status,created_at,attempts) VALUES(?,?,?,?,?,?,0)",(job_id,case_id,normalized,target_type.value,"queued",_now()))
 if os.getenv("NEXUS_USE_CELERY","false").lower()=="true" and _celery_run:
  try:_celery_run.apply_async(args=[job_id,case_id,normalized,target_type.value],task_id=job_id)
  except Exception as exc:_set(job_id,status="failed",error=f"celery unavailable: {type(exc).__name__}: {exc}",finished_at=_now())
 else:_executor.submit(_run,job_id,case_id,normalized,target_type)
 return _row(job_id)
def cancel(job_id):
 job=_row(job_id)
 if not job:return None
 if job["status"] in {"queued","running"}:_set(job_id,status="cancelled",finished_at=_now())
 if celery_app:
  try:celery_app.control.revoke(job_id,terminate=False)
  except Exception:pass
 return _row(job_id)
