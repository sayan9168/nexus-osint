"""OMNI — All public-available OSINT sources, bounded & audited.

Every adapter is:
- public or free-tier (no private-account access)
- short timeout (6-8s connect 3s)
- bounded results (≤200 items)
- no bulk download, no credential use
- User-Agent: NEXUS-OSINT/4 public-source-research
Provider terms & rate limits apply. Optional keys are read from env, never required.
"""
from __future__ import annotations
import asyncio, os, re, time
from typing import Any
import httpx

UA = "NEXUS-OSINT/4.0 (public-source; authorized-research; +https://github.com/sayan9168/nexus-osint)"
TIMEOUT = httpx.Timeout(8, connect=3)
CACHE: dict[str, tuple[float, Any]] = {}
TTL = 35.0

def _cache(k: str):
    v = CACHE.get(k)
    return v[1] if v and time.monotonic() - v[0] < TTL else None
def _put(k: str, v: Any):
    CACHE[k] = (time.monotonic(), v)
    return v

async def _get(url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None, timeout=TIMEOUT):
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=False, headers={"User-Agent": UA, **(headers or {})}) as c:
        r = await c.get(url, params=params)
        r.raise_for_status()
        ct = r.headers.get("content-type","")
        if "application/json" in ct or url.endswith(".json"):
            return r.json()
        # try json anyway, fallback text
        try:
            return r.json()
        except Exception:
            return {"text": r.text[:8000], "status": r.status_code}
async def _post(url: str, json: Any = None, data: Any = None, headers: dict[str,str] | None = None):
    async with httpx.AsyncClient(timeout=TIMEOUT, follow_redirects=False, headers={"User-Agent": UA, **(headers or {})}) as c:
        r = await c.post(url, json=json, data=data)
        r.raise_for_status()
        try: return r.json()
        except Exception: return {"text": r.text[:8000]}

