from __future__ import annotations
from fastapi import APIRouter,HTTPException,Depends
from pydantic import BaseModel,Field
from api.security import require_permission
from osint_core.audit import list_events,record,verify_chain
from osint_core.jobs import enqueue,list_jobs,status,cancel
from osint_core.models import EntityType
from osint_core.plugins import list_plugins,health
from osint_core.rbac import allowed
router=APIRouter()
class JobRequest(BaseModel):case_id:str;target:str=Field(min_length=1,max_length=2048);target_type:EntityType;authorized:bool=False
@router.get("/plugins")
def plugins(user=Depends(require_permission("case:read"))):return {"plugins":list_plugins()}
@router.get("/plugins/health")
def plugin_health(user=Depends(require_permission("case:read"))):return {"plugins":health()}
@router.get("/rbac/{role}")
def rbac(role:str,user=Depends(require_permission("case:read"))):return {"role":role,"permissions":[p for p in ("case:read","case:write","scan:run","report:read","graph:read","job:run","audit:read","source:manage") if allowed(role,p)]}
@router.post("/jobs")
def create_job(request:JobRequest,user=Depends(require_permission("job:run"))):
 if not request.authorized:raise HTTPException(403,"Explicit authorization is required")
 job=enqueue(request.case_id,request.target,request.target_type);record("job.enqueue",user["username"],request.case_id,{"target":request.target});return job
@router.get("/jobs")
def jobs(user=Depends(require_permission("job:run"))):return {"jobs":list_jobs()}
@router.get("/jobs/{job_id}")
def job(job_id:str,user=Depends(require_permission("job:run"))):
 result=status(job_id)
 if not result:raise HTTPException(404,"Job not found")
 return result
@router.post("/jobs/{job_id}/cancel")
def cancel_job(job_id:str,user=Depends(require_permission("job:run"))):
 result=cancel(job_id)
 if not result:raise HTTPException(404,"Job not found")
 record("job.cancel",user["username"],job_id,{});return result
@router.get("/audit")
def audit(limit:int=100,user=Depends(require_permission("audit:read"))):return {"events":list_events(limit)}
@router.get("/audit/verify")
def audit_verify(user=Depends(require_permission("audit:read"))):return verify_chain()
