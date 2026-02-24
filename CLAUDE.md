# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ShopVirge Backend — a FastAPI REST API for managing shop data (products, categories, orders, attributes) with PostgreSQL. Python 3.10+, targets 3.11 in CI/Docker.

## Common Commands

All commands require `PYTHONPATH=.` prefix.

```bash
# Install dependencies
pip install -r requirements/all.txt

# Run dev server (hot reload)
PYTHONPATH=. uvicorn server.main:app --reload --port 8080

# Run all tests
PYTHONPATH=. pytest tests/unit_tests

# Run a single test file
PYTHONPATH=. pytest tests/unit_tests/api/test_shops.py

# Run a single test
PYTHONPATH=. pytest tests/unit_tests/api/test_shops.py::test_get_shops -v

# Run tests with coverage
PYTHONPATH=. pytest --cov-branch --cov=server tests/unit_tests

# Lint (check only, as CI runs it)
isort -c .
black --check .

# Format
isort .
black .

# Apply all DB migrations
PYTHONPATH=. alembic upgrade heads

# Create schema migration (DDL)
PYTHONPATH=. alembic revision --autogenerate -m "Description"

# Create data migration (DML)
PYTHONPATH=. alembic revision --message "Description"
```

Line length: **120** (configured in `pyproject.toml` for both black and isort).

## Architecture

**Three-layer pattern:** API endpoints → CRUD classes → SQLAlchemy models

### Key directories
- `server/api/endpoints/` — top-level endpoints (login, users, health, images, etc.)
- `server/api/endpoints/shop_endpoints/` — shop-scoped endpoints (`/shops/{shop_id}/...`)
- `server/crud/` — CRUD layer; each model has a `crud_<model>.py` with a `CRUDBase` subclass
- `server/db/models.py` — all SQLAlchemy ORM models (single file)
- `server/schemas/` — Pydantic request/response models
- `server/api/api.py` — central router that registers all sub-routers
- `server/api/deps.py` — FastAPI dependency injection (auth, pagination via `common_parameters`)
- `server/settings.py` — all config via `pydantic-settings` (`AppSettings`, `AuthSetting`, `MailSettings`)
- `migrations/versions/schema/` — DDL migrations; `migrations/versions/general/` — data migrations

### Important patterns

**Shop isolation:** Most resources carry a `shop_id` FK. Endpoints are scoped as `/shops/{shop_id}/...` and queries always filter by shop.

**Translation tables:** Content models (Product, Category, Tag, Attribute) use separate `*TranslationTable` with `main_name`, `alt1_name`, `alt2_name` for multi-language support. CRUD operations handle creating/updating/deleting translations alongside the main model.

**CRUDBase generic:** `server/crud/base.py` provides `CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType]` with standard methods (`get`, `get_multi`, `get_multi_by_shop_id`, `create`, `create_by_shop_id`, `update`, `delete`, `delete_by_shop_id`). Per-model CRUD classes extend this.

**Database session:** `DBSessionMiddleware` creates a scoped session per request. The `db` proxy object in `server/db/__init__.py` wraps the actual `Database`, allowing late initialization and test overrides.

**Transactional context manager:** Use `transactional(db, logger)` from `server.db.database` for atomic operations:
```python
from server.db import transactional
from structlog import get_logger
logger = get_logger(__name__)
with transactional(db, logger):
    # atomic operations here
```

**Pagination/filtering/sorting:** List endpoints use the `common_parameters` dependency. Filter format: `key:value`. Sort format: `col:ASC` or `col:DESC`. Responses include `Content-Range` header.

**Error handling:** `ProblemDetailException` and `raise_status()` in `server/api/error_handling.py` for RFC 7807-style error responses.

**Dual auth:**
- **AWS Cognito JWT** (primary, most endpoints): via `auth_required` dependency in `server/security.py`
- **Local JWT** (legacy login endpoint): OAuth2 password flow via `/login/access-token`, decoded in `server/api/deps.py`
- Roles: `admin` (superuser) and `employee` checked via `is_superuser`/`is_employee` properties on `UserTable`

## Naming Conventions

- SQLAlchemy models: `PascalCase` with `Table` suffix (e.g., `ProductTable`, `CategoryTable`) — some legacy models omit it (`Account`, `License`)
- CRUD classes: `CRUD<ModelName>`, instances: `<model_name>_crud`
- Pydantic schemas: `PascalCase` without `Table` suffix
- API JSON fields: `snake_case`

## Testing

- Tests in `tests/unit_tests/` using pytest with FastAPI `TestClient`
- Fixtures and factories in `tests/unit_tests/conftest.py` and `tests/unit_tests/factories/`
- Each test session creates a clean database by running all migrations
- Cognito auth is overridden in tests with a fake `CognitoToken`
- Requires a `shop-test` PostgreSQL database (default: `postgresql://shop:shop@localhost/shop-test`)

## Database Setup

PostgreSQL required with UUID extension:
```bash
createuser -sP shop          # password: shop
createdb shop -O shop
createdb shop-test -O shop   # for tests
```

## Configuration

All config via environment variables (see `server/settings.py`). FastAPI auto-loads `.env` file. Key vars: `DATABASE_URI`, `SESSION_SECRET`, `TESTING`, `AWS_COGNITO_*`, `S3_BUCKET_*`.