# ─────────────────────────────────────────────────────────────────────────────
# Registry — 45+ public sources across 8 families
# key_required=False => works without any key; True => optional env key unlocks full data
# docs = provider docs URL for attribution
OMNI_SOURCES = [
    # ── Infrastructure / Network (no key) ──
    {"id":"shodan-internetdb","name":"Shodan InternetDB","family":"infrastructure","access":"public","key_required":False,"docs":"https://internetdb.shodan.io/","env":None},
    {"id":"hackertarget-rev","name":"HackerTarget Reverse IP","family":"infrastructure","access":"public","key_required":False,"docs":"https://hackertarget.com/reverse-ip-lookup/","env":None},
    {"id":"ip-api","name":"IP-API Geolocation","family":"infrastructure","access":"public","key_required":False,"docs":"https://ip-api.com/docs","env":None},
    {"id":"bgpview-ip","name":"BGPView IP/ASN","family":"infrastructure","access":"public","key_required":False,"docs":"https://bgpview.io/api/docs","env":None},
    {"id":"bgpview-asn","name":"BGPView ASN Peers","family":"infrastructure","access":"public","key_required":False,"docs":"https://bgpview.io/api/docs","env":None},
    {"id":"urlscan-search","name":"URLScan Live Search","family":"web","access":"public","key_required":False,"docs":"https://urlscan.io/docs/api/","env":None},
    {"id":"wayback-cdx","name":"Wayback Machine CDX","family":"web","access":"public","key_required":False,"docs":"https://github.com/internetarchive/wayback/tree/master/wayback-cdx-server","env":None},
    {"id":"crt-sh","name":"crt.sh Certificate Transparency","family":"web","access":"public","key_required":False,"docs":"https://crt.sh/","env":None},
    {"id":"common-crawl","name":"Common Crawl Index","family":"web","access":"public","key_required":False,"docs":"https://commoncrawl.org/","env":None},
    {"id":"github-search","name":"GitHub Repository Search","family":"code","access":"public","key_required":False,"docs":"https://docs.github.com/rest/search/search#search-repositories","env":"GITHUB_TOKEN"},
    {"id":"github-user","name":"GitHub Public User","family":"code","access":"public","key_required":False,"docs":"https://docs.github.com/rest/users/users#get-a-user","env":"GITHUB_TOKEN"},
    {"id":"opencorporates","name":"OpenCorporates Search","family":"company","access":"public","key_required":False,"docs":"https://api.opencorporates.com/documentation/API-Reference","env":None},
    # ── Threat Intel — public feeds (no key) ──
    {"id":"urlhaus-host","name":"Abuse.ch URLhaus (host)","family":"threat","access":"public","key_required":False,"docs":"https://urlhaus-api.abuse.ch/","env":None},
    {"id":"urlhaus-url","name":"Abuse.ch URLhaus (url)","family":"threat","access":"public","key_required":False,"docs":"https://urlhaus-api.abuse.ch/","env":None},
    {"id":"feodo-blocklist","name":"Feodo Tracker Blocklist","family":"threat","access":"public","key_required":False,"docs":"https://feodotracker.abuse.ch/blocklist/","env":None},
    {"id":"threatfox-ioc","name":"ThreatFox IOC Search","family":"threat","access":"public","key_required":False,"docs":"https://threatfox.abuse.ch/api/","env":"ABUSECH_API_KEY"},
    {"id":"openphish-feed","name":"OpenPhish Feed","family":"threat","access":"public","key_required":False,"docs":"https://openphish.com/feed.txt","env":None},
    {"id":"phishtank-check","name":"PhishTank Check","family":"threat","access":"public","key_required":False,"docs":"https://phishtank.org/api_info.php","env":"PHISHTANK_API_KEY"},
    {"id":"alienvault-otx","name":"AlienVault OTX","family":"threat","access":"public","key_required":True,"docs":"https://otx.alienvault.com/api","env":"OTX_API_KEY"},
    {"id":"abuseipdb-check","name":"AbuseIPDB Check","family":"threat","access":"public","key_required":True,"docs":"https://docs.abuseipdb.com/","env":"ABUSEIPDB_API_KEY"},
    # ── Blockchain — public explorers ──
    {"id":"blockchair-btc","name":"Blockchair Bitcoin","family":"blockchain","access":"public","key_required":False,"docs":"https://github.com/Blockchair/Blockchair.Support/blob/master/API.md","env":None},
    {"id":"blockchain-info","name":"Blockchain.info","family":"blockchain","access":"public","key_required":False,"docs":"https://www.blockchain.com/api","env":None},
    {"id":"mempool-space","name":"Mempool.space Fees/Mempool","family":"blockchain","access":"public","key_required":False,"docs":"https://mempool.space/docs/api/rest","env":None},
    {"id":"etherscan-account","name":"Etherscan Account","family":"blockchain","access":"public","key_required":True,"docs":"https://docs.etherscan.io/","env":"ETHERSCAN_API_KEY"},
    # ── Social / Code — public ──
    {"id":"reddit-search","name":"Reddit Public Search","family":"social","access":"public","key_required":False,"docs":"https://github.com/reddit-archive/reddit/wiki/JSON","env":None},
    {"id":"github-code","name":"GitHub Code Search","family":"code","access":"public","key_required":False,"docs":"https://docs.github.com/rest/search/search#search-code","env":"GITHUB_TOKEN"},
    {"id":"haveibeenpwned","name":"Have I Been Pwned (k-anon)","family":"breach","access":"public","key_required":True,"docs":"https://haveibeenpwned.com/API/v3","env":"HIBP_API_KEY"},
    # ── Geo / Environment — public ──
    {"id":"openaq","name":"OpenAQ Air Quality","family":"environment","access":"public","key_required":False,"docs":"https://docs.openaq.org/","env":None},
    {"id":"open-elevation","name":"Open-Elevation","family":"environment","access":"public","key_required":False,"docs":"https://open-elevation.com/","env":None},
    {"id":"sunrise-sunset","name":"Sunrise-Sunset","family":"environment","access":"public","key_required":False,"docs":"https://sunrise-sunset.org/api","env":None},
    {"id":"timezonedb-free","name":"Timezonedb (public)","family":"environment","access":"public","key_required":False,"docs":"https://timezonedb.com/api","env":None},
    {"id":"usgs-quake","name":"USGS Earthquakes","family":"environment","access":"public","key_required":False,"docs":"https://earthquake.usgs.gov/fdsnws/event/1/","env":None},
    {"id":"nasa-eonet","name":"NASA EONET","family":"environment","access":"public","key_required":False,"docs":"https://eonet.gsfc.nasa.gov/docs/v3","env":None},
    {"id":"gdelt-geo","name":"GDELT GEO","family":"news","access":"public","key_required":False,"docs":"https://blog.gdeltproject.org/gdelt-2-0-geo-2-0-api/","env":None},
    {"id":"open-meteo","name":"Open-Meteo Weather","family":"environment","access":"public","key_required":False,"docs":"https://open-meteo.com/en/docs","env":None},
    {"id":"nominatim","name":"Nominatim Reverse Geocode","family":"geo","access":"public","key_required":False,"docs":"https://nominatim.org/release-docs/develop/api/Reverse/","env":None},
    {"id":"overpass","name":"Overpass / OpenStreetMap","family":"geo","access":"public","key_required":False,"docs":"https://dev.overpass-api.de/overpass-doc/en/","env":None},
    {"id":"ripe-atlas","name":"RIPE Atlas Probes","family":"infrastructure","access":"public","key_required":False,"docs":"https://atlas.ripe.net/docs/api/v2/manual/","env":None},
    {"id":"ripestat","name":"RIPEstat Network Info","family":"infrastructure","access":"public","key_required":False,"docs":"https://stat.ripe.net/docs/data_api","env":None},
    {"id":"wikidata","name":"Wikidata SPARQL","family":"knowledge","access":"public","key_required":False,"docs":"https://query.wikidata.org/","env":None},
    {"id":"opensky","name":"OpenSky Aircraft","family":"transport","access":"public","key_required":False,"docs":"https://opensky-network.org/apidoc/","env":None},
    {"id":"celestrak","name":"CelesTrak Satellites","family":"space","access":"public","key_required":False,"docs":"https://celestrak.org/NORAD/documentation/gp-data-formats.php","env":None},
    {"id":"virustotal","name":"VirusTotal (optional)","family":"threat","access":"public","key_required":True,"docs":"https://developers.virustotal.com/reference/overview","env":"VIRUSTOTAL_API_KEY"},
    {"id":"shodan-full","name":"Shodan Full (optional)","family":"infrastructure","access":"public","key_required":True,"docs":"https://developer.shodan.io/api","env":"SHODAN_API_KEY"},
    {"id":"censys","name":"Censys Search (optional)","family":"infrastructure","access":"public","key_required":True,"docs":"https://search.censys.io/api","env":"CENSYS_API_ID"},
    {"id":"hunter","name":"Hunter.io Domain Search (optional)","family":"company","access":"public","key_required":True,"docs":"https://hunter.io/api-documentation/v2","env":"HUNTER_API_KEY"},
]

