"""NEXUS Intelligence V3: search, replay, analytics, evidence vault, pipelines and teams.
All operations stay inside authenticated cases and public/authorized investigation scope.
"""
from __future__ import annotations
import hashlib,json,uuid
from datetime import datetime,timezone
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,Field
from api.security import require_permission
from osint_core.persistence import db,json_dumps

router=APIRouter()
def now(): return datetime.now(timezone.utc).isoformat()
def uid(): return str(uuid.uuid4())
def require_case(case_id:str):
 rows=db.execute("SELECT * FROM cases WHERE id=?",(case_id,))
 if not rows: raise HTTPException(404,"Case not found")
 return rows[0]

class SearchRequest(BaseModel):
 q:str=Field(min_length=1,max_length=200)
 case_id:str|None=None
 entity_type:str|None=None
 limit:int=Field(default=50,ge=1,le=200)

@router.post("/search",tags=["Intelligence V3"])
def search(req:SearchRequest,user=Depends(require_permission("case:read"))):
 q=f"%{req.q.strip()}%"; rows=[]
 casesql="SELECT id,name,description,status,created_at,tags_json FROM cases WHERE name LIKE ? OR description LIKE ?"
 params=(q,q)
 if req.case_id: casesql+=" AND id=?";params+=(req.case_id,)
 for r in db.execute(casesql+" ORDER BY created_at DESC LIMIT ?",params+(req.limit,)): rows.append({"kind":"case",**dict(r)})
 esql="SELECT id,case_id,entity_type,canonical,first_seen,last_seen,metadata_json FROM entities WHERE (canonical LIKE ? OR entity_type LIKE ?)"
 ep=(q,q)
 if req.case_id: esql+=" AND case_id=?";ep+=(req.case_id,)
 if req.entity_type: esql+=" AND entity_type=?";ep+=(req.entity_type,)
 for r in db.execute(esql+" ORDER BY last_seen DESC LIMIT ?",ep+(req.limit,)): rows.append({"kind":"entity",**dict(r)})
 evsql="SELECT id,case_id,source,target,observed_at,confidence FROM evidence WHERE source LIKE ? OR target LIKE ? OR data_json LIKE ? ORDER BY observed_at DESC LIMIT ?"
 for r in db.execute(evsql,(q,q,q,req.limit)): rows.append({"kind":"evidence",**dict(r)})
 return {"query":req.q,"count":len(rows),"results":rows[:req.limit]}

class SavedSearch(BaseModel): name:str=Field(min_length=1,max_length=100); query:SearchRequest
@router.post("/search/saved",tags=["Intelligence V3"])
def save_search(req:SavedSearch,user=Depends(require_permission("case:read"))):
 sid=uid(); db.insert("INSERT INTO saved_searches VALUES(?,?,?,?,?)",(sid,user["sub"],req.name,json.dumps(req.query.model_dump(),sort_keys=True),now())); return {"id":sid,"name":req.name}
@router.get("/search/saved",tags=["Intelligence V3"])
def list_saved(user=Depends(require_permission("case:read"))):
 return [dict(r) for r in db.execute("SELECT id,name,query_json,created_at FROM saved_searches WHERE user_id=? ORDER BY created_at DESC",(user["sub"],))]

@router.get("/analytics/{case_id}",tags=["Analytics"])
def analytics(case_id:str,user=Depends(require_permission("case:read"))):
 require_case(case_id)
 counts={"targets":db.execute("SELECT COUNT(*) n FROM targets WHERE case_id=?",(case_id,))[0]["n"],"evidence":db.execute("SELECT COUNT(*) n FROM evidence WHERE case_id=?",(case_id,))[0]["n"],"entities":db.execute("SELECT COUNT(*) n FROM entities WHERE case_id=?",(case_id,))[0]["n"],"relationships":db.execute("SELECT COUNT(*) n FROM relationships WHERE case_id=?",(case_id,))[0]["n"],"jobs":db.execute("SELECT COUNT(*) n FROM jobs WHERE case_id=?",(case_id,))[0]["n"]}
 avg=db.execute("SELECT COALESCE(AVG(confidence),0) v FROM evidence WHERE case_id=?",(case_id,))[0]["v"]
 return {"case_id":case_id,"counts":counts,"average_confidence":round(float(avg),4),"evidence_coverage":round(min(1,counts["evidence"]/max(1,counts["targets"])),4)}

@router.get("/entities/correlate/{case_id}",tags=["Entity Intelligence"])
def correlate(case_id:str,user=Depends(require_permission("case:read"))):
 require_case(case_id)
 rows=db.execute("SELECT entity_type,fingerprint,COUNT(*) cases,MIN(first_seen) first_seen,MAX(last_seen) last_seen FROM entities WHERE fingerprint IN (SELECT fingerprint FROM entities GROUP BY fingerprint HAVING COUNT(DISTINCT case_id)>1) GROUP BY entity_type,fingerprint ORDER BY cases DESC")
 return [dict(r) for r in rows]

