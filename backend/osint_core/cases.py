"""Local-first investigation case management primitives."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from pydantic import BaseModel, Field


class CaseNote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    body: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Case(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str = ""
    status: str = "open"
    targets: list[str] = Field(default_factory=list)
    notes: list[CaseNote] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CaseStore:
    def __init__(self) -> None:
        self._cases: dict[str, Case] = {}

    def create(self, name: str, description: str = "") -> Case:
        case = Case(name=name, description=description)
        self._cases[case.id] = case
        return case

    def list(self) -> list[Case]:
        return list(self._cases.values())

    def get(self, case_id: str) -> Case | None:
        return self._cases.get(case_id)

    def add_target(self, case_id: str, target: str) -> Case | None:
        case = self.get(case_id)
        if case and target not in case.targets:
            case.targets.append(target)
        return case

    def add_note(self, case_id: str, body: str) -> Case | None:
        case = self.get(case_id)
        if case:
            case.notes.append(CaseNote(body=body))
        return case

    def close(self, case_id: str) -> Case | None:
        case = self.get(case_id)
        if case:
            case.status = "closed"
        return case


store = CaseStore()
