.PHONY: up down build logs clean restart

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
