"""Public-source spatial fusion endpoints."""
from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from api.security import get_current_user
from osint_core.source_fusion import fused_snapshot, fused_context

router=APIRouter()

@router.get("/fusion")
async def fusion(_: dict=Depends(get_current_user)):
    return await fused_snapshot()

@router.get("/fusion/context")
async def fusion_context(lat: float=Query(...,ge=-90,le=90),lon: float=Query(...,ge=-180,le=180),radius_m: int=Query(3000,ge=250,le=5000),_: dict=Depends(get_current_user)):
    return await fused_context(lat,lon,radius_m)
