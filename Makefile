.DEFAULT_GOAL := help

.PHONY: help preflight build run run-today logs clean test smoke-test \
	db-up db-down db-init db-load run-and-load run-and-load-today

help: ## Show available targets
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

preflight: ## Validate required tooling and Docker daemon
	@bash scripts/preflight.sh

build: preflight ## Build docker image via compose
	@docker compose build app

run: preflight ## Run export for DATE=YYYY-MM-DD
	@if [ -z "$(DATE)" ]; then \
		echo "ERROR: DATE is required. Usage: make run DATE=YYYY-MM-DD"; \
		exit 1; \
	fi
	@docker compose run --rm --build app --date "$(DATE)" --output-dir /app

run-today: preflight ## Run export for today's date in Europe/Madrid
	@$(MAKE) run DATE=$$(TZ=Europe/Madrid date +%F)

# ---- Phase 2: Postgres + loader ----

db-up: preflight ## Start Postgres service (detached)
	@docker compose up -d postgres

db-down: ## Stop Postgres service
	@docker compose stop postgres

db-init: ## Initialize schema (requires Postgres running)
	@docker compose run --rm --build --entrypoint /app/.venv/bin/python app scripts/db_init.py

db-load: ## Load CSV for DATE=YYYY-MM-DD into Postgres
	@if [ -z "$(DATE)" ]; then \
		echo "ERROR: DATE is required. Usage: make db-load DATE=YYYY-MM-DD"; \
		exit 1; \
	fi
	@docker compose run --rm --build --entrypoint /app/.venv/bin/python app scripts/load_csv_to_postgres.py --date "$(DATE)"

run-and-load: preflight ## Run export then load CSV for DATE=YYYY-MM-DD
	@if [ -z "$(DATE)" ]; then \
		echo "ERROR: DATE is required. Usage: make run-and-load DATE=YYYY-MM-DD"; \
		exit 1; \
	fi
	@$(MAKE) run DATE="$(DATE)"
	@$(MAKE) db-load DATE="$(DATE)"

run-and-load-today: preflight ## Run export+load for today's date (Europe/Madrid)
	@$(MAKE) run-and-load DATE=$$(TZ=Europe/Madrid date +%F)

logs: ## Follow compose logs
	@docker compose logs -f app

clean: ## Remove compose resources created by this project
	@docker compose down --remove-orphans

test: ## Run test suite on host
	@uv run pytest -q

smoke-test: ## Quick e2e smoke: db-up + db-init + db-load + SQL checks (DATE optional)
	@bash scripts/smoke_test.sh "$(DATE)"
