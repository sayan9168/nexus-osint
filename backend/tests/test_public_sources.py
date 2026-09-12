from pathlib import Path
import py_compile

ROOT=Path(__file__).resolve().parents[1]

def test_public_sources_compiles():
    py_compile.compile(str(ROOT/"osint_core"/"public_sources.py"), doraise=True)

def test_public_source_registry_is_public_only():
    from osint_core.public_sources import SOURCES
    assert SOURCES
    assert all(x["access"] == "public" for x in SOURCES)
    assert any(x["id"] == "nasa-eonet" for x in SOURCES)
    assert any(x["id"] == "osm-overpass" for x in SOURCES)
