"""Case-management API with authenticated actor attribution."""
from fastapi import APIRouter,HTTPException,Depends
from pydantic import BaseModel,Field
from api.security import require_permission
from osint_core.audit import record
from osint_core.cases import Case,store
router=APIRouter()
class CreateCase(BaseModel):
 name:str=Field(min_length=1,max_length=120)
 description:str=Field(default="",max_length=2000)
 authorized:bool=False
class TargetInput(BaseModel):target:str=Field(min_length=1,max_length=512)
class NoteInput(BaseModel):body:str=Field(min_length=1,max_length=5000)
@router.post("/",response_model=Case)
def create_case(payload:CreateCase,user=Depends(require_permission("case:write"))):
 if not payload.authorized:raise HTTPException(403,"Explicit authorization is required before creating an investigation case")
 c=store.create(payload.name,payload.description,payload.authorized);record("case.create",user["username"],c.id,{"name":c.name,"authorized":c.authorized});return c
@router.get("/",response_model=list[Case])
def list_cases(user=Depends(require_permission("case:read"))):return store.list()
@router.get("/{case_id}",response_model=Case)
def get_case(case_id:str,user=Depends(require_permission("case:read"))):
 c=store.get(case_id)
 if not c:raise HTTPException(404,"Case not found")
 return c
@router.post("/{case_id}/targets",response_model=Case)
def add_target(case_id:str,payload:TargetInput,user=Depends(require_permission("case:write"))):
 c=store.get(case_id)
 if not c:raise HTTPException(404,"Case not found")
 if not c.authorized:raise HTTPException(403,"Case is not authorized for collection")
 c=store.add_target(case_id,payload.target.strip());record("case.target.add",user["username"],case_id,{"target":payload.target.strip()});return c
@router.post("/{case_id}/notes",response_model=Case)
def add_note(case_id:str,payload:NoteInput,user=Depends(require_permission("case:write"))):
 c=store.add_note(case_id,payload.body.strip())
 if not c:raise HTTPException(404,"Case not found")
 record("case.note.add",user["username"],case_id,{});return c
@router.post("/{case_id}/close",response_model=Case)
def close_case(case_id:str,user=Depends(require_permission("case:write"))):
 c=store.close(case_id)
 if not c:raise HTTPException(404,"Case not found")
 record("case.close",user["username"],case_id,{});return c
