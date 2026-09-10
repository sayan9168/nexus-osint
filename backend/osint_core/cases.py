"""Persistent investigation case management primitives."""
from __future__ import annotations
import hashlib,json
from datetime import datetime,timezone
from uuid import uuid4
from pydantic import BaseModel,Field
from .models import Evidence
from .persistence import db,json_dumps
class CaseNote(BaseModel):
 id:str=Field(default_factory=lambda:str(uuid4()));body:str;created_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))
class Case(BaseModel):
 id:str=Field(default_factory=lambda:str(uuid4()));name:str;description:str="";status:str="open";workflow:str="triage";authorized:bool=False;tags:list[str]=Field(default_factory=list);targets:list[str]=Field(default_factory=list);notes:list[CaseNote]=Field(default_factory=list);evidence:list[Evidence]=Field(default_factory=list);created_at:datetime=Field(default_factory=lambda:datetime.now(timezone.utc))
class CaseStore:
 def create(self,name:str,description:str="",authorized:bool=False)->Case:
  case=Case(name=name,description=description,authorized=authorized);db.insert("INSERT INTO cases(id,name,description,status,created_at,tags_json,workflow,authorized) VALUES(?,?,?,?,?,?,?,?)",(case.id,case.name,case.description,case.status,case.created_at.isoformat(),"[]",case.workflow,int(case.authorized)));return case
 def _hydrate(self,row)->Case:
  targets=[r[0] for r in db.execute("SELECT target FROM targets WHERE case_id=? ORDER BY target",(row["id"],))]
  notes=[CaseNote(id=r["id"],body=r["body"],created_at=datetime.fromisoformat(r["created_at"])) for r in db.execute("SELECT id,body,created_at FROM notes WHERE case_id=? ORDER BY created_at",(row["id"],))]
  evidence=[]
  for r in db.execute("SELECT * FROM evidence WHERE case_id=? ORDER BY observed_at",(row["id"],)):
   evidence.append(Evidence(id=r["id"],source=r["source"],target=r["target"],observed_at=datetime.fromisoformat(r["observed_at"]),data=json.loads(r["data_json"]),confidence=r["confidence"],notes=r["notes"],provenance_hash=r["provenance_hash"]))
  tags=json.loads(row["tags_json"] or "[]") if "tags_json" in row.keys() else []
  workflow=row["workflow"] if "workflow" in row.keys() else ("closed" if row["status"]=="closed" else "triage")
  authorized=bool(row["authorized"]) if "authorized" in row.keys() else False
  return Case(id=row["id"],name=row["name"],description=row["description"],status=row["status"],workflow=workflow,authorized=authorized,tags=tags,targets=targets,notes=notes,evidence=evidence,created_at=datetime.fromisoformat(row["created_at"]))
 def list(self)->list[Case]:return [self._hydrate(r) for r in db.execute("SELECT * FROM cases ORDER BY created_at DESC")]
 def get(self,case_id:str)->Case|None:
  rows=db.execute("SELECT * FROM cases WHERE id=?",(case_id,));return self._hydrate(rows[0]) if rows else None
 def add_target(self,case_id:str,target:str)->Case|None:
  if not self.get(case_id):return None
  db.insert("INSERT OR IGNORE INTO targets(case_id,target) VALUES(?,?)",(case_id,target));return self.get(case_id)
 def add_note(self,case_id:str,body:str)->Case|None:
  if not self.get(case_id):return None
  note=CaseNote(body=body);db.insert("INSERT INTO notes VALUES(?,?,?,?)",(note.id,case_id,note.body,note.created_at.isoformat()));return self.get(case_id)
 def add_evidence(self,case_id:str,evidence:Evidence)->Case|None:
  if not self.get(case_id):return None
  payload=json_dumps(evidence.data);provenance=hashlib.sha256((evidence.source+"|"+evidence.target+"|"+evidence.observed_at.isoformat()+"|"+payload).encode()).hexdigest();evidence.provenance_hash=provenance
  db.insert("INSERT OR IGNORE INTO evidence VALUES(?,?,?,?,?,?,?,?,?)",(evidence.id,case_id,evidence.source,evidence.target,evidence.observed_at.isoformat(),payload,evidence.confidence,evidence.notes,provenance));return self.get(case_id)
 def close(self,case_id:str)->Case|None:
  if not self.get(case_id):return None
  db.insert("UPDATE cases SET status='closed',workflow='closed' WHERE id=?",(case_id,));return self.get(case_id)
store=CaseStore()
