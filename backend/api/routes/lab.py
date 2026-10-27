"""NEXUS LAB — experimental OSINT primitives. All bounded & authenticated."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from api.security import require_permission
from osint_core.persistence import db
from osint_core import lab_engine as lab

router = APIRouter()

def _case(case_id: str):
    rows=db.execute("SELECT * FROM cases WHERE id=?",(case_id,))
    if not rows: raise HTTPException(404,"Case not found")
    return dict(rows[0])

def _evidence(case_id: str):
    return [dict(r) for r in db.execute("SELECT * FROM evidence WHERE case_id=? ORDER BY observed_at",(case_id,))]
def _entities(case_id: str):
    return [dict(r) for r in db.execute("SELECT * FROM entities WHERE case_id=?",(case_id,))]
def _relationships(case_id: str):
    return [dict(r) for r in db.execute("SELECT * FROM relationships WHERE case_id=?",(case_id,))]
def _jobs(case_id: str):
    return [dict(r) for r in db.execute("SELECT * FROM jobs WHERE case_id=? ORDER BY created_at DESC",(case_id,))]
def _snapshots(case_id: str):
    return [dict(r) for r in db.execute("SELECT * FROM evidence_snapshots WHERE case_id=? ORDER BY version",(case_id,))]

@router.get("/prism/{case_id}")
def prism(case_id: str, user=Depends(require_permission("case:read"))):
    _case(case_id)
    return lab.prism_vault(_evidence(case_id), _snapshots(case_id))

class NeuralReq(BaseModel):
    threshold: float = Field(default=0.52, ge=0.1, le=0.95)
@router.post("/neural/{case_id}")
def neural(case_id: str, req: NeuralReq, user=Depends(require_permission("case:read"))):
    _case(case_id)
    return lab.neural_mesh(_entities(case_id), _relationships(case_id), _evidence(case_id), req.threshold)

@router.get("/shadow/{case_id}/{entity_id}")
def shadow(case_id: str, entity_id: str, user=Depends(require_permission("case:read"))):
    _case(case_id)
    rows=db.execute("SELECT * FROM entities WHERE id=? AND case_id=?",(entity_id, case_id))
    if not rows: raise HTTPException(404,"Entity not found in this case")
    ent=dict(rows[0])
    ev=_evidence(case_id)
    # related evidence: target contains canonical substring
    can=str(ent.get("canonical","")).lower()
    rel_ev=[e for e in ev if can and (can in str(e.get("target","")).lower() or can in str(e.get("source","")).lower())]
    if not rel_ev: rel_ev=ev[:4]
    rels=[r for r in _relationships(case_id) if str(r.get("source_entity"))==entity_id or str(r.get("target_entity"))==entity_id]
    return lab.shadow_profile(ent, rel_ev, rels, _entities(case_id))

@router.get("/prophet/{case_id}")
def prophet(case_id: str, horizon: int = 3, user=Depends(require_permission("case:read"))):
    _case(case_id)
    if horizon<1 or horizon>6: raise HTTPException(400,"horizon 1..6")
    return lab.causality_prophet(_evidence(case_id), _jobs(case_id), horizon)

class QuantumReq(BaseModel):
    query: str = Field(min_length=1, max_length=280)
@router.post("/quantum/{case_id}")
def quantum(case_id: str, req: QuantumReq, user=Depends(require_permission("case:read"))):
    _case(case_id)
    cases=[dict(r) for r in db.execute("SELECT * FROM cases WHERE id=?",(case_id,))]
    return lab.quantum_search(req.query, _entities(case_id), _evidence(case_id), cases)

class CopilotReq(BaseModel):
    question: str = Field(min_length=1, max_length=600)
@router.post("/copilot/{case_id}")
def copilot(case_id: str, req: CopilotReq, user=Depends(require_permission("case:read"))):
    row=_case(case_id)
    ctx={
        "name": row.get("name"),
        "targets": [r["target"] for r in db.execute("SELECT target FROM targets WHERE case_id=?",(case_id,))],
        "evidence": _evidence(case_id),
        "entities": _entities(case_id),
    }
    return lab.copilot_answer(req.question, ctx)
