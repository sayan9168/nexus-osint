from osint_core.dedup import canonicalize, unique
from osint_core.plugins import Plugin, register, list_plugins
from osint_core.models import EntityType, Evidence
from osint_core.rbac import allowed


def test_deduplication():
    assert canonicalize("Example.COM.", EntityType.DOMAIN) == "example.com"
    assert unique(["Example.com", "example.com."], EntityType.DOMAIN) == ["example.com"]


def test_rbac_policy():
    assert allowed("viewer", "case:read")
    assert not allowed("viewer", "case:write")
    assert allowed("admin", "audit:read")


def test_plugin_registry():
    name = "test-public-plugin"
    register(Plugin(name=name, version="0.1.0", entity_type=EntityType.DOMAIN,
                     description="test", collector=lambda target: [Evidence(source=name, target=target)]))
    assert any(p["name"] == name for p in list_plugins())
