"""Safe breach-exposure metadata adapter."""
from __future__ import annotations
import os,re,httpx
HIBP_URL="https://haveibeenpwned.com/api/v3/breachedaccount"
EMAIL_RE=re.compile(r"^[^@\s]{1,254}@[^\s@]{1,253}$")
def _api_key()->str:return os.getenv("HIBP_API_KEY","").strip()
def _validate_account(account:str)->str:
    value=account.strip().lower()
    if len(value)>320 or not EMAIL_RE.match(value):raise ValueError("Only a valid email address is supported for breach-exposure checks.")
    return value
async def check_account(account:str)->dict:
    account=_validate_account(account);key=_api_key()
    if not key:return {"status":"not_configured","account":account,"matches":[],"message":"Set HIBP_API_KEY to enable breach metadata checks. No leaked database is stored or downloaded.","source":"Have I Been Pwned"}
    headers={"hibp-api-key":key,"user-agent":"NEXUS-OSINT/4.0 breach-exposure","accept":"application/json"};safe_url=str(httpx.URL(HIBP_URL)/account)
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(8,connect=3),follow_redirects=False) as client:r=await client.get(safe_url,params={"truncateResponse":"true"},headers=headers)
        if r.status_code==404:return {"status":"no_known_breaches","account":account,"matches":[],"source":"Have I Been Pwned"}
        if r.status_code==429:return {"status":"rate_limited","account":account,"matches":[],"source":"Have I Been Pwned"}
        if r.status_code in (401,403):return {"status":"provider_auth_error","account":account,"matches":[],"source":"Have I Been Pwned"}
        r.raise_for_status();rows=r.json() if isinstance(r.json(),list) else [];matches=[]
        for x in rows[:200]:matches.append({"name":x.get("Name"),"title":x.get("Title"),"domain":x.get("Domain"),"breach_date":x.get("BreachDate"),"added_date":x.get("AddedDate"),"modified_date":x.get("ModifiedDate"),"pwn_count":x.get("PwnCount"),"data_classes":x.get("DataClasses") or [],"is_verified":x.get("IsVerified"),"is_sensitive":x.get("IsSensitive"),"is_fabricated":x.get("IsFabricated")})
        return {"status":"match" if matches else "no_known_breaches","account":account,"matches":matches,"source":"Have I Been Pwned"}
    except httpx.HTTPError as exc:return {"status":"provider_error","account":account,"matches":[],"error":type(exc).__name__,"source":"Have I Been Pwned"}