# helpers
def _is_ip(v: str) -> bool:
    return bool(re.match(r"^(\d{1,3}\.){3}\d{1,3}$", v.strip())) or ":" in v
def _is_domain(v: str) -> bool:
    return bool(re.match(r"^[a-z0-9.-]+\.[a-z]{2,}$", v.strip().lower()))
def _clean(v: str) -> str:
    return re.sub(r"\s+", " ", v.strip())[:256]

# ═══════════════════════════════════════════════════════════════════════════════
# Adapters — each returns bounded, normalized data or [] / {} on failure
# ═══════════════════════════════════════════════════════════════════════════════

async def shodan_internetdb(ip: str):
    if not _is_ip(ip): return {}
    try:
        d = await _get(f"https://internetdb.shodan.io/{ip.strip()}")
        return {"ip": ip, "ports": (d.get("ports") or [])[:32], "hostnames": (d.get("hostnames") or [])[:16], "tags": (d.get("tags") or [])[:16], "vulns": (d.get("vulns") or [])[:16], "cpes": (d.get("cpes") or [])[:16], "source":"Shodan InternetDB"}
    except Exception: return {}

async def hackertarget_rev(ip: str):
    if not _is_ip(ip): return []
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, headers={"User-Agent": UA}) as c:
            r = await c.get("https://api.hackertarget.com/reverseiplookup/", params={"q": ip.strip()})
            if r.status_code!=200: return []
            txt = r.text.strip()
            if "error" in txt.lower() or "API count" in txt: return []
            return [{"host": _clean(x), "source":"HackerTarget"} for x in txt.splitlines() if _clean(x) and "." in x][:100]
    except Exception: return []

