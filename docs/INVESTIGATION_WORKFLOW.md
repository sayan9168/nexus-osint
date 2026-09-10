# NEXUS-OSINT Investigation Workflow

NEXUS-OSINT is designed as a controlled investigation workspace for public-source research and authorized defensive work.

## Workflow

1. Create a case.
2. Record the target and authorization scope.
3. Run bounded OSINT collection through `/api/v1/osint/scan`.
4. Preserve evidence source, timestamp, observed data and confidence.
5. Correlate observations in the graph layer.
6. Add analyst notes and review findings.
7. Export a deterministic Markdown or HTML report.

## Current API

- `POST /api/v1/cases/` — create a case
- `GET /api/v1/cases/` — list cases
- `GET /api/v1/cases/{case_id}` — retrieve a case
- `POST /api/v1/cases/{case_id}/targets` — attach a target
- `POST /api/v1/cases/{case_id}/notes` — add an analyst note
- `POST /api/v1/cases/{case_id}/close` — close a case
- `POST /api/v1/osint/scan` — bounded authorized collection
- `GET /api/v1/reports/{case_id}.md` — Markdown report
- `GET /api/v1/reports/{case_id}.html` — HTML report

## Safety model

The collection layer is intentionally bounded. It does not provide credential attacks, account takeover, private-account access, exploitation, stealth scraping, or bulk profiling. Operators remain responsible for authorization, source terms, rate limits, and applicable law.

## Roadmap

Planned production layers include persistent case storage, evidence graph persistence, source/plugin contracts, provenance hashing, scheduled collection with rate limits, analyst RBAC, richer report formats, and a frontend investigation workspace.
