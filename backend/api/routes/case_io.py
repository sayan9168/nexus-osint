from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel,Field
from api.security import require_permission
from osint_core.cases import store
from osint_core.models import Evidence
from osint_core.persistence import db
from osint_core.intelligence import merge_relationship
router=APIRouter()
class ImportBundle(BaseModel):
 schema_version:str="2.0";name:str=Field(min_length=1,max_length=120);description:str="";targets:list[str]=[];notes:list[str]=[];evidence:list[Evidence]=[];relationships:list[dict]=[]
@router.get("/{case_id}/bundle.json")
def export_bundle(case_id:str,user=Depends(require_permission("case:read"))):
 c=store.get(case_id)
 if not c:raise HTTPException(404,"Case not found")
 entities=[dict(r) for r in db.execute("SELECT * FROM entities WHERE case_id=?",(case_id,))];rels=[dict(r) for r in db.execute("SELECT * FROM relationships WHERE case_id=?",(case_id,))]
 return {"schema_version":"2.0","case":c.model_dump(mode="json"),"entities":entities,"relationships":rels}
@router.post("/import")
def import_bundle(bundle:ImportBundle,user=Depends(require_permission("case:write"))):
 if bundle.schema_version!="2.0":raise HTTPException(400,"unsupported schema version")
 c=store.create(bundle.name,bundle.description)
 for t in bundle.targets:store.add_target(c.id,t)
 for n in bundle.notes:store.add_note(c.id,n)
 for e in bundle.evidence:store.add_evidence(c.id,e)
 for r in bundle.relationships:
  try:merge_relationship(c.id,r["source_entity"],r["target_entity"],r["relation"],float(r.get("confidence",.5)))
  except (KeyError,ValueError):continue
 return store.get(c.id)
