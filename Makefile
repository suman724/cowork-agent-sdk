.PHONY: help install lint format format-check typecheck test build check clean coverage

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install all dependencies
	pip install -e "../cowork-platform[sdk]" -e ".[dev]"

lint: ## Run linter
	.venv/bin/ruff check src/ tests/

format: ## Auto-format code
	.venv/bin/ruff format src/ tests/
	.venv/bin/ruff check --fix src/ tests/

format-check: ## Check formatting without modifying
	.venv/bin/ruff format --check src/ tests/

typecheck: ## Run type checker
	.venv/bin/mypy src/

test: ## Run unit tests
	.venv/bin/pytest -m "unit or not integration" -x -q

build: ## Build package
	.venv/bin/python -m build

check: lint format-check typecheck test ## CI gate: lint + format-check + typecheck + test

clean: ## Remove build artifacts and caches
	rm -rf build/ dist/ *.egg-info .mypy_cache .pytest_cache .ruff_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

coverage: ## Run tests with coverage
	.venv/bin/coverage run -m pytest -m "unit or not integration" -x -q
	.venv/bin/coverage report
	.venv/bin/coverage html
