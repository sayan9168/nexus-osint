"""Versioned plugin SDK v2 for bounded public-source collectors."""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from typing import Callable
from .models import EntityType, Evidence

Collector = Callable[[str], list[Evidence]]
SDK_VERSION = "2.0"

class PluginHealth(StrEnum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"

@dataclass(frozen=True)
class Plugin:
    name: str
    version: str
    entity_type: EntityType
    description: str
    collector: Collector
    permissions: tuple[str, ...] = ()
    sources: tuple[str, ...] = ()
    scope: tuple[str, ...] = ()
    timeout_seconds: int = 10
    rate_limit_per_minute: int = 30
    compatibility: str = "2.x"
    health_check: Callable[[], bool] | None = None
    author: str = "SAYANOX NEXUS"

    def manifest(self) -> dict:
        return {
            "sdk_version": SDK_VERSION,
            "name": self.name,
            "version": self.version,
            "entity_type": self.entity_type.value,
            "description": self.description,
            "permissions": list(self.permissions),
            "sources": list(self.sources),
            "scope": list(self.scope),
            "timeout_seconds": self.timeout_seconds,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "compatibility": self.compatibility,
            "author": self.author,
        }

_registry: dict[str, Plugin] = {}

def register(plugin: Plugin) -> None:
    if not plugin.name or plugin.name in _registry:
        raise ValueError("plugin name must be non-empty and unique")
    if not plugin.version:
        raise ValueError("plugin version is required")
    if not plugin.description:
        raise ValueError("plugin description is required")
    if plugin.compatibility not in {"2.x", SDK_VERSION}:
        raise ValueError("plugin is incompatible with SDK 2.x")
    if plugin.timeout_seconds < 1 or plugin.timeout_seconds > 60:
        raise ValueError("timeout must be 1..60 seconds")
    if plugin.rate_limit_per_minute < 1 or plugin.rate_limit_per_minute > 600:
        raise ValueError("rate limit must be 1..600/min")
    _registry[plugin.name] = plugin

def list_plugins() -> list[dict]:
    return [p.manifest() for p in _registry.values()]

def health() -> list[dict]:
    result = []
    for plugin in _registry.values():
        try:
            ok = plugin.health_check() if plugin.health_check else True
            state = PluginHealth.HEALTHY if ok else PluginHealth.DEGRADED
        except Exception:
            state = PluginHealth.UNAVAILABLE
        result.append({**plugin.manifest(), "healthy": state == PluginHealth.HEALTHY, "health": state.value})
    return result

def get(name: str) -> Plugin | None:
    return _registry.get(name)

def run(name: str, target: str) -> list[Evidence]:
    plugin = _registry.get(name)
    if not plugin:
        raise KeyError(name)
    return plugin.collector(target)
