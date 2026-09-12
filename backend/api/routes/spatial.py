"""NEXUS public spatial-intelligence API."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query
from api.security import get_current_user
from osint_core.persistence import db
from osint_core.spatial import evidence_points, public_layers
from osint_core.public_sources import context, crt_subdomains, public_snapshot, ripestat_network, wikidata_search

router = APIRouter()

@router.get("/layers")
async def layers(_: dict = Depends(get_current_user)):
    base = await public_layers(); extra = await public_snapshot()
    base["layers"].update(extra["layers"]); base["sources"] = base.get("sources", []) + extra["sources"]
    base["updated_at"] = max(base.get("updated_at", 0), extra.get("updated_at", 0)); return base

@router.get("/sources")
async def sources(_: dict = Depends(get_current_user)):
    return await public_snapshot()

@router.get("/context")
async def spatial_context(lat: float = Query(..., ge=-90, le=90), lon: float = Query(..., ge=-180, le=180), radius_m: int = Query(3000, ge=250, le=5000), _: dict = Depends(get_current_user)):
    return await context(lat, lon, radius_m)

@router.get("/passive/certificates")
async def certificates(domain: str = Query(..., min_length=1, max_length=253), _: dict = Depends(get_current_user)):
    return {"domain":domain,"results":await crt_subdomains(domain),"source":"crt.sh","passive":True}

@router.get("/passive/network")
async def network(resource: str = Query(..., min_length=1, max_length=128), _: dict = Depends(get_current_user)):
    return {"resource":resource,"result":await ripestat_network(resource),"source":"RIPEstat","passive":True}

@router.get("/passive/knowledge")
async def knowledge(term: str = Query(..., min_length=1, max_length=120), _: dict = Depends(get_current_user)):
    return {"term":term,"results":await wikidata_search(term),"source":"Wikidata","passive":True}

@router.get("/cases/{case_id}/points")
def case_points(case_id: str, _: dict = Depends(get_current_user)):
    rows = db.execute("SELECT id,source,target,observed_at,data_json,confidence FROM evidence WHERE case_id=? ORDER BY observed_at DESC LIMIT 1000", (case_id,))
    if not db.execute("SELECT id FROM cases WHERE id=?", (case_id,)):
        raise HTTPException(status_code=404, detail="case not found")
    return {"case_id": case_id, "points": evidence_points([dict(r) for r in rows])}
