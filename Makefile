COMPOSE=docker compose

.PHONY: up down seed public-ingest test lint logs

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down


test:
	$(COMPOSE) run --rm backend pytest app/tests -q

lint:
	$(COMPOSE) run --rm backend ruff check app

logs:
	$(COMPOSE) logs -f backend frontend
