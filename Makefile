.PHONY: help
help:  ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

.PHONY: format
format:  ## Format and lint code
	uv run ruff format src/ tests/
	uv run ruff check --fix src/ tests/

.PHONY: lint
lint:  ## Check code style
	uv run ruff check src/ tests/

.PHONY: test
test:  ## Run unit tests
	uv run pytest tests/ -v

.PHONY: test-cov
test-cov:  ## Run tests with coverage
	uv run pytest tests/ -v --cov=src/merkato --cov-report=html --cov-report=term

.PHONY: test-watch
test-watch:  ## Run tests in watch mode
	uv run pytest-watch tests/

.PHONY: integration-test
it:  ## Run integration tests for stock monitor
	uv run it

.PHONY: run-monitor
run-monitor:  ## Run stock monitor
	uv run stock-monitor

.PHONY: run-report
run-report:  ## Run weekly report
	uv run weekly-report