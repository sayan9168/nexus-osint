"""Evidence timeline helpers."""
from __future__ import annotations

from .models import Evidence


def build_timeline(evidence: list[Evidence]) -> list[dict]:
    return [
        {
            "id": e.id,
            "timestamp": e.observed_at.isoformat(),
            "source": e.source,
            "target": e.target,
            "confidence": e.confidence,
            "provenance_hash": e.provenance_hash,
            "summary": e.notes or f"Observed data from {e.source}",
        }
        for e in sorted(evidence, key=lambda item: item.observed_at)
    ]
