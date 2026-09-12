# NEXUS Spatial Intelligence

NEXUS now includes a safe public-signal globe inspired by the visual and interaction ideas popularized by projects such as God's Eye View.

## Included

- Interactive Three.js 3D globe with orbit/zoom controls.
- Live public USGS earthquake layer.
- Live public OpenSky aircraft telemetry layer.
- Case-evidence geospatial overlay when evidence contains valid latitude/longitude data.
- Click/focus tracking for public signals.
- Layer toggles and live signal counts.
- Tactical visual presets: standard, NVG, FLIR and noir.
- Shareable view URLs carrying case/style context.
- Authenticated backend proxy with short caching and bounded upstream requests.
- Explicit public-source/authorized-use boundary; no named-person search or face recognition.

## Routes

- `GET /api/v1/v3/spatial/layers`
- `GET /api/v1/v3/spatial/cases/{case_id}/points`
- UI: `/spatial?case={case_id}`

The globe is an intelligence visualization, not a navigation or safety-critical system. Public telemetry can be delayed, incomplete, modeled, or wrong.

## Why this is not a copy

NEXUS implements the product concepts independently on its existing FastAPI + Next.js + Three.js architecture. It does not copy source code, proprietary assets, screenshots, or third-party project branding.
