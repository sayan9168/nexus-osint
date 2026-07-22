"""
NEXUS-OSINT: DNS/IP Resolution Transform
Resolves domain names to IP addresses (A, AAAA, MX, NS, TXT records).
"""
import asyncio
from typing import Any, Optional

import dns.resolver
import dns.rdatatype
import structlog

from .base import BaseTransform, RateLimiter
from db.schemas import NodeLabel, EdgeType, TransformResult

logger = structlog.get_logger(__name__)


class DNSResolutionTransform(BaseTransform):
    """Resolve DNS records for a given domain."""

    name = "dns_resolution"
    description = "Resolves domain to IP addresses via DNS (A, AAAA, MX, NS, TXT)"
    input_type = NodeLabel.DOMAIN
    output_types = [NodeLabel.IP, NodeLabel.DOMAIN, NodeLabel.EMAIL]
    rate_limit = RateLimiter(max_calls=50, period_seconds=60.0)

    RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]

    async def execute(
        self, entity_value: str, parameters: Optional[dict[str, Any]] = None
    ) -> TransformResult:
        domain = entity_value.lower().strip()
        record_types = parameters.get("record_types", self.RECORD_TYPES) if parameters else self.RECORD_TYPES

        new_nodes: list[dict[str, Any]] = []
        new_edges: list[dict[str, Any]] = []
        seen_values: set[str] = set()

        # Ensure source domain node exists
        new_nodes.append({
            "label": "Domain",
            "value": domain,
            "source_transform": self.name,
        })
        seen_values.add(domain)

        for rtype in record_types:
            try:
                answers = await asyncio.to_thread(
                    dns.resolver.resolve, domain, rtype
                )
                for rdata in answers:
                    if rtype in ("A", "AAAA"):
                        ip_value = str(rdata)
                        if ip_value not in seen_values:
                            new_nodes.append({
                                "label": "IP",
                                "value": ip_value,
                                "ip_version": 4 if rtype == "A" else 6,
                                "source_transform": self.name,
                            })
                            new_edges.append({
                                "source_value": domain,
                                "target_value": ip_value,
                                "edge_type": EdgeType.RESOLVES_TO.value,
                                "properties": {"record_type": rtype, "ttl": answers.rrset.ttl},
                            })
                            seen_values.add(ip_value)

                    elif rtype == "MX":
                        mx_host = str(rdata.exchange).rstrip(".")
                        if mx_host and mx_host not in seen_values:
                            new_nodes.append({
                                "label": "Domain",
                                "value": mx_host,
                                "source_transform": self.name,
                                "metadata": {"mx_priority": rdata.preference},
                            })
                            new_edges.append({
                                "source_value": domain,
                                "target_value": mx_host,
                                "edge_type": EdgeType.LINKED_TO.value,
                                "properties": {"record_type": "MX", "priority": rdata.preference},
                            })
                            seen_values.add(mx_host)

                    elif rtype == "NS":
                        ns_host = str(rdata).rstrip(".")
                        if ns_host and ns_host not in seen_values:
                            new_nodes.append({
                                "label": "Domain",
                                "value": ns_host,
                                "source_transform": self.name,
                            })
                            new_edges.append({
                                "source_value": domain,
                                "target_value": ns_host,
                                "edge_type": EdgeType.LINKED_TO.value,
                                "properties": {"record_type": "NS"},
                            })
                            seen_values.add(ns_host)

                    elif rtype == "TXT":
                        txt_value = str(rdata).strip('"')
                        # Extract email addresses from TXT (SPF, DMARC)
                        if "include:" in txt_value or "a:" in txt_value:
                            parts = txt_value.split()
                            for part in parts:
                                if part.startswith("include:"):
                                    inc_domain = part.replace("include:", "")
                                    if inc_domain not in seen_values:
                                        new_nodes.append({
                                            "label": "Domain",
                                            "value": inc_domain,
                                            "source_transform": self.name,
                                        })
                                        new_edges.append({
                                            "source_value": domain,
                                            "target_value": inc_domain,
                                            "edge_type": EdgeType.LINKED_TO.value,
                                            "properties": {"record_type": "TXT", "context": "SPF"},
                                        })
                                        seen_values.add(inc_domain)

            except dns.resolver.NXDOMAIN:
                logger.warning("dns.nxdomain", domain=domain, record=rtype)
            except dns.resolver.NoAnswer:
                pass
            except dns.resolver.NoNameservers:
                logger.warning("dns.no_nameservers", domain=domain)
            except Exception as e:
                logger.warning("dns.error", domain=domain, record=rtype, error=str(e))

        return TransformResult(
            transform_name=self.name,
            status="success",
            new_nodes=new_nodes,
            new_edges=new_edges,
        )
