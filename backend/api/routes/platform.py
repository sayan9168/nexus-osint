from __future__ import annotations
from fastapi import APIRouter,HTTPException,Depends
from fastapi.responses import JSONResponse
from api.security import require_permission
from osint_core.cases import store
from osint_core.scoring import score_evidence
from osint_core.sources import catalog
from osint_core.timeline import build_timeline
from osint_core.persistence import db
router=APIRouter()
@router.get("/health",tags=["Platform"])
def health():return {"status":"ok","service":"nexus-osint"}
@router.get("/sources",tags=["Platform"])
def sources(user=Depends(require_permission("case:read"))):return {"sources":catalog()}
@router.get("/metrics",tags=["Observability"])
def metrics(user=Depends(require_permission("case:read"))):
 return {"cases":db.execute("SELECT COUNT(*) n FROM cases")[0]["n"],"evidence":db.execute("SELECT COUNT(*) n FROM evidence")[0]["n"],"entities":db.execute("SELECT COUNT(*) n FROM entities")[0]["n"],"jobs":{str(r["status"]):r["n"] for r in db.execute("SELECT status,COUNT(*) n FROM jobs GROUP BY status")}}
@router.get("/cases/{case_id}/timeline",tags=["Investigation"])
def timeline(case_id:str,user=Depends(require_permission("case:read"))):
 c=store.get(case_id)
 if not c:raise HTTPException(404,"Case not found")
 return {"case_id":case_id,"events":build_timeline(c.evidence)}
@router.get("/cases/{case_id}/score",tags=["Investigation"])
def score(case_id:str,user=Depends(require_permission("case:read"))):
 c=store.get(case_id)
 if not c:raise HTTPException(404,"Case not found")
 return {"case_id":case_id,**score_evidence(c.evidence)}
@router.get("/cases/{case_id}/export.json",tags=["Export"])
def export_json(case_id:str,user=Depends(require_permission("case:read"))):
 c=store.get(case_id)
 if not c:raise HTTPException(404,"Case not found")
 return JSONResponse(content=c.model_dump(mode="json"))
