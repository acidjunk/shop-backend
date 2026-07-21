"""Manual repro: revision-numbering race on parallel product-attribute-value creates.

The shop UI saves attribute values with parallel requests right after creating a
product. Each write records a product revision; without a FOR UPDATE lock on the
product row, concurrent writers computed the same max(revision_no)+1 and hit the
uq_revision_entity_no constraint -> HTTP 500.

Mirrors that flow: POST /products/ then N parallel POST /product-attribute-values/.
Runs its own uvicorn with auth overridden (like tests/unit_tests/conftest.py)
against a scratch database (dropped and recreated on every run). The regular test
suite can't cover this: its fixtures bind all sessions to a single connection, so
truly concurrent transactions are impossible there.

Run:  PYTHONPATH=. ./venv/bin/python bin/repro_parallel_revision_race.py
Exit 1 (RED) if any 5xx is observed, exit 0 (GREEN) otherwise.
"""

import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
DB_NAME = "shop-repro500"
DB_URI = f"postgresql://shop:shop@localhost/{DB_NAME}"
PORT = 8123
ROUNDS = 5
N_ATTRS = 4

os.environ["DATABASE_URI"] = DB_URI
os.chdir(BACKEND)
sys.path.insert(0, str(BACKEND))

from sqlalchemy import create_engine, make_url, text

admin_url = make_url(DB_URI).set(database="postgres")
admin_engine = create_engine(admin_url)
with closing(admin_engine.connect()) as conn:
    conn.execute(text("COMMIT;"))
    conn.execute(text(f'DROP DATABASE IF EXISTS "{DB_NAME}";'))
    conn.execute(text("COMMIT;"))
    conn.execute(text(f'CREATE DATABASE "{DB_NAME}";'))

from server.settings import app_settings

app_settings.DATABASE_URI = DB_URI  # type: ignore

from alembic import command
from alembic.config import Config

cfg = Config(file_=str(BACKEND / "alembic.ini"))
cfg.set_main_option("sqlalchemy.url", DB_URI)
cfg.set_main_option(
    "version_locations",
    f"{BACKEND}/migrations/versions/schema {BACKEND}/migrations/versions/general",
)
command.upgrade(cfg, "heads")

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from server.api.api import api_router
from server.api.error_handling import ProblemDetailException
from server.db import db, init_database
from server.db.database import DBSessionMiddleware
from server.exception_handlers.generic_exception_handlers import problem_detail_handler
from server.security import CustomCognitoToken, auth_required, auth_required_any

init_database(app_settings)

app = FastAPI(default_response_class=JSONResponse)
app.include_router(api_router)
app.add_middleware(SessionMiddleware, secret_key=app_settings.SESSION_SECRET)
app.add_middleware(DBSessionMiddleware, database=db)
app.add_exception_handler(ProblemDetailException, problem_detail_handler)


def _auth_override() -> CustomCognitoToken:
    return CustomCognitoToken(
        client_id=app_settings.AWS_COGNITO_CLIENT_ID,
        sub="5678",
        token_use="access",
        scope="openid profile email",
        auth_time=1727169594,
        iss="https://cognito-idp.eu-central-1.amazonaws.com/local-repro",
        exp=9727169594,
        iat=9727169594,
        jti="jti",
        username="5678",
        **{"cognito:groups": ["Admins"]},
    )


app.dependency_overrides[auth_required] = _auth_override
app.dependency_overrides[auth_required_any] = _auth_override

# ---- seed (factories commit directly via db.session) ----
from tests.unit_tests.factories.attribute import make_attribute, make_option
from tests.unit_tests.factories.categories import make_category
from tests.unit_tests.factories.shop import make_shop

shop_id = str(make_shop())
category_id = str(make_category(shop_id=shop_id))
attrs = []
for i in range(N_ATTRS):
    attr_id = make_attribute(shop_id, name=f"attr-{i}")
    opt_id = make_option(attr_id, f"opt-{i}")
    attrs.append((str(attr_id), str(opt_id)))
db.wrapped_database.scoped_session.remove()

# ---- serve ----
import uvicorn

server = uvicorn.Server(
    uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning")
)
threading.Thread(target=server.run, daemon=True).start()

import httpx

for _ in range(200):
    try:
        httpx.get(f"http://127.0.0.1:{PORT}/openapi.json", timeout=1)
        break
    except Exception:
        time.sleep(0.1)

client = httpx.Client(base_url=f"http://127.0.0.1:{PORT}", timeout=30)


def create_product(round_no: int) -> str:
    body = {
        "shop_id": shop_id,
        "category_id": category_id,
        "price": 1.0,
        "tax_category": "vat_zero",
        "max_one": False,
        "shippable": True,
        "featured": False,
        "new_product": False,
        "translation": {
            "main_name": f"Repro product {round_no}",
            "main_description": "Repro",
            "main_description_short": "Repro",
        },
        "image_1": "",
        "image_2": "",
        "image_3": "",
        "image_4": "",
        "image_5": "",
        "image_6": "",
    }
    r = client.post(f"/shops/{shop_id}/products/", json=body)
    assert r.status_code == 201, f"product create failed: {r.status_code} {r.text}"
    return r.json()["id"]


def create_pav(product_id: str, attr_id: str, opt_id: str) -> httpx.Response:
    return client.post(
        f"/shops/{shop_id}/product-attribute-values/",
        json={"product_id": product_id, "attribute_id": attr_id, "option_id": opt_id},
    )


red = False
for round_no in range(ROUNDS):
    product_id = create_product(round_no)
    with ThreadPoolExecutor(max_workers=N_ATTRS) as ex:
        results = list(
            ex.map(lambda ao: create_pav(product_id, ao[0], ao[1]), attrs)
        )
    codes = [r.status_code for r in results]
    print(f"round {round_no}: PAV status codes = {codes}")
    for r in results:
        if r.status_code >= 500:
            red = True
            print("  5xx body:", r.text[:300])

if red:
    print("RED: reproduced 5xx on parallel attribute-value creates")
    sys.exit(1)
print("GREEN: no 5xx observed")
sys.exit(0)
