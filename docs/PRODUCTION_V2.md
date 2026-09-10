# NEXUS-OSINT Production V2

## Security model
- All `/api/v1/*` endpoints except authentication require a signed Bearer session.
- RBAC roles: `viewer`, `analyst`, `admin`.
- Active collection requires explicit authorization in the request and is limited to public/authorized sources.
- URL collection performs public-address preflight and bounded HEAD/TLS collection.
- CORS is configured with `NEXUS_CORS_ORIGINS`; do not use wildcard origins with credentials.
- Set a strong random `NEXUS_JWT_SECRET` in deployment secrets.

## Workers
Set `NEXUS_USE_CELERY=true` and configure `CELERY_BROKER_URL` / `CELERY_RESULT_BACKEND` for Redis/Celery workers. The local bounded executor remains the development fallback. Jobs persist in SQLite and expose queued/running/completed/failed/cancelled states.

## Deployment checklist
1. Configure secrets and a non-local database path.
2. Set frontend `NEXT_PUBLIC_API_URL` to the API origin.
3. Set explicit CORS origins.
4. Run the CI workflow before release.
5. Run a Celery worker when distributed jobs are enabled.
6. Back up the SQLite database if SQLite is used.
7. Review provider terms and rate limits for every plugin/source.

## Scope boundary
NEXUS-OSINT is for public-source research and authorized defensive investigations. It intentionally does not implement credential theft, authentication bypass, private-account access, exploitation, stealth/evasion, or indiscriminate mass profiling.
