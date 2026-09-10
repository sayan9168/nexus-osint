from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from api.security import require_permission
from osint_core.intelligence import domain_intelligence,upsert_entity,merge_relationship
from osint_core.persistence import db
router=APIRouter()
class DomainRequest(BaseModel):domain:str=Field(min_length=1,max_length=253,pattern=r"^[A-Za-z0-9][A-Za-z0-9.-]*[A-Za-z0-9]$")
class EntityRequest(BaseModel):case_id:str=Field(min_length=1,max_length=128);entity_type:str=Field(min_length=1,max_length=64);canonical:str=Field(min_length=1,max_length=2048);metadata:dict={}
class RelationRequest(BaseModel):case_id:str;source_entity:str;target_entity:str;relation:str=Field(min_length=1,max_length=128);confidence:float=Field(default=.5,ge=0,le=1)
@router.post("/dns-rdap")
def dns_rdap(body:DomainRequest,user=Depends(require_permission("scan:run"))):return domain_intelligence(body.domain)
@router.post("/entities")
def entity(body:EntityRequest,user=Depends(require_permission("case:write"))):
 try:return upsert_entity(body.case_id,body.entity_type,body.canonical,body.metadata)
 except Exception as exc:raise HTTPException(400,str(exc)) from exc
@router.get("/entities/{case_id}")
def entities(case_id:str,user=Depends(require_permission("case:read"))):return {"entities":[dict(r) for r in db.execute("SELECT * FROM entities WHERE case_id=? ORDER BY first_seen",(case_id,))]}
@router.post("/relationships")
def relationship(body:RelationRequest,user=Depends(require_permission("case:write"))):return merge_relationship(body.case_id,body.source_entity,body.target_entity,body.relation,body.confidence)
@router.get("/relationships/{case_id}")
def relationships(case_id:str,user=Depends(require_permission("case:read"))):return {"relationships":[dict(r) for r in db.execute("SELECT * FROM relationships WHERE case_id=? ORDER BY created_at",(case_id,))]}
