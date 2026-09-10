"""Tamper-evident, append-only audit events backed by the existing SQLite DB."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from uuid import uuid4

from .persistence import db


def record(action: str, actor: str, resource: str = "", metadata: str = "") -> dict:
    now = datetime.now(timezone.utc).isoformat()
    event_id = str(uuid4())
    previous = db.execute("SELECT event_hash FROM audit_events ORDER BY created_at DESC LIMIT 1")
    prev_hash = previous[0]["event_hash"] if previous else "GENESIS"
    digest = hashlib.sha256(f"{prev_hash}|{event_id}|{now}|{actor}|{action}|{resource}|{metadata}".encode()).hexdigest()
    db.insert("INSERT INTO audit_events VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (event_id, now, actor, action, resource, metadata, prev_hash, digest))
    return {"id": event_id, "created_at": now, "actor": actor, "action": action, "resource": resource, "metadata": metadata, "event_hash": digest}


def list_events(limit: int = 100) -> list[dict]:
    limit = max(1, min(limit, 500))
    return [dict(r) for r in db.execute("SELECT * FROM audit_events ORDER BY created_at DESC LIMIT ?", (limit,))]