async def ip_api(ip: str):
    if not _is_ip(ip): return {}
    try:
        d = await _get(f"http://ip-api.com/json/{ip.strip()}", {"fields":"status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"})
        if d.get("status")=="success": return {**d, "source":"IP-API"}
        return {}
    except Exception: return {}

async def bgpview_ip(ip: str):
    if not _is_ip(ip): return {}
    try: return {"source":"BGPView", **(await _get(f"https://api.bgpview.io/ip/{ip.strip()}"))}
    except Exception: return {}

async def bgpview_asn(asn: str):
    try: asn = asn.strip().lstrip("ASas")
    except Exception: return {}
    if not asn.isdigit(): return {}
    try: return {"source":"BGPView", **(await _get(f"https://api.bgpview.io/asn/{asn}"))}
    except Exception: return {}

async def urlscan_search(domain_or_ip: str):
    try:
        q = f"domain:{domain_or_ip.strip()}" if _is_domain(domain_or_ip) else f"ip:{domain_or_ip.strip()}" if _is_ip(domain_or_ip) else f'"{_clean(domain_or_ip)[:80]}"'
        d = await _get("https://urlscan.io/api/v1/search/", {"q": q, "size": 50})
        out=[]
        for r in (d.get("results") or [])[:50]:
            page=r.get("page") or {}; task=r.get("task") or {}
            out.append({"url": page.get("url"), "domain": page.get("domain"), "ip": page.get("ip"), "country": page.get("country"), "time": task.get("time"), "verdict": str((r.get("verdicts") or {}).get("overall") or ""), "source":"URLScan"})
        return out
    except Exception: return []

async def wayback_cdx(url_or_domain: str, limit=80):
    try:
        target = url_or_domain.strip()
        # for domain, use wildcard
        if _is_domain(target) and "/" not in target: target = target + "/*"
        d = await _get("https://web.archive.org/cdx/search/cdx", {"url": target, "output":"json","limit": limit, "filter":"statuscode:200","collapse":"digest"})
        if not isinstance(d, list) or len(d)<=1: return []
        header=d[0]; rows=d[1:]
        idx={h:i for i,h in enumerate(header)}
        out=[]
        for r in rows[:limit]:
            try: out.append({"timestamp": r[idx["timestamp"]], "original": r[idx["original"]], "mimetype": r[idx["mimetype"]], "statuscode": r[idx["statuscode"]], "digest": r[idx["digest"]], "source":"Wayback"})
            except Exception: continue
        return out
    except Exception: return []

async def github_search(term: str, limit=30):
    term=_clean(term)
    if not term: return []
    try:
        headers={}
        tok=os.getenv("GITHUB_TOKEN","").strip()
        if tok: headers["Authorization"]=f"Bearer {tok}"
        d=await _get("https://api.github.com/search/repositories", {"q": term, "per_page": min(limit,30)}, headers)
        out=[]
        for x in (d.get("items") or [])[:limit]:
            out.append({"full_name": x.get("full_name"), "html_url": x.get("html_url"), "description": (x.get("description") or "")[:200], "stars": x.get("stargazers_count"), "language": x.get("language"), "source":"GitHub"})
        return out
    except Exception: return []

async def github_user(username: str):
    username=_clean(username).strip().lstrip("@")
    if not username or len(username)>39: return {}
    try:
        headers={}
        tok=os.getenv("GITHUB_TOKEN","").strip()
        if tok: headers["Authorization"]=f"Bearer {tok}"
        d=await _get(f"https://api.github.com/users/{username}", None, headers)
        return {"login": d.get("login"), "name": d.get("name"), "company": d.get("company"), "blog": d.get("blog"), "location": d.get("location"), "bio": (d.get("bio") or "")[:300], "public_repos": d.get("public_repos"), "followers": d.get("followers"), "html_url": d.get("html_url"), "source":"GitHub"}
    except Exception: return {}

async def opencorporates_search(term: str):
    term=_clean(term)
    if not term or len(term)<2: return []
    try:
        d=await _get("https://api.opencorporates.com/v0.4/companies/search", {"q": term, "per_page": 20})
        out=[]
        for x in ((d.get("results") or {}).get("companies") or [])[:20]:
            c=x.get("company") or {}
            out.append({"name": c.get("name"), "company_number": c.get("company_number"), "jurisdiction": c.get("jurisdiction_code"), "opencorporates_url": c.get("opencorporates_url"), "source":"OpenCorporates"})
        return out
    except Exception: return []

