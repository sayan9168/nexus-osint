# Changelog

## 3.0.0 — Intelligence Platform Jump

- Added global authenticated intelligence search across cases, entities and evidence.
- Added saved-search persistence for repeatable investigations.
- Added cross-case entity correlation queries using stable fingerprints.
- Added graph analysis with bounded shortest-path discovery and connected clusters.
- Added evidence vault snapshots with version numbers and SHA-256 integrity hashes.
- Added pipeline-run planning for the standard target → DNS/RDAP → HTTP/TLS → entity → graph → score → timeline → report workflow.
- Added case analytics for evidence coverage and confidence metrics.
- Added deterministic investigation replay over audit and evidence history.
- Added organization and membership foundations for future team collaboration.
- Enforced server-side case authorization in the durable job engine; client-supplied authorization flags are no longer sufficient.
- Added V3 schema and compilation coverage.

## 2.0.0 — Investigation Platform

- Added local user registration/login and signed JWT sessions.
- Added endpoint-level role enforcement for viewer/analyst/admin permissions.
- Added persistent jobs with retry, cancellation, concurrency bounds and optional Redis/Celery execution.
- Added richer public DNS records: A, AAAA, MX, NS, TXT, CNAME and CAA.
- Added structured RDAP metadata extraction.
- Added stable case-scoped entity fingerprints and relationship merging.
- Added tamper-evident audit verification.
- Added functional responsive investigation workspace UI.
- Added versioned investigation import/export bundles.
- Added CI compile/test/frontend/Docker/dependency-audit stages.
- Added production security and deployment documentation.

All collection remains restricted to public/authorized defensive research boundaries.
