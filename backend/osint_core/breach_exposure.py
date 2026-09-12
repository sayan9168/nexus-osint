"""Safe breach-exposure metadata adapter.

This module deliberately does not ingest, download, search, or redistribute
raw leaked databases, credentials, tokens, or stealer logs. It can query the
Have I Been Pwned API when an operator supplies an API key and returns breach
metadata only (service name, date, categories). Provider terms and rate limits
apply.
"""
from __future__ import annotations
import os
import re
import httpx

HIBP_URL = "https://haveibeenpwned.com/api/v3/breachedaccount"
EMAIL_RE = re.compile(r"^[^@\s]{1,254}@[^ -\u007f\s]{1,253}$")

def _api_key() -> str:
    return os.getenv("HIBP_API_KEY", "").strip()

def _validate_account(account: str) -> str:
    value = account.strip().lower()
    if len(value) > 320 or "@" not in value or not EMAIL_RE.match(value):
        raise ValueError("Only a valid email address is supported for breach-exposure checks.")
    return value

async def check_account(account: str) -> dict:
    account = _validate_account(account)
    key = _api_key()
    if not key:
        return {"status":"not_configured","account":account,"matches":[],"message":"Set HIBP_API_KEY to enable breach metadata checks. No leaked database is stored or downloaded.","source":"Have I Been Pwned"}
    headers={"hibp-api-key":key,"user-agent":"NEXUS-OSINT/4.0 breach-exposure","accept":"application/json"}
    safe_url=str(httpx.URL(HIBP_URL) / account)
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(8,connect=3),follow_redirects=False) as client:
            response=await client.get(safe_url,params={"truncateResponse":"true"},headers=headers)
        if response.status_code==404:return {"status":"no_known_breaches","account":account,"matches":[],"source":"Have I Been Pwned"}
        if response.status_code==429:return {"status":"rate_limited","account":account,"matches":[],"source":"Have I Been Pwned"}
        if response.status_code in (401,403):return {"status":"provider_auth_error","account":account,"matches":[],"source":"Have I Been Pwned"}
        response.raise_for_status(); payload=response.json(); rows=payload if isinstance(payload,list) else []
        matches=[]
        for item in rows[:200]:
            matches.append({"name":item.get("Name"),"title":item.get("Title"),"domain":item.get("Domain"),"breach_date":item.get("BreachDate"),"added_date":item.get("AddedDate"),"modified_date":item.get("ModifiedDate"),"pwn_count":item.get("PwnCount"),"data_classes":item.get("DataClasses") or [],"is_verified":item.get("IsVerified"),"is_sensitive":item.get("IsSensitive"),"is_fabricated":item.get("IsFabricated")})
        return {"status":"match" if matches else "no_known_breaches","account":account,"matches":matches,"source":"Have I Been Pwned"}
    except httpx.HTTPError as exc:
        return {"status":"provider_error","account":account,"matches":[],"error":type(exc).__name__,"source":"Have I Been Pwned"}
