"""
NEXUS-OSINT: VirusTotal Threat Intelligence Transform
Queries VirusTotal API for domain/IP/hash reputation and associated indicators.
"""
import asyncio
from typing import Any, Optional

import httpx
import structlog

from .base import BaseTransform, RateLimiter
from config import get_settings
from db.schemas import NodeLabel, EdgeType, TransformResult

logger = structlog.get_logger(__name__)


class VirusTotalTransform(BaseTransform):
    """Query VirusTotal for threat intelligence on domains, IPs, and hashes."""

    name = "virustotal_lookup"
    description = "Queries VirusTotal API for threat intelligence and IOCs"
    input_type = NodeLabel.DOMAIN  # Also supports IP, Hash
    output_types = [NodeLabel.IP, NodeLabel.DOMAIN, NodeLabel.HASH, NodeLabel.EMAIL]
    rate_limit = RateLimiter(max_calls=4, period_seconds=60.0)  # VT free tier

    BASE_URL = "https://www.virustotal.com/api/v3"

    def __init__(self):
        super().__init__()
        self._settings = get_settings()
        self._api_key = self._settings.VIRUSTOTAL_API_KEY

    async def execute(
        self, entity_value: str, parameters: Optional[dict[str, Any]] = None
    ) -> TransformResult:
        if not self._api_key:
            return TransformResult(
                transform_name=self.name,
                status="error",
                error_message="VirusTotal API key not configured",
            )

        entity_type = (parameters or {}).get("entity_type", "domain")
        new_nodes: list[dict[str, Any]] = []
        new_edges: list[dict[str, Any]] = []
        seen_values: set[str] = set()

        headers = {"x-apikey": self._api_key}

        async with httpx.AsyncClient(timeout=30.0) as client:
            # Determine endpoint based on entity type
            if entity_type == "domain":
                endpoint = f"{self.BASE_URL}/domains/{entity_value}"
            elif entity_type == "ip":
                endpoint = f"{self.BASE_URL}/ip_addresses/{entity_value}"
            elif entity_type == "hash":
                endpoint = f"{self.BASE_URL}/files/{entity_value}"
            else:
                endpoint = f"{self.BASE_URL}/domains/{entity_value}"

            try:
                response = await client.get(endpoint, headers=headers)
                response.raise_for_status()
                data = response.json().get("data", {})
                attributes = data.get("attributes", {})

                # Source node with threat data
                source_node = {
                    "label": entity_type.capitalize() if entity_type != "hash" else "Hash",
                    "value": entity_value,
                    "source_transform": self.name,
                    "metadata": {
                        "reputation": attributes.get("reputation", 0),
                        "last_analysis_stats": attributes.get("last_analysis_stats", {}),
                    },
                }
                new_nodes.append(source_node)
                seen_values.add(entity_value)

                # Extract resolved IPs (for domains)
                if entity_type == "domain":
                    resolutions = attributes.get("last_dns_records", [])
                    for record in resolutions:
                        if record.get("type") in ("A", "AAAA"):
                            ip_val = record.get("value", "")
                            if ip_val and ip_val not in seen_values:
                                new_nodes.append({
                                    "label": "IP",
                                    "value": ip_val,
                                    "source_transform": self.name,
                                })
                                new_edges.append({
                                    "source_value": entity_value,
                                    "target_value": ip_val,
                                    "edge_type": EdgeType.RESOLVES_TO.value,
                                    "properties": {"source": "virustotal", "record_type": record.get("type")},
                                })
                                seen_values.add(ip_val)

                # Extract communicating files (hashes)
                communicating_files = attributes.get("last_https_certificate", {})
                # Also check for downloaded files
                files_endpoint = f"{endpoint}/communicating_files"
                try:
                    files_resp = await client.get(files_endpoint, headers=headers)
                    if files_resp.status_code == 200:
                        files_data = files_resp.json().get("data", [])
                        for file_entry in files_data[:10]:  # Limit to 10
                            file_hash = file_entry.get("id", "")
                            file_attrs = file_entry.get("attributes", {})
                            if file_hash and file_hash not in seen_values:
                                detection = file_attrs.get("last_analysis_stats", {})
                                new_nodes.append({
                                    "label": "Hash",
                                    "value": file_hash,
                                    "hash_type": "sha256",
                                    "detection_ratio": f"{detection.get('malicious', 0)}/{detection.get('harmless', 0) + detection.get('malicious', 0)}",
                                    "source_transform": self.name,
                                })
                                new_edges.append({
                                    "source_value": entity_value,
                                    "target_value": file_hash,
                                    "edge_type": EdgeType.ASSOCIATED_WITH.value,
                                    "properties": {"relationship": "communicating_file"},
                                })
                                seen_values.add(file_hash)
                except Exception:
                    pass

                # Extract WHOIS email from VT data
                whois_email = attributes.get("whois", "")
                if "Registrant Email:" in whois_email:
                    import re
                    email_match = re.search(
                        r"Registrant Email:\s*(\S+@\S+)", whois_email
                    )
                    if email_match:
                        email_val = email_match.group(1).lower()
                        if email_val not in seen_values:
                            new_nodes.append({
                                "label": "Email",
                                "value": email_val,
                                "source_transform": self.name,
                            })
                            new_edges.append({
                                "source_value": entity_value,
                                "target_value": email_val,
                                "edge_type": EdgeType.REGISTERED_BY.value,
                                "properties": {"source": "virustotal_whois"},
                            })
                            seen_values.add(email_val)

            except httpx.HTTPStatusError as e:
                logger.error("virustotal.http_error", status=e.response.status_code)
                return TransformResult(
                    transform_name=self.name,
                    status="error",
                    error_message=f"VT API error: {e.response.status_code}",
                )
            except Exception as e:
                logger.error("virustotal.error", error=str(e))
                return TransformResult(
                    transform_name=self.name,
                    status="error",
                    error_message=str(e),
                )

        return TransformResult(
            transform_name=self.name,
            status="success",
            new_nodes=new_nodes,
            new_edges=new_edges,
        )