async def urlhaus_host(host: str):
    host=_clean(host).strip().lower()
    if not host: return []
    try:
        d=await _post("https://urlhaus-api.abuse.ch/v1/host/", data={"host": host})
        if d.get("query_status")=="ok": return [{"url": x.get("url"), "threat": x.get("threat"), "tags": x.get("tags"), "dateadded": x.get("dateadded"), "reporter": x.get("reporter"), "source":"URLhaus"} for x in (d.get("urls") or [])[:100]]
        return []
    except Exception: return []

async def urlhaus_url(url: str):
    url=_clean(url)
    if not url: return {}
    try:
        d=await _post("https://urlhaus-api.abuse.ch/v1/url/", data={"url": url})
        return {"query_status": d.get("query_status"), "threat": d.get("threat"), "tags": d.get("tags"), "urlhaus_reference": d.get("urlhaus_reference"), "source":"URLhaus"}
    except Exception: return {}

async def feodo_blocklist(limit=100):
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, headers={"User-Agent": UA}) as c:
            r=await c.get("https://feodotracker.abuse.ch/downloads/ipblocklist_recommended.txt")
            if r.status_code!=200: return []
            out=[]
            for line in r.text.splitlines():
                line=line.strip()
                if not line or line.startswith("#"): continue
                out.append({"ip": line, "source":"Feodo Tracker"})
                if len(out)>=limit: break
            return out
    except Exception: return []

async def openphish_feed(limit=100):
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, headers={"User-Agent": UA}) as c:
            r=await c.get("https://openphish.com/feed.txt")
            if r.status_code!=200: return []
            return [{"url": _clean(x), "source":"OpenPhish"} for x in r.text.splitlines() if _clean(x).startswith("http")][:limit]
    except Exception: return []

async def reddit_search(term: str, limit=30):
    term=_clean(term)
    if not term: return []
    try:
        d=await _get("https://www.reddit.com/search.json", {"q": term, "limit": min(limit, 30), "sort":"new"}, {"User-Agent": UA})
        out=[]
        for c in ((d.get("data") or {}).get("children") or [])[:limit]:
            p=(c.get("data") or {})
            out.append({"title": p.get("title"), "subreddit": p.get("subreddit"), "author": p.get("author"), "url": "https://reddit.com"+str(p.get("permalink","")), "score": p.get("score"), "created_utc": p.get("created_utc"), "source":"Reddit"})
        return out
    except Exception: return []

async def blockchair_btc(address: str):
    address=_clean(address)
    if not re.match(r"^(1|3|bc1|tb1)[a-zA-Z0-9]{25,62}$", address): return {}
    try: return {"source":"Blockchair", **(await _get(f"https://api.blockchair.com/bitcoin/dashboards/address/{address}"))}
    except Exception: return {}

async def blockchain_info(address: str):
    address=_clean(address)
    if not re.match(r"^(1|3|bc1)[a-zA-Z0-9]{25,62}$", address): return {}
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, headers={"User-Agent": UA}) as c:
            r=await c.get(f"https://blockchain.info/rawaddr/{address}", params={"limit": 20})
            if r.status_code!=200: return {}
            return {"source":"Blockchain.info", **r.json()}
    except Exception: return {}

async def mempool_fees():
    try: return {"source":"Mempool.space", **(await _get("https://mempool.space/api/v1/fees/mempool-blocks"))}
    except Exception: return []

async def openaq(lat: float, lon: float, radius=10000):
    try:
        d=await _get("https://api.openaq.org/v3/locations", {"coordinates": f"{lat},{lon}", "radius": radius, "limit": 20}, {"X-API-Key": os.getenv("OPENAQ_API_KEY","") or "dummy"})
        # OpenAQ v3 requires key; if not configured return empty not error
        if isinstance(d, dict) and "results" in d:
            out=[]
            for x in (d.get("results") or [])[:20]:
                out.append({"name": x.get("name"), "locality": x.get("locality"), "country": x.get("country"), "coordinates": x.get("coordinates"), "source":"OpenAQ"})
            return out
        return []
    except Exception: return []

