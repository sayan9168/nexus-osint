"""Next-generation public-signal intelligence primitives.

All algorithms operate on public, non-sensitive signals already collected by NEXUS.
No private-account access, credential material, raw breach dumps, or person tracking.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from math import floor
from typing import Any

def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def source_health(sources: list[dict[str, Any]]) -> dict[str, Any]:
    rows=[]
    for s in sources:
        rows.append({"id":s.get("id"),"name":s.get("name"),"status":s.get("status", "unknown"),"access":s.get("access"),"configured":bool(s.get("configured", True)),"last_checked":s.get("last_checked"),"latency_ms":s.get("latency_ms"),"error":s.get("error")})
    counts=defaultdict(int)
    for r in rows: counts[str(r["status"])] += 1
    return {"updated_at":_utc(),"total":len(rows),"counts":dict(counts),"sources":rows}

def correlate_signals(signals: list[dict[str, Any]], grid_deg: float = 5.0) -> dict[str, Any]:
    clusters: dict[tuple[int,int], list[dict[str,Any]]] = defaultdict(list)
    for s in signals:
        lat,lon=s.get("lat"),s.get("lon")
        if not isinstance(lat,(int,float)) or not isinstance(lon,(int,float)): continue
        key=(floor((float(lat)+90)/grid_deg),floor((float(lon)+180)/grid_deg))
        clusters[key].append(s)
    out=[]
    for key,items in clusters.items():
        confidence=sum(float(x.get("confidence",0.5)) for x in items)/len(items)
        sources=sorted({str(x.get("source","unknown")) for x in items})
        out.append({"cluster_id":f"geo-{key[0]}-{key[1]}","count":len(items),"confidence":round(min(confidence,0.99),3),"sources":sources,"signals":items[:100]})
    out.sort(key=lambda x:(-x["count"],-x["confidence"]))
    return {"updated_at":_utc(),"grid_deg":grid_deg,"cluster_count":len(out),"clusters":out}

def density_heatmap(signals: list[dict[str, Any]], grid_deg: float = 5.0) -> dict[str, Any]:
    buckets: dict[tuple[int,int],dict[str,float]]={}
    for s in signals:
        lat,lon=s.get("lat"),s.get("lon")
        if not isinstance(lat,(int,float)) or not isinstance(lon,(int,float)): continue
        k=(floor((float(lat)+90)/grid_deg),floor((float(lon)+180)/grid_deg))
        b=buckets.setdefault(k,{"count":0,"weight":0.0});b["count"]+=1;b["weight"]+=max(0.0,min(1.0,float(s.get("confidence",0.5))))
    cells=[]
    for (a,b),v in buckets.items():
        cells.append({"lat":a*grid_deg-90+grid_deg/2,"lon":b*grid_deg-180+grid_deg/2,"count":int(v["count"]),"weight":round(v["weight"],3)})
    return {"updated_at":_utc(),"grid_deg":grid_deg,"cells":cells}

def fuse_timeline(evidence: list[dict[str,Any]], signals: list[dict[str,Any]]) -> list[dict[str,Any]]:
    rows=[]
    for x in [*evidence,*signals]:
        ts=x.get("observed_at") or x.get("timestamp") or x.get("created_at")
        if not ts: continue
        rows.append({"timestamp":ts,"kind":x.get("kind","evidence"),"source":x.get("source","case"),"target":x.get("target") or x.get("label"),"confidence":x.get("confidence"),"provenance":x.get("provenance_hash") or x.get("fingerprint")})
    return sorted(rows,key=lambda x:str(x["timestamp"]))

def graph_fusion(entities: list[dict[str,Any]], relationships: list[dict[str,Any]], signals: list[dict[str,Any]]) -> dict[str,Any]:
    nodes=[{"id":str(e.get("id")),"type":e.get("entity_type"),"label":e.get("canonical"),"confidence":e.get("confidence")} for e in entities]
    edges=[{"source":r.get("source_entity"),"target":r.get("target_entity"),"relation":r.get("relation"),"confidence":r.get("confidence")} for r in relationships]
    for s in signals:
        fp=s.get("fingerprint")
        if fp:
            nodes.append({"id":f"signal:{fp}","type":"public_signal","label":s.get("label") or s.get("kind"),"confidence":s.get("confidence")})
    return {"nodes":nodes,"edges":edges,"signal_count":len(signals)}
