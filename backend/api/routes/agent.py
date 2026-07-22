"""
NEXUS-OSINT: AI Agent Endpoints
"""
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

AGENT_URL = "http://agent:8001"


class AgentInvestigateRequest(BaseModel):
    target: str
    goal: str = "Conduct comprehensive OSINT investigation"
    max_iterations: int = 10


class AgentInvestigateResponse(BaseModel):
    status: str
    report: str
    entities_found: int
    correlations_found: int
    transforms_executed: list[str]


@router.post("/investigate", response_model=AgentInvestigateResponse)
async def trigger_investigation(req: AgentInvestigateRequest):
    """Trigger an autonomous AI investigation."""
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            resp = await client.post(
                f"{AGENT_URL}/investigate",
                json={
                    "target": req.target,
                    "goal": req.goal,
                    "max_iterations": req.max_iterations,
                },
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Agent service unavailable")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def agent_health():
    """Check agent service health."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{AGENT_URL}/health")
            return resp.json()
    except Exception:
        return {"status": "unavailable"}
