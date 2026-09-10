"""Small SQLite persistence layer for local-first investigations.

The database is intentionally local and dependency-free. Deployments can point
NEXUS_DB_PATH at a durable volume.
"""
from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path
from typing import Any

DEFAULT_DB = Path(os.getenv("NEXUS_DB_PATH", "data/nexus.db"))


class Database:
    def __init__(self, path: str | Path = DEFAULT_DB) -> None:
        self.path = Path(path)
        if self.path != Path(":memory:"):
            self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS cases (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS targets (
                    case_id TEXT NOT NULL,
                    target TEXT NOT NULL,
                    PRIMARY KEY (case_id, target),
                    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS notes (
                    id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    body TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
                );
                CREATE TABLE IF NOT EXISTS evidence (
                    id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    target TEXT NOT NULL,
                    observed_at TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    confidence REAL NOT NULL,
                    notes TEXT,
                    provenance_hash TEXT NOT NULL,
                    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS idx_evidence_case ON evidence(case_id);
                CREATE TABLE IF NOT EXISTS audit_events (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    previous_hash TEXT NOT NULL,
                    event_hash TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_audit_created ON audit_events(created_at);
                """
            )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def execute(self, sql: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        with self._connect() as db:
            cur = db.execute(sql, params)
            rows = cur.fetchall()
        return rows

    def insert(self, sql: str, params: tuple[Any, ...] = ()) -> None:
        with self._connect() as db:
            db.execute(sql, params)


# Shared application database. Override NEXUS_DB_PATH for production volumes.
db = Database()


def json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