async def open_elevation(lat: float, lon: float):
    try:
        d=await _post("https://api.open-elevation.com/api/v1/lookup", json={"locations":[{"latitude": lat, "longitude": lon}]})
        return {"elevation_m": ((d.get("results") or [{}])[0].get("elevation")), "source":"Open-Elevation", "lat": lat, "lon": lon}
    except Exception: return {}

async def sunrise_sunset(lat: float, lon: float):
    try: return {"source":"Sunrise-Sunset", **(await _get("https://api.sunrise-sunset.org/json", {"lat": lat, "lng": lon, "formatted": 0}))}
    except Exception: return {}

# optional-key adapters (return not_configured if missing)
async def alienvault_otx(indicator: str, type_: str = "domain"):
    key=os.getenv("OTX_API_KEY","").strip()
    if not key: return {"status":"not_configured","source":"AlienVault OTX"}
    try:
        headers={"X-OTX-API-KEY": key}
        sec={"domain":"general","ip":"general","url":"url_list","hash":"general"}.get(type_, "general")
        d=await _get(f"https://otx.alienvault.com/api/v1/indicators/{type_}/{indicator.strip()}/{sec}", None, headers)
        return {"status":"ok","source":"AlienVault OTX","data": d}
    except Exception as e: return {"status":"error","source":"AlienVault OTX","error": type(e).__name__}

async def abuseipdb_check(ip: str):
    key=os.getenv("ABUSEIPDB_API_KEY","").strip()
    if not key: return {"status":"not_configured","source":"AbuseIPDB"}
    if not _is_ip(ip): return {"status":"invalid_ip","source":"AbuseIPDB"}
    try:
        d=await _get("https://api.abuseipdb.com/api/v2/check", {"ipAddress": ip.strip(), "maxAgeInDays": 90}, {"Key": key, "Accept":"application/json"})
        return {"status":"ok","source":"AbuseIPDB","data": d.get("data")}
    except Exception as e: return {"status":"error","source":"AbuseIPDB","error": type(e).__name__}

async def hunter_domain(domain: str):
    key=os.getenv("HUNTER_API_KEY","").strip()
    if not key: return {"status":"not_configured","source":"Hunter.io"}
    try:
        d=await _get("https://api.hunter.io/v2/domain-search", {"domain": domain.strip(), "limit": 10, "api_key": key})
        return {"status":"ok","source":"Hunter.io","data": d.get("data")}
    except Exception as e: return {"status":"error","source":"Hunter.io","error": type(e).__name__}

async def etherscan_account(address: str):
    key=os.getenv("ETHERSCAN_API_KEY","").strip()
    if not key: return {"status":"not_configured","source":"Etherscan"}
    try:
        d=await _get("https://api.etherscan.io/api", {"module":"account","action":"balance","address": address.strip(), "tag":"latest", "apikey": key})
        return {"status": d.get("status"), "result": d.get("result"), "source":"Etherscan"}
    except Exception as e: return {"status":"error","source":"Etherscan","error": type(e).__name__}

