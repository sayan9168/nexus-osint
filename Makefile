.PHONY: up down build logs clean restart backend-logs agent-logs frontend-logs memgraph-console \
        ci ci-backend ci-frontend ci-agent ci-docker audit

PY ?= python3
NPM ?= npm

up:
	docker compose up -d --build

down:
	docker compose down -v

build:
	docker compose build --no-cache

logs:
	docker compose logs -f

clean:
	docker compose down -v --rmi all --remove-orphans

restart:
	docker compose restart

backend-logs:
	docker compose logs -f backend celery-worker

agent-logs:
	docker compose logs -f agent

frontend-logs:
	docker compose logs -f frontend

memgraph-console:
	docker exec -it nexus-memgraph mgconsole

# ─── Continuous integration (mirrors .github/workflows/ci.yml) ───────────────

ci: ci-backend ci-frontend ci-agent ci-docker

ci-backend:
	cd backend && $(PY) -m compileall -q . && $(PY) -m pytest -q

ci-frontend:
	cd frontend && $(NPM) ci --no-audit --no-fund \
		&& $(NPM) run lint \
		&& $(NPM) run typecheck \
		&& $(NPM) run build \
		&& $(NPM) audit --omit=dev --audit-level=high \
		&& $(NPM) audit --audit-level=high

ci-agent:
	cd agent && $(PY) -m compileall -q .

ci-docker:
	docker compose -f docker-compose.yml config --quiet

audit:
	cd backend && $(PY) -m pip_audit -r requirements.txt
	cd frontend && $(NPM) audit --audit-level=high
