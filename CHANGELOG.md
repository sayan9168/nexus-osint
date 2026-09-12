# Changelog

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
