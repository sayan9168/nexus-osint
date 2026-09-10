"""Read-only report rendering endpoints for investigation objects."""
from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse

from osint_core.cases import store
from osint_core.models import Investigation, EntityType
from osint_core.reporting import to_html, to_markdown

router = APIRouter()


def _investigation(case_id: str) -> Investigation:
    case = store.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    target = case.targets[0] if case.targets else ""
    return Investigation(
        id=case.id,
        target=target,
        target_type=EntityType.DOMAIN,
        authorized=True,
        evidence=[],
    )


@router.get("/{case_id}.md", response_class=PlainTextResponse)
def markdown_report(case_id: str) -> str:
    return to_markdown(_investigation(case_id))


@router.get("/{case_id}.html", response_class=HTMLResponse)
def html_report(case_id: str) -> str:
    return to_html(_investigation(case_id))
