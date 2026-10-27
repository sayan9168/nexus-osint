"""OMNI — All public sources, unified."""
from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from api.security import require_permission, get_current_user
from osint_core import omni_sources as omni

router = APIRouter()

class OmniQuery(BaseModel):
    target: str = Field(min_length=1, max_length=320)
    target_type: str = Field(default="domain", pattern="^(domain|ip|url|email|wallet|hash|btc|eth|term)$")

@router.get("/catalog")
async def catalog(_: dict = Depends(get_current_user)):
    return {"count": len(omni.OMNI_SOURCES), "sources": omni.catalog()}

@router.get("/overview")
async def overview(_: dict = Depends(get_current_user)):
    return await omni.omni_overview()

@router.post("/query")
async def query(body: OmniQuery, _: dict = Depends(require_permission("case:read"))):
    return await omni.omni_query(body.target, body.target_type)

@router.get("/query")
async def query_get(target: str = Query(..., min_length=1, max_length=320), target_type: str = Query("domain", pattern="^(domain|ip|url|email|wallet|hash|btc|eth|term)$"), _: dict = Depends(require_permission("case:read"))):
    return await omni.omni_query(target, target_type)

# direct adapters for granular use
@router.get("/shodan/{ip}")
async def shodan(ip: str, _: dict = Depends(require_permission("case:read"))):
    return await omni.shodan_internetdb(ip)

@router.get("/ip/{ip}")
async def ip_geo(ip: str, _: dict = Depends(require_permission("case:read"))):
    return await omni.ip_api(ip)

@router.get("/bgp/ip/{ip}")
async def bgp_ip(ip: str, _: dict = Depends(require_permission("case:read"))):
    return await omni.bgpview_ip(ip)

@router.get("/bgp/asn/{asn}")
async def bgp_asn(asn: str, _: dict = Depends(require_permission("case:read"))):
    return await omni.bgpview_asn(asn)

@router.get("/wayback")
async def wayback(target: str = Query(..., min_length=1, max_length=320), _: dict = Depends(require_permission("case:read"))):
    return {"target": target, "snapshots": await omni.wayback_cdx(target)}

@router.get("/github/user/{username}")
async def gh_user(username: str, _: dict = Depends(require_permission("case:read"))):
    return await omni.github_user(username)

@router.get("/reddit")
async def reddit(q: str = Query(..., min_length=1, max_length=120), _: dict = Depends(require_permission("case:read"))):
    return {"query": q, "results": await omni.reddit_search(q)}

@router.get("/feeds/feodo")
async def feodo(_: dict = Depends(get_current_user)):
    return {"feed": "Feodo Tracker", "ips": await omni.feodo_blocklist(100)}

@router.get("/feeds/openphish")
async def openphish(_: dict = Depends(get_current_user)):
    return {"feed": "OpenPhish", "urls": await omni.openphish_feed(100)}

@router.get("/blockchair/btc/{addr}")
async def btc(addr: str, _: dict = Depends(require_permission("case:read"))):
    return await omni.blockchair_btc(addr)
