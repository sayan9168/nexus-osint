"""Tamper-evident audit log with deterministic verification."""
from __future__ import annotations
import hashlib
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4
from .persistence import db, json_dumps

_write_lock = Lock()

def record(action: str, actor: str, resource: str = "", metadata=None) -> dict:
    meta = metadata if isinstance(metadata, str) else json_dumps(metadata or {})
    with _write_lock:
        now = datetime.now(timezone.utc).isoformat()
        event_id = str(uuid4())
        previous = db.execute("SELECT event_hash FROM audit_events ORDER BY created_at DESC,id DESC LIMIT 1")
        prev = previous[0]["event_hash"] if previous else "GENESIS"
        digest = hashlib.sha256(f"{prev}|{event_id}|{now}|{actor}|{action}|{resource}|{meta}".encode()).hexdigest()
        db.insert("INSERT INTO audit_events VALUES(?,?,?,?,?,?,?,?)", (event_id, now, actor, action, resource, meta, prev, digest))
    return {"id": event_id, "created_at": now, "actor": actor, "action": action, "resource": resource, "metadata": meta, "previous_hash": prev, "event_hash": digest}

def list_events(limit: int = 100):
    limit = max(1, min(limit, 500))
    return [dict(r) for r in db.execute("SELECT * FROM audit_events ORDER BY created_at DESC,id DESC LIMIT ?", (limit,))]

def verify_chain() -> dict:
    rows = db.execute("SELECT * FROM audit_events ORDER BY created_at ASC,id ASC")
    previous = "GENESIS"
    for row in rows:
        expected = hashlib.sha256(f"{previous}|{row['id']}|{row['created_at']}|{row['actor']}|{row['action']}|{row['resource']}|{row['metadata']}".encode()).hexdigest()
        if row["previous_hash"] != previous or row["event_hash"] != expected:
            return {"valid": False, "broken_event": row["id"]}
        previous = row["event_hash"]
    return {"valid": True, "events": len(rows), "head_hash": previous}
