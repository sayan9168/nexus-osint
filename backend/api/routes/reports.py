"""Read-only deterministic report rendering endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse
from api.security import require_permission
from osint_core.cases import store
from osint_core.models import EntityType, Investigation
from osint_core.reporting import to_html, to_markdown
from osint_core.persistence import db

router = APIRouter()

def _target_type(target: str) -> EntityType:
    if target.startswith(("http://", "https://")):
        return EntityType.URL
    if "@" in target and " " not in target:
        return EntityType.EMAIL
    parts = target.split(".")
    if len(parts) >= 2:
        return EntityType.DOMAIN
    return EntityType.USERNAME

def _investigation(case_id: str) -> Investigation:
    case = store.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    target = case.targets[0] if case.targets else ""
    return Investigation(id=case.id, target=target, target_type=_target_type(target), authorized=True, evidence=case.evidence)

def _bundle(case_id: str) -> dict:
    case = store.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    entities = [dict(r) for r in db.execute("SELECT * FROM entities WHERE case_id=? ORDER BY first_seen", (case_id,))]
    relationships = [dict(r) for r in db.execute("SELECT * FROM relationships WHERE case_id=? ORDER BY created_at", (case_id,))]
    return {
        "schema_version": "2.1",
        "case": case.model_dump(mode="json"),
        "entities": entities,
        "relationships": relationships,
        "evidence_count": len(case.evidence),
    }

@router.get("/{case_id}.md", response_class=PlainTextResponse)
def markdown_report(case_id: str, user=Depends(require_permission("report:read"))) -> str:
    return to_markdown(_investigation(case_id))

@router.get("/{case_id}.html", response_class=HTMLResponse)
def html_report(case_id: str, user=Depends(require_permission("report:read"))) -> str:
    return to_html(_investigation(case_id))

@router.get("/{case_id}.json", response_class=JSONResponse)
def json_report(case_id: str, user=Depends(require_permission("report:read"))):
    return _bundle(case_id)
