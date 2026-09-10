from osint_core.collectors import normalize_target
from osint_core.models import EntityType
from osint_core.service import OSINTService


def test_normalize_domain():
    assert normalize_target(" Example.COM. ", EntityType.DOMAIN) == "example.com"


def test_scan_requires_authorization():
    result = OSINTService().scan("example.com", EntityType.DOMAIN, authorized=False)
    assert result.evidence == []
    assert result.warnings


def test_private_ip_is_not_collected():
    result = OSINTService().scan("127.0.0.1", EntityType.IP, authorized=True)
    assert result.evidence[0].data["public_routable"] is False
