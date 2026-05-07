.PHONY: help install db-up db-down migrate dev tailwind test lint format

help:
	@echo "Available targets:"
	@echo "  install   Install dependencies (run inside an activated venv)"
	@echo "  db-up     Start Postgres in Docker"
	@echo "  db-down   Stop Postgres"
	@echo "  migrate   Run Django migrations"
	@echo "  dev       Run Django dev server on :8000"
	@echo "  tailwind  Run Tailwind CLI in watch mode"
	@echo "  test      Run pytest"
	@echo "  lint      Run ruff + black checks (no changes)"
	@echo "  format    Auto-fix lint + format issues"

install:
	python -m pip install -e ".[dev]"

db-up:
	docker compose up -d db

db-down:
	docker compose down

migrate:
	python manage.py migrate

dev:
	python manage.py runserver

tailwind:
	python manage.py tailwind watch

test:
	python -m pytest

lint:
	python -m ruff check .
	python -m black --check .

format:
	python -m ruff check . --fix
	python -m black .
