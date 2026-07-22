"""
NEXUS-OSINT: Entity Schemas (Pydantic v2 Models)
Defines all node types, edge types, and their validation rules.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator
import re


# ─── Edge Types ───
class EdgeType(str, Enum):
    RESOLVES_TO = "RESOLVES_TO"
    OWNS = "OWNS"
    LINKED_TO = "LINKED_TO"
    COMMUNICATES_WITH = "COMMUNICATES_WITH"
    TRANSACTED_WITH = "TRANSACTED_WITH"
    HOSTED_ON = "HOSTED_ON"
    REGISTERED_BY = "REGISTERED_BY"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"
    POSTED_ON = "POSTED_ON"
    MENTIONS = "MENTIONS"


# ─── Node Labels ───
class NodeLabel(str, Enum):
    DOMAIN = "Domain"
    IP = "IP"
    EMAIL = "Email"
    HASH = "Hash"
    WALLET = "Wallet"
    PERSON = "Person"
    SOCIAL_HANDLE = "SocialHandle"
    DARKNET_FORUM_POST = "DarknetForumPost"


# ─── Base Node Schema ───
class BaseNode(BaseModel):
    id: Optional[str] = None
    label: NodeLabel
    value: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    source_transform: Optional[str] = None
    confidence_score: float = Field(default=1.0, ge=0.0, le=1.0)


# ─── Domain Node ───
class DomainNode(BaseNode):
    label: NodeLabel = NodeLabel.DOMAIN
    registrar: Optional[str] = None
    registration_date: Optional[str] = None
    expiry_date: Optional[str] = None
    name_servers: list[str] = Field(default_factory=list)
    status: list[str] = Field(default_factory=list)

    @field_validator("value")
    @classmethod
    def validate_domain(cls, v: str) -> str:
        pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError(f"Invalid domain format: {v}")
        return v.lower()


# ─── IP Node ───
class IPNode(BaseNode):
    label: NodeLabel = NodeLabel.IP
    ip_version: int = 4
    asn: Optional[str] = None
    asn_org: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    is_malicious: bool = False

    @field_validator("value")
    @classmethod
    def validate_ip(cls, v: str) -> str:
        import ipaddress
        try:
            ipaddress.ip_address(v)
        except ValueError:
            raise ValueError(f"Invalid IP address: {v}")
        return v


# ─── Email Node ───
class EmailNode(BaseNode):
    label: NodeLabel = NodeLabel.EMAIL
    domain: Optional[str] = None
    is_disposable: bool = False
    breach_count: int = 0

    @field_validator("value")
    @classmethod
    def validate_email(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError(f"Invalid email format: {v}")
        return v.lower()


# ─── Hash Node ───
class HashNode(BaseNode):
    label: NodeLabel = NodeLabel.HASH
    hash_type: str = "sha256"  # md5, sha1, sha256
    file_name: Optional[str] = None
    file_size: Optional[int] = None
    detection_ratio: Optional[str] = None
    malware_family: Optional[str] = None

    @field_validator("value")
    @classmethod
    def validate_hash(cls, v: str) -> str:
        v = v.lower()
        if len(v) == 32 and re.match(r"^[a-f0-9]{32}$", v):
            return v
        elif len(v) == 40 and re.match(r"^[a-f0-9]{40}$", v):
            return v
        elif len(v) == 64 and re.match(r"^[a-f0-9]{64}$", v):
            return v
        raise ValueError(f"Invalid hash format: {v}")


# ─── Wallet Node ───
class WalletNode(BaseNode):
    label: NodeLabel = NodeLabel.WALLET
    blockchain: str = "bitcoin"  # bitcoin, ethereum, monero
    balance: Optional[float] = None
    transaction_count: Optional[int] = None
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None

    @field_validator("value")
    @classmethod
    def validate_wallet(cls, v: str) -> str:
        if len(v) < 26:
            raise ValueError(f"Wallet address too short: {v}")
        return v


# ─── Person Node ───
class PersonNode(BaseNode):
    label: NodeLabel = NodeLabel.PERSON
    full_name: Optional[str] = None
    aliases: list[str] = Field(default_factory=list)
    nationality: Optional[str] = None
    occupation: Optional[str] = None

    @field_validator("value")
    @classmethod
    def validate_person(cls, v: str) -> str:
        if len(v.strip()) < 2:
            raise ValueError("Person name too short")
        return v.strip()


# ─── Social Handle Node ───
class SocialHandleNode(BaseNode):
    label: NodeLabel = NodeLabel.SOCIAL_HANDLE
    platform: str = "twitter"  # twitter, github, telegram, discord
    profile_url: Optional[str] = None
    follower_count: Optional[int] = None
    is_verified: bool = False

    @field_validator("value")
    @classmethod
    def validate_handle(cls, v: str) -> str:
        if not v.startswith("@") and "@" not in v:
            v = f"@{v}"
        return v


# ─── Darknet Forum Post Node ───
class DarknetForumPostNode(BaseNode):
    label: NodeLabel = NodeLabel.DARKNET_FORUM_POST
    forum_name: Optional[str] = None
    post_title: Optional[str] = None
    post_url: Optional[str] = None
    author_handle: Optional[str] = None
    post_date: Optional[str] = None
    category: Optional[str] = None

    @field_validator("value")
    @classmethod
    def validate_post_id(cls, v: str) -> str:
        if len(v.strip()) < 1:
            raise ValueError("Post ID cannot be empty")
        return v.strip()


# ─── Edge Schema ───
class EdgeSchema(BaseModel):
    source_id: str
    target_id: str
    edge_type: EdgeType
    properties: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    discovered_by: Optional[str] = None


# ─── Graph Response Schemas ───
class GraphNodeResponse(BaseModel):
    id: str
    label: str
    value: str
    properties: dict[str, Any]


class GraphEdgeResponse(BaseModel):
    source: str
    target: str
    type: str
    properties: dict[str, Any]


class GraphResponse(BaseModel):
    nodes: list[GraphNodeResponse]
    edges: list[GraphEdgeResponse]
    total_nodes: int
    total_edges: int


# ─── Transform Request/Response ───
class TransformRequest(BaseModel):
    transform_name: str
    entity_type: NodeLabel
    entity_value: str
    parameters: dict[str, Any] = Field(default_factory=dict)


class TransformResult(BaseModel):
    transform_name: str
    status: str  # "success", "error", "rate_limited"
    new_nodes: list[dict[str, Any]] = Field(default_factory=list)
    new_edges: list[dict[str, Any]] = Field(default_factory=list)
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0
