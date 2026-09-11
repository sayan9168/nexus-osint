from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EntityType(StrEnum):
    DOMAIN = "domain"
    IP = "ip"
    URL = "url"
    EMAIL = "email"
    USERNAME = "username"


class Evidence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    source: str
    target: str
    observed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    notes: str | None = None
    provenance_hash: str | None = None


class Investigation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    target: str
    target_type: EntityType
    authorized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evidence: list[Evidence] = Field(default_factory=list)


class ScanRequest(BaseModel):
    target: str = Field(min_length=1, max_length=2048)
    target_type: EntityType
    authorized: bool = False
    case_id: str | None = None


class ScanResponse(BaseModel):
    target: str
    target_type: EntityType
    evidence: list[Evidence]
    warnings: list[str] = Field(default_factory=list)
    case_id: str | None = None
