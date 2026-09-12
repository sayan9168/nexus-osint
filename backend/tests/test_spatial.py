from pathlib import Path


def test_spatial_modules_compile():
    for path in (Path("osint_core/spatial.py"), Path("api/routes/spatial.py")):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")


def test_spatial_coordinate_extraction():
    from osint_core.spatial import _coord_from_obj
    assert _coord_from_obj({"metadata": {"latitude": 22.57, "longitude": 88.36}}) == (22.57, 88.36)
    assert _coord_from_obj({"lat": 91, "lon": 1}) is None
