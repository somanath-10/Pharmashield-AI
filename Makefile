COMPOSE=docker compose

.PHONY: up down seed-users test test-unit test-integration lint logs clean-zip

up:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

seed-users:
	$(COMPOSE) run --rm backend python scripts/seed_demo_users.py

test:
	$(COMPOSE) run --rm -e APP_ENV=test backend pytest app/tests -q -m "not integration"

test-unit:
	$(COMPOSE) run --rm -e APP_ENV=test backend pytest app/tests -q -m "not integration"

test-integration:
	$(COMPOSE) run --rm backend pytest app/tests -q -m "integration"

lint:
	$(COMPOSE) run --rm backend ruff check app

logs:
	$(COMPOSE) logs -f backend frontend

clean-zip:
	zip -r Pharmashield-AI-final.zip . \
	  -x ".git/*" "*/.git/*" ".next/*" "*/.next/*" "node_modules/*" "*/node_modules/*" "*/__pycache__/*" \
	  ".pytest_cache/*" "*/.pytest_cache/*" ".DS_Store" "*/.DS_Store" "__MACOSX/*" "*/__MACOSX/*" "*.env" \
	  "*.egg-info/*" "*/venv/*" "*.tsbuildinfo"
