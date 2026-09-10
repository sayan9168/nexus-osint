# NEXUS-OSINT Security Boundaries

NEXUS-OSINT is designed for authorized security research and public-source intelligence.

## Intentionally excluded capabilities

The project does **not** implement credential theft, password/token/session capture,
private-account access, exploitation of vulnerabilities, stealth/evasion controls,
or indiscriminate mass profiling.

These exclusions are deliberate. The platform can still support serious authorized
work through scoped collection, evidence provenance, audit logging, RBAC policy
primitives, background jobs, graph analysis, and deterministic reporting.

## Safe extension rules

Plugins should collect only public or explicitly authorized data, respect provider
terms and rate limits, avoid authentication bypass, and return attributable evidence.
Deployments should put real authentication and authorization in front of the API;
the included RBAC module is a policy primitive, not an identity provider.

Background jobs are currently process-local. Production deployments should replace
that queue with a durable worker system before relying on it for long-running work.
