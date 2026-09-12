<div align="center">

# NEXUS-OSINT

### Public-Source Intelligence, Investigation Graphs & Spatial Analysis

A security-focused, open-source intelligence platform for authorized investigations. NEXUS-OSINT combines case management, evidence provenance, public-source collection, relationship analysis, 3D visualization, spatial intelligence, and reproducible reporting in one investigation workspace.

[![License](https://img.shields.io/badge/License-Sayanox%20v1.1-cyan)](./LICENSE)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/Frontend-Next.js-111111)](https://nextjs.org/)
[![Language](https://img.shields.io/badge/Language-Python%203.11%2B-3776AB)](https://www.python.org/)
[![Security](https://img.shields.io/badge/Focus-Authorized%20OSINT-0B7285)](./SECURITY.md)

**Investigate. Correlate. Preserve. Explain.**

[Issues](https://github.com/sayan9168/nexus-osint/issues) · [Security Policy](./SECURITY.md) · [Documentation](./docs/)

</div>

---

## Overview

NEXUS-OSINT is an investigation platform built around a simple principle: **public intelligence should be collected with clear provenance, bounded execution, and an auditable chain of evidence**.

The platform is designed for security researchers, defenders, investigators, analysts, students, and organizations performing legitimate research. It provides a persistent workspace where public signals can be collected, normalized, correlated, visualized, scored, reviewed, and exported.

NEXUS is intentionally not a private-account access tool, credential harvesting framework, exploitation platform, or covert people-tracking system.

### Core workflow

```text
Target / Case
      │
      ▼
Public Sources ──► Collectors ──► Normalization
      │                               │
      │                               ▼
      │                         Deduplication
      │                               │
      ▼                               ▼
Evidence ◄──────────────► Entities & Relationships
      │                               │
      ▼                               ▼
Evidence Snapshots              Investigation Graph
      │                               │
      └──────────────┬────────────────┘
                     ▼
              Timeline + Scoring
                     │
                     ▼
             Spatial Intelligence
                     │
                     ▼
          Reports / JSON / Case Bundle
```

---

## Highlights

### Investigation Workspace

- Persistent cases with status, tags, workflow state, and authorization metadata
- Targets, notes, evidence, audit events, and investigation history
- Case-aware workspace navigation
- Evidence provenance and deterministic fingerprints
- JSON case bundle export/import

### Intelligence & Correlation

- DNS and RDAP intelligence
- Entity and relationship modeling
- Idempotent relationship merging
- Public-source signal normalization
- Confidence scoring
- Signal fingerprinting and deduplication
- Correlated spatial context
- Investigation graph analysis
- Timeline reconstruction

### Spatial Intelligence

The Spatial Intelligence workspace combines public geographic, environmental, infrastructure, transport, aviation, maritime, space, and event data where the corresponding source is available and permitted.

Current source families include:

| Source | Intelligence |
|---|---|
| OpenSky | Public aircraft data |
| USGS | Earthquake and earth-science events |
| NASA EONET | Natural-event feeds |
| CelesTrak | Public satellite orbital catalog data |
| Launch Library 2 | Public launch/event data |
| Radio Browser | Public geolocated radio metadata |
| GDELT | Public open-web geographic event signals |
| OpenStreetMap / Overpass | Public geographic and infrastructure context |
| Nominatim | Reverse geocoding |
| Open-Meteo | Weather and environmental context |
| NOAA | Public weather and alert data |
| RIPE Atlas | Public Internet measurement/probe metadata |
| RIPEstat | Public Internet and network intelligence |
| NASA FIRMS | Fire data when configured/available |
| AISStream | Maritime data when configured/available |
| Public feed adapters | Authorized/configured traffic and camera metadata |

Availability, rate limits, API keys, attribution requirements, and provider terms vary by source. NEXUS does not claim that every source is continuously available.

### 3D Investigation Interface

- Interactive Three.js globe
- Orbit and cockpit-style viewing modes
- Signal focus/tracking
- Layer visibility controls
- Sensor-style visual presets
- Tactical HUD and detection overlays
- Scene director
- Browser-based investigation whiteboard
- Shareable view state
- Case evidence visualization
- Spatial source registry

The spatial module models **events, infrastructure, geographic context, and public signals**. It does not provide facial recognition or covert named-person tracking.

### Evidence & Auditability

NEXUS treats evidence as a first-class object.

Each investigation can preserve:

- Source
- Target
- Observed data
- Timestamp
- Confidence
- Evidence payload
- Provenance hash
- Evidence snapshots
- Actor/audit information
- Relationship context

This makes an investigation easier to reproduce, review, and explain instead of presenting an opaque collection of search results.

### Authentication & Authorization

The platform includes:

- Persistent user accounts
- JWT authentication
- Role-based access control
- Viewer / Analyst / Admin roles
- Permission-aware API routes
- Case authorization checks
- Audit logging
- Security-focused request controls

### Resilience & Operations

- Persistent background jobs
- Bounded worker concurrency
- Retry and cancellation state
- Optional Redis/Celery execution
- Structured logging
- CORS allowlisting
- Request-size controls
- Rate limiting
- Security headers and CSP
- Public-address/SSRF preflight controls for network collectors
- Health and platform metrics endpoints

---

## Architecture

```text
┌──────────────────────────────────────────────────────────────────┐
│                         NEXUS-OSINT                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐        ┌───────────────────────────┐  │
│  │ Next.js Investigation│ REST   │ FastAPI Investigation API │  │
│  │ Workspace + 3D Globe │◄──────►│ Auth / RBAC / Cases       │  │
│  └──────────────────────┘        └─────────────┬─────────────┘  │
│                                               │                 │
│                     ┌─────────────────────────┼────────────┐    │
│                     ▼                         ▼            ▼    │
│             ┌──────────────┐        ┌──────────────┐ ┌────────┐│
│             │ OSINT Core   │        │ Spatial Core │ │ Jobs   ││
│             │ DNS / RDAP   │        │ Public Feeds │ │ Celery ││
│             │ Cases / Graph│        │ Context/Fusion│ │ Redis  ││
│             └──────┬───────┘        └──────┬───────┘ └────────┘│
│                    │                       │                    │
│                    └──────────┬────────────┘                    │
│                               ▼                                 │
│                    ┌────────────────────┐                       │
│                    │ Persistence Layer  │                       │
│                    │ Cases / Evidence   │                       │
│                    │ Entities / Audit   │                       │
│                    │ Jobs / Snapshots   │                       │
│                    └────────────────────┘                       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

The repository also contains extension foundations for plugins, workflows, analytics, reporting, organizations, saved searches, and durable investigation pipelines.

---

## Technology

| Area | Technology |
|---|---|
| API | FastAPI / Python 3.11+ |
| Validation | Pydantic |
| HTTP | HTTPX |
| Database | SQLite persistence layer with WAL/foreign-key support |
| Jobs | ThreadPoolExecutor with optional Celery + Redis |
| Authentication | JWT + password hashing |
| Frontend | Next.js + TypeScript |
| 3D | Three.js |
| Logging | Structured logging |
| Deployment | Docker / Docker Compose |
| CI | GitHub Actions |

The architecture is intentionally modular so optional infrastructure can be introduced without making the core investigation workflow dependent on a paid external service.

---

## Project Structure

```text
nexus-osint/
├── backend/
│   ├── main.py
│   ├── api/
│   │   ├── app.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── cases.py
│   │   │   ├── intelligence.py
│   │   │   ├── reports.py
│   │   │   ├── spatial.py
│   │   │   ├── spatial_fusion.py
│   │   │   ├── v3.py
│   │   │   └── ...
│   │   └── security.py
│   ├── osint_core/
│   │   ├── auth.py
│   │   ├── audit.py
│   │   ├── cases.py
│   │   ├── collectors.py
│   │   ├── dedup.py
│   │   ├── graph.py
│   │   ├── intelligence.py
│   │   ├── jobs.py
│   │   ├── persistence.py
│   │   ├── plugins.py
│   │   ├── public_sources.py
│   │   ├── scoring.py
│   │   ├── source_fusion.py
│   │   ├── spatial.py
│   │   └── timeline.py
│   └── tests/
│
├── frontend/
│   └── src/
│       ├── app/
│       │   ├── page.tsx
│       │   ├── spatial/
│       │   └── ...
│       └── lib/
│
├── docs/
├── .github/
│   └── workflows/
├── docker-compose.production.yml
├── .env.example
├── CHANGELOG.md
├── LICENSE
└── README.md
```

---

## Quick Start

### Requirements

- Python 3.11+
- Node.js 18+
- npm
- Git
- Docker and Docker Compose are recommended for production-style deployment

### Clone

```bash
git clone https://github.com/sayan9168/nexus-osint.git
cd nexus-osint
```

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend normally runs on the Next.js development port shown by the terminal. Configure the backend URL through `NEXT_PUBLIC_API_URL` when required.

### Environment

Start from the supplied template:

```bash
cp .env.example .env
```

Important settings include JWT configuration, CORS origins, database location, optional Redis/Celery settings, and optional public-source credentials.

Never commit secrets to Git.

---

## Docker

For a production-style local environment:

```bash
docker compose -f docker-compose.production.yml up --build
```

For a Celery worker when Redis/Celery execution is enabled:

```bash
celery -A osint_core.jobs worker --loglevel=INFO --concurrency=2
```

Review the deployment documentation and environment template before exposing the service to an untrusted network.

---

## Investigation Workflow

A recommended workflow is:

1. Create a case.
2. Mark the case as authorized for the intended investigation.
3. Add one or more public targets.
4. Run bounded collectors.
5. Review returned evidence and provenance.
6. Inspect entities and relationships.
7. Open the Investigation Graph.
8. Open Spatial Intelligence for geographic signals and context.
9. Review timeline and confidence scoring.
10. Preserve important evidence snapshots.
11. Export a report or case bundle.
12. Review the audit trail before sharing results.

See `docs/INVESTIGATION_WORKFLOW.md` and `docs/SECURITY_BOUNDARIES.md` for operational guidance.

---

## API Surface

The API is organized into versioned functional areas.

### Authentication

```text
/api/v1/auth/register
/api/v1/auth/login
/api/v1/auth/me
```

### Cases & Evidence

```text
/api/v1/cases/...
/api/v1/reports/...
/api/v1/cases/{case_id}/bundle.json
/api/v1/cases/import
```

### Intelligence

```text
/api/v1/intelligence/dns-rdap
/api/v1/intelligence/entities/{case_id}
/api/v1/intelligence/relationships
```

### Platform

```text
/api/v1/platform/health
/api/v1/platform/sources
/api/v1/platform/cases/{case_id}/timeline
/api/v1/platform/cases/{case_id}/score
/api/v1/platform/cases/{case_id}/export.json
/api/v1/platform/jobs
/api/v1/platform/metrics
```

### V3

```text
/api/v1/v3/search
/api/v1/v3/search/saved
/api/v1/v3/analytics/{case_id}
/api/v1/v3/entities/correlate/{case_id}
/api/v1/v3/graph/{case_id}/analysis
/api/v1/v3/evidence/{evidence_id}/snapshot
/api/v1/v3/pipelines/{case_id}
/api/v1/v3/orgs
/api/v1/v3/replay/{case_id}
```

### Spatial Intelligence

```text
/api/v1/v3/spatial/layers
/api/v1/v3/spatial/sources
/api/v1/v3/spatial/context
/api/v1/v3/spatial/cases/{case_id}/points
/api/v1/v3/spatial/fusion
/api/v1/v3/spatial/fusion/context
```

Exact schemas and authentication requirements should be treated as authoritative in the running OpenAPI documentation.

---

## Public Source Model

NEXUS uses a source-registry approach rather than hard-coding a single intelligence provider.

Each source can carry metadata such as:

- Source identifier
- Display name
- Category
- Access model
- Availability
- Rate-limit expectations
- Optional configuration requirements
- Attribution requirements
- Collection status

The long-term architecture is designed around:

```text
Source Adapter
     ↓
Normalized Signal
     ↓
Validation
     ↓
Fingerprint / Dedup
     ↓
Confidence
     ↓
Evidence
     ↓
Entity / Relationship
     ↓
Timeline / Graph / Spatial View
```

This allows additional public datasets and APIs to be integrated without redesigning the investigation model.

---

## Spatial Intelligence Design

Spatial signals are intentionally separated into layers so analysts can inspect source provenance and avoid treating every point as ground truth.

Examples include:

- Aircraft
- Earthquakes
- Satellites
- Launches
- Radio stations
- Natural events
- Open-web geographic events
- Case evidence
- Maritime signals when configured
- Traffic data when configured
- Public camera metadata when configured
- Fire data when configured
- Internet measurement probes

### Satellite positioning

The spatial architecture supports public orbital catalog integration. Live geographic propagation should be treated as derived data: the source orbital elements are preserved, propagation parameters are explicit, and derived positions are not represented as authoritative observations.

---

## Security Model

NEXUS is designed for **authorized, public-source intelligence work**.

### Included safeguards

- JWT authentication
- RBAC permissions
- Case authorization checks
- Audit logging
- Evidence provenance
- Hash-based evidence snapshots
- Bounded network timeouts
- Result-size limits
- Request-size controls
- Rate limiting
- CORS allowlisting
- Security headers/CSP
- SSRF/public-address preflight for applicable collectors
- Explicit public-source boundaries

### Explicitly out of scope

NEXUS does not provide features intended to:

- Steal passwords, API keys, tokens, or sessions
- Bypass authentication or access controls
- Access private accounts or private datasets without authorization
- Exploit vulnerable systems
- Evade detection or conceal malicious activity
- Perform covert surveillance
- Perform facial recognition or named-person spatial tracking
- Conduct indiscriminate mass profiling

If a source requires authorization, an API key, an account, or contractual access, it is treated as an optional/configured source rather than falsely presented as unrestricted public access.

See `SECURITY.md` and `docs/SECURITY_BOUNDARIES.md`.

---

## Data Provenance

A central design goal is reproducibility.

For important observations, NEXUS can retain source and timing metadata together with normalized evidence. Evidence snapshots provide versioned representations so an analyst can distinguish:

```text
What the source returned
        ↓
What NEXUS normalized
        ↓
What relationship was inferred
        ↓
What the analyst concluded
```

This distinction is important because **correlation is not proof**. Confidence scores are analytical aids, not guarantees of truth.

---

## Reporting

Supported report formats include:

- Markdown
- HTML
- JSON
- Case bundle JSON for portable investigations

Reports are intended to preserve enough context for another analyst to understand the evidence, sources, timestamps, relationships, and limitations behind a conclusion.

---

## Plugin & Extension Model

NEXUS includes a plugin foundation with metadata for:

- Plugin identity and version
- Entity types
- Description
- Required permissions
- Source declarations
- Scope
- Timeout
- Rate limit
- Compatibility
- Health checks
- Author metadata

Future extensions can build source adapters, transforms, enrichment modules, and visualization providers without coupling them to the core case model.

Production deployments should add appropriate sandboxing and signature verification before accepting untrusted third-party plugins.

---

## Development

Run backend tests from the backend directory:

```bash
cd backend
pytest -q
```

Compile-check Python modules when making low-level changes:

```bash
python -m compileall -q .
```

Frontend:

```bash
cd frontend
npm install
npm run build
```

GitHub Actions provides the repository CI workflow for automated validation. A local green build is not a substitute for reviewing deployment configuration, provider limits, and security controls.

---

## Operational Principles

NEXUS follows these principles:

1. **Public by default, private by explicit authorization.**
2. **Every important observation should have provenance.**
3. **Derived intelligence must be distinguishable from source observations.**
4. **Correlation must not be presented as certainty.**
5. **Network collection must be bounded and SSRF-aware.**
6. **Provider terms, attribution, and rate limits matter.**
7. **Case authorization is part of the workflow, not an afterthought.**
8. **Sensitive capabilities should be excluded rather than hidden behind vague labels.**

---

## Roadmap

### Intelligence Platform

- [x] Persistent investigation cases
- [x] Evidence provenance and snapshots
- [x] Investigation graph
- [x] Timeline and scoring
- [x] Authentication and RBAC
- [x] Durable background jobs
- [x] Case import/export
- [x] Public source registry
- [x] Public signal fusion

### Spatial Platform

- [x] 3D globe
- [x] Aircraft and earthquake layers
- [x] Public natural-event layers
- [x] Satellite catalog integration
- [x] Launch and radio layers
- [x] Geographic context lookup
- [x] Spatial signal fusion
- [x] Source registry
- [ ] Satellite orbital propagation and live derived positions
- [ ] Signal-density heatmaps
- [ ] Advanced temporal playback
- [ ] Source health dashboard
- [ ] Automated spatial clustering

### Platform

- [x] Role-based access control
- [x] Audit chain
- [x] Structured logging
- [x] Rate limiting
- [x] Security headers
- [x] Docker deployment foundation
- [ ] Distributed rate limiting
- [ ] Prometheus/OpenTelemetry observability
- [ ] Hardened plugin sandbox
- [ ] Signed plugin marketplace

Roadmap items are engineering targets, not claims of current availability.

---

## Contributing

Contributions are welcome when they improve reliability, documentation, source coverage, security, usability, or investigation quality.

Before submitting a change:

1. Keep public-source integrations bounded and documented.
2. Preserve provenance and attribution metadata.
3. Add or update tests for behavioral changes.
4. Do not introduce credential theft, access-control bypass, exploitation, covert tracking, or private-data collection.
5. Document new environment variables and provider requirements.
6. Update the changelog for meaningful platform changes.

Please open an issue before large architectural changes so the design can be discussed clearly.

---

## License

NEXUS-OSINT is distributed under the repository's **Sayanox v1.1** license. See [`LICENSE`](./LICENSE) for the complete terms.

---

## Status

NEXUS-OSINT is an actively evolving research and engineering project. Some integrations depend on third-party availability, provider policies, credentials, rate limits, or deployment configuration.

Do not interpret a source appearing in the registry as a guarantee that the source is available, accurate, unrestricted, or suitable for every investigation.

---

<div align="center">

### NEXUS-OSINT

**Public intelligence, connected evidence, explainable investigations.**

</div>
