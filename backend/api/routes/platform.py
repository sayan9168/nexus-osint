from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from osint_core.cases import store
from osint_core.scoring import score_evidence
from osint_core.sources import catalog
from osint_core.timeline import build_timeline

router = APIRouter()


@router.get("/health", tags=["Platform"])
def health() -> dict:
    return {"status": "ok", "service": "nexus-osint"}


@router.get("/sources", tags=["Platform"])
def sources() -> dict:
    return {"sources": catalog()}


@router.get("/cases/{case_id}/timeline", tags=["Investigation"])
def timeline(case_id: str) -> dict:
    case = store.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"case_id": case_id, "events": build_timeline(case.evidence)}


@router.get("/cases/{case_id}/score", tags=["Investigation"])
def score(case_id: str) -> dict:
    case = store.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"case_id": case_id, **score_evidence(case.evidence)}


@router.get("/cases/{case_id}/export.json", tags=["Export"])
def export_json(case_id: str) -> JSONResponse:
    case = store.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return JSONResponse(content=case.model_dump(mode="json"))
