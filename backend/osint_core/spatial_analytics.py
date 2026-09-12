"""Deterministic spatial intelligence analytics for public signals and case evidence."""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from math import floor
from osint_core.cases import store
from osint_core.public_sources import public_snapshot


def _cell(lat: float, lon: float, size: float = 5.0) -> tuple[int,int]:
    return floor((lat + 90.0) / size), floor((lon + 180.0) / size)

async def source_health() -> dict:
    snap = await public_snapshot()
    sources=[]
    for s in snap.get("sources",[]):
        sources.append({**s,"health":"available" if s.get("access")=="public" or s.get("status") in {"live","configured"} else "optional"})
    return {"checked_at":datetime.now(timezone.utc).isoformat(),"sources":sources,"source_count":len(sources)}

async def correlation(case_id: str) -> dict:
    case=store.get(case_id)
    if not case: return {"case_id":case_id,"clusters":[],"correlations":[]}
    snap=await public_snapshot()
    signals=[]
    for layer,rows in (snap.get("layers") or {}).items():
        for row in rows: signals.append({**row,"layer":layer})
    for e in case.evidence:
        signals.append({"id":e.id,"kind":"case_evidence","label":e.target,"source":e.source,"observed_at":e.observed_at.isoformat(),"confidence":e.confidence,"layer":"case_evidence"})
    clusters=defaultdict(list)
    for s in signals:
        if isinstance(s.get("lat"),(int,float)) and isinstance(s.get("lon"),(int,float)):
            clusters[_cell(float(s["lat"]),float(s["lon"]))].append(s)
    cluster_rows=[]
    for key,rows in sorted(clusters.items(),key=lambda x:-len(x[1]))[:100]:
        cluster_rows.append({"cell":f"{key[0]}:{key[1]}","count":len(rows),"sources":sorted({str(x.get("source")) for x in rows if x.get("source")}),"signals":[x.get("id") for x in rows[:50]]})
    return {"case_id":case_id,"signal_count":len(signals),"clusters":cluster_rows,"correlations":[],"method":"deterministic 5-degree spatial clustering; no identity inference"}

async def density() -> dict:
    snap=await public_snapshot(); bins=defaultdict(lambda:{"count":0,"confidence_sum":0.0})
    for rows in (snap.get("layers") or {}).values():
        for s in rows:
            if isinstance(s.get("lat"),(int,float)) and isinstance(s.get("lon"),(int,float)):
                k=_cell(float(s["lat"]),float(s["lon"]));bins[k]["count"]+=1;bins[k]["confidence_sum"]+=float(s.get("confidence",1.0) or 1.0)
    cells=[{"x":k[1],"y":k[0],"count":v["count"],"weight":round(v["confidence_sum"],3)} for k,v in bins.items()]
    return {"updated_at":snap.get("updated_at"),"cell_size_degrees":5,"cells":sorted(cells,key=lambda x:-x["weight"])[:2000],"signal_count":sum(x["count"] for x in cells)}

async def timeline(case_id: str) -> dict:
    case=store.get(case_id)
    if not case:return {"case_id":case_id,"events":[]}
    events=[{"timestamp":e.observed_at.isoformat(),"kind":"case_evidence","source":e.source,"target":e.target,"confidence":e.confidence,"provenance_hash":e.provenance_hash} for e in case.evidence]
    events.sort(key=lambda x:x["timestamp"])
    return {"case_id":case_id,"events":events,"event_count":len(events)}
