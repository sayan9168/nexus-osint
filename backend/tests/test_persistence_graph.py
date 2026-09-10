from datetime import datetime, timezone

from osint_core.cases import Case
from osint_core.graph import project
from osint_core.models import Evidence


def test_graph_projection_contains_provenance():
    ev = Evidence(
        source="rdap",
        target="example.org",
        observed_at=datetime.now(timezone.utc),
        data={"status": ["active"]},
        confidence=0.9,
        provenance_hash="abc123",
    )
    case = Case(name="graph", targets=["example.org"], evidence=[ev])
    graph = project(case)
    assert {n.kind for n in graph.nodes} == {"target", "source"}
    assert len(graph.edges) == 1
    assert graph.edges[0].provenance_hash == "abc123"
