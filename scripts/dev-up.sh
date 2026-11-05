#!/usr/bin/env bash
# NEXUS-OSINT — start the whole local stack (FastAPI + Next.js) with one command.
# No Docker required. Memgraph/Redis are optional: without Memgraph the app still
# starts and only the Cypher graph endpoints are unavailable.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${PYTHON:-python3}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
WEB_PORT="${WEB_PORT:-3000}"
VENV="$ROOT/backend/.venv"

# ── Backend dependencies ────────────────────────────────────────────────────
if [ ! -x "$VENV/bin/python" ]; then
  echo "› creating backend virtualenv (backend/.venv)"
  "$PYTHON" -m venv "$VENV"
fi
echo "› syncing backend dependencies"
"$VENV/bin/pip" install -q -r "$ROOT/backend/requirements.txt"

# ── Frontend dependencies ───────────────────────────────────────────────────
if [ ! -d "$ROOT/frontend/node_modules" ]; then
  echo "› installing frontend dependencies"
  (cd "$ROOT/frontend" && npm install --no-audit --no-fund)
fi

# ── Frontend environment (relative API base, proxied by next.config.js) ─────
if [ ! -f "$ROOT/frontend/.env.local" ]; then
  printf 'NEXT_PUBLIC_API_URL=/api/v1\n' >"$ROOT/frontend/.env.local"
fi

# ── Backend environment ─────────────────────────────────────────────────────
export NEXUS_JWT_SECRET="${NEXUS_JWT_SECRET:-dev-local-secret-change-me}"
export NEXUS_BOOTSTRAP_ADMIN="${NEXUS_BOOTSTRAP_ADMIN:-admin}"
export NEXUS_BOOTSTRAP_PASSWORD="${NEXUS_BOOTSTRAP_PASSWORD:-nexus-admin-2026}"
export NEXUS_CORS_ORIGINS="${NEXUS_CORS_ORIGINS:-http://localhost:$WEB_PORT,http://127.0.0.1:$WEB_PORT}"

echo "› starting API on port $BACKEND_PORT"
(cd "$ROOT/backend" && exec "$VENV/bin/uvicorn" main:app \
  --host 0.0.0.0 --port "$BACKEND_PORT" --reload) &
BACKEND_PID=$!
trap 'kill "$BACKEND_PID" 2>/dev/null || true' EXIT INT TERM

for _ in $(seq 1 120); do
  if curl -fs "http://127.0.0.1:$BACKEND_PORT/health" >/dev/null 2>&1; then break; fi
  sleep 0.5
done

echo
echo "  API   → http://localhost:$BACKEND_PORT        (OpenAPI docs: /docs)"
echo "  Web   → http://localhost:$WEB_PORT"
echo "  Login → ${NEXUS_BOOTSTRAP_ADMIN} / ${NEXUS_BOOTSTRAP_PASSWORD}"
echo

# ── Frontend (foreground; Ctrl-C stops both) ────────────────────────────────
cd "$ROOT/frontend"
NEXUS_BACKEND_URL="http://127.0.0.1:$BACKEND_PORT" \
  npm run dev -- --hostname 0.0.0.0 --port "$WEB_PORT"
