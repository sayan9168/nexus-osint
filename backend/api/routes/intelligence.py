from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from api.security import require_permission
from osint_core.intelligence import domain_intelligence, upsert_entity
router=APIRouter()
class DomainRequest(BaseModel): domain:str=Field(min_length=1,max_length=253,pattern=r"^[A-Za-z0-9][A-Za-z0-9.-]*[A-Za-z0-9]$")
class EntityRequest(BaseModel):
    case_id:str=Field(min_length=1,max_length=128); entity_type:str=Field(min_length=1,max_length=64); canonical:str=Field(min_length=1,max_length=2048); metadata:dict=dict
@router.post("/dns-rdap")
def dns_rdap(body:DomainRequest,user=Depends(require_permission("scan:run"))): return domain_intelligence(body.domain)
@router.post("/entities")
def entity(body:EntityRequest,user=Depends(require_permission("case:write"))):
    try: return upsert_entity(body.case_id,body.entity_type,body.canonical,body.metadata)
    except Exception as exc: raise HTTPException(400,str(exc)) from exc
@router.get("/entities/{case_id}")
def entities(case_id:str,user=Depends(require_permission("case:read"))):
    rows=db.execute("SELECT * FROM entities WHERE case_id=? ORDER BY first_seen",(case_id,))
    return {"entities":[dict(r) for r in rows]}
