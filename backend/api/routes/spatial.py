"""NEXUS public spatial-intelligence API."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.security import get_current_user
from osint_core.persistence import db
from osint_core.spatial import evidence_points, public_layers

router = APIRouter()


@router.get("/layers")
async def layers(_: dict = Depends(get_current_user)):
    return await public_layers()


@router.get("/cases/{case_id}/points")
def case_points(case_id: str, _: dict = Depends(get_current_user)):
    rows = db.execute("SELECT id,source,target,observed_at,data_json,confidence FROM evidence WHERE case_id=? ORDER BY observed_at DESC LIMIT 1000", (case_id,))
    if not db.execute("SELECT id FROM cases WHERE id=?", (case_id,)):
        raise HTTPException(status_code=404, detail="case not found")
    return {"case_id": case_id, "points": evidence_points([dict(r) for r in rows])}
