import os
from contextlib import closing
from pathlib import Path
from typing import cast

import pytest
from alembic import command
from alembic.config import Config
from fastapi import HTTPException
from fastapi.applications import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, make_url, text
from sqlalchemy.orm import scoped_session, sessionmaker
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse

from server.api.api import api_router
from server.api.deps import get_current_active_superuser
from server.api.error_handling import ProblemDetailException
from server.db import db, init_database
from server.db.database import (
    ENGINE_ARGUMENTS,
    SESSION_ARGUMENTS,
    BaseModel,
    Database,
    DBSessionMiddleware,
    SearchQuery,
)
from server.db.models import ProductTable, UserTable
from server.exception_handlers.generic_exception_handlers import problem_detail_handler
from server.settings import app_settings
from tests.unit_tests.factories.account import make_account
from tests.unit_tests.factories.categories import make_category, make_category_translated
from tests.unit_tests.factories.order import make_pending_order
from tests.unit_tests.factories.product import make_product, make_translated_product
from tests.unit_tests.factories.shop import make_shop
from tests.unit_tests.factories.tag import make_tag


def run_migrations(db_uri: str) -> None:
    """Configure the alembic context and run the migrations.

    Each test will start with a clean database. This a heavy operation but ensures that our database is clean and
    tests run within their own context.

    Args:
        db_uri: The database uri configuration to run the migration on.

    Returns:
    ---
        None

    """
    path = Path(__file__).resolve().parent
    os.environ["DATABASE_URI"] = db_uri
    app_settings.DATABASE_URI = db_uri  # type: ignore
    alembic_cfg = Config(file_=path / "../../alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", db_uri)

    version_locations = alembic_cfg.get_main_option("version_locations")
    alembic_cfg.set_main_option(
        "version_locations",
        f"{os.path.join(path, '../../migrations/versions/schema')} {os.path.join(path, '../../migrations/versions/general')}",
    )
    # alembic_cfg.set_main_option(
    #     "version_locations", f"{version_locations} {os.path.dirname(orchestrator.__file__)}/migrations/versions/schema"
    # )

    command.upgrade(alembic_cfg, "heads")


@pytest.fixture(scope="session")
def db_uri(worker_id):
    """Ensure each pytest thread has its database.

    When running tests with the -j option make sure each test worker is isolated within its own database.

    Args:
        worker_id: the worker id

    Returns:
        Database uri to be used in the test thread

    """
    database_uri = os.environ.get("DATABASE_URI", "postgresql://shop:shop@localhost/shop-test")
    if worker_id == "master":
        # pytest is being run without any workers
        return database_uri
    url = make_url(database_uri)
    if hasattr(url, "set"):
        url = url.set(database=f"{url.database}-{worker_id}")
    else:
        url.database = f"{url.database}-{worker_id}"
    return url.render_as_string(hide_password=False)


@pytest.fixture(scope="session")
def database(db_uri):
    """Create database and run migrations and cleanup afterward.

    Args:
        db_uri: fixture for providing the application context and an initialized database. Although specifying this
            as an explicit parameter is redundant due to `fastapi_app`'s autouse setting, we have made the dependency
            explicit here for the purpose of documentation.

    """
    db.update(Database(db_uri))
    url = make_url(db_uri)
    db_to_create = url.database
    if hasattr(url, "set"):
        url = url.set(database="postgres")
    else:
        url.database = "postgres"
    engine = create_engine(url)
    with closing(engine.connect()) as conn:
        conn.execute(text("COMMIT;"))
        conn.execute(text(f'DROP DATABASE IF EXISTS "{db_to_create}";'))
        conn.execute(text("COMMIT;"))
        conn.execute(text(f'CREATE DATABASE "{db_to_create}";'))

    run_migrations(db_uri)
    db.wrapped_database.engine = create_engine(db_uri, **ENGINE_ARGUMENTS)

    try:
        yield
    finally:
        db.wrapped_database.engine.dispose()
        with closing(engine.connect()) as conn:
            conn.execute(text("COMMIT;"))
            conn.execute(text(f'DROP DATABASE IF EXISTS "{db_to_create}";'))


@pytest.fixture(autouse=True)
def db_session(database):
    """Ensure tests are run in a transaction with automatic rollback.

    This implementation creates a connection and transaction before yielding to the test function. Any transactions
    started and committed from within the test will be tied to this outer transaction. From the test function's
    perspective it looks like everything will indeed be committed; allowing for queries on the database to be
    performed to see if functions under test have persisted their changes to the database correctly. However once
    the test function returns this fixture will clean everything up by rolling back the outer transaction; leaving the
    database in a known state (=empty with the exception of what migrations have added as the initial state).

    Args:
        database: fixture for providing an initialized database.

    """
    with closing(db.wrapped_database.engine.connect()) as test_connection:
        db.wrapped_database.session_factory = sessionmaker(**SESSION_ARGUMENTS, bind=test_connection)
        db.wrapped_database.scoped_session = scoped_session(
            db.wrapped_database.session_factory, db.wrapped_database._scopefunc
        )
        BaseModel.set_query(cast(SearchQuery, db.wrapped_database.scoped_session.query_property()))

        trans = test_connection.begin()
        try:
            yield
        finally:
            if not trans._deactivated_from_connection:
                trans.rollback()


