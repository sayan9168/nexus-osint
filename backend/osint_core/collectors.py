from __future__ import annotations

import ipaddress
import socket
import ssl
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlparse

from .models import EntityType, Evidence


USER_AGENT = "NEXUS-OSINT/1.0 (+authorized-security-research)"


def _public_ip(value: str) -> bool:
    try:
        ip = ipaddress.ip_address(value)
        return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast)
    except ValueError:
        return False


def normalize_target(target: str, target_type: EntityType) -> str:
    value = target.strip()
    if target_type == EntityType.DOMAIN:
        value = value.lower().rstrip(".")
    elif target_type == EntityType.EMAIL:
        value = value.lower()
    elif target_type == EntityType.URL:
        if not value.startswith(("http://", "https://")):
            value = "https://" + value
    return value


def collect_domain(target: str) -> list[Evidence]:
    domain = normalize_target(target, EntityType.DOMAIN)
    results: list[Evidence] = []
    try:
        infos = socket.getaddrinfo(domain, None, type=socket.SOCK_STREAM)
        ips = sorted({item[4][0] for item in infos})
        public_ips = [ip for ip in ips if _public_ip(ip)]
        results.append(Evidence(source="system-dns", target=domain, data={"addresses": public_ips}))
    except socket.gaierror as exc:
        results.append(Evidence(source="system-dns", target=domain, data={"error": str(exc)}, confidence=0.2))

    try:
        with urllib.request.urlopen(
            urllib.request.Request(f"https://rdap.org/domain/{domain}", headers={"User-Agent": USER_AGENT}),
            timeout=8,
        ) as response:
            body = response.read(256_000).decode("utf-8", errors="replace")
            results.append(Evidence(source="rdap.org", target=domain, data={"status": response.status, "raw": body[:20_000]}))
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        results.append(Evidence(source="rdap.org", target=domain, data={"error": str(exc)}, confidence=0.2))
    return results


def collect_ip(target: str) -> list[Evidence]:
    value = normalize_target(target, EntityType.IP)
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return [Evidence(source="validator", target=value, data={"valid_ip": False}, confidence=1.0)]

    if not _public_ip(value):
        return [Evidence(source="scope", target=value, data={"public_routable": False}, notes="Private, reserved, or special-use address." )]

    hostname = None
    try:
        hostname = socket.gethostbyaddr(value)[0]
    except (socket.herror, socket.gaierror):
        pass
    return [Evidence(source="reverse-dns", target=value, data={"hostname": hostname, "public_routable": True})]


def collect_url(target: str) -> list[Evidence]:
    url = normalize_target(target, EntityType.URL)
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return [Evidence(source="validator", target=url, data={"valid_url": False}, confidence=1.0)]

    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(parsed.hostname, parsed.port or 443, type=socket.SOCK_STREAM)}
    except socket.gaierror as exc:
        return [Evidence(source="url-preflight", target=url, data={"error": str(exc)}, confidence=0.2)]

    if not addresses or not all(_public_ip(address) for address in addresses):
        return [Evidence(source="scope", target=url, data={"blocked": True, "reason": "hostname resolves to non-public address"}, confidence=1.0)]

    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            headers = {k.lower(): v for k, v in response.headers.items()}
            tls = parsed.scheme == "https"
            return [Evidence(source="http-head", target=url, data={"status": response.status, "final_url": response.geturl(), "headers": headers, "https": tls})]
    except urllib.error.HTTPError as exc:
        return [Evidence(source="http-head", target=url, data={"status": exc.code, "headers": dict(exc.headers.items())}, confidence=0.8)]
    except (urllib.error.URLError, TimeoutError) as exc:
        return [Evidence(source="http-head", target=url, data={"error": str(exc)}, confidence=0.2)]


def collect_email(target: str) -> list[Evidence]:
    value = normalize_target(target, EntityType.EMAIL)
    if "@" not in value or value.count("@") != 1:
        return [Evidence(source="validator", target=value, data={"valid_email_syntax": False})]
    local, domain = value.rsplit("@", 1)
    valid = bool(local and domain and "." in domain)
    return [Evidence(source="validator", target=value, data={"valid_email_syntax": valid, "domain": domain})]


def collect(target: str, target_type: EntityType) -> list[Evidence]:
    if target_type == EntityType.DOMAIN:
        return collect_domain(target)
    if target_type == EntityType.IP:
        return collect_ip(target)
    if target_type == EntityType.URL:
        return collect_url(target)
    if target_type == EntityType.EMAIL:
        return collect_email(target)
    return [Evidence(source="normalizer", target=normalize_target(target, target_type), data={"supported": False}, confidence=1.0)]
