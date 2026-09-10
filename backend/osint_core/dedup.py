"""Deterministic entity canonicalization and deduplication helpers."""
from __future__ import annotations

import ipaddress
from urllib.parse import urlparse, urlunparse

from .models import EntityType


def canonicalize(value: str, entity_type: EntityType) -> str:
    value = value.strip()
    if entity_type == EntityType.DOMAIN:
        return value.lower().rstrip(".")
    if entity_type == EntityType.EMAIL:
        return value.lower()
    if entity_type == EntityType.IP:
        try:
            return str(ipaddress.ip_address(value))
        except ValueError:
            return value.lower()
    if entity_type == EntityType.URL:
        if not value.startswith(("http://", "https://")):
            value = "https://" + value
        p = urlparse(value)
        return urlunparse((p.scheme.lower(), p.netloc.lower(), p.path or "/", "", p.query, ""))
    return value.strip()


def unique(values: list[str], entity_type: EntityType) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        key = canonicalize(value, entity_type)
        if key not in seen:
            seen.add(key)
            result.append(key)
    return result
