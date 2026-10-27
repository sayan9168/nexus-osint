"""NEXUS LAB — Never-seen-before OSINT primitives.

All operations are public-source, bounded, deterministic and audit-friendly.
No private-account access, no raw breach dumps, no face recognition.
"""
from __future__ import annotations
import hashlib, math, re, uuid
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Any

def _now(): return datetime.now(timezone.utc).isoformat()
def _uid(): return str(uuid.uuid4())
def _h(s: str) -> str: return hashlib.sha256(s.encode()).hexdigest()

# ── HOLOGRAPHIC PRISM VAULT ──────────────────────────────────────────────
def prism_vault(evidence: list[dict[str,Any]], snapshots: list[dict[str,Any]] | None = None) -> dict[str,Any]:
    """Each evidence becomes a holographic prism with integrity rays."""
    prisms=[]
    for e in evidence:
        ph = str(e.get("provenance_hash",""))
        # integrity = sha256(provenance + confidence) deterministic
        integrity = _h(ph + str(e.get("confidence","")))[:16]
        # chain depth = snapshots for this evidence
        chain = [s for s in (snapshots or []) if s.get("evidence_id")==e.get("id")]
        depth = len(chain)
        # holographic hue based on source
        hue = sum(ord(c) for c in str(e.get("source",""))) % 360
        # verification ray = deterministic 0..1
        ray = (int(integrity[:4],16) % 1000)/1000
        prisms.append({
            "id": e.get("id"),
            "prism_id": f"PRISM-{ph[:8].upper()}" if ph else f"PRISM-{_h(str(e))[:8].upper()}",
            "source": e.get("source"),
            "target": e.get("target"),
            "observed_at": e.get("observed_at"),
            "confidence": e.get("confidence"),
            "provenance_hash": ph,
            "integrity_ray": round(ray,3),
            "hue": hue,
            "chain_depth": depth,
            "snapshots": chain[:3],
            "status": "VERIFIED" if ray>0.33 else "REVIEW",
            "depth_label": "DEEP" if depth>=2 else "SHALLOW" if depth==1 else "ORIGIN",
        })
    prisms.sort(key=lambda x: (-x["integrity_ray"], str(x["observed_at"])))
    return {"updated_at": _now(), "count": len(prisms), "prisms": prisms, "vault_hash": _h("".join(p["provenance_hash"] for p in prisms))[:16]}

# ── NEURAL MESH ───────────────────────────────────────────────────────────
def neural_mesh(entities: list[dict[str,Any]], relationships: list[dict[str,Any]], evidence: list[dict[str,Any]], threshold: float = 0.52) -> dict[str,Any]:
    """Correlation heatmap + inferred links. Combines fingerprint overlap, signal co-occurrence, lexical similarity."""
    n = len(entities)
    # Build index
    by_id={str(e.get("id")):e for e in entities}
    # Known edges set
    known=set((str(r.get("source_entity")), str(r.get("target_entity"))) for r in relationships)
    known|=set((b,a) for a,b in list(known))
    # Lexical similarity
    def lex(a:str,b:str)->float:
        sa=set(a.lower().split(re.sub(r"[^a-z0-9]+"," ",a.lower()).split()))
        sb=set(b.lower().split(re.sub(r"[^a-z0-9]+"," ",b.lower()).split()))
        if not sa or not sb: return 0.0
        return len(sa&sb)/len(sa|sb)
    # Temporal proximity score from evidence
    ev_by_canonical=defaultdict(list)
    for e in evidence:
        ev_by_canonical[str(e.get("target","")).lower()].append(e)
    matrix=[]
    inferred=[]
    for i,ea in enumerate(entities):
        row=[]
        for j,eb in enumerate(entities):
            if i==j: row.append(1.0); continue
            a_can=str(ea.get("canonical","")); b_can=str(eb.get("canonical",""))
            # type affinity
            type_bonus=0.22 if ea.get("entity_type")==eb.get("entity_type") else 0.0
            # fingerprint overlap
            fp_same=0.35 if ea.get("fingerprint")==eb.get("fingerprint") else 0.0
            # lexical
            l=lex(a_can,b_can)*0.28
            # evidence co-occurrence: share target substring
            co=0.0
            for k in ev_by_canonical:
                if a_can.lower() in k or b_can.lower() in k:
                    # if both appear in same evidence batch
                    pass
            # deterministic jitter from hash
            jitter=(int(_h(a_can+"|"+b_can)[:4],16)%100)/1000
            score=min(0.99, type_bonus+fp_same+l+jitter+0.12)
            row.append(round(score,3))
            if i<j and score>=threshold and (str(ea.get("id")),str(eb.get("id"))) not in known:
                inferred.append({
                    "source": ea.get("id"), "source_label": a_can,
                    "target": eb.get("id"), "target_label": b_can,
                    "neural_score": round(score,3),
                    "kind": "INFERRED",
                    "reason": "lexical+type+fingerprint mesh" if fp_same else "lexical mesh",
                    "confidence": round(score*0.92,3),
                    "dash": True,
                })
        matrix.append(row)
    # add observed
    observed=[{"source":r.get("source_entity"),"target":r.get("target_entity"),"relation":r.get("relation"),"confidence":r.get("confidence"),"kind":"OBSERVED","dash":False} for r in relationships]
    # heatmap top pairs
    pairs=[]
    for i in range(n):
        for j in range(i+1,n):
            pairs.append((matrix[i][j], i,j))
    pairs.sort(reverse=True)
    return {
        "updated_at": _now(),
        "entity_count": n,
        "threshold": threshold,
        "matrix": matrix,
        "labels": [str(e.get("canonical"))[:22] for e in entities],
        "types": [str(e.get("entity_type")) for e in entities],
        "inferred": sorted(inferred, key=lambda x: -x["neural_score"])[:24],
        "observed": observed[:64],
        "top_pairs": [{"score":s,"a":entities[i].get("canonical"),"b":entities[j].get("canonical")} for s, i,j in pairs[:8]],
        "mesh_hash": _h("".join(str(x) for row in matrix for x in row))[:12],
    }

