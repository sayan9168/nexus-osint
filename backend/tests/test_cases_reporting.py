from osint_core.cases import CaseStore
from osint_core.models import Investigation, EntityType, Evidence
from osint_core.reporting import to_markdown, to_html


def test_case_lifecycle() -> None:
    store = CaseStore()
    case = store.create("demo", "authorized test")
    assert store.add_target(case.id, "example.com").targets == ["example.com"]
    assert store.add_note(case.id, "initial observation").notes[0].body == "initial observation"
    assert store.close(case.id).status == "closed"


def test_reports_render_evidence() -> None:
    investigation = Investigation(
        target="example.com",
        target_type=EntityType.DOMAIN,
        authorized=True,
        evidence=[Evidence(source="dns", target="example.com", data={"ip": "203.0.113.10"}, confidence=0.9)],
    )
    assert "example.com" in to_markdown(investigation)
    assert "203.0.113.10" in to_html(investigation)
