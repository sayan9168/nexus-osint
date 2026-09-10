from fastapi import APIRouter, HTTPException

from osint_core.cases import store
from osint_core.graph import GraphProjection, project

router = APIRouter()


@router.get("/{case_id}", response_model=GraphProjection)
def get_case_graph(case_id: str) -> GraphProjection:
    case = store.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return project(case)
