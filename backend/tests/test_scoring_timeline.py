from datetime import datetime, timezone

from osint_core.models import Evidence
from osint_core.scoring import score_evidence
from osint_core.timeline import build_timeline


def test_score_is_explainable():
    evidence = [Evidence(source="test", target="example.org", confidence=0.9)]
    result = score_evidence(evidence)
    assert result["score"] == 90.0
    assert result["level"] == "high"
    assert result["reasons"]


def test_timeline_is_chronological():
    old = Evidence(source="a", target="x", observed_at=datetime(2025, 1, 1, tzinfo=timezone.utc))
    new = Evidence(source="b", target="x", observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc))
    events = build_timeline([new, old])
    assert [event["source"] for event in events] == ["a", "b"]
