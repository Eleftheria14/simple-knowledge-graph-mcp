# GraphRAG MCP Toolkit Makefile
# Development and project management commands

.PHONY: help install install-dev clean test lint format check-format type-check security pre-commit docs build publish

# Default target
help:
	@echo "Available commands:"
	@echo "  install        Install package in production mode"
	@echo "  install-dev    Install package in development mode with all dependencies"
	@echo "  clean          Clean build artifacts and cache files"
	@echo "  test           Run tests with coverage"
	@echo "  lint           Run linters (ruff, black, mypy)"
	@echo "  format         Format code with black and ruff"
	@echo "  check-format   Check code formatting without making changes"
	@echo "  type-check     Run type checking with mypy"
	@echo "  security       Run security checks with bandit and safety"
	@echo "  pre-commit     Run pre-commit hooks"
	@echo "  docs           Build documentation"
	@echo "  build          Build package"
	@echo "  publish        Publish package to PyPI"
	@echo "  setup-ollama   Set up Ollama with required models"
	@echo "  setup-neo4j    Set up Neo4j with Docker"
	@echo "  clear-db       Clear all ChromaDB databases"
	@echo "  tutorial       Start tutorial system"

# Installation commands
install:
	@echo "Activating graphrag-env and installing..."
	@bash -c "source graphrag-env/bin/activate && pip install -e ."

install-dev:
	@echo "Activating graphrag-env and installing dev dependencies..."
	@bash -c "source graphrag-env/bin/activate && pip install -e '.[dev,test,docs]'"

# Setup commands
setup-ollama:
	@echo "Setting up Ollama..."
	ollama pull llama3.1:8b
	ollama pull nomic-embed-text
	@echo "Ollama setup complete"

setup-neo4j:
	@echo "Setting up Neo4j with Docker..."
	docker run -d --name neo4j -p 7474:7474 -p 7687:7687 \
		-e NEO4J_AUTH=neo4j/password neo4j:latest
	@echo "Neo4j setup complete - access at http://localhost:7474"

clear-db:
	./clear_chromadb.sh

tutorial:
	./start_tutorial.sh

# Cleaning commands
clean:
	@echo "Cleaning build artifacts and cache files..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf .venv/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✅ Cleanup complete"

# Testing commands
test:
	@echo "Activating graphrag-env and running tests..."
	@bash -c "source graphrag-env/bin/activate && python -m pytest tests/ -v --cov=graphrag_mcp --cov-report=term-missing --cov-report=html"

test-quick:
	@echo "Activating graphrag-env and running quick tests..."
	@bash -c "source graphrag-env/bin/activate && python -m pytest tests/ -v --tb=short"

# Code quality commands
lint:
	@echo "Activating graphrag-env and running linters..."
	@bash -c "source graphrag-env/bin/activate && ruff check . && black --check . && mypy graphrag_mcp"

format:
	@echo "Activating graphrag-env and formatting code..."
	@bash -c "source graphrag-env/bin/activate && ruff check . --fix && black . && isort ."

check-format:
	@echo "Activating graphrag-env and checking format..."
	@bash -c "source graphrag-env/bin/activate && black --check . && isort --check-only ."

type-check:
	@echo "Activating graphrag-env and running type check..."
	@bash -c "source graphrag-env/bin/activate && mypy graphrag_mcp"

security:
	@echo "Activating graphrag-env and running security checks..."
	@bash -c "source graphrag-env/bin/activate && bandit -r graphrag_mcp && safety check"

# Pre-commit commands
pre-commit:
	@echo "Activating graphrag-env and running pre-commit..."
	@bash -c "source graphrag-env/bin/activate && pre-commit run --all-files"

pre-commit-install:
	uv run pre-commit install

# Documentation commands
docs:
	uv run mkdocs build

docs-serve:
	uv run mkdocs serve

# Build and publish commands
build:
	uv build

publish:
	uv publish

publish-test:
	uv publish --repository testpypi

# Combined quality check
quality: lint type-check security
	@echo "All quality checks passed!"

# CI simulation
ci: clean install-dev quality test
	@echo "CI simulation complete!"

# Development workflow
dev: install-dev pre-commit-install
	@echo "Development environment ready!"