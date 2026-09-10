"""Small, explicit RBAC policy primitives.

Authentication is intentionally left to the deployment layer. These helpers only
make authorization decisions from an already-authenticated role.
"""
from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"


PERMISSIONS: dict[Role, set[str]] = {
    Role.VIEWER: {"case:read", "report:read", "graph:read"},
    Role.ANALYST: {"case:read", "case:write", "scan:run", "report:read", "graph:read", "job:run"},
    Role.ADMIN: {"case:read", "case:write", "scan:run", "report:read", "graph:read", "job:run", "audit:read", "source:manage"},
}


def allowed(role: str, permission: str) -> bool:
    try:
        return permission in PERMISSIONS[Role(role.lower())]
    except ValueError:
        return False
