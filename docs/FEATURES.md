# NEXUS-OSINT Feature Matrix

## Investigation core
- Explicit authorization gate before active collection
- Domain, public IP, URL and email validation/collection
- Public DNS and RDAP evidence
- URL HTTP metadata and security-header assessment
- HTTPS TLS certificate metadata
- Reverse DNS for public IPs
- SSRF-oriented protection against private/special-use destinations

## Evidence & integrity
- Persistent SQLite case storage
- Targets, notes and evidence attached to cases
- UTC observation timestamps
- Confidence values
- SHA-256 provenance hashes for persisted evidence
- Deterministic evidence timeline
- Explainable confidence scoring

## Analysis
- Investigation graph projection with source/target relationships
- Evidence provenance on graph edges
- Case score endpoint
- Source/connector catalog

## Reporting & export
- Deterministic Markdown reports
- Deterministic HTML reports
- JSON case export
- No mandatory LLM dependency for core reports

## API operations
- Health endpoint
- Case lifecycle endpoints
- Authorized scan endpoint
- Investigation graph endpoint
- Timeline endpoint
- Score endpoint
- Source catalog endpoint
- JSON export endpoint

## Safety boundaries
NEXUS-OSINT is designed for public-source OSINT and authorized security research. It intentionally does not provide credential theft, password attacks, private-account access, exploitation, stealth/evasion, or indiscriminate bulk profiling. External connectors should respect provider terms, rate limits, robots policies where applicable, and applicable law.

## Next expansion targets
- Pluggable connector SDK with per-source rate limits
- Entity normalization and deduplication
- More public DNS/RDAP record types
- Case tags and audit events
- Authentication/RBAC for multi-user deployments
- Background jobs and resumable investigations
- Import/export schemas for interoperability
- Frontend investigation workspace and graph controls
- Stronger automated test and security scanning coverage
