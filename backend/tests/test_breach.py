import os
import pytest
from osint_core.breach_exposure import check_account

@pytest.mark.asyncio
async def test_breach_not_configured(monkeypatch):
    monkeypatch.delenv("HIBP_API_KEY", raising=False)
    result=await check_account("research@example.com")
    assert result["status"]=="not_configured"
    assert result["matches"]==[]

@pytest.mark.asyncio
async def test_breach_rejects_non_email():
    with pytest.raises(ValueError):
        await check_account("not-an-email")
