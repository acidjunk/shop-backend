# Testing

Tests live under `tests/unit_tests/` and run against a real PostgreSQL database (`shop-test`), not mocks — the test suite catches migration-incompatible and query-specific regressions that mocks would hide.

## Running the suite

```bash
# All unit tests
PYTHONPATH=. pytest tests/unit_tests

# Single file
PYTHONPATH=. pytest tests/unit_tests/api/test_products.py

# Single function
PYTHONPATH=. pytest tests/unit_tests/api/test_products.py::test_function_name

# With branch coverage
PYTHONPATH=. pytest --cov-branch --cov=server tests/unit_tests
```

`PYTHONPATH=.` is required so `server` imports resolve without installing the project.

## Test database

Pytest connects to a `shop-test` PostgreSQL database. Create it once locally:

```bash
createdb shop-test -O shop
```

The test harness applies migrations and tears down / recreates fixtures per test — there's nothing you need to run manually between suites.

## Fixtures and factories

- **`tests/unit_tests/conftest.py`** — shared fixtures: app, authenticated client, DB session, shop, user.
- **`tests/unit_tests/factories/`** — [`factory_boy`](https://factoryboy.readthedocs.io/)-style factories for building test data:
    - `shop.py`, `product.py`, `categories.py`, `attribute.py`, `tag.py`, `account.py`, `order.py`.

Prefer factories over inline row construction — they track relationships and keep test data coherent as the schema evolves.

## Test layout

```text
tests/unit_tests/
├── api/          # endpoint-level tests
├── crud/         # CRUD-layer tests
├── factories/    # factory_boy factories
├── scripts/      # test data generation helpers
├── utils/        # test helpers
├── conftest.py
└── test_db.py
```

## CI

Tests run on every push via `.github/workflows/run-unit-tests.yml` in a `python:3.11-slim` container with a `postgres:12.7-alpine` service container. Environment is injected via job env:

```yaml
POSTGRES_DB: shop-test
POSTGRES_USER: shop
POSTGRES_PASSWORD: shop
POSTGRES_HOST: postgres
```

The CI command is equivalent to:

```bash
PYTHONPATH=. DATABASE_URI=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST/$POSTGRES_DB \
  pytest --cov-branch --cov=server tests/unit_tests
```
