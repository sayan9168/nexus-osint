"""Bounded public-source spatial intelligence adapters."""
from __future__ import annotations
import asyncio, json, math, os, time
from typing import Any
import httpx
USGS_URL="https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
OPENSKY_URL="https://opensky-network.org/api/states/all"
CELESTRAK_URL="https://celestrak.org/NORAD/elements/gp.php"
LAUNCH_URL="https://ll.thespacedevs.com/2.2.0/launch/upcoming/"
RADIO_URL="https://de1.api.radio-browser.info/json/stations/topclick/100"
_CACHE:dict[str,tuple[float,Any]]={}; TTL=30.0

def _cached(k):
    x=_CACHE.get(k); return x[1] if x and time.monotonic()-x[0]<TTL else None

def _put(k,v): _CACHE[k]=(time.monotonic(),v); return v
async def _get(url,params=None):
    async with httpx.AsyncClient(timeout=httpx.Timeout(8,connect=3),follow_redirects=False) as c:
        r=await c.get(url,params=params,headers={"User-Agent":"NEXUS-OSINT/3.1"}); r.raise_for_status(); return r.json()
def _num(v):
    try:
        x=float(v); return x if math.isfinite(x) else None
    except (TypeError,ValueError): return None
def _coord(v):
    if isinstance(v,dict):
        a,b=_num(v.get("lat",v.get("latitude"))),_num(v.get("lon",v.get("longitude")))
        if a is not None and b is not None and -90<=a<=90 and -180<=b<=180:return a,b
        for x in v.values():
            z=_coord(x)
            if z:return z
    if isinstance(v,list):
        for x in v:
            z=_coord(x)
            if z:return z
    return None

def _coord_from_obj(v):
    """Backward-compatible coordinate extraction helper."""
    return _coord(v)

def evidence_points(rows):
    out=[]
    for row in rows:
        try:p=json.loads(row.get("data_json") or "{}")
        except (TypeError,json.JSONDecodeError):p={}
        z=_coord(p)
        if z:out.append({"id":row.get("id"),"kind":"evidence","label":row.get("target"),"lat":z[0],"lon":z[1],"source":row.get("source"),"confidence":row.get("confidence"),"observed_at":row.get("observed_at")})
    return out[:500]
async def _earthquakes():
    try:
        d=await _get(USGS_URL);out=[]
        for f in d.get("features",[])[:1000]:
            c=f.get("geometry",{}).get("coordinates",[]); p=f.get("properties",{})
            if len(c)>=2 and _num(c[0]) is not None and _num(c[1]) is not None:out.append({"id":f.get("id"),"kind":"earthquake","label":p.get("place"),"lat":float(c[1]),"lon":float(c[0]),"magnitude":p.get("mag"),"time":p.get("time"),"source":"USGS"})
        return out
    except Exception:return []
async def _aircraft():
    try:
        d=await _get(OPENSKY_URL);out=[]
        for s in (d.get("states") or [])[:500]:
            if len(s)<8:continue
            lat,lon=_num(s[6]),_num(s[5])
            if lat is not None and lon is not None:out.append({"id":s[0],"kind":"aircraft","label":(s[1] or "").strip() or s[0],"lat":lat,"lon":lon,"altitude_m":s[7],"velocity_mps":s[9],"heading":s[10],"source":"OpenSky"})
        return out
    except Exception:return []
async def _catalog():
    try:
        sats=await _get(CELESTRAK_URL,{"GROUP":"active","FORMAT":"JSON"}); sat=[{"id":str(x.get("NORAD_CAT_ID") or x.get("OBJECT_NAME")),"kind":"satellite","label":x.get("OBJECT_NAME"),"source":"CelesTrak","norad_id":x.get("NORAD_CAT_ID"),"inclination":x.get("INCLINATION")} for x in (sats or [])[:500]]
    except Exception:sat=[]
    try:
        d=await _get(LAUNCH_URL,{"limit":100});launch=[]
        for x in d.get("results",[])[:100]:
            loc=((x.get("pad") or {}).get("location") or {});a,b=_num(loc.get("latitude")),_num(loc.get("longitude"));q={"id":x.get("id"),"kind":"launch","label":x.get("name"),"source":"Launch Library 2","window_start":x.get("window_start"),"status":(x.get("status") or {}).get("name")}
            if a is not None and b is not None:q.update(lat=a,lon=b)
            launch.append(q)
    except Exception:launch=[]
    try:
        d=await _get(RADIO_URL);radio=[]
        for x in (d or [])[:100]:
            a,b=_num(x.get("geo_lat")),_num(x.get("geo_long"))
            if a is not None and b is not None:radio.append({"id":x.get("stationuuid"),"kind":"radio","label":x.get("name"),"lat":a,"lon":b,"source":"Radio Browser"})
    except Exception:radio=[]
    return sat,launch,radio
async def public_layers():
    cached=_cached("layers-v4")
    if cached is not None:return cached
    eq,ac=await asyncio.gather(_earthquakes(),_aircraft());sat,launch,radio=await _catalog()
    result={"updated_at":int(time.time()),"layers":{"earthquakes":eq,"aircraft":ac,"satellites":sat,"launches":launch,"radio":radio,"vessels":[],"traffic":[],"cctv":[],"fires":[]},"capabilities":{"vessels":bool(os.getenv("AISSTREAM_API_KEY")),"traffic":bool(os.getenv("NEXUS_TRAFFIC_GEOJSON_URL")),"cctv":bool(os.getenv("NEXUS_CCTV_GEOJSON_URL")),"fires":bool(os.getenv("NASA_FIRMS_API_KEY")),"basemap":True,"cockpit":True,"hud":True,"detection":True,"scene_director":True,"whiteboard":True},"sources":[{"id":"usgs","name":"USGS Earthquakes","status":"live","key_required":False},{"id":"opensky","name":"OpenSky Aircraft","status":"live","key_required":False},{"id":"celestrak","name":"CelesTrak Satellites","status":"live","key_required":False},{"id":"launch-library","name":"Launch Library 2","status":"live","key_required":False},{"id":"radio-browser","name":"Radio Browser","status":"live","key_required":False},{"id":"aisstream","name":"AISStream Vessels","status":"configured" if os.getenv("AISSTREAM_API_KEY") else "optional","key_required":True}],"disclaimer":"Public telemetry may be delayed or incomplete. NEXUS does not provide named-person search, face recognition, private-account access, or safety-critical navigation."}
    return _put("layers-v4",result)
