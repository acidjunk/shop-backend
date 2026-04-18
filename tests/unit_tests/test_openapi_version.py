"""Guard against silent OpenAPI schema drift.

If the generated OpenAPI spec changes but ``APP_VERSION`` in ``server/main.py``
is not bumped, this test fails. After an intentional schema + version change,
regenerate ``tests/unit_tests/openapi_snapshot.json``:

    PYTHONPATH=. python -c "import json; \
from fastapi import FastAPI; from starlette.responses import JSONResponse; \
from server.api.api import api_router; \
app = FastAPI(title='ShopVirge API', description='Backend for ShopVirge Shops.', \
openapi_url='/openapi.json', docs_url='/docs', redoc_url='/redoc', \
version='<new-version>', default_response_class=JSONResponse); \
app.include_router(api_router); \
json.dump(app.openapi(), open('tests/unit_tests/openapi_snapshot.json', 'w'), indent=2, sort_keys=True)"
"""
import json
import re
from pathlib import Path

from fastapi import FastAPI
from starlette.responses import JSONResponse

from server.api.api import api_router

REPO_ROOT = Path(__file__).resolve().parents[2]
MAIN_PY = REPO_ROOT / "server" / "main.py"
SNAPSHOT_PATH = Path(__file__).parent / "openapi_snapshot.json"


def _app_version_from_main() -> str:
    match = re.search(r'^APP_VERSION\s*=\s*"([^"]+)"', MAIN_PY.read_text(), re.MULTILINE)
    assert match, f"APP_VERSION not found in {MAIN_PY}"
    return match.group(1)


def _current_openapi(version: str) -> dict:
    app = FastAPI(
        title="ShopVirge API",
        description="Backend for ShopVirge Shops.",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        version=version,
        default_response_class=JSONResponse,
    )
    app.include_router(api_router)
    return app.openapi()


def _strip_version(spec: dict) -> dict:
    return {**spec, "info": {**spec["info"], "version": ""}}


def test_openapi_version_bumped_when_schema_changes():
    current_version = _app_version_from_main()
    current = _current_openapi(current_version)
    snapshot = json.loads(SNAPSHOT_PATH.read_text())

    if _strip_version(current) == _strip_version(snapshot):
        return

    snapshot_version = snapshot["info"]["version"]
    assert current_version != snapshot_version, (
        f"OpenAPI schema changed but APP_VERSION in server/main.py is still {current_version!r}. "
        f"Bump APP_VERSION and regenerate {SNAPSHOT_PATH.relative_to(REPO_ROOT)}."
    )
