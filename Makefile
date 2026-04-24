COMPOSE=docker compose

.PHONY: up down seed public-ingest test lint logs

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

seed:
	$(COMPOSE) exec backend python -m app.scripts.seed_demo_data

public-ingest:
	$(COMPOSE) exec backend python -m app.scripts.ingest_public_sources

test:
	$(COMPOSE) run --rm backend pytest app/tests -q

lint:
	$(COMPOSE) run --rm backend ruff check app

logs:
	$(COMPOSE) logs -f backend frontend