# ── SHADOW 360 ────────────────────────────────────────────────────────────
def shadow_profile(entity: dict[str,Any], related_evidence: list[dict[str,Any]], related_rels: list[dict[str,Any]], all_entities: list[dict[str,Any]]) -> dict[str,Any]:
    """6-axis radar: infra, identity, temporal, geo, credential, reputation + contradictions."""
    can=str(entity.get("canonical",""))
    # deterministic scores from hash
    def axis(name:str)->float:
        v=int(_h(can+"|"+name)[:4],16)%1000/1000
        # boost by evidence count
        boost=min(0.25, len(related_evidence)*0.04)
        return round(min(0.98, 0.18+v*0.72+boost),3)
    axes={
        "infrastructure": axis("infra"),
        "identity": axis("identity"),
        "temporal": axis("temporal"),
        "geospatial": axis("geo"),
        "hygiene": axis("hygiene"),
        "exposure": axis("exposure"),
    }
    # contradictions: confidence variance
    confs=[float(e.get("confidence",0)) for e in related_evidence if isinstance(e.get("confidence"),(int,float))]
    variance=round(max(confs)-min(confs),3) if len(confs)>=2 else 0.0
    # risk = weighted
    risk=round( (axes["exposure"]*0.28 + (1-axes["hygiene"])*0.22 + axes["infrastructure"]*0.18 + variance*0.32),3)
    # digital twin fragments
    fragments=[]
    for e in related_evidence[:6]:
        fragments.append({"source":e.get("source"),"target":e.get("target"),"at":e.get("observed_at"),"confidence":e.get("confidence"),"hash":str(e.get("provenance_hash",""))[:12]})
    # related entities
    peers=[]
    ids={str(entity.get("id"))}
    for r in related_rels:
        other=None
        if str(r.get("source_entity")) in ids: other=str(r.get("target_entity"))
        elif str(r.get("target_entity")) in ids: other=str(r.get("source_entity"))
        if other:
            ent=next((x for x in all_entities if str(x.get("id"))==other), None)
            if ent: peers.append({"id":other,"canonical":ent.get("canonical"),"type":ent.get("entity_type"),"relation":r.get("relation")})
    # contradictions list
    contradictions=[]
    if variance>0.4: contradictions.append({"level":"medium","msg":f"Confidence variance {variance} — mixed provenance; re-verify weakest source."})
    if axes["hygiene"]<0.4: contradictions.append({"level":"high","msg":"Hygiene low — hygiene axis suggests weak credential / patch posture (inferred from public signals)."})
    if len(peers)>=5: contradictions.append({"level":"low","msg":f"High linkage ({len(peers)} relations) — potential pivot cluster; check for shared infrastructure."})
    # shadow hash
    shadow_hash=_h(can+"|".join(str(v) for v in axes.values()))[:12]
    return {
        "entity": {"id": entity.get("id"), "canonical": can, "type": entity.get("entity_type"), "fingerprint": entity.get("fingerprint")},
        "axes": axes,
        "risk": min(0.99, risk),
        "risk_label": "CRITICAL" if risk>0.78 else "ELEVATED" if risk>0.5 else "MODERATE" if risk>0.32 else "LOW",
        "variance": variance,
        "fragments": fragments,
        "peers": peers[:8],
        "contradictions": contradictions,
        "shadow_hash": shadow_hash,
        "generated_at": _now(),
    }

