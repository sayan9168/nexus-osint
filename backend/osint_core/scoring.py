"""Deterministic, explainable risk and confidence scoring for OSINT evidence."""
from __future__ import annotations

from .models import Evidence


def score_evidence(evidence: list[Evidence]) -> dict:
    if not evidence:
        return {"score": 0.0, "level": "unknown", "reasons": ["No evidence collected."]}
    confidence = sum(e.confidence for e in evidence) / len(evidence)
    errors = sum(1 for e in evidence if "error" in e.data or e.data.get("valid_url") is False or e.data.get("valid_email_syntax") is False)
    score = max(0.0, min(100.0, confidence * 100.0 - errors * 10.0))
    level = "high" if score >= 80 else "medium" if score >= 50 else "low"
    return {"score": round(score, 2), "level": level, "reasons": [f"Average evidence confidence: {confidence:.2f}", f"Evidence records: {len(evidence)}", f"Error/invalid records: {errors}"]}
