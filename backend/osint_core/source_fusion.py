"""Normalize and fuse bounded public spatial signals."""
from __future__ import annotations
import hashlib, time
from typing import Any
from .public_sources import public_snapshot, context

SOURCE_WEIGHTS = {"USGS":0.95,"OpenSky":0.85,"NASA EONET":0.92,"GDELT GEO":0.65,"OpenStreetMap":0.80,"RIPE Atlas":0.75,"Open-Meteo":0.75}

def _fingerprint(signal: dict[str, Any]) -> str:
    raw="|".join(str(signal.get(k,"")) for k in ("source","kind","id","lat","lon","label"))
    return hashlib.sha256(raw.encode()).hexdigest()[:20]

def _confidence(source: str, item: dict[str, Any]) -> float:
    base=SOURCE_WEIGHTS.get(source,0.55)
    if item.get("time") or item.get("updated_at"): base+=0.03
    return round(min(base,0.99),3)

async def fused_snapshot() -> dict[str,Any]:
    snapshot=await public_snapshot(); signals=[]
    for layer,items in snapshot.get("layers",{}).items():
        for item in items[:500]:
            source=str(item.get("source") or "unknown")
            if item.get("lat") is None or item.get("lon") is None: continue
            signal=dict(item); signal["layer"]=layer; signal["confidence"]=_confidence(source,item); signal["fingerprint"]=_fingerprint(signal); signals.append(signal)
    dedup={s["fingerprint"]:s for s in signals}
    return {"updated_at":int(time.time()),"source_count":len(snapshot.get("sources",[])),"signal_count":len(dedup),"signals":list(dedup.values())[:1500],"sources":snapshot.get("sources",[]),"disclaimer":snapshot.get("disclaimer")}

async def fused_context(lat: float, lon: float, radius_m: int=3000) -> dict[str,Any]:
    base=await context(lat,lon,radius_m); nearby=[]
    for item in base.get("osm",[])[:250]:
        x=dict(item); x["confidence"]=_confidence("OpenStreetMap",x); x["fingerprint"]=_fingerprint(x); nearby.append(x)
    return {**base,"correlated_signals":nearby,"correlation_count":len(nearby)}
