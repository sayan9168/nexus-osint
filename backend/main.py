"""
NEXUS-OSINT: Application Entry Point
"""
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from db.memgraph import get_memgraph
from api.app import create_router
from api.websocket.graph_ws import router as ws_router

logger = structlog.get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown."""
    # Startup
    logger.info("app.starting", version=settings.APP_VERSION)
    memgraph = await get_memgraph()
    logger.info("app.memgraph_connected")
    yield
    # Shutdown
    await memgraph.disconnect()
    logger.info("app.shutdown_complete")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Native OSINT & 3D Link Analysis Platform",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(create_router(), prefix="/api/v1")
app.include_router(ws_router)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
