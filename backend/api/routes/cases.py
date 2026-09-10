"""Case-management API with in-memory storage for the foundation edition."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from osint_core.cases import Case, store

router = APIRouter()


class CreateCase(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field(default="", max_length=2000)


class TargetInput(BaseModel):
    target: str = Field(min_length=1, max_length=512)


class NoteInput(BaseModel):
    body: str = Field(min_length=1, max_length=5000)


@router.post("/", response_model=Case)
def create_case(payload: CreateCase) -> Case:
    return store.create(payload.name, payload.description)


@router.get("/", response_model=list[Case])
def list_cases() -> list[Case]:
    return store.list()


@router.get("/{case_id}", response_model=Case)
def get_case(case_id: str) -> Case:
    case = store.get(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.post("/{case_id}/targets", response_model=Case)
def add_target(case_id: str, payload: TargetInput) -> Case:
    case = store.add_target(case_id, payload.target.strip())
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.post("/{case_id}/notes", response_model=Case)
def add_note(case_id: str, payload: NoteInput) -> Case:
    case = store.add_note(case_id, payload.body.strip())
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.post("/{case_id}/close", response_model=Case)
def close_case(case_id: str) -> Case:
    case = store.close(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case