@pytest.fixture(scope="session", autouse=True)
def fastapi_app(database, db_uri):
    app = FastAPI(
        title="Shop backend",
        description="Backend for shop.",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        version="0.2.0",
        default_response_class=JSONResponse,
    )
    init_database(app_settings)

    app.include_router(api_router)

    app.add_middleware(SessionMiddleware, secret_key=app_settings.SESSION_SECRET)
    app.add_middleware(DBSessionMiddleware, database=db)
    origins = app_settings.CORS_ORIGINS.split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=app_settings.CORS_ALLOW_METHODS,
        allow_headers=app_settings.CORS_ALLOW_HEADERS,
        expose_headers=app_settings.CORS_EXPOSE_HEADERS,
    )

    # app.add_exception_handler(FormException, form_error_handler)
    app.add_exception_handler(ProblemDetailException, problem_detail_handler)

    def get_current_active_superuser_override() -> UserTable:
        import uuid

        return UserTable(
            id=uuid.uuid4(),
            username="test",
            email="test@pricelist.info",
        )

    app.dependency_overrides[get_current_active_superuser] = get_current_active_superuser_override

    return app


@pytest.fixture(scope="session", autouse=True)
def fastapi_app_not_authenticated(database, db_uri):
    app = FastAPI(
        title="Shop backend",
        description="Backend for shop.",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        version="0.2.0",
        default_response_class=JSONResponse,
    )
    init_database(app_settings)

    app.include_router(api_router)

    app.add_middleware(SessionMiddleware, secret_key=app_settings.SESSION_SECRET)
    app.add_middleware(DBSessionMiddleware, database=db)
    origins = app_settings.CORS_ORIGINS.split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=app_settings.CORS_ALLOW_METHODS,
        allow_headers=app_settings.CORS_ALLOW_HEADERS,
        expose_headers=app_settings.CORS_EXPOSE_HEADERS,
    )

    # app.add_exception_handler(FormException, form_error_handler)
    app.add_exception_handler(ProblemDetailException, problem_detail_handler)

    def get_current_active_superuser_override():
        raise HTTPException(status_code=401, detail="Not authenticated")

    app.dependency_overrides[get_current_active_superuser] = get_current_active_superuser_override

    return app


@pytest.fixture(scope="session")
def test_client(fastapi_app):
    return TestClient(fastapi_app)


@pytest.fixture()
def shop():
    return make_shop(with_config=False)


@pytest.fixture()
def shop_with_config():
    return make_shop(with_config=True)


@pytest.fixture()
def shop_with_categories():
    shop_id = make_shop(with_config=False)
    make_category(shop_id=shop_id)
    make_category(shop_id=shop_id, main_name="Main Cat 2", main_description="Main Cat Desc 2")
    return shop_id


@pytest.fixture()
def shop_with_products():
    shop_id = make_shop(with_config=False)
    category = make_category(shop_id=shop_id)
    make_product(shop_id=shop_id, category_id=category)
    make_product(shop_id=shop_id, category_id=category, main_name="Main Product 2")
    return shop_id


@pytest.fixture()
def shop_with_tags():
    shop_id = make_shop(with_config=False)
    make_tag(shop_id=shop_id)
    make_tag(shop_id=shop_id)
    return shop_id


@pytest.fixture()
def category(shop):
    return make_category(shop_id=shop)


@pytest.fixture()
def tag(shop):
    return make_tag(shop_id=shop)


@pytest.fixture()
def product(shop):
    category = make_category(shop_id=shop)
    return make_product(shop_id=shop, category_id=category)


@pytest.fixture()
def product_translated(shop):
    category = make_category_translated(shop_id=shop)
    return make_translated_product(shop_id=shop, category_id=category)


@pytest.fixture()
def product_translated_category_untranslated(shop):
    category = make_category(shop_id=shop)
    return make_translated_product(shop_id=shop, category_id=category)


@pytest.fixture()
def pending_order(shop):
    account = make_account(shop_id=shop)
    category = make_category(shop_id=shop)
    product_1 = make_product(shop_id=shop, category_id=category)
    product_2 = make_product(shop_id=shop, category_id=category)
    return make_pending_order(shop_id=shop, account_id=account, product_id_1=product_1, product_id_2=product_2)
