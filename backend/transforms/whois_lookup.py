"""
NEXUS-OSINT: WHOIS Lookup Transform
Retrieves domain registration data including registrant, registrar, and dates.
"""
import asyncio
from typing import Any, Optional
from datetime import datetime

import whois
import structlog

from .base import BaseTransform, RateLimiter
from db.schemas import NodeLabel, EdgeType, TransformResult

logger = structlog.get_logger(__name__)


class WhoisLookupTransform(BaseTransform):
    """Perform WHOIS lookup on a domain."""

    name = "whois_lookup"
    description = "Retrieves WHOIS registration data for a domain"
    input_type = NodeLabel.DOMAIN
    output_types = [NodeLabel.DOMAIN, NodeLabel.EMAIL, NodeLabel.PERSON]
    rate_limit = RateLimiter(max_calls=5, period_seconds=60.0)

    async def execute(
        self, entity_value: str, parameters: Optional[dict[str, Any]] = None
    ) -> TransformResult:
        domain = entity_value.lower().strip()
        new_nodes: list[dict[str, Any]] = []
        new_edges: list[dict[str, Any]] = []
        seen_values: set[str] = set()

        # Source node
        new_nodes.append({
            "label": "Domain",
            "value": domain,
            "source_transform": self.name,
        })
        seen_values.add(domain)

        try:
            w = await asyncio.to_thread(whois.whois, domain)

            # Extract registrar
            registrar = w.registrar
            if registrar:
                new_nodes[0]["registrar"] = registrar

            # Extract registration dates
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            if creation_date:
                new_nodes[0]["registration_date"] = str(creation_date)

            expiry_date = w.expiration_date
            if isinstance(expiry_date, list):
                expiry_date = expiry_date[0]
            if expiry_date:
                new_nodes[0]["expiry_date"] = str(expiry_date)

            # Extract name servers
            name_servers = w.name_servers
            if name_servers:
                if isinstance(name_servers, str):
                    name_servers = [name_servers]
                new_nodes[0]["name_servers"] = [ns.lower() for ns in name_servers]

                for ns in name_servers:
                    ns_lower = ns.lower().rstrip(".")
                    if ns_lower and ns_lower not in seen_values:
                        new_nodes.append({
                            "label": "Domain",
                            "value": ns_lower,
                            "source_transform": self.name,
                        })
                        new_edges.append({
                            "source_value": domain,
                            "target_value": ns_lower,
                            "edge_type": EdgeType.LINKED_TO.value,
                            "properties": {"relationship": "nameserver"},
                        })
                        seen_values.add(ns_lower)

            # Extract registrant email
            emails = w.emails
            if emails:
                if isinstance(emails, str):
                    emails = [emails]
                for email in emails:
                    email_lower = email.lower().strip()
                    if email_lower and email_lower not in seen_values:
                        new_nodes.append({
                            "label": "Email",
                            "value": email_lower,
                            "domain": email_lower.split("@")[-1] if "@" in email_lower else None,
                            "source_transform": self.name,
                        })
                        new_edges.append({
                            "source_value": domain,
                            "target_value": email_lower,
                            "edge_type": EdgeType.REGISTERED_BY.value,
                            "properties": {"role": "registrant_email"},
                        })
                        seen_values.add(email_lower)

            # Extract registrant name/org
            org = w.org or w.name
            if org:
                org_clean = str(org).strip()
                if org_clean and org_clean not in seen_values:
                    new_nodes.append({
                        "label": "Person",
                        "value": org_clean,
                        "full_name": org_clean,
                        "source_transform": self.name,
                    })
                    new_edges.append({
                        "source_value": domain,
                        "target_value": org_clean,
                        "edge_type": EdgeType.OWNS.value,
                        "properties": {"role": "registrant"},
                    })
                    seen_values.add(org_clean)

            # Extract status
            status = w.status
            if status:
                if isinstance(status, str):
                    status = [status]
                new_nodes[0]["status"] = status

        except Exception as e:
            logger.error("whois.error", domain=domain, error=str(e))
            return TransformResult(
                transform_name=self.name,
                status="error",
                error_message=f"WHOIS lookup failed: {str(e)}",
                new_nodes=new_nodes,
                new_edges=new_edges,
            )

        return TransformResult(
            transform_name=self.name,
            status="success",
            new_nodes=new_nodes,
            new_edges=new_edges,
        )
