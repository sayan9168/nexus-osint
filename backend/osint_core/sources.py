"""Safe public-source registry and connector metadata."""
from __future__ import annotations

SOURCES = [
    {"id": "system-dns", "name": "System DNS", "category": "network", "active": True, "privacy": "public"},
    {"id": "rdap.org", "name": "RDAP", "category": "registration", "active": True, "privacy": "public"},
    {"id": "reverse-dns", "name": "Reverse DNS", "category": "network", "active": True, "privacy": "public"},
    {"id": "http-head", "name": "HTTP HEAD", "category": "web", "active": True, "privacy": "public"},
    {"id": "validator", "name": "Local Validator", "category": "validation", "active": True, "privacy": "local"},
]


def catalog() -> list[dict]:
    return [dict(item) for item in SOURCES]
