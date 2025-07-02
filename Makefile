.PHONY: help install test lint format type-check clean setup dev-install run-tests coverage pre-commit

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Initial project setup
	python3 -m venv venv
	@echo "Virtual environment created. Activate it with:"
	@echo "source venv/bin/activate  # On macOS/Linux"
	@echo "venv\\Scripts\\activate    # On Windows"

install: ## Install dependencies
	pip install -r requirements.txt

dev-install: ## Install development dependencies
	pip install -r requirements.txt
	pip install -e .
	pre-commit install

test: ## Run all tests
	pytest tests/ -v

test-unit: ## Run unit tests only
	pytest tests/unit/ -v

test-integration: ## Run integration tests only
	pytest tests/integration/ -v -m integration

coverage: ## Run tests with coverage
	pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

lint: ## Run linting
	flake8 src/ tests/

format: ## Format code
	black src/ tests/

format-check: ## Check code formatting
	black --check src/ tests/

type-check: ## Run type checking
	mypy src/

quality: format lint type-check ## Run all quality checks

clean: ## Clean up generated files
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

pre-commit: ## Run pre-commit hooks
	pre-commit run --all-files

run: ## Run the agent in interactive mode
	python -m src.main interactive

run-help: ## Show agent help
	python -m src.main --help

config: ## Show current configuration
	python -m src.main config

build: ## Build the package
	python -m build

install-local: ## Install package locally
	pip install -e .

docker-build: ## Build Docker image (if Dockerfile exists)
	docker build -t ai-browser-agent .

docker-run: ## Run Docker container (if image exists)
	docker run -it --rm ai-browser-agent

# Development workflow targets
dev: dev-install pre-commit ## Set up development environment

check: format-check lint type-check test ## Run all checks (CI pipeline)

release-check: clean quality test ## Pre-release checks