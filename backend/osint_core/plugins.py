"""Versioned plugin SDK for bounded public-source collectors."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from .models import EntityType,Evidence
Collector=Callable[[str],list[Evidence]]
@dataclass(frozen=True)
class Plugin:
    name:str; version:str; entity_type:EntityType; description:str; collector:Collector
    permissions:tuple[str,...]=(); sources:tuple[str,...]=(); timeout_seconds:int=10; rate_limit_per_minute:int=30
_registry:dict[str,Plugin]={}
def register(plugin:Plugin)->None:
    if not plugin.name or plugin.name in _registry:raise ValueError("plugin name must be non-empty and unique")
    if plugin.timeout_seconds<1 or plugin.timeout_seconds>60:raise ValueError("timeout must be 1..60 seconds")
    if plugin.rate_limit_per_minute<1 or plugin.rate_limit_per_minute>600:raise ValueError("rate limit must be 1..600/min")
    _registry[plugin.name]=plugin
def list_plugins():
    return [{"name":p.name,"version":p.version,"entity_type":p.entity_type.value,"description":p.description,"permissions":list(p.permissions),"sources":list(p.sources),"timeout_seconds":p.timeout_seconds,"rate_limit_per_minute":p.rate_limit_per_minute} for p in _registry.values()]
def health(): return [{**p,"healthy":True} for p in list_plugins()]
def run(name:str,target:str)->list[Evidence]:
    plugin=_registry.get(name)
    if not plugin:raise KeyError(name)
    return plugin.collector(target)
