# NEXUS Spatial Intelligence 3.1

NEXUS now covers the remaining safe concepts from God's Eye View as an independent implementation.

## Added

- CelesTrak active satellite catalog
- Launch Library 2 upcoming launch layer
- Radio Browser geolocated radio layer
- Layer slots for vessels, traffic, public cameras and fires with explicit optional-provider status
- Cockpit/orbit UI modes
- Tactical HUD
- Detection overlay
- Scene director camera tour
- Canvas whiteboard annotations
- Snow sensor look in addition to CRT/NVG/FLIR/Noir-style presets
- Expanded share state

## Provider boundary

Optional provider secrets stay server-side. AISStream vessels, NASA FIRMS fires, configured traffic GeoJSON and configured public-camera GeoJSON are capability-gated and disabled unless the deployment explicitly configures them.

The implementation does not copy God's Eye View source code, proprietary assets or branding. It only implements compatible public-source concepts for NEXUS.

NEXUS does not implement named-person search, face recognition, private-account access, credential capture, stealth/evasion or individual tracking.
