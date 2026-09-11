"""SQLite persistence layer for local-first investigations."""
from __future__ import annotations
import json,os,sqlite3
from pathlib import Path
from typing import Any
DEFAULT_DB=Path(os.getenv("NEXUS_DB_PATH","data/nexus.db"))
class Database:
 def __init__(self,path:str|Path=DEFAULT_DB):
  self.path=Path(path)
  if self.path!=Path(":memory:"):self.path.parent.mkdir(parents=True,exist_ok=True)
  self._init()
 def _connect(self):
  c=sqlite3.connect(self.path,timeout=15);c.row_factory=sqlite3.Row;c.execute("PRAGMA foreign_keys=ON");c.execute("PRAGMA journal_mode=WAL");return c
 def _init(self):
  with self._connect() as db:
   db.executescript("""
   CREATE TABLE IF NOT EXISTS cases(id TEXT PRIMARY KEY,name TEXT NOT NULL,description TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL,tags_json TEXT NOT NULL DEFAULT '[]',workflow TEXT NOT NULL DEFAULT 'triage',authorized INTEGER NOT NULL DEFAULT 0);
   CREATE TABLE IF NOT EXISTS targets(case_id TEXT NOT NULL,target TEXT NOT NULL,PRIMARY KEY(case_id,target),FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE);
   CREATE TABLE IF NOT EXISTS notes(id TEXT PRIMARY KEY,case_id TEXT NOT NULL,body TEXT NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE);
   CREATE TABLE IF NOT EXISTS evidence(id TEXT PRIMARY KEY,case_id TEXT NOT NULL,source TEXT NOT NULL,target TEXT NOT NULL,observed_at TEXT NOT NULL,data_json TEXT NOT NULL,confidence REAL NOT NULL,notes TEXT,provenance_hash TEXT NOT NULL,FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE);
   CREATE INDEX IF NOT EXISTS idx_evidence_case ON evidence(case_id);
   CREATE UNIQUE INDEX IF NOT EXISTS idx_evidence_provenance ON evidence(case_id,provenance_hash);
   CREATE TABLE IF NOT EXISTS audit_events(id TEXT PRIMARY KEY,created_at TEXT NOT NULL,actor TEXT NOT NULL,action TEXT NOT NULL,resource TEXT NOT NULL,metadata TEXT NOT NULL,previous_hash TEXT NOT NULL,event_hash TEXT NOT NULL);
   CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_events(created_at);
   CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,username TEXT UNIQUE NOT NULL,password_salt TEXT NOT NULL,password_hash TEXT NOT NULL,role TEXT NOT NULL,created_at TEXT NOT NULL);
   CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,case_id TEXT NOT NULL,target TEXT NOT NULL,target_type TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL,started_at TEXT,finished_at TEXT,error TEXT,attempts INTEGER NOT NULL DEFAULT 0,FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE);
   CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
   CREATE TABLE IF NOT EXISTS entities(id TEXT PRIMARY KEY,case_id TEXT NOT NULL,entity_type TEXT NOT NULL,canonical TEXT NOT NULL,fingerprint TEXT NOT NULL,first_seen TEXT NOT NULL,last_seen TEXT NOT NULL,metadata_json TEXT NOT NULL,UNIQUE(case_id,entity_type,fingerprint),FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE);
   CREATE INDEX IF NOT EXISTS idx_entities_case ON entities(case_id);
   CREATE TABLE IF NOT EXISTS relationships(id TEXT PRIMARY KEY,case_id TEXT NOT NULL,source_entity TEXT NOT NULL,target_entity TEXT NOT NULL,relation TEXT NOT NULL,confidence REAL NOT NULL,created_at TEXT NOT NULL,UNIQUE(case_id,source_entity,target_entity,relation),FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE);
   CREATE TABLE IF NOT EXISTS evidence_snapshots(id TEXT PRIMARY KEY,evidence_id TEXT NOT NULL,case_id TEXT NOT NULL,version INTEGER NOT NULL,created_at TEXT NOT NULL,actor TEXT NOT NULL,payload_json TEXT NOT NULL,payload_hash TEXT NOT NULL,UNIQUE(evidence_id,version),FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE,FOREIGN KEY(evidence_id) REFERENCES evidence(id) ON DELETE CASCADE);
   CREATE TABLE IF NOT EXISTS organizations(id TEXT PRIMARY KEY,name TEXT UNIQUE NOT NULL,created_at TEXT NOT NULL);
   CREATE TABLE IF NOT EXISTS memberships(org_id TEXT NOT NULL,user_id TEXT NOT NULL,role TEXT NOT NULL,created_at TEXT NOT NULL,PRIMARY KEY(org_id,user_id),FOREIGN KEY(org_id) REFERENCES organizations(id) ON DELETE CASCADE,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
   CREATE TABLE IF NOT EXISTS saved_searches(id TEXT PRIMARY KEY,user_id TEXT NOT NULL,name TEXT NOT NULL,query_json TEXT NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE);
   CREATE TABLE IF NOT EXISTS pipeline_runs(id TEXT PRIMARY KEY,case_id TEXT NOT NULL,target TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL,started_at TEXT,finished_at TEXT,steps_json TEXT NOT NULL,result_json TEXT NOT NULL,FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE);
   CREATE INDEX IF NOT EXISTS idx_pipeline_case ON pipeline_runs(case_id);
   """)
   cols={r[1] for r in db.execute("PRAGMA table_info(cases)").fetchall()}
   if "tags_json" not in cols: db.execute("ALTER TABLE cases ADD COLUMN tags_json TEXT NOT NULL DEFAULT '[]'")
   if "workflow" not in cols: db.execute("ALTER TABLE cases ADD COLUMN workflow TEXT NOT NULL DEFAULT 'triage'")
   if "authorized" not in cols: db.execute("ALTER TABLE cases ADD COLUMN authorized INTEGER NOT NULL DEFAULT 0")
 def execute(self,sql:str,params:tuple[Any,...]=()):
  with self._connect() as db:return db.execute(sql,params).fetchall()
 def insert(self,sql:str,params:tuple[Any,...]=()):
  with self._connect() as db:db.execute(sql,params)
db=Database()
def json_dumps(value:Any)->str:return json.dumps(value,sort_keys=True,separators=(",",":"),default=str)
