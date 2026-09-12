"""Deterministic public-signal analytics endpoints."""
from __future__ import annotations
from fastapi import APIRouter, Depends
from api.security import get_current_user
from osint_core.spatial_analytics import source_health,correlation,density,timeline
router=APIRouter()

@router.get("/source-health")
async def health(_:dict=Depends(get_current_user)): return await source_health()

@router.get("/cases/{case_id}/correlation")
async def case_correlation(case_id:str,_:dict=Depends(get_current_user)): return await correlation(case_id)

@router.get("/density")
async def signal_density(_:dict=Depends(get_current_user)): return await density()

@router.get("/cases/{case_id}/timeline-fusion")
async def timeline_fusion(case_id:str,_:dict=Depends(get_current_user)): return await timeline(case_id)
