"""NEXUS-OSINT API router assembly."""
from fastapi import APIRouter
from .routes import graph,entities,transforms,agent,osint,cases,reports,graph_osint,platform,platform_ext,intelligence,case_io,workflow,v3,spatial,spatial_fusion,breach

def create_router():
 r=APIRouter()
 r.include_router(graph.router,prefix="/graph",tags=["Graph"])
 r.include_router(entities.router,prefix="/entities",tags=["Entities"])
 r.include_router(transforms.router,prefix="/transforms",tags=["Transforms"])
 r.include_router(agent.router,prefix="/agent",tags=["Agent"])
 r.include_router(osint.router,prefix="/osint",tags=["OSINT"])
 r.include_router(cases.router,prefix="/cases",tags=["Cases"])
 r.include_router(reports.router,prefix="/reports",tags=["Reports"])
 r.include_router(graph_osint.router,prefix="/investigation-graph",tags=["Investigation Graph"])
 r.include_router(platform.router,prefix="/platform",tags=["Platform"])
 r.include_router(platform_ext.router,prefix="/platform",tags=["Platform Extended"])
 r.include_router(intelligence.router,prefix="/intelligence",tags=["Intelligence"])
 r.include_router(case_io.router,prefix="/cases",tags=["Case Import Export"])
 r.include_router(workflow.router,prefix="/workflow",tags=["Workflow"])
 r.include_router(breach.router,prefix="/breach",tags=["Breach Exposure"])
 r.include_router(v3.router,prefix="/v3",tags=["NEXUS V3"])
 r.include_router(spatial.router,prefix="/v3/spatial",tags=["Spatial Intelligence"])
 r.include_router(spatial_fusion.router,prefix="/v3/spatial",tags=["Spatial Fusion"])
 return r
