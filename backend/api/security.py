"""HTTP authentication/RBAC helpers."""
from __future__ import annotations
from fastapi import HTTPException, Request
from osint_core.auth import decode_session
from osint_core.rbac import allowed

def current_user(request: Request) -> dict:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "): raise HTTPException(401, "Bearer session required")
    try: return decode_session(auth[7:].strip())
    except ValueError as exc: raise HTTPException(401, str(exc)) from exc

def require_permission(permission: str):
    def dependency(request: Request) -> dict:
        user = current_user(request)
        if not allowed(user.get("role", ""), permission): raise HTTPException(403, "Insufficient role")
        return user
    return dependency
