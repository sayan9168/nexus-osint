"""Additional bounded public-source adapters for spatial context.

All adapters use public endpoints, short timeouts, bounded result sizes and
no authenticated/private-account access. Provider terms and rate limits apply.
"""
from __future__ import annotations
import asyncio, time
from typing import Any
import httpx

EONET_URL = "https://eonet.gsfc.nasa.gov/api/v3/events"
GDELT_URL = "https://api.gdeltproject.org/api/v2/geo/geo"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
NOAA_ALERTS_URL = "https://api.weather.gov/alerts/active"
CRT_URL = "https://crt.sh/"
RIPE_PROBES_URL = "https://atlas.ripe.net/api/v2/probes/"
RIPESTAT_URL = "https://stat.ripe.net/data/network-info/data.json"
WIKIDATA_URL = "https://query.wikidata.org/sparql"
_CACHE: dict[str, tuple[float, Any]] = {}
TTL = 30.0

SOURCES = [
    {"id":"nasa-eonet","name":"NASA EONET","kind":"natural-events","access":"public","key_required":False},
    {"id":"gdelt-geo","name":"GDELT GEO","kind":"public-news-events","access":"public","key_required":False},
    {"id":"osm-overpass","name":"OpenStreetMap / Overpass","kind":"map-context","access":"public","key_required":False},
    {"id":"nominatim","name":"Nominatim","kind":"reverse-geocoding","access":"public","key_required":False},
    {"id":"open-meteo","name":"Open-Meteo","kind":"weather","access":"public","key_required":False},
    {"id":"noaa-alerts","name":"NOAA Weather Alerts","kind":"weather-alerts","access":"public","key_required":False},
    {"id":"wikidata","name":"Wikidata / SPARQL","kind":"open-knowledge","access":"public","key_required":False},
    {"id":"common-crawl","name":"Common Crawl Index","kind":"web-archive","access":"public","key_required":False},
    {"id":"crt-sh","name":"crt.sh Certificate Transparency","kind":"certificate-transparency","access":"public","key_required":False},
    {"id":"ripe-atlas","name":"RIPE Atlas","kind":"internet-measurements","access":"public","key_required":False},
    {"id":"ripestat","name":"RIPEstat","kind":"internet-routing","access":"public","key_required":False},
]

async def _get(url: str, params: dict[str, Any] | None = None, headers: dict[str, str] | None = None):
    async with httpx.AsyncClient(timeout=httpx.Timeout(8, connect=3), follow_redirects=False) as c:
        r = await c.get(url, params=params, headers={"User-Agent":"NEXUS-OSINT/3.3 public-source-research", **(headers or {})})
        r.raise_for_status()
        return r.json()

def _cache(key: str):
    x = _CACHE.get(key)
    return x[1] if x and time.monotonic() - x[0] < TTL else None

def _put(key: str, value: Any):
    _CACHE[key] = (time.monotonic(), value)
    return value

async def natural_events():
    try:
        d = await _get(EONET_URL, {"status":"open", "limit":300}); out=[]
        for e in (d.get("events") or [])[:300]:
            g=(e.get("geometry") or [])[-1:]
            if not g: continue
            c=g[0].get("coordinates") or []
            if len(c)<2: continue
            try: lon,lat=float(c[0]),float(c[1])
            except (TypeError,ValueError): continue
            if -180<=lon<=180 and -90<=lat<=90:
                out.append({"id":e.get("id"),"kind":"natural_event","label":e.get("title"),"lat":lat,"lon":lon,"time":g[0].get("date"),"source":"NASA EONET","categories":[x.get("title") for x in e.get("categories",[])][:5]})
        return out
    except Exception: return []

async def news_events():
    try:
        d=await _get(GDELT_URL,{"query":"world","format":"GeoJSON","timespan":"24h","maxpoints":200}); out=[]
        for f in (d.get("features") or [])[:200]:
            c=(f.get("geometry") or {}).get("coordinates") or []; p=f.get("properties") or {}
            if len(c)<2: continue
            try: lon,lat=float(c[0]),float(c[1])
            except (TypeError,ValueError): continue
            if -180<=lon<=180 and -90<=lat<=90: out.append({"id":str(p.get("id") or f.get("id") or len(out)),"kind":"news_event","label":p.get("name") or p.get("title") or "Public news event","lat":lat,"lon":lon,"source":"GDELT GEO","url":p.get("url")})
        return out
    except Exception: return []

async def ripe_probes():
    try:
        d=await _get(RIPE_PROBES_URL,{"status":1,"is_public":1,"limit":500}); out=[]
        for p in d.get("results",[]):
            lat,lon=p.get("latitude"),p.get("longitude")
            if lat is not None and lon is not None: out.append({"id":str(p.get("id")),"kind":"internet_probe","label":p.get("country_code") or "RIPE probe","lat":lat,"lon":lon,"asn":p.get("asn_v4"),"source":"RIPE Atlas"})
        return out
    except Exception: return []

