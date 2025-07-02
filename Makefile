.PHONY: help build install test lint format type-check clean setup dev-install run-tests coverage pre-commit run check-build

VENV_DIR = venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip
VENV_ACTIVATE = source $(VENV_DIR)/bin/activate

help: ## Show this help message
	@echo 'AI Browser Agent - Quick Commands:'
	@echo ''
	@echo '  make build                       - Build project (setup venv + install dependencies)'
	@echo '  make run                         - Run the agent (builds if needed)'
	@echo '  make run-with-profile TASK="..." - Run with your Chrome profile (logged-in accounts)'
	@echo '  make run-with-specific-profile   - Run with specific profile (TASK="..." PROFILE="Name")'
	@echo '  make run-interactive-profile     - Interactive mode with your Chrome profile'
	@echo '  make list-profiles               - List available Chrome profiles'
	@echo '  make clean                       - Clean up all generated files and venv'
	@echo ''
	@echo 'Profile Mode: Access your logged-in accounts (Gmail, Facebook, etc.)'
	@echo '  • Use --use-profile to be prompted for profile selection'
	@echo '  • Use --profile-name "Profile Name" to specify directly'
	@echo '  • Use --list-profiles to see available profiles'
	@echo ''
	@echo 'All available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-25s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

check-build: ## Check if project is built
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "❌ Project not built. Run 'make build' first."; \
		exit 1; \
	fi
	@if [ ! -f "$(VENV_DIR)/pyvenv.cfg" ]; then \
		echo "❌ Virtual environment corrupted. Run 'make clean && make build'."; \
		exit 1; \
	fi
	@echo "✅ Project is built and ready"

build: ## Build project (setup venv + install dependencies)
	@echo "🔨 Building AI Browser Agent..."
	@if [ -d "$(VENV_DIR)" ]; then \
		echo "📁 Virtual environment exists, removing..."; \
		rm -rf $(VENV_DIR); \
	fi
	@echo "🐍 Creating virtual environment..."
	python3 -m venv $(VENV_DIR)
	@echo "📦 Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "✅ Build complete! Run 'make run' to start the agent."

install: ## Install dependencies (requires existing venv)
	@$(MAKE) check-build
	$(PIP) install -r requirements.txt

dev-install: check-build ## Install development dependencies
	$(VENV_ACTIVATE) && $(PIP) install -r requirements.txt
	$(VENV_ACTIVATE) && $(PIP) install -e .
	$(VENV_ACTIVATE) && pre-commit install

test: check-build ## Run all tests
	$(VENV_ACTIVATE) && pytest tests/ -v

test-unit: check-build ## Run unit tests only
	$(VENV_ACTIVATE) && pytest tests/unit/ -v

test-integration: check-build ## Run integration tests only
	$(VENV_ACTIVATE) && pytest tests/integration/ -v -m integration

coverage: check-build ## Run tests with coverage
	$(VENV_ACTIVATE) && pytest tests/ --cov=src --cov-report=term-missing --cov-report=html

lint: check-build ## Run linting
	$(VENV_ACTIVATE) && flake8 src/ tests/

format: check-build ## Format code
	$(VENV_ACTIVATE) && black src/ tests/

format-check: check-build ## Check code formatting
	$(VENV_ACTIVATE) && black --check src/ tests/

type-check: check-build ## Run type checking
	$(VENV_ACTIVATE) && mypy src/

quality: format lint type-check ## Run all quality checks

clean: ## Clean up all generated files and virtual environment
	@echo "🧹 Cleaning up AI Browser Agent..."
	rm -rf $(VENV_DIR)
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf logs/
	rm -rf screenshots/
	rm -rf chrome_data/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	@echo "✅ Cleanup complete!"

pre-commit: check-build ## Run pre-commit hooks
	$(VENV_ACTIVATE) && pre-commit run --all-files

run: check-build ## Run the agent in interactive mode (builds if needed)
	@echo "🚀 Starting AI Browser Agent..."
	$(VENV_ACTIVATE) && python -m src.main interactive

run-execute: check-build ## Run a single task (usage: make run-execute TASK="your task here")
	@if [ -z "$(TASK)" ]; then \
		echo "❌ Please specify a task: make run-execute TASK=\"your task here\""; \
		exit 1; \
	fi
	@echo "🚀 Executing task: $(TASK)"
	$(VENV_ACTIVATE) && python -m src.main execute --task "$(TASK)"

run-with-profile: check-build ## Run with your existing Chrome profile (usage: make run-with-profile TASK="your task here")
	@if [ -z "$(TASK)" ]; then \
		echo "❌ Please specify a task: make run-with-profile TASK=\"your task here\""; \
		exit 1; \
	fi
	@echo "🚀 Executing task with your Chrome profile: $(TASK)"
	$(VENV_ACTIVATE) && python -m src.main execute --task "$(TASK)" --use-profile

run-with-specific-profile: check-build ## Run with a specific Chrome profile (usage: make run-with-specific-profile TASK="your task" PROFILE="Profile Name")
	@if [ -z "$(TASK)" ]; then \
		echo "❌ Please specify a task: make run-with-specific-profile TASK=\"your task\" PROFILE=\"Profile Name\""; \
		exit 1; \
	fi
	@if [ -z "$(PROFILE)" ]; then \
		echo "❌ Please specify a profile: make run-with-specific-profile TASK=\"your task\" PROFILE=\"Profile Name\""; \
		exit 1; \
	fi
	@echo "🚀 Executing task with Chrome profile '$(PROFILE)': $(TASK)"
	$(VENV_ACTIVATE) && python -m src.main execute --task "$(TASK)" --use-profile --profile-name "$(PROFILE)"

run-interactive-profile: check-build ## Run interactive mode with your existing Chrome profile
	@echo "🚀 Starting AI Browser Agent with your Chrome profile..."
	$(VENV_ACTIVATE) && python -m src.main interactive --use-profile

list-profiles: check-build ## List available Chrome profiles
	@echo "📁 Listing available Chrome profiles..."
	$(VENV_ACTIVATE) && python -m src.main list-profiles

start-chrome-debug: ## Start Chrome with remote debugging enabled (use before profile commands)
	@echo "🌐 Starting Chrome with remote debugging..."
	@echo "Leave this running and use profile commands in another terminal"
	./start_chrome_debug.sh

run-help: check-build ## Show agent help
	$(VENV_ACTIVATE) && python -m src.main --help

config: check-build ## Show current configuration
	$(VENV_ACTIVATE) && python -m src.main config

package: check-build ## Build the package for distribution
	$(VENV_ACTIVATE) && python -m build

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