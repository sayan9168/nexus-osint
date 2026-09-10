"""Deterministic investigation report generation with no LLM dependency."""
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from .models import Evidence, Investigation


def to_markdown(investigation: Investigation) -> str:
    lines = [
        f"# NEXUS-OSINT Investigation {investigation.id}",
        "",
        f"- **Target:** `{investigation.target}`",
        f"- **Type:** `{investigation.target_type}`",
        f"- **Authorized:** `{investigation.authorized}`",
        f"- **Generated:** `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Evidence",
        "",
    ]
    if not investigation.evidence:
        lines.append("No evidence collected.")
    for i, item in enumerate(investigation.evidence, 1):
        lines.extend([
            f"### {i}. {item.source}",
            f"- Target: `{item.target}`",
            f"- Observed: `{item.observed_at.isoformat()}`",
            f"- Confidence: `{item.confidence:.2f}`",
            f"- Data: `{item.data}`",
            f"- Notes: {item.notes or 'None'}",
            "",
        ])
    return "\n".join(lines)


def to_html(investigation: Investigation) -> str:
    return "<!doctype html><html><head><meta charset='utf-8'>" \
        "<title>NEXUS-OSINT Report</title></head><body>" \
        f"<h1>NEXUS-OSINT Investigation {escape(investigation.id)}</h1>" \
        f"<p><b>Target:</b> {escape(investigation.target)}<br>" \
        f"<b>Type:</b> {escape(str(investigation.target_type))}<br>" \
        f"<b>Authorized:</b> {investigation.authorized}</p>" \
        + "".join(
            f"<article><h2>{escape(e.source)}</h2><p>"
            f"Target: {escape(e.target)}<br>Confidence: {e.confidence:.2f}<br>"
            f"Observed: {escape(e.observed_at.isoformat())}</p>"
            f"<pre>{escape(str(e.data))}</pre></article>"
            for e in investigation.evidence
        ) + "</body></html>"
