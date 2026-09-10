"""Minimal plugin SDK for safe, public-source collectors."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .models import EntityType, Evidence

Collector = Callable[[str], list[Evidence]]


@dataclass(frozen=True)
class Plugin:
    name: str
    version: str
    entity_type: EntityType
    description: str
    collector: Collector


_registry: dict[str, Plugin] = {}


def register(plugin: Plugin) -> None:
    if not plugin.name or plugin.name in _registry:
        raise ValueError("plugin name must be non-empty and unique")
    _registry[plugin.name] = plugin


def list_plugins() -> list[dict[str, str]]:
    return [{"name": p.name, "version": p.version, "entity_type": p.entity_type.value, "description": p.description}
            for p in _registry.values()]


def run(name: str, target: str) -> list[Evidence]:
    plugin = _registry.get(name)
    if not plugin:
        raise KeyError(name)
    return plugin.collector(target)
