# Changelog

## 3.1.1 — Spatial Feature Completion

- Added CelesTrak active satellite catalog layer.
- Added Launch Library 2 upcoming launch layer.
- Added Radio Browser geolocated radio layer.
- Added capability-gated slots for vessels, traffic, public cameras and fires.
- Added cockpit/orbit mode, tactical HUD, detection overlay and scene director controls.
- Added browser canvas whiteboard annotations and a Snow sensor preset.
- Kept optional provider credentials server-side and never exposed them to the browser.
- Added expanded spatial compilation/shape tests and documentation.

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
