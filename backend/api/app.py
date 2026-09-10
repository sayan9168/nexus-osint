"""
NEXUS-OSINT: API Router Assembly
"""
from fastapi import APIRouter

from .routes import graph, entities, transforms, agent, osint, cases, reports


def create_router() -> APIRouter:
    router = APIRouter()
    router.include_router(graph.router, prefix="/graph", tags=["Graph"])
    router.include_router(entities.router, prefix="/entities", tags=["Entities"])
    router.include_router(transforms.router, prefix="/transforms", tags=["Transforms"])
    router.include_router(agent.router, prefix="/agent", tags=["Agent"])
    router.include_router(osint.router, prefix="/osint", tags=["OSINT"])
    router.include_router(cases.router, prefix="/cases", tags=["Cases"])
    router.include_router(reports.router, prefix="/reports", tags=["Reports"])
    return router
