# Changelog

## 3.6.0 — CI/CD Hardening & Dependency Upgrade

### Pipeline
- Replaced `backend-tests.yml` with a single `ci.yml` (jobs: `backend`, `frontend`, `agent`, `docker`) exposing one `CI gate` status check for branch protection.
- Upgraded every action: `checkout` v4→v7, `setup-python` v5→v7, `setup-node` v4→v7, `setup-buildx-action` v3→v4, and Docker builds now go through `docker/build-push-action` v7 with GitHub Actions layer caching.
- Added job timeouts, least-privilege permissions, `persist-credentials: false`, and cancellation of superseded runs.
- Added ESLint (`eslint.config.mjs`, flat config), `tsc --noEmit` and blocking `npm audit` (production + full tree at `high`) to the frontend job.
- Added Docker Compose manifest validation and an agent service job to CI.
- Added `cd.yml`: tagged releases publish GHCR images with SBOM, provenance attestations and a Trivy scan, then open a GitHub release with generated notes.
- Added `codeql.yml` (Python + TypeScript, `security-extended`) and `security.yml` (dependency review, weekly audits, advisory agent audit).
- Added `.github/dependabot.yml` with grouped weekly updates for Actions, pip, npm and Docker images.
- Added `docs/CI.md` and Makefile `ci` / `audit` targets so the pipeline can be reproduced locally.

### Security
- `dnspython` 2.6.1 → 2.9.1 (CVE-2026-114605) — this was the failing `pip-audit` step on `main`.
- `fastapi` 0.111.0 → 0.141.1 and `pydantic` 2.7.4 → 2.13.5 in the agent service, clearing the `starlette` advisories.

### Frontend
- Next.js 14.2.35 → 16.4.3 with React 18.3.1 → 19.3.1 (clears the critical Next.js advisory), ESLint 9, TypeScript 5.9, PostCSS 8.5.32, `react-force-graph-3d` 1.29.2, `3d-force-graph` 1.80.1, `zustand` 5.0.16, `lucide-react` 1.65.0, Tailwind 3.4.19.
- Migrated to Turbopack, which is the default bundler in Next.js 16; the old `webpack` externals hook became a `turbopack.resolveAlias` entry.
- **Fixed Tailwind never compiling** — the repository had no `postcss.config.js`, so `@tailwind` directives were served unprocessed and utility classes such as `bg-nexus-900` did not exist. Adding the PostCSS config emits the real ~36 KB utility stylesheet.
- Fixed a React 19 `useRef` typing error in `useWebSocket`.
- `package.json` version bumped to 3.6.0.

### Containers
- Frontend image is now a multi-stage production build (`node:22-alpine`, Next.js `output: "standalone"`, non-root user, healthcheck) instead of running the dev server.
- Backend and agent images build dependencies in a builder stage, run as uid 10001, and ship healthchecks; `libpq-dev` and other unused build packages were dropped.
- Added `.dockerignore` files, pinned `docker-compose.production.yml` images (no more `:latest`), added build args, healthchecks and named volumes, and dropped the obsolete Compose `version` key.
- Development compose keeps working by targeting the frontend `deps` stage.

## 3.3.1 — Passive Intelligence Expansion

- Added passive certificate-transparency lookups through crt.sh with bounded subdomain results.
- Added RIPE Atlas public-probe layer for Internet measurement context.
- Added RIPEstat network metadata lookup for explicitly supplied IP/ASN resources.
- Added Wikidata public-knowledge lookup for explicitly supplied search terms.
- Added authenticated `/v3/spatial/passive/certificates` endpoint.
- Added authenticated `/v3/spatial/passive/network` endpoint.
- Added authenticated `/v3/spatial/passive/knowledge` endpoint.
- Kept all passive lookups bounded, read-only and server-side.
- Maintained the public/authorized boundary: no credential collection, private-account access, named-person tracking, face recognition, exploitation or stealth collection.

## 3.3.0 — Open Public Source Expansion

- Added a bounded public-source adapter registry for the Spatial Intelligence module.
- Added NASA EONET natural-event signals as live public geospatial data.
- Added GDELT GEO public-news event signals with bounded 24-hour results.
- Added OpenStreetMap/Overpass on-demand local map context around a selected signal.
- Added Nominatim reverse geocoding for selected spatial signals.
- Added Open-Meteo weather context for selected coordinates without an API key.
- Added NOAA active weather-alert context for supported US coordinates.
- Added a public-source registry panel inside the Spatial workspace.
- Added selected-signal context retrieval so investigators can inspect nearby public map features, weather and public alerts.
- Added source-registry tests and explicit provider/rate-limit disclaimers.
- Preserved the existing public/authorized-use boundary: no named-person tracking, face recognition, private-account access or safety-critical navigation.

## 3.2.0 — Spatial Workspace Integration

- Integrated Spatial Intelligence directly into the authenticated NEXUS investigation dashboard.
- Added header and sidebar launch controls for the Spatial workspace.
- Added a case-aware Spatial Intelligence banner to the main investigation workspace.
- Opening Spatial Intelligence now carries the selected case ID into `/spatial?case=...`.
- Added a guarded navigation path that asks investigators to select a case before opening case-linked spatial analysis.
- Preserved the existing authenticated public-source spatial API and 3D globe workflow.

## 3.1.0 — Spatial Intelligence Jump

- Added an authenticated public-signal spatial API.
- Added live USGS earthquake ingestion with bounded caching.
- Added live OpenSky aircraft telemetry ingestion with bounded caching.
- Added case-evidence coordinate extraction for geospatial evidence overlays.
- Added a Three.js 3D globe workspace with orbit, zoom and signal focus interactions.
- Added layer controls, signal counts, tracked-signal details and shareable view URLs.
- Added standard/NVG/FLIR/noir visualization presets.
- Added explicit public-source/authorized-use boundaries and spatial safety disclaimers.
- Added backend spatial compilation and coordinate-extraction tests.

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
