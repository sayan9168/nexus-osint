"""
NEXUS-OSINT: Transform Registry
Central registry for discovering and instantiating transforms.
"""
from typing import Optional, Type

from .base import BaseTransform
from .dns_resolution import DNSResolutionTransform
from .whois_lookup import WhoisLookupTransform
from .virustotal import VirusTotalTransform


class TransformRegistry:
    """Singleton registry for all available transforms."""

    _transforms: dict[str, Type[BaseTransform]] = {}
    _instances: dict[str, BaseTransform] = {}

    @classmethod
    def register(cls, transform_class: Type[BaseTransform]) -> None:
        """Register a transform class."""
        cls._transforms[transform_class.name] = transform_class

    @classmethod
    def get(cls, name: str) -> Optional[BaseTransform]:
        """Get a transform instance by name."""
        if name not in cls._instances:
            if name in cls._transforms:
                cls._instances[name] = cls._transforms[name]()
            else:
                return None
        return cls._instances[name]

    @classmethod
    def list_all(cls) -> list[dict]:
        """List all registered transforms with metadata."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_type": t.input_type.value,
                "output_types": [o.value for o in t.output_types],
            }
            for t in cls._transforms.values()
        ]

    @classmethod
    def get_by_input_type(cls, node_type: str) -> list[BaseTransform]:
        """Get all transforms that accept a given input type."""
        results = []
        for t in cls._transforms.values():
            if t.input_type.value == node_type:
                results.append(cls.get(t.name))
        return results


# ─── Auto-register built-in transforms ───
TransformRegistry.register(DNSResolutionTransform)
TransformRegistry.register(WhoisLookupTransform)
TransformRegistry.register(VirusTotalTransform)
