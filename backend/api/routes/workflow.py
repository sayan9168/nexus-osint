"""Case workflow, tags, templates and operational metadata endpoints."""
from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from api.security import require_permission
from osint_core.audit import record
from osint_core.cases import store
from osint_core.workflow import get_case_meta,update_case_meta,workflow_catalog
router=APIRouter()
class WorkflowUpdate(BaseModel):
 tags:list[str]=Field(default_factory=list,max_length=30)
 workflow:str|None=None
 status:str|None=None
@router.get("/catalog")
def catalog(user=Depends(require_permission("case:read"))):return {"workflow":workflow_catalog(),"templates":[{"id":"domain-investigation","name":"Domain investigation","targets":["domain","url","ip"]},{"id":"identity-review","name":"Identity review","targets":["email"]}]}
@router.get("/{case_id}/meta")
def meta(case_id:str,user=Depends(require_permission("case:read"))):
 if not store.get(case_id):raise HTTPException(404,"Case not found")
 return get_case_meta(case_id)
@router.patch("/{case_id}/meta")
def update(case_id:str,payload:WorkflowUpdate,user=Depends(require_permission("case:write"))):
 try: result=update_case_meta(case_id,tags=payload.tags,workflow=payload.workflow,status=payload.status)
 except ValueError as exc:raise HTTPException(422,str(exc)) from exc
 if result is None:raise HTTPException(404,"Case not found")
 record("case.meta.update",user["username"],case_id,result);return result