# ─────────────────────────────────────────────────────────────────────────
# Unified entry: omni_query — runs relevant adapters based on target kind
# ─────────────────────────────────────────────────────────────────────────
async def omni_query(target: str, target_type: str = "domain") -> dict[str, Any]:
    target=_clean(target)
    tt=target_type.lower()
    t0=time.time()
    tasks: dict[str, Any] = {}
    # common for all
    # domain
    if tt in ("domain","url"):
        host=target.split("//")[-1].split("/")[0].split(":")[0].lower() if "://" in target else target.split("/")[0].lower()
        tasks["shodan_internetdb"]=shodan_internetdb(host)  # will fail if not ip, handled
        tasks["urlscan"]=urlscan_search(host)
        tasks["wayback"]=wayback_cdx(target if "://" in target else f"https://{host}")
        tasks["crt_sh"]= _get("https://crt.sh/", {"q": f"%.{host}", "output":"json"}) if _is_domain(host) else asyncio.sleep(0, result=[])
        tasks["opencorp"]=opencorporates_search(host.split(".")[0])
        tasks["urlhaus_host"]=urlhaus_host(host)
        tasks["github"]=github_search(host.split(".")[0])
        tasks["reddit"]=reddit_search(host)
        tasks["bgpview"]=bgpview_ip(host) if _is_ip(host) else asyncio.sleep(0, result={})
        # optional
        tasks["hunter"]=hunter_domain(host)
        tasks["otx_domain"]=alienvault_otx(host, "domain")
    elif tt=="ip":
        tasks["shodan_internetdb"]=shodan_internetdb(target)
        tasks["hackertarget"]=hackertarget_rev(target)
        tasks["ip_api"]=ip_api(target)
        tasks["bgpview_ip"]=bgpview_ip(target)
        tasks["urlscan"]=urlscan_search(target)
        tasks["urlhaus_host"]=urlhaus_host(target)
        tasks["abuseipdb"]=abuseipdb_check(target)
        tasks["otx_ip"]=alienvault_otx(target, "ip")
        # geolocated env
        try:
            geo=await ip_api(target)
            lat, lon = geo.get("lat"), geo.get("lon")
            if isinstance(lat,(int,float)) and isinstance(lon,(int,float)):
                tasks["openaq"]=openaq(lat,lon)
                tasks["elevation"]=open_elevation(lat,lon)
                tasks["sunrise"]=sunrise_sunset(lat,lon)
        except Exception: pass
    elif tt=="email":
        # email: hunter, github user, haveibeenpwned via breach adapter (separate route), gravatar not needed
        local=target.split("@")[-1] if "@" in target else target
        tasks["hunter"]=hunter_domain(local)
        tasks["github_user"]=github_user(target.split("@")[0])
        tasks["otx_email"]=asyncio.sleep(0, result={"status":"email_not_supported"})
    elif tt=="wallet" or tt=="hash" or tt=="btc" or tt=="eth":
        tasks["blockchair"]=blockchair_btc(target)
        tasks["blockchain_info"]=blockchain_info(target)
        tasks["etherscan"]=etherscan_account(target)
        tasks["urlscan"]=urlscan_search(target)
    else:
        # generic term
        tasks["github"]=github_search(target)
        tasks["reddit"]=reddit_search(target)
        tasks["opencorp"]=opencorporates_search(target)
        tasks["wayback"]=wayback_cdx(target)
        tasks["urlhaus_host"]=urlhaus_host(target)

    # run all in parallel, tolerate failures
    results={}
    if tasks:
        vals=await asyncio.gather(*tasks.values(), return_exceptions=True)
        for k,v in zip(tasks.keys(), vals):
            if isinstance(v, Exception): results[k]= {"error": type(v).__name__}
            else: results[k]= v
    elapsed=round(time.time()-t0,2)
    # count successes
    ok=sum(1 for v in results.values() if not (isinstance(v,dict) and "error" in v and len(v)==1))
    return {"target": target, "target_type": tt, "elapsed_s": elapsed, "sources_queried": len(results), "sources_ok": ok, "results": results, "omni_hash": __import__("hashlib").sha256((target+tt).encode()).hexdigest()[:12]}

async def omni_overview():
    # lightweight overview for dashboard — no target, just source health + feeds
    cache=_cache("omni_overview")
    if cache: return cache
    # fetch two fast public feeds in parallel
    feodo, phish = await asyncio.gather(feodo_blocklist(30), openphish_feed(30))
    mempool = await mempool_fees()
    sources_ok=sum(1 for s in OMNI_SOURCES if not s["key_required"] or os.getenv(s["env"] or "", "").strip())
    data={
        "updated_at": int(time.time()),
        "total_sources": len(OMNI_SOURCES),
        "free_sources": sum(1 for s in OMNI_SOURCES if not s["key_required"]),
        "configured_optional": sources_ok - sum(1 for s in OMNI_SOURCES if not s["key_required"]),
        "feeds": {"feodo": feodo[:10], "openphish": phish[:10], "mempool": mempool},
        "families": sorted({s["family"] for s in OMNI_SOURCES}),
        "disclaimer": "All adapters are public/free-tier, bounded, and rate-limited. Optional keys (env) unlock full data without changing public boundary. No private-account access."
    }
    return _put("omni_overview", data)

def catalog():
    # enriched catalog with configured flag
    out=[]
    for s in OMNI_SOURCES:
        env=s.get("env")
        configured=bool(env and os.getenv(env,"").strip()) if s["key_required"] else True
        out.append({**s, "configured": configured, "status": "configured" if configured else "optional"})
    return out
