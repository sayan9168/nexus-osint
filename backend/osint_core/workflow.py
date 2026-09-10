"""Case workflow and tag primitives."""
from __future__ import annotations
import json
from osint_core.persistence import db, json_dumps
WORKFLOW_STATES = ("triage", "active", "review", "closed")
def get_case_meta(case_id: str) -> dict:
    rows = db.execute("SELECT status,tags_json,workflow FROM cases WHERE id=?", (case_id,))
    if not rows: return {}
    return {"status": rows[0]["status"], "tags": json.loads(rows[0]["tags_json"]), "workflow": rows[0]["workflow"]}
def update_case_meta(case_id: str, *, tags: list[str] | None = None, workflow: str | None = None, status: str | None = None) -> dict | None:
    current = get_case_meta(case_id)
    if not current: return None
    if tags is not None:
        clean = sorted({t.strip().lower() for t in tags if t.strip()})[:30]
        db.insert("UPDATE cases SET tags_json=? WHERE id=?", (json_dumps(clean), case_id))
    if workflow is not None:
        if workflow not in WORKFLOW_STATES: raise ValueError("invalid workflow state")
        db.insert("UPDATE cases SET workflow=? WHERE id=?", (workflow, case_id))
    if status is not None:
        if status not in ("open", "closed"): raise ValueError("invalid status")
        db.insert("UPDATE cases SET status=? WHERE id=?", (status, case_id))
    return get_case_meta(case_id)
def workflow_catalog() -> list[dict]:
    return [{"id": s, "label": s.replace("_", " ").title()} for s in WORKFLOW_STATES]
