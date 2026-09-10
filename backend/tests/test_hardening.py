from datetime import datetime, timezone

from osint_core.models import Evidence, EntityType
from osint_core.rbac import allowed
from osint_core.scoring import score_evidence
from osint_core.timeline import build_timeline


def evidence(ts: int, data=None) -> Evidence:
    return Evidence(
        source="test",
        target="example.com",
        observed_at=datetime.fromtimestamp(ts, tz=timezone.utc),
        data=data or {"ok": True},
        confidence=0.9,
    )


def test_timeline_sorts_oldest_first():
    result = build_timeline([evidence(20), evidence(10)])
    assert result[0]["timestamp"] < result[1]["timestamp"]


def test_scoring_handles_non_mapping_payload():
    item = evidence(10)
    item.data = "unexpected"  # type: ignore[assignment]
    result = score_evidence([item])
    assert 0 <= result["score"] <= 100


def test_rbac_boundaries_are_explicit():
    assert allowed("viewer", "case:read")
    assert not allowed("viewer", "scan:run")
    assert allowed("analyst", "scan:run")
    assert allowed("admin", "source:manage")
    assert not allowed("unknown", "case:read")


def test_entity_type_contract_is_stable():
    assert EntityType.DOMAIN.value == "domain"
