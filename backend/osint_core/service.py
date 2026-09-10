from __future__ import annotations

from uuid import uuid4

from .collectors import collect, normalize_target
from .models import EntityType, Investigation, ScanResponse


class OSINTService:
    """Orchestrates bounded, public-source collection for an authorized case."""

    def scan(self, target: str, target_type: EntityType, authorized: bool) -> ScanResponse:
        normalized = normalize_target(target, target_type)
        if not authorized:
            return ScanResponse(
                target=normalized,
                target_type=target_type,
                evidence=[],
                warnings=["Authorization is required before active collection is performed."],
            )

        evidence = collect(normalized, target_type)
        return ScanResponse(target=normalized, target_type=target_type, evidence=evidence)

    def new_investigation(self, target: str, target_type: EntityType, authorized: bool) -> Investigation:
        return Investigation(
            id=str(uuid4()),
            target=normalize_target(target, target_type),
            target_type=target_type,
            authorized=authorized,
        )