@router.get("/graph/{case_id}/analysis",tags=["Advanced Graph"])
def graph_analysis(case_id:str,source:str|None=None,target:str|None=None,max_hops:int=Query(3,ge=1,le=8),user=Depends(require_permission("graph:read"))):
 require_case(case_id); edges=[dict(r) for r in db.execute("SELECT source_entity,target_entity,relation,confidence FROM relationships WHERE case_id=?",(case_id,))]
 adjacency={}
 for e in edges: adjacency.setdefault(e["source_entity"],set()).add(e["target_entity"])
 path=None
 if source and target:
  q=[(source,[source])];seen={source}
  while q:
   node,p=q.pop(0)
   if node==target: path=p;break
   if len(p)-1>=max_hops: continue
   for nxt in adjacency.get(node,()):
    if nxt not in seen: seen.add(nxt);q.append((nxt,p+[nxt]))
 return {"nodes":len({x for e in edges for x in (e["source_entity"],e["target_entity"])}),"edges":len(edges),"path":path,"clusters":_clusters(edges)}
def _clusters(edges):
 parent={}
 def f(x):
  parent.setdefault(x,x)
  while parent[x]!=x: parent[x]=parent[parent[x]];x=parent[x]
  return x
 for e in edges:
  a,b=e["source_entity"],e["target_entity"];ra,rb=f(a),f(b)
  if ra!=rb:parent[rb]=ra
 groups={}
 for x in parent:groups.setdefault(f(x),[]).append(x)
 return sorted(groups.values(),key=len,reverse=True)

@router.post("/evidence/{evidence_id}/snapshot",tags=["Evidence Vault"])
def snapshot(evidence_id:str,user=Depends(require_permission("case:write"))):
 rows=db.execute("SELECT * FROM evidence WHERE id=?",(evidence_id,))
 if not rows: raise HTTPException(404,"Evidence not found")
 e=dict(rows[0]); prev=db.execute("SELECT COALESCE(MAX(version),0) v FROM evidence_snapshots WHERE evidence_id=?",(evidence_id,))[0]["v"]; ver=int(prev)+1
 payload=json_dumps(e); h=hashlib.sha256(payload.encode()).hexdigest(); sid=uid()
 db.insert("INSERT INTO evidence_snapshots VALUES(?,?,?,?,?,?,?,?)",(sid,evidence_id,e["case_id"],ver,now(),user["sub"],payload,h))
 return {"id":sid,"evidence_id":evidence_id,"version":ver,"sha256":h}
@router.get("/evidence/{evidence_id}/snapshots",tags=["Evidence Vault"])
def snapshots(evidence_id:str,user=Depends(require_permission("case:read"))):
 return [dict(r) for r in db.execute("SELECT id,version,created_at,actor,payload_hash FROM evidence_snapshots WHERE evidence_id=? ORDER BY version",(evidence_id,))]

class PipelineRequest(BaseModel): target:str=Field(min_length=1,max_length=253)
@router.post("/pipelines/{case_id}",tags=["Pipelines"])
def start_pipeline(case_id:str,req:PipelineRequest,user=Depends(require_permission("job:run"))):
 c=require_case(case_id)
 if not c["authorized"]: raise HTTPException(403,"Case must be explicitly authorized before collection")
 pid=uid(); steps=["scope","dns","rdap","http","tls","entities","graph","score","timeline","report"]
 db.insert("INSERT INTO pipeline_runs VALUES(?,?,?,?,?,?,?,?,?)",(pid,case_id,req.target,"planned",now(),None,None,json.dumps(steps),"{}"))
 return {"id":pid,"status":"planned","steps":steps,"note":"Pipeline plan created; execute individual bounded collectors through the existing job engine."}
@router.get("/pipelines/{case_id}",tags=["Pipelines"])
def pipelines(case_id:str,user=Depends(require_permission("case:read"))):
 require_case(case_id);return [dict(r) for r in db.execute("SELECT * FROM pipeline_runs WHERE case_id=? ORDER BY created_at DESC",(case_id,))]

class OrgRequest(BaseModel): name:str=Field(min_length=2,max_length=100)
@router.post("/orgs",tags=["Organizations"])
def create_org(req:OrgRequest,user=Depends(require_permission("source:manage"))):
 oid=uid()
 try: db.insert("INSERT INTO organizations VALUES(?,?,?)",(oid,req.name,now()));db.insert("INSERT INTO memberships VALUES(?,?,?,?)",(oid,user["sub"],"owner",now()))
 except Exception as exc: raise HTTPException(409,"Organization name already exists") from exc
 return {"id":oid,"name":req.name,"role":"owner"}
@router.get("/orgs",tags=["Organizations"])
def orgs(user=Depends(require_permission("case:read"))):
 return [dict(r) for r in db.execute("SELECT o.id,o.name,m.role FROM organizations o JOIN memberships m ON m.org_id=o.id WHERE m.user_id=? ORDER BY o.name",(user["sub"],))]

@router.get("/replay/{case_id}",tags=["Investigation Replay"])
def replay(case_id:str,user=Depends(require_permission("case:read"))):
 require_case(case_id)
 timeline=[]
 for r in db.execute("SELECT created_at,actor,action,resource,metadata FROM audit_events WHERE resource LIKE ? ORDER BY created_at",(f"case:{case_id}%",)): timeline.append(dict(r))
 for r in db.execute("SELECT observed_at AS created_at,source,target,confidence,provenance_hash FROM evidence WHERE case_id=? ORDER BY observed_at",(case_id,)): timeline.append({"action":"evidence.observed",**dict(r)})
 timeline.sort(key=lambda x:x.get("created_at", "")); return {"case_id":case_id,"events":timeline,"event_count":len(timeline),"deterministic":True}