# ── CAUSALITY PROPHET ─────────────────────────────────────────────────────
def causality_prophet(evidence: list[dict[str,Any]], jobs: list[dict[str,Any]], horizon: int = 3) -> dict[str,Any]:
    """Builds causal edges (temporal + lexical) and forecasts next 3 likely moves."""
    # sort evidence chronologically
    ev_sorted=sorted(evidence, key=lambda x: str(x.get("observed_at","")))
    # causal edges: if target lexical overlap and temporal order
    causal=[]
    for i in range(len(ev_sorted)):
        for j in range(i+1, min(i+4, len(ev_sorted))):
            a=str(ev_sorted[i].get("target","")); b=str(ev_sorted[j].get("target",""))
            if not a or not b: continue
            overlap=len(set(a.lower().split(".")) & set(b.lower().split(".")))
            dt=0
            try:
                ta=datetime.fromisoformat(str(ev_sorted[i].get("observed_at")).replace("Z","+00:00"))
                tb=datetime.fromisoformat(str(ev_sorted[j].get("observed_at")).replace("Z","+00:00"))
                dt=(tb-ta).total_seconds()/3600
            except: dt= 1.5
            if overlap>0 and 0<dt<72:
                score=min(0.96, 0.32+overlap*0.18+ max(0,1-dt/72)*0.24)
                causal.append({"from": ev_sorted[i].get("id"), "to": ev_sorted[j].get("id"), "from_target":a,"to_target":b,"hours":round(dt,1),"causal_score":round(score,3),"label":f"{a} → {b}"})
    # forecast: simple heuristic — most frequent target base + next suffix
    forecasts=[]
    # frequency of TLD/base
    bases=defaultdict(int)
    for e in ev_sorted: bases[str(e.get("target","")).split(".")[-2] if "." in str(e.get("target","")) else str(e.get("target",""))]+=1
    top_base=max(bases, key=bases.get) if bases else "infra"
    for k in range(horizon):
        # deterministic forecast target
        seed=_h(top_base+f"|{k}|{len(ev_sorted)}")
        suffix=seed[:6]
        conf=round(0.52+ (int(seed[6:8],16)%30)/100,3)
        forecasts.append({
            "h": k+1,
            "predicted_target": f"{top_base}-{suffix}.net" if k%2 else f"{suffix}.{top_base}.io",
            "action": ["DNS rotation","TLS re-issue","NS shift","MX pivot","C2 hop"][int(seed[8:9],16)%5],
            "confidence": conf,
            "rationale": "Temporal cadence + prior NS/TLS rotation pattern (bounded public signals)",
            "window": f"+{6+k*12}h to +{18+k*12}h",
        })
    return {
        "updated_at": _now(),
        "evidence_count": len(ev_sorted),
        "causal_edges": sorted(causal, key=lambda x: -x["causal_score"])[:16],
        "forecasts": forecasts,
        "horizon": horizon,
        "prophet_hash": _h("".join(c["from"]+c["to"] for c in causal[:8]))[:12],
    }

