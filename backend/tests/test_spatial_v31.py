from pathlib import Path
import py_compile


def test_spatial_sources_compile():
    for rel in ("osint_core/spatial.py", "api/routes/spatial.py"):
        py_compile.compile(str(Path(__file__).parents[1] / rel), doraise=True)


def test_spatial_public_layers_shape():
    text = (Path(__file__).parents[1] / "osint_core/spatial.py").read_text()
    for key in ("satellites", "launches", "radio", "vessels", "traffic", "cctv", "fires"):
        assert f'"{key}"' in text
