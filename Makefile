PYTHON ?= python
PNPM ?= pnpm
COMPOSE ?= docker compose
BACKEND_PYTHON ?= backend/.venv/bin/python
BACKEND_ENV = PYTHONPATH=backend/src

.PHONY: setup dev lint format typecheck test test-integration migrate seed-demo data-validate synthetic-data \
	train-baseline train-cognitive-classifier train-difficulty-classifier evaluate-models \
	evaluate-extraction evaluate-retrieval evaluate-assessment smoke build verify

setup:
	$(PYTHON) -m venv backend/.venv
	$(BACKEND_PYTHON) -m pip install -e "./backend[dev]"
	$(PNPM) --dir frontend install

dev:
	$(COMPOSE) up --build

lint:
	cd backend && .venv/bin/ruff check . ../scripts && .venv/bin/ruff format --check . ../scripts
	$(PNPM) --dir frontend lint
	$(PNPM) --dir frontend format:check

format:
	cd backend && .venv/bin/ruff check --fix . ../scripts && .venv/bin/ruff format . ../scripts
	$(PNPM) --dir frontend format

typecheck:
	cd backend && .venv/bin/mypy src tests ../scripts
	$(PNPM) --dir frontend typecheck

test:
	cd backend && .venv/bin/pytest -m "not integration"
	$(PNPM) --dir frontend test -- --run

test-integration:
	cd backend && .venv/bin/pytest -m integration

migrate:
	cd backend && .venv/bin/alembic upgrade head

seed-demo:
	cd backend && PYTHONPATH=src .venv/bin/python -m classpath.scripts.seed_demo_curriculum

data-validate:
	$(PYTHON) scripts/validate_demo_data.py

synthetic-data:
	$(BACKEND_PYTHON) scripts/generate_synthetic_evaluation_data.py

train-baseline evaluate-models:
	$(BACKEND_PYTHON) scripts/evaluate_classifiers.py

evaluate-extraction:
	PYTHONPATH=backend/src $(BACKEND_PYTHON) scripts/evaluate_extraction.py

evaluate-retrieval:
	PYTHONPATH=backend/src $(BACKEND_PYTHON) scripts/evaluate_retrieval.py

evaluate-assessment:
	PYTHONPATH=backend/src $(BACKEND_PYTHON) scripts/evaluate_assessment.py

build:
	$(PNPM) --dir frontend build
	$(COMPOSE) build backend frontend

smoke:
	$(PYTHON) scripts/smoke_test.py
	$(BACKEND_PYTHON) scripts/demo_journey_smoke.py

verify:
	$(COMPOSE) down -v
	$(COMPOSE) up -d db
	$(COMPOSE) run --rm backend alembic upgrade head
	$(COMPOSE) run --rm backend alembic check
	$(COMPOSE) run --rm backend python -m classpath.scripts.seed_demo_curriculum
	$(COMPOSE) up -d backend
	$(PYTHON) scripts/smoke_test.py
	$(MAKE) lint typecheck test
	cd backend && DATABASE_URL=postgresql+psycopg://classpath:classpath_dev@localhost:5432/classpath .venv/bin/pytest -m integration
	$(PNPM) --dir frontend build
	$(COMPOSE) build backend frontend

train-cognitive-classifier train-difficulty-classifier:
	@echo "Blocked honestly: human-reviewed labels and a frozen test set are required before DistilBERT training."
	@exit 2