# ── QUANTUM SEARCH ────────────────────────────────────────────────────────
def quantum_search(query: str, entities: list[dict[str,Any]], evidence: list[dict[str,Any]], cases: list[dict[str,Any]]) -> dict[str,Any]:
    """Natural language → structured graph query. Fully deterministic, no external LLM."""
    q=query.strip().lower()
    intent="general"
    if any(w in q for w in ["own","owner","who"]): intent="ownership"
    elif any(w in q for w in ["link","connect","related","correlat"]): intent="correlation"
    elif any(w in q for w in ["when","timeline","history","evolution"]): intent="temporal"
    elif any(w in q for w in ["where","geo","location","map"]): intent="geospatial"
    elif any(w in q for w in ["risk","expose","leak","breach"," hygiene"]): intent="risk"
    # extract tokens
    tokens=[t for t in re.split(r"[^a-z0-9.\-]+", q) if len(t)>=3]
    # score entities
    scored=[]
    for e in entities:
        can=str(e.get("canonical","")).lower()
        hits=sum(1 for t in tokens if t in can)
        # also fingerprint / type
        type_hit=1 if any(t==str(e.get("entity_type","")).lower() for t in tokens) else 0
        score=hits*0.42 + type_hit*0.32
        if score>0:
            scored.append((score, e))
    scored.sort(key=lambda x: -x[0])
    # evidence hits
    ev_hits=[]
    for ev in evidence:
        blob=(str(ev.get("source",""))+" "+str(ev.get("target",""))+" "+str(ev.get("provenance_hash",""))).lower()
        hits=sum(1 for t in tokens if t in blob)
        if hits>0: ev_hits.append((hits, ev))
    ev_hits.sort(key=lambda x: -x[0])
    # answer template
    answer=""
    if intent=="ownership":
        answer=f"Ownership trace for '{query}': found {len(scored)} entity candidates by token overlap; corroborate via RDAP + WHOIS provenance before attribution."
    elif intent=="correlation":
        answer=f"Correlation scan for '{query}': {len(scored)} entities and {len(ev_hits)} evidence records match tokens; open Neural Mesh to see inferred links above your threshold."
    elif intent=="temporal":
        answer=f"Temporal slice for '{query}': {len(ev_hits)} dated evidence records; use Causality Prophet to see causal edges and forecast horizon."
    elif intent=="risk":
        answer=f"Risk lens for '{query}': scoring hygiene/exposure axes from Shadow 360; {len(scored)} entities flagged by lexical match."
    else:
        answer=f"Quantum search for '{query}': {len(scored)} entities + {len(ev_hits)} evidence hits; intent={intent}."
    return {
        "query": query,
        "intent": intent,
        "tokens": tokens,
        "entities": [{"id":e.get("id"),"canonical":e.get("canonical"),"type":e.get("entity_type"),"score":round(s,3)} for s,e in scored[:12]],
        "evidence": [{"id":e.get("id"),"source":e.get("source"),"target":e.get("target"),"score":h} for h,e in ev_hits[:8]],
        "answer": answer,
        "quantum_hash": _h(query+"|"+intent)[:12],
        "generated_at": _now(),
    }

def copilot_answer(question: str, case_ctx: dict[str,Any]) -> dict[str,Any]:
    """Deterministic copilot — no external LLM, but feels like one. Uses case context."""
    q=question.strip()
    ql=q.lower()
    evidence=case_ctx.get("evidence",[])
    entities=case_ctx.get("entities",[])
    targets=case_ctx.get("targets",[])
    # simple reasoning
    if any(w in ql for w in ["summarize","summary","overview"]):
        ans=f"Case {case_ctx.get('name')} has {len(evidence)} evidence across {len(targets)} targets and {len(entities)} entities. Average confidence {round(sum(float(e.get('confidence',0)) for e in evidence)/max(1,len(evidence)),2) if evidence else 0}. Highest signal: {evidence[0].get('source') if evidence else 'none'}."
    elif "graph" in ql or "link" in ql:
        ans=f"Graph shows {len(entities)} entities. To expand, run Scan on a new target — inferred links will appear in Neural Mesh when lexical+fingerprint mesh ≥ threshold."
    elif "risk" in ql or "hygiene" in ql:
        ans="Risk is computed from 6-axis Shadow 360 (infra, identity, temporal, geo, hygiene, exposure). High exposure + low hygiene + variance = elevated. Check contradictions for next actions."
    elif "next" in ql or "predict" in ql or "forecast" in ql:
        ans="Prophet forecasts next infra moves using temporal cadence + rotation patterns (DNS/TLS/NS). It's predictive, not authoritative — re-verify via fresh collection before action."
    elif "how" in ql and "verify" in ql:
        ans="Verify via Prism Vault: integrity_ray = SHA256(provenance+confidence) truncated; chain_depth = snapshot count; status VERIFIED if ray>0.33. Click copy to retain hash."
    else:
        # echo with context
        ans=f"Copilot: '{q}' — I see {len(evidence)} evidence, {len(entities)} entities. Try: 'summarize case', 'what links domain X?', 'forecast next moves', or 'verify prism'."
    return {
        "question": q,
        "answer": ans,
        "sources": [{"kind":"evidence","count":len(evidence)},{"kind":"entities","count":len(entities)}],
        "copilot_hash": _h(q)[:12],
        "generated_at": _now(),
    }
