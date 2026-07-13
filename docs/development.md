# Development and verification

## Backend without Make

```bash
python -m venv backend/.venv
backend/.venv/bin/python -m pip install -e "backend[dev]"
backend/.venv/bin/ruff check backend
backend/.venv/bin/ruff format --check backend
backend/.venv/bin/mypy backend/src backend/tests
backend/.venv/bin/pytest backend/tests -m "not integration"
```

On Windows, replace `backend/.venv/bin` with `backend\.venv\Scripts`.

## Frontend without Make

```bash
pnpm --dir frontend install
pnpm --dir frontend lint
pnpm --dir frontend format:check
pnpm --dir frontend typecheck
pnpm --dir frontend test -- --run
pnpm --dir frontend build
```

## Clean database and integration verification

The following deletes only the disposable Compose development volume named by this project:

```bash
docker compose down -v
docker compose up -d db
docker compose run --rm backend alembic upgrade head
docker compose run --rm backend python -m classpath.scripts.seed_demo_curriculum
docker compose up -d backend
python scripts/smoke_test.py
docker compose run --rm backend pytest -m integration
```

Run `docker compose down` afterward to stop services without deleting data, or `docker compose down -v` to delete the disposable local database.

