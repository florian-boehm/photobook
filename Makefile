# Photobook Makefile
# Common development tasks

.PHONY: help install run test lint format clean docker-up docker-down docker-build

# Default target
help:
	@echo "Photobook - Media Streaming Service"
	@echo ""
	@echo "Available targets:"
	@echo "  install    - Install Python dependencies"
	@echo "  run        - Run the application locally"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linters"
	@echo "  format     - Format code"
	@echo "  clean      - Clean build artifacts"
	@echo "  docker-up  - Start Docker containers"
	@echo "  docker-down - Stop Docker containers"
	@echo "  docker-build - Build Docker images"
	@echo ""

# Install dependencies
install:
	pip install -r backend/requirements.txt

# Run the application
run:
	python -m uvicorn backend.app.main:app --reload

# Run tests
test:
	python -m pytest backend/tests/ -v

# Run linters
lint:
	python -m flake8 backend/app/ backend/tests/

# Format code
format:
	python -m black backend/app/ backend/tests/
	python -m isort backend/app/ backend/tests/

# Clean build artifacts
clean:
	rm -rf __pycache__/ *.pyc *.pyo *.pyd
	rm -rf backend/__pycache__/ backend/*.pyc backend/*.pyo backend/*.pyd
	rm -rf backend/app/__pycache__/ backend/app/*.pyc backend/app/*.pyo backend/app/*.pyd
	rm -rf backend/tests/__pycache__/ backend/tests/*.pyc backend/tests/*.pyo backend/tests/*.pyd

# Docker commands
docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-build:
	docker-compose build

docker-logs:
	docker-compose logs -f

# Development server with Docker
docker-run:
	docker-compose up

# Production build
docker-prod:
	docker-compose --profile production up -d
