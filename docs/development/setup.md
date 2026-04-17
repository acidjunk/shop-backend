# Local setup

See the [Quickstart](../quickstart.md) for the canonical setup instructions (sourced from `README.md`). This page covers the parts specific to day-to-day development.

## Prerequisites

- Python **3.11** (the project's declared target; `README.md` still mentions 3.10+, but CI and tooling target 3.11).
- PostgreSQL running locally with a `shop` superuser and two databases: `shop` (main) and `shop-test` (for the test suite).

## Virtual environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements/all.txt   # everything including docs and test tooling
```

If you only need the API running (no docs, no tests), `requirements/base.txt` is enough.

## Environment variables

Settings come from `server/settings.py` (Pydantic `BaseSettings`). FastAPI auto-loads a `.env` file if present. Minimum set for a local server:

```bash
SESSION_SECRET=dev-secret-change-me
DATABASE_URI=postgresql://shop:shop@localhost/shop
TESTING=false
```

For the full list of knobs (Cognito, Sentry, Stripe, SMTP, S3 buckets, CORS), inspect `server/settings.py` directly — the pydantic model is the source of truth.

## Running the server

```bash
PYTHONPATH=. uvicorn server.main:app --reload --port 8080
```

The startup hook runs `alembic upgrade heads` automatically, so both migration branches are applied.

Visit:

- <http://127.0.0.1:8080/docs> — Swagger UI.
- <http://127.0.0.1:8080/redoc> — ReDoc.
- <http://127.0.0.1:8080/> — the tiny info root route.

## Creating an initial user

```bash
export FIRST_USER=you@example.com
PYTHONPATH=. python server/create_initial_user.py
```

## Docs preview

```bash
pip install -r requirements/docs.txt
mkdocs serve
```

Then open <http://127.0.0.1:8000>.
