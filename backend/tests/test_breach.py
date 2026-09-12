import asyncio

import pytest

from osint_core.breach_exposure import check_account


def test_breach_not_configured(monkeypatch):
    monkeypatch.delenv("HIBP_API_KEY", raising=False)
    result = asyncio.run(check_account("research@example.com"))
    assert result["status"] == "not_configured"
    assert result["matches"] == []


def test_breach_rejects_non_email():
    with pytest.raises(ValueError):
        asyncio.run(check_account("not-an-email"))
