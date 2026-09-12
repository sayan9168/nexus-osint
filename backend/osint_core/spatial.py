"""Safe public-source spatial intelligence adapters for NEXUS OSINT.

This module intentionally models public infrastructure/events and aircraft telemetry,
not named-person tracking. External feeds are bounded, read-only, and cached briefly.
"""
from __future__ import annotations

import asyncio
import json
import math
import time
from typing import Any

import httpx

USGS_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
OPENSKY_URL = "https://opensky-network.org/api/states/all"
_CACHE: dict[str, tuple[float, Any]] = {}
_CACHE_TTL = 30.0


def _cached(key: str) -> Any | None:
    item = _CACHE.get(key)
    if item and time.monotonic() - item[0] < _CACHE_TTL:
        return item[1]
    return None


def _put(key: str, value: Any) -> Any:
    _CACHE[key] = (time.monotonic(), value)
    return value


async def _get_json(url: str, params: dict[str, Any] | None = None) -> Any:
    async with httpx.AsyncClient(timeout=httpx.Timeout(8.0, connect=3.0), follow_redirects=False) as client:
        response = await client.get(url, params=params, headers={"User-Agent": "NEXUS-OSINT/3.0"})
        response.raise_for_status()
        return response.json()


def _num(value: Any) -> float | None:
    try:
        n = float(value)
        return n if math.isfinite(n) else None
    except (TypeError, ValueError):
        return None


def _coord_from_obj(value: Any) -> tuple[float, float] | None:
    if isinstance(value, dict):
        lat = _num(value.get("lat", value.get("latitude")))
        lon = _num(value.get("lon", value.get("longitude")))
        if lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180:
            return lat, lon
        for child in value.values():
            found = _coord_from_obj(child)
            if found:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _coord_from_obj(child)
            if found:
                return found
    return None


def evidence_points(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    points: list[dict[str, Any]] = []
    for row in rows:
        try:
            payload = json.loads(row.get("data_json") or "{}")
        except (TypeError, json.JSONDecodeError):
            payload = {}
        coord = _coord_from_obj(payload)
        if coord:
            points.append({
                "id": row.get("id"), "kind": "evidence", "label": row.get("target"),
                "lat": coord[0], "lon": coord[1], "source": row.get("source"),
                "confidence": row.get("confidence"), "observed_at": row.get("observed_at"),
            })
    return points[:500]


async def public_layers() -> dict[str, Any]:
    cached = _cached("layers")
    if cached is not None:
        return cached

    async def earthquakes() -> list[dict[str, Any]]:
        try:
            data = await _get_json(USGS_URL)
            out = []
            for feature in data.get("features", [])[:1000]:
                coords = feature.get("geometry", {}).get("coordinates", [])
                if len(coords) < 2:
                    continue
                lon, lat = _num(coords[0]), _num(coords[1])
                if lat is None or lon is None:
                    continue
                props = feature.get("properties", {})
                out.append({"id": feature.get("id"), "kind": "earthquake", "label": props.get("place"),
                            "lat": lat, "lon": lon, "magnitude": props.get("mag"),
                            "time": props.get("time"), "source": "USGS"})
            return out
        except Exception:
            return []

    async def aircraft() -> list[dict[str, Any]]:
        try:
            data = await _get_json(OPENSKY_URL)
            out = []
            for state in (data.get("states") or [])[:500]:
                if not state or len(state) < 8:
                    continue
                lon, lat = _num(state[5]), _num(state[6])
                if lat is None or lon is None:
                    continue
                out.append({"id": state[0], "kind": "aircraft", "label": (state[1] or "").strip() or state[0],
                            "lat": lat, "lon": lon, "altitude_m": state[7],
                            "velocity_mps": state[9], "heading": state[10], "source": "OpenSky"})
            return out
        except Exception:
            return []

    eq, ac = await asyncio.gather(earthquakes(), aircraft())
    return _put("layers", {
        "updated_at": int(time.time()),
        "layers": {"earthquakes": eq, "aircraft": ac},
        "sources": [
            {"id": "usgs", "name": "USGS Earthquakes", "status": "live", "key_required": False},
            {"id": "opensky", "name": "OpenSky Aircraft", "status": "live", "key_required": False},
        ],
        "disclaimer": "Public telemetry may be delayed or incomplete. Not for navigation, emergency response, or safety-critical decisions.",
    })
