from __future__ import annotations
import os,tempfile

def test_v3_module_compiles():
    import py_compile
    py_compile.compile("backend/api/routes/v3.py",doraise=True)

def test_v3_schema_tables_initialize():
    from osint_core.persistence import Database
    with tempfile.TemporaryDirectory() as td:
        d=Database(os.path.join(td,"nexus.db"))
        names={r[0] for r in d.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        assert {"evidence_snapshots","organizations","memberships","saved_searches","pipeline_runs"} <= names
