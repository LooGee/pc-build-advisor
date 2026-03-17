.PHONY: dev prod down logs ps build seed migrate

dev:
	docker-compose -f infra/docker/docker-compose.yml up --build

prod:
	docker-compose -f infra/docker/docker-compose.prod.yml up -d --build

down:
	docker-compose -f infra/docker/docker-compose.yml down

logs:
	docker-compose -f infra/docker/docker-compose.yml logs -f

ps:
	docker-compose -f infra/docker/docker-compose.yml ps

build:
	docker-compose -f infra/docker/docker-compose.yml build

seed:
	docker-compose -f infra/docker/docker-compose.yml exec backend python -m app.db.seeds.run_seeds

migrate:
	docker-compose -f infra/docker/docker-compose.yml exec backend alembic upgrade head

test-backend:
	docker-compose -f infra/docker/docker-compose.yml exec backend pytest tests/ -v

test-frontend:
	docker-compose -f infra/docker/docker-compose.yml exec frontend npm test

lint-backend:
	docker-compose -f infra/docker/docker-compose.yml exec backend ruff check app/

format-backend:
	docker-compose -f infra/docker/docker-compose.yml exec backend black app/
