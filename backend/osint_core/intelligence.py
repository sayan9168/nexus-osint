"""Safe public DNS/RDAP intelligence and case-scoped entity correlation."""
from __future__ import annotations
import hashlib, ipaddress, socket, urllib.parse, urllib.request, json
from datetime import datetime, timezone
from .persistence import db, json_dumps

DNS_TYPES=("A","AAAA","MX","NS","TXT","CNAME","CAA")
def _name(value:str)->str: return value.strip().lower().rstrip(".")
def fingerprint(entity_type:str, canonical:str)->str: return hashlib.sha256(f"{entity_type}:{_name(canonical)}".encode()).hexdigest()
def upsert_entity(case_id:str, entity_type:str, canonical:str, metadata:dict|None=None)->dict:
    canonical=_name(canonical); fp=fingerprint(entity_type,canonical); now=datetime.now(timezone.utc).isoformat()
    rows=db.execute("SELECT * FROM entities WHERE case_id=? AND entity_type=? AND fingerprint=?",(case_id,entity_type,fp))
    if rows:
        db.insert("UPDATE entities SET last_seen=?,metadata_json=? WHERE id=?",(now,json_dumps(metadata or {}),rows[0]["id"]))
        return dict(db.execute("SELECT * FROM entities WHERE id=?",(rows[0]["id"],))[0])
    eid=hashlib.sha256(f"{case_id}:{entity_type}:{fp}".encode()).hexdigest()[:32]
    db.insert("INSERT INTO entities VALUES(?,?,?,?,?,?,?,?)",(eid,case_id,entity_type,canonical,fp,now,now,json_dumps(metadata or {})))
    return dict(db.execute("SELECT * FROM entities WHERE id=?",(eid,))[0])

def _dns_json(domain:str, qtype:str)->list:
    url="https://dns.google/resolve?name="+urllib.parse.quote(domain,safe="")+"&type="+qtype
    req=urllib.request.Request(url,headers={"Accept":"application/dns-json","User-Agent":"NEXUS-OSINT/1.0"})
    with urllib.request.urlopen(req,timeout=5) as r:
        if r.status!=200: return []
        body=r.read(256_000)
    data=json.loads(body.decode("utf-8")); return [a.get("data") for a in data.get("Answer",[]) if "data" in a]

def domain_intelligence(domain:str)->dict:
    domain=_name(domain); result={"domain":domain,"records":{},"errors":[]}
    try: socket.gethostbyname(domain)
    except OSError: pass
    for qtype in DNS_TYPES:
        try: result["records"][qtype]=_dns_json(domain,qtype)
        except Exception as exc: result["records"][qtype]=[]; result["errors"].append(f"{qtype}: {type(exc).__name__}")
    try:
        req=urllib.request.Request(f"https://rdap.org/domain/{urllib.parse.quote(domain,safe='')}",headers={"Accept":"application/rdap+json","User-Agent":"NEXUS-OSINT/1.0"})
        with urllib.request.urlopen(req,timeout=7) as r: rdap=json.loads(r.read(512_000).decode())
        result["rdap"]={"handle":rdap.get("handle"),"ldhName":rdap.get("ldhName"),"status":rdap.get("status",[]),"nameservers":[n.get("ldhName") for n in rdap.get("nameservers",[]) if n.get("ldhName")],"events":[e for e in rdap.get("events",[]) if e.get("eventAction") in {"registration","expiration","last changed"}],"entities":[e.get("handle") for e in rdap.get("entities",[]) if e.get("handle")]}
    except Exception as exc: result["rdap"]={"error":type(exc).__name__}
    return result
