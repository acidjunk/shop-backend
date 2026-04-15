# Code style

The project uses a small, opinionated toolchain. All settings live in `pyproject.toml` and `mypy.ini`.

## Formatters

| Tool | Config | Purpose |
|------|--------|---------|
| [black](https://black.readthedocs.io/) | `pyproject.toml` `[tool.black]` | Code formatting. Line length **120**, target Python 3.11. |
| [isort](https://pycqa.github.io/isort/) | `pyproject.toml` `[tool.isort]` | Import ordering. Profile `black`, line length **120**. |

Run them both before committing:

```bash
isort . && black .
```

CI verifies formatting without modifying files:

```bash
isort -c .
black --check .
```

See `.github/workflows/run-linting-tests.yml`.

## Type checking

[mypy](https://mypy.readthedocs.io/) runs in strict mode (see `mypy.ini`):

```bash
mypy .
```

Key strict-mode flags enabled:

- `disallow_untyped_calls`, `disallow_untyped_defs`, `disallow_incomplete_defs`
- `strict_optional`, `strict_equality`
- `warn_no_return`, `warn_unreachable`

Tests have a narrower exemption (see the `[mypy-tests.unit_tests.app.api.endpoints.*]` section in `mypy.ini`) because of a known mypy interaction with pytest fixtures. Migration files are excluded too.

## Python target

Python **3.11**. Type hints are required on function signatures. `PYTHONPATH=.` is required for all CLI invocations (pytest, alembic, uvicorn).

## Pre-commit

`requirements/dev.txt` pulls in `pre-commit`. Install hooks once:

```bash
pre-commit install
```

(If no `.pre-commit-config.yaml` is committed yet, this is a no-op — isort/black run manually.)
