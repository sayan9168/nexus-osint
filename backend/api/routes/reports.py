"""Read-only deterministic report rendering endpoints."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse

from osint_core.cases import store
from osint_core.models import EntityType, Investigation
from osint_core.reporting import to_html, to_markdown

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
    return Investigation(
        id=case.id,
        target=target,
        target_type=_target_type(target),
        authorized=True,
        evidence=case.evidence,
    )


@router.get("/{case_id}.md", response_class=PlainTextResponse)
def markdown_report(case_id: str) -> str:
    return to_markdown(_investigation(case_id))


@router.get("/{case_id}.html", response_class=HTMLResponse)
def html_report(case_id: str) -> str:
    return to_html(_investigation(case_id))
