# Migrations

ShopVirge uses [Alembic](https://alembic.sqlalchemy.org/) with **two independent migration branches**:

- **`schema`** — DDL changes (new tables, columns, indexes, FKs). Files live in `migrations/versions/schema/`.
- **`general`** / **data** — data migrations (seed data, backfills, enum fixes). Files live in `migrations/versions/general/`.

Keeping schema and data on separate branches means a data migration that runs on a slow table can't block the next schema release from landing, and the two can be reasoned about in isolation.

Both branches are applied on server startup via the `lifespan` hook in `server/main.py` (`alembic upgrade heads`).

## Configuration

`alembic.ini` sets both `version_locations`:

```ini
version_locations =
    %(here)s/migrations/versions/schema
    %(here)s/migrations/versions/general
```

Migration filenames follow the template `YYYY-MM-DD_<rev>_<slug>.py`.

## Applying migrations locally

```bash
PYTHONPATH=. alembic upgrade heads
```

`heads` (plural) advances both branches. Using `head` without the `s` will only move one and is almost never what you want.

## Creating migrations

See [Writing migrations](../development/migrations.md) for concrete commands.
