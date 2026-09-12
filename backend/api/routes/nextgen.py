"""Next-generation analytics endpoints for public signals."""
from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from api.security import get_current_user
from osint_core.nextgen_intelligence import correlate_signals, density_heatmap, fuse_timeline, graph_fusion, source_health
from osint_core.public_sources import SOURCES
from osint_core.persistence import Database

router=APIRouter()

def _db(): return Database()

@router.get("/health")
async def health(_:dict=Depends(get_current_user)):
    return source_health([dict(s) for s in SOURCES])

@router.post("/correlation")
async def correlation(payload:dict, _:dict=Depends(get_current_user)):
    return correlate_signals(payload.get("signals") or [], float(payload.get("grid_deg",5)))

@router.post("/density")
async def density(payload:dict, _:dict=Depends(get_current_user)):
    return density_heatmap(payload.get("signals") or [], float(payload.get("grid_deg",5)))

@router.post("/timeline")
async def timeline(payload:dict, _:dict=Depends(get_current_user)):
    return {"timeline":fuse_timeline(payload.get("evidence") or [],payload.get("signals") or [])}

@router.post("/graph")
async def graph(payload:dict, _:dict=Depends(get_current_user)):
    return graph_fusion(payload.get("entities") or [],payload.get("relationships") or [],payload.get("signals") or [])

@router.get("/case/{case_id}/timeline")
async def case_timeline(case_id:str, _:dict=Depends(get_current_user)):
    db=_db();
    with db._connect() as conn:
        evidence=[dict(r) for r in conn.execute("SELECT * FROM evidence WHERE case_id=? ORDER BY observed_at",(case_id,)).fetchall()]
        entities=[dict(r) for r in conn.execute("SELECT * FROM entities WHERE case_id=?",(case_id,)).fetchall()]
        relationships=[dict(r) for r in conn.execute("SELECT * FROM relationships WHERE case_id=?",(case_id,)).fetchall()]
    return {"case_id":case_id,"timeline":fuse_timeline(evidence,[]),"graph":graph_fusion(entities,relationships,[])}

@router.get("/case/{case_id}/analytics")
async def case_analytics(case_id:str, _:dict=Depends(get_current_user)):
    db=_db()
    with db._connect() as conn:
        evidence=[dict(r) for r in conn.execute("SELECT * FROM evidence WHERE case_id=?",(case_id,)).fetchall()]
    return {"case_id":case_id,"evidence_count":len(evidence),"timeline":fuse_timeline(evidence,[]),"density":density_heatmap([])}
