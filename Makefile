.DEFAULT_GOAL := help

.PHONY: help preflight build run run-today logs clean test

help: ## Show available targets
	@awk 'BEGIN {FS = ":.*## "}; /^[a-zA-Z0-9_.-]+:.*## / {printf "  %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

preflight: ## Validate required tooling and Docker daemon
	@bash scripts/preflight.sh

build: preflight ## Build docker image via compose
	@docker compose build app

run: preflight ## Run export for DATE=YYYY-MM-DD
	@if [ -z "$(DATE)" ]; then \
		echo "ERROR: DATE is required. Usage: make run DATE=YYYY-MM-DD"; \
		exit 1; \
	fi
	@docker compose run --rm app --date "$(DATE)" --output-dir /app

run-today: preflight ## Run export for today's date in Europe/Madrid
	@$(MAKE) run DATE=$$(TZ=Europe/Madrid date +%F)

logs: ## Follow compose logs
	@docker compose logs -f app

clean: ## Remove compose resources created by this project
	@docker compose down --remove-orphans

test: ## Run test suite on host
	@uv run pytest -q
