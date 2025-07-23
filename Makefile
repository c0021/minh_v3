# MinhOS v3 Makefile
# ==================

.PHONY: help install dev test clean lint format type-check run bridge-test logs status

# Default target
help:
	@echo "MinhOS v3 Development Commands"
	@echo "============================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  install      Install Python dependencies"
	@echo "  dev          Setup development environment"
	@echo ""
	@echo "Development:"
	@echo "  run          Start MinhOS v3 system"
	@echo "  test         Run test suite"
	@echo "  lint         Run code linting"
	@echo "  format       Format code with Black/isort"
	@echo "  type-check   Run type checking with mypy"
	@echo ""
	@echo "Monitoring:"
	@echo "  logs         View system logs"
	@echo "  status       Check system status"
	@echo "  bridge-test  Test connection to Windows bridge"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean        Clean temporary files"
	@echo ""
	@echo "Configuration:"
	@echo "  Environment variables:"
	@echo "    SIERRA_HOST=trading-pc    # Tailscale hostname"
	@echo "    SIERRA_PORT=8765          # Bridge port"
	@echo "    MINHOS_ENV=dev            # Environment (dev/prod/test)"

# Installation
install:
	@echo "Installing MinhOS v3 dependencies..."
	pip install -r requirements.txt
	@echo "Installation complete!"

dev: install
	@echo "Setting up development environment..."
	docker-compose up -d redis postgres
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "Development environment ready!"

# Testing
test:
	@echo "Running MinhOS v3 tests..."
	pytest tests/ -v --cov=minhos --cov-report=html --cov-report=term
	@echo "Tests complete! Coverage report: htmlcov/index.html"

test-fast:
	@echo "Running fast tests (no slow tests)..."
	pytest tests/ -v -m "not slow"

# Code Quality
lint:
	@echo "Running code linting..."
	ruff check minhos/ tests/
	@echo "Linting complete!"

format:
	@echo "Formatting code..."
	black minhos/ tests/ scripts/
	isort minhos/ tests/ scripts/
	@echo "Code formatting complete!"

type-check:
	@echo "Running type checking..."
	mypy minhos/
	@echo "Type checking complete!"

check: lint type-check test-fast
	@echo "All checks passed!"

# Running
run:
	@echo "Starting MinhOS v3..."
	python -m minhos.main

run-dev:
	@echo "Starting MinhOS v3 in development mode..."
	MINHOS_ENV=dev python -m minhos.main

run-dashboard:
	@echo "Starting dashboard only..."
	python -m minhos.dashboard.main

# Monitoring
logs:
	@echo "Showing recent logs..."
	tail -f logs/minhos.log

logs-error:
	@echo "Showing error logs..."
	grep -E "(ERROR|CRITICAL)" logs/minhos.log | tail -20

status:
	@echo "Checking system status..."
	curl -s http://localhost:8000/health | python -m json.tool || echo "System not responding"

bridge-test:
	@echo "Testing connection to Windows bridge..."
	@if [ -z "$$SIERRA_HOST" ]; then \
		export SIERRA_HOST=trading-pc; \
	fi; \
	echo "Testing connection to $$SIERRA_HOST:$${SIERRA_PORT:-8765}..."; \
	curl -s "http://$$SIERRA_HOST:$${SIERRA_PORT:-8765}/health" | python -m json.tool || \
	echo "❌ Bridge connection failed. Check:"
	@echo "  1. Windows bridge is running"
	@echo "  2. Tailscale is connected"  
	@echo "  3. Hostname is correct ($$SIERRA_HOST)"

bridge-market:
	@echo "Testing market data from bridge..."
	@if [ -z "$$SIERRA_HOST" ]; then \
		export SIERRA_HOST=trading-pc; \
	fi; \
	curl -s "http://$$SIERRA_HOST:$${SIERRA_PORT:-8765}/api/market_data" | python -m json.tool

# Database
db-migrate:
	@echo "Running database migrations..."
	alembic upgrade head

db-reset:
	@echo "Resetting database..."
	rm -f data/minhos.db*
	alembic upgrade head

# Containers
docker-up:
	@echo "Starting supporting services..."
	docker-compose up -d

docker-down:
	@echo "Stopping supporting services..."
	docker-compose down

docker-logs:
	@echo "Showing container logs..."
	docker-compose logs -f

# Maintenance
clean:
	@echo "Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .mypy_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	@echo "Cleanup complete!"

# Production
build:
	@echo "Building production package..."
	python -m build

install-prod:
	@echo "Installing for production..."
	pip install -r requirements.txt --no-dev
	
deploy-systemd:
	@echo "Installing systemd service..."
	sudo cp scripts/minhos.service /etc/systemd/system/
	sudo systemctl daemon-reload
	sudo systemctl enable minhos
	@echo "Service installed! Use: sudo systemctl start minhos"

# Analysis
profile:
	@echo "Running performance profiling..."
	python -m cProfile -o profile.stats -m minhos.main &
	sleep 30
	pkill -f "minhos.main"
	python -c "import pstats; pstats.Stats('profile.stats').sort_stats('tottime').print_stats(20)"

memory:
	@echo "Memory usage analysis..."
	python -m memory_profiler scripts/memory_test.py

# Development Utilities
notebook:
	@echo "Starting Jupyter notebook server..."
	jupyter notebook notebooks/

shell:
	@echo "Starting Python shell with MinhOS imports..."
	python -c "from minhos import *; import IPython; IPython.embed()"

# Version info
version:
	@python -c "from minhos import __version__; print(f'MinhOS v{__version__}')"
	@echo "Python: $$(python --version)"
	@echo "Platform: $$(uname -a)"

info: version
	@echo ""
	@echo "Configuration:"
	@echo "  SIERRA_HOST: $${SIERRA_HOST:-trading-pc}"
	@echo "  SIERRA_PORT: $${SIERRA_PORT:-8765}" 
	@echo "  MINHOS_ENV: $${MINHOS_ENV:-dev}"
	@echo "  PWD: $$(pwd)"