async def crt_subdomains(domain: str):
    """Passive certificate-transparency lookup; domain must be explicitly supplied."""
    domain=domain.strip().lower().lstrip("*.")
    if not domain or len(domain)>253 or any(c in domain for c in "/\\ \t\r\n"): return []
    try:
        data=await _get(CRT_URL,{"q":f"%.{domain}","output":"json"}); names=set()
        for row in data[:500]:
            for name in str(row.get("name_value") or "").splitlines():
                name=name.strip().lower().lstrip("*.")
                if name==domain or name.endswith("."+domain): names.add(name)
        return [{"name":n,"source":"crt.sh","kind":"certificate_name"} for n in sorted(names)[:500]]
    except Exception:return []

async def ripestat_network(asn_or_ip: str):
    value=asn_or_ip.strip()
    if not value or len(value)>128:return {}
    try:return await _get(RIPESTAT_URL,{"resource":value})
    except Exception:return {}

async def wikidata_search(term: str):
    term=term.strip()
    if not term or len(term)>120:return []
    query="SELECT ?item ?itemLabel ?coord WHERE { ?item rdfs:label ?itemLabel. FILTER(CONTAINS(LCASE(STR(?itemLabel)), LCASE(%s))). OPTIONAL { ?item wdt:P625 ?coord. } SERVICE wikibase:label { bd:serviceParam wikibase:language \"en\". } } LIMIT 50" % repr(term)
    try:
        d=await _get(WIKIDATA_URL,{"query":query,"format":"json"},{"Accept":"application/sparql-results+json"})
        out=[]
        for b in d.get("results",{}).get("bindings",[]): out.append({"id":b.get("item",{}).get("value"),"label":b.get("itemLabel",{}).get("value"),"coordinate":b.get("coord",{}).get("value"),"source":"Wikidata"})
        return out
    except Exception:return []

async def context(lat: float, lon: float, radius_m: int = 3000):
    lat, lon = float(lat), float(lon); radius_m=max(250,min(int(radius_m),5000)); key=f"context:{lat:.4f}:{lon:.4f}:{radius_m}"
    cached=_cache(key)
    if cached is not None:return cached
    query=f"[out:json][timeout:6];(nwr(around:{radius_m},{lat},{lon})[name];nwr(around:{radius_m},{lat},{lon})[amenity];nwr(around:{radius_m},{lat},{lon})[public_transport];);out center tags 120;"
    async def osm():
        try:return await _get(OVERPASS_URL,{"data":query})
        except Exception:return {"elements":[]}
    async def reverse():
        try:return await _get(NOMINATIM_URL,{"lat":lat,"lon":lon,"format":"jsonv2","zoom":18})
        except Exception:return {}
    async def weather():
        try:return await _get(WEATHER_URL,{"latitude":lat,"longitude":lon,"current":"temperature_2m,relative_humidity_2m,wind_speed_10m,wind_direction_10m,weather_code","hourly":"precipitation_probability,visibility","forecast_days":1})
        except Exception:return {}
    async def alerts():
        if not (-130<=lon<=-60 and 20<=lat<=55):return {"features":[]}
        try:return await _get(NOAA_ALERTS_URL,{"point":f"{lat},{lon}"},{"Accept":"application/geo+json"})
        except Exception:return {"features":[]}
    od,rd,wd,ad=await asyncio.gather(osm(),reverse(),weather(),alerts()); pois=[]
    for e in (od.get("elements") or [])[:200]:
        t=e.get("tags") or {}; c=e.get("center") or {}
        try:a=float(e.get("lat",c.get("lat"))); b=float(e.get("lon",c.get("lon")))
        except (TypeError,ValueError):continue
        if -90<=a<=90 and -180<=b<=180:pois.append({"id":str(e.get("id")),"kind":"osm_poi","label":t.get("name") or t.get("amenity") or t.get("public_transport") or "OSM feature","lat":a,"lon":b,"source":"OpenStreetMap","tags":t})
    alerts=[{"id":f.get("id"),"kind":"weather_alert","label":(f.get("properties") or {}).get("headline"),"source":"NOAA","severity":(f.get("properties") or {}).get("severity")} for f in (ad.get("features") or [])[:30]]
    return _put(key,{"center":{"lat":lat,"lon":lon},"reverse_geocode":rd,"weather":wd,"weather_alerts":alerts,"osm":pois,"sources":["OpenStreetMap/Overpass","Nominatim","Open-Meteo","NOAA Weather Alerts"]})

async def public_snapshot():
    cached=_cache("snapshot")
    if cached is not None:return cached
    natural,news,probes=await asyncio.gather(natural_events(),news_events(),ripe_probes())
    return _put("snapshot",{"updated_at":int(time.time()),"layers":{"natural_events":natural,"news_events":news,"internet_probes":probes},"sources":SOURCES,"disclaimer":"Public open data can be delayed, incomplete, rate-limited or subject to provider-specific terms. NEXUS is limited to public/authorized research and does not perform named-person tracking, face recognition, private-account access or safety-critical navigation."})
