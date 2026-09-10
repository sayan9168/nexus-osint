"""SQLite persistence layer for local-first investigations."""
from __future__ import annotations
import json, os, sqlite3
from pathlib import Path
from typing import Any
DEFAULT_DB = Path(os.getenv("NEXUS_DB_PATH", "data/nexus.db"))
class Database:
    def __init__(self, path: str | Path = DEFAULT_DB) -> None:
        self.path = Path(path)
        if self.path != Path(":memory:"): self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()
    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, timeout=15)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        return conn
    def _init(self) -> None:
        with self._connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS cases (id TEXT PRIMARY KEY,name TEXT NOT NULL,description TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS targets (case_id TEXT NOT NULL,target TEXT NOT NULL,PRIMARY KEY(case_id,target),FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE);
            CREATE TABLE IF NOT EXISTS notes (id TEXT PRIMARY KEY,case_id TEXT NOT NULL,body TEXT NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE);
            CREATE TABLE IF NOT EXISTS evidence (id TEXT PRIMARY KEY,case_id TEXT NOT NULL,source TEXT NOT NULL,target TEXT NOT NULL,observed_at TEXT NOT NULL,data_json TEXT NOT NULL,confidence REAL NOT NULL,notes TEXT,provenance_hash TEXT NOT NULL,FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE);
            CREATE INDEX IF NOT EXISTS idx_evidence_case ON evidence(case_id);
            CREATE TABLE IF NOT EXISTS audit_events (id TEXT PRIMARY KEY,created_at TEXT NOT NULL,actor TEXT NOT NULL,action TEXT NOT NULL,resource TEXT NOT NULL,metadata TEXT NOT NULL,previous_hash TEXT NOT NULL,event_hash TEXT NOT NULL);
            CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_events(created_at);
            CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY,username TEXT UNIQUE NOT NULL,password_salt TEXT NOT NULL,password_hash TEXT NOT NULL,role TEXT NOT NULL,created_at TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY,case_id TEXT NOT NULL,target TEXT NOT NULL,target_type TEXT NOT NULL,status TEXT NOT NULL,created_at TEXT NOT NULL,started_at TEXT,finished_at TEXT,error TEXT,attempts INTEGER NOT NULL DEFAULT 0,FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE);
            CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
            CREATE TABLE IF NOT EXISTS entities (id TEXT PRIMARY KEY,case_id TEXT NOT NULL,entity_type TEXT NOT NULL,canonical TEXT NOT NULL,fingerprint TEXT NOT NULL,first_seen TEXT NOT NULL,last_seen TEXT NOT NULL,metadata_json TEXT NOT NULL,UNIQUE(case_id,entity_type,fingerprint),FOREIGN KEY(case_id) REFERENCES cases(id) ON DELETE CASCADE);
            CREATE INDEX IF NOT EXISTS idx_entities_case ON entities(case_id);
            """)
    def execute(self, sql: str, params: tuple[Any,...]=()) -> list[sqlite3.Row]:
        with self._connect() as db: return db.execute(sql,params).fetchall()
    def insert(self, sql: str, params: tuple[Any,...]=()) -> None:
        with self._connect() as db: db.execute(sql,params)
db = Database()
def json_dumps(value: Any) -> str: return json.dumps(value,sort_keys=True,separators=(",",":"),default=str)
