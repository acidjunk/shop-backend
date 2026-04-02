# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ShopVirge Backend — a FastAPI REST API for managing shop pricelists, products, categories, orders, and attributes. Multi-tenant architecture with shop-scoped endpoints (`/shops/{shop_id}/...`).

## Commands

```bash
# Run dev server (hot reload, port 8080)
PYTHONPATH=. uvicorn server.main:app --reload --port 8080

# Run all tests
PYTHONPATH=. pytest tests/unit_tests

# Run single test file
PYTHONPATH=. pytest tests/unit_tests/api/test_products.py

# Run single test function
PYTHONPATH=. pytest tests/unit_tests/api/test_products.py::test_function_name

# Tests with coverage
PYTHONPATH=. pytest --cov-branch --cov=server tests/unit_tests

# Format code
isort . && black .

# Check formatting (CI runs these)
isort -c . && black --check .

# Type checking
mypy .

# Apply migrations
PYTHONPATH=. alembic upgrade heads

# Create schema migration
PYTHONPATH=. alembic revision --autogenerate -m "Description" --head=schema@head --version-path=migrations/versions/schema

# Create data migration
PYTHONPATH=. alembic revision --message "Description"
```

## Architecture

**Request flow:** Request → SessionMiddleware → DBSessionMiddleware → CORS → API Router → Endpoint → CRUD → Database

**Key layers:**
- `server/api/endpoints/` and `server/api/endpoints/shop_endpoints/` — route handlers. Shop-scoped endpoints live in `shop_endpoints/`.
- `server/crud/` — CRUD classes inheriting `CRUDBase` from `server/crud/base.py`. Named `CRUD<Model>` with instances `<model>_crud`.
- `server/db/models.py` — SQLAlchemy models. Suffixed with `Table` (e.g., `ProductTable`). All inherit `BaseModel` from `server.db.database`.
- `server/schemas/` — Pydantic models for request/response validation.
- `server/api/api.py` — aggregates all routers into `api_router`.
- `server/settings.py` — Pydantic `BaseSettings` configuration, loads from env vars / `.env`.

**Database sessions:** Managed via `DBSessionMiddleware`, accessible as `db`. Use `@transactional` decorator or `transactional(db, logger)` context manager for atomic operations.

**Translations:** Multi-language support via translation tables (e.g., `ProductTranslationTable`).

**Migrations:** Alembic with two independent branches — `schema` (in `migrations/versions/schema/`) and `general/data` (in `migrations/versions/general/`). Migrations auto-apply on server startup.

## Code Style

- **Formatter:** black (line length 120), **imports:** isort (profile="black", line length 120)
- Python 3.11, type hints required on function signatures
- `PYTHONPATH=.` required for all CLI commands

## Testing

- Tests in `tests/unit_tests/` — shared fixtures in `conftest.py`, test data factories in `tests/unit_tests/factories/`
- Test database: `shop-test` (PostgreSQL)
- CI runs tests with a PostgreSQL service container (see `.github/workflows/run-unit-tests.yml`)
