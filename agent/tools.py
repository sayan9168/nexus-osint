"""
NEXUS-OSINT: Agent Tools for LangGraph Tool Calling
Wraps OSINT transforms and graph operations as LLM-callable tools.
"""
import httpx
from typing import Any, Optional
from langchain_core.tools import tool
import structlog

logger = structlog.get_logger(__name__)

BACKEND_URL = "http://backend:8000"


@tool
def run_dns_resolution(domain: str) -> str:
    """
    Resolve DNS records (A, AAAA, MX, NS, TXT) for a given domain.
    Use this to discover IP addresses, mail servers, and name servers.

    Args:
        domain: The domain name to resolve (e.g., "example.com")
    """
    import asyncio

    async def _run():
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{BACKEND_URL}/api/v1/transforms/execute",
                json={
                    "transform_name": "dns_resolution",
                    "entity_type": "Domain",
                    "entity_value": domain,
                    "parameters": {},
                },
            )
            return resp.json()

    result = asyncio.get_event_loop().run_until_complete(_run())
    return f"DNS Resolution for {domain}: {result}"


@tool
def run_whois_lookup(domain: str) -> str:
    """
    Perform WHOIS lookup on a domain to find registrant info, emails, and name servers.
    Use this to discover ownership information and registration details.

    Args:
        domain: The domain name to look up (e.g., "example.com")
    """
    import asyncio

    async def _run():
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{BACKEND_URL}/api/v1/transforms/execute",
                json={
                    "transform_name": "whois_lookup",
                    "entity_type": "Domain",
                    "entity_value": domain,
                    "parameters": {},
                },
            )
            return resp.json()

    result = asyncio.get_event_loop().run_until_complete(_run())
    return f"WHOIS for {domain}: {result}"


@tool
def run_virustotal_lookup(entity_value: str, entity_type: str = "domain") -> str:
    """
    Query VirusTotal for threat intelligence on a domain, IP, or file hash.
    Use this to check reputation, find associated malware, and discover IOCs.

    Args:
        entity_value: The domain, IP address, or SHA256 hash to query
        entity_type: One of "domain", "ip", or "hash"
    """
    import asyncio

    async def _run():
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{BACKEND_URL}/api/v1/transforms/execute",
                json={
                    "transform_name": "virustotal_lookup",
                    "entity_type": entity_type.capitalize(),
                    "entity_value": entity_value,
                    "parameters": {"entity_type": entity_type},
                },
            )
            return resp.json()

    result = asyncio.get_event_loop().run_until_complete(_run())
    return f"VirusTotal for {entity_value}: {result}"


@tool
def query_graph_neighbors(entity_value: str, depth: int = 2) -> str:
    """
    Query the knowledge graph for all entities connected to a given entity.
    Use this to understand the current investigation context and find related entities.

    Args:
        entity_value: The entity value to find neighbors for
        depth: How many hops to traverse (1-3)
    """
    import asyncio

    async def _run():
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                f"{BACKEND_URL}/api/v1/graph/neighbors",
                params={"entity_value": entity_value, "depth": depth},
            )
            return resp.json()

    result = asyncio.get_event_loop().run_until_complete(_run())
    return f"Graph neighbors for {entity_value}: {result}"


@tool
def find_semantic_correlations(entity_value: str, entity_type: str = "Domain") -> str:
    """
    Use vector similarity search to find hidden correlations between entities.
    Discovers non-obvious links based on semantic similarity of entity metadata.

    Args:
        entity_value: The entity to find correlations for
        entity_type: The type of entity (Domain, IP, Email, Hash, Person, etc.)
    """
    import asyncio

    async def _run():
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{BACKEND_URL}/api/v1/graph/correlate",
                json={
                    "entity_value": entity_value,
                    "entity_type": entity_type,
                },
            )
            return resp.json()

    result = asyncio.get_event_loop().run_until_complete(_run())
    return f"Correlations for {entity_value}: {result}"


@tool
def get_investigation_summary() -> str:
    """
    Get a summary of the current investigation state including all discovered
    entities, relationships, and key findings so far.
    """
    import asyncio

    async def _run():
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{BACKEND_URL}/api/v1/graph/summary")
            return resp.json()

    result = asyncio.get_event_loop().run_until_complete(_run())
    return f"Investigation Summary: {result}"


# All tools available to the agent
ALL_TOOLS = [
    run_dns_resolution,
    run_whois_lookup,
    run_virustotal_lookup,
    query_graph_neighbors,
    find_semantic_correlations,
    get_investigation_summary,
]
