"""Deterministic, explainable confidence scoring for OSINT evidence."""
from __future__ import annotations

from collections.abc import Mapping

from .models import Evidence


def score_evidence(evidence: list[Evidence]) -> dict:
    """Return a bounded score without assuming a particular evidence payload shape."""
    if not evidence:
        return {"score": 0.0, "level": "unknown", "reasons": ["No evidence collected."]}

    confidence = sum(max(0.0, min(1.0, float(e.confidence))) for e in evidence) / len(evidence)
    errors = 0
    for item in evidence:
        data = item.data if isinstance(item.data, Mapping) else {}
        if "error" in data or data.get("valid_url") is False or data.get("valid_email_syntax") is False:
            errors += 1

    score = max(0.0, min(100.0, confidence * 100.0 - errors * 10.0))
    level = "high" if score >= 80 else "medium" if score >= 50 else "low"
    return {
        "score": round(score, 2),
        "level": level,
        "reasons": [
            f"Average evidence confidence: {confidence:.2f}",
            f"Evidence records: {len(evidence)}",
            f"Error/invalid records: {errors}",
        ],
    }
