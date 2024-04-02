import json
import os
import re
import uuid
from contextlib import closing
from datetime import datetime
from os import listdir
from typing import Dict, cast

import pytest
import respx
import structlog
from alembic import command
from alembic.config import Config
from fastapi.applications import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from server.api.api_v1.api import api_router
from server.api.error_handling import ProblemDetailException
from server.db import db
from server.db.database import ENGINE_ARGUMENTS, SESSION_ARGUMENTS, BaseModel, DBSessionMiddleware, SearchQuery
from server.db.models import (
    Category,
    Flavor,
    Kind,
    KindToFlavor,
    KindToStrain,
    KindToTag,
    License,
    MainCategory,
    Order,
    Price,
    ProductsTable,
    RolesTable,
    Shop,
    ShopToPrice,
    Strain,
    Tag,
    UsersTable,
)
from server.exception_handlers.generic_exception_handlers import problem_detail_handler
from server.pydantic_forms.exception_handlers.fastapi import form_error_handler
from server.pydantic_forms.exceptions import FormException
from server.security import get_password_hash
from server.settings import app_settings
from server.types import UUIDstr
from server.utils.date_utils import nowtz

logger = structlog.getLogger(__name__)

CWI: UUIDstr = "2f47f65a-0911-e511-80d0-005056956c1a"
SURFNET: UUIDstr = "4c237817-e64b-47a3-ba0d-0d57bf263266"

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "Adminnetje"
CUSTOMER_EMAIL = "customer@example.com"
CUSTOMER_PASSWORD = "Customertje"
EMPLOYEE_EMAIL = "employee@example.com"
EMPLOYEE_PASSWORD = "Employeetje"


def run_migrations(db_uri: str) -> None:
    """
    Configure the alembic context and run the migrations.

    Each test will start with a clean database. This a heavy operation but ensures that our database is clean and
    tests run within their own context.

    Args:
        db_uri: The database uri configuration to run the migration on.

    Returns:
        None

    """
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)))
    os.environ["DATABASE_URI"] = db_uri
    app_settings.DATABASE_URI = db_uri
    alembic_cfg = Config(file_=os.path.join(path, "../../alembic.ini"))
    alembic_cfg.set_main_option("script_location", os.path.join(path, "../../migrations"))
    alembic_cfg.set_main_option(
        "version_locations",
        f"{os.path.join(path, '../../migrations/versions/schema')} {os.path.join(path, '../../migrations/versions/general')}",
    )
    alembic_cfg.set_main_option("sqlalchemy.url", db_uri)
    command.upgrade(alembic_cfg, "heads")


@pytest.fixture(scope="session")
def db_uri(worker_id):
    """
    Ensure each pytest thread has its database.

    When running tests with the -j option make sure each test worker is isolated within its own database.

    Args:
        worker_id: the worker id

    Returns:
        Database uri to be used in the test thread

    """
    database_uri = os.environ.get(
        "DATABASE_URI",
        "postgresql://boilerplate:boilerplate@localhost/pricelist-test",
    )
    if worker_id == "master":
        # pytest is being run without any workers
        return database_uri
    url = make_url(database_uri)
    if hasattr(url, "set"):
        url = url.set(database=f"{url.database}-{worker_id}")
    else:
        url.database = f"{url.database}-{worker_id}"
    return str(url)


@pytest.fixture(scope="session")
def database(db_uri):
    """Create database and run migrations and cleanup afterwards.

    Args:
        db_uri: fixture for providing the application context and an initialized database.

    """
    url = make_url(db_uri)
    db_to_create = url.database
    if hasattr(url, "set"):
        url = url.set(database="postgres")
    else:
        url.database = "postgres"
    engine = create_engine(url)
    with closing(engine.connect()) as conn:
        conn.execute("COMMIT;")
        conn.execute(f'DROP DATABASE IF EXISTS "{db_to_create}";')
        conn.execute("COMMIT;")
        conn.execute(f'CREATE DATABASE "{db_to_create}";')

    run_migrations(db_uri)
    db.engine = create_engine(db_uri, **ENGINE_ARGUMENTS)

    try:
        yield
    finally:
        db.engine.dispose()
        with closing(engine.connect()) as conn:
            conn.execute("COMMIT;")
            conn.execute(f'DROP DATABASE IF EXISTS "{db_to_create}";')


@pytest.fixture(autouse=True)
def db_session(database):
    """
    Ensure tests are run in a transaction with automatic rollback.

    This implementation creates a connection and transaction before yielding to the test function. Any transactions
    started and committed from within the test will be tied to this outer transaction. From the test function's
    perspective it looks like everything will indeed be committed; allowing for queries on the database to be
    performed to see if functions under test have persisted their changes to the database correctly. However once
    the test function returns this fixture will clean everything up by rolling back the outer transaction; leaving the
    database in a known state (=empty with the exception of what migrations have added as the initial state).

    Args:
        database: fixture for providing an initialized database.

    """
    with closing(db.engine.connect()) as test_connection:
        db.session_factory = sessionmaker(**SESSION_ARGUMENTS, bind=test_connection)
        db.scoped_session = scoped_session(db.session_factory, db._scopefunc)
        BaseModel.set_query(cast(SearchQuery, db.scoped_session.query_property()))

        trans = test_connection.begin()
        try:
            yield
        finally:
            trans.rollback()


@pytest.fixture(scope="session", autouse=True)
def fastapi_app(database, db_uri):
    app = FastAPI(
        title="orchestrator",
        openapi_url="/openapi/openapi.yaml",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        default_response_class=JSONResponse,
    )

    app.include_router(api_router, prefix="/api")
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
    app.add_exception_handler(FormException, form_error_handler)
    app.add_exception_handler(ProblemDetailException, problem_detail_handler)

    return app


@pytest.fixture(scope="session")
def test_client(fastapi_app):
    return TestClient(fastapi_app)


@pytest.fixture
def mocked_api():
    with respx.mock(base_url="https://foo.bar") as respx_mock:
        respx_mock.get("/users/", content=[], alias="list_users")
        ...
        yield respx_mock


@pytest.fixture
def user_roles():
    roles = ["customer", "employee", "admin"]
    [db.session.add(RolesTable(id=str(uuid.uuid4()), name=role)) for role in roles]
    db.session.commit()


@pytest.fixture
def user_admin(shop_1, shop_2):
    admin = UsersTable(
        username="Admin",
        email="admin@admin",
        password=get_password_hash("admin"),
        active=True,
        roles=[RolesTable(name="admin", description="Admin Role")],
        shops=[shop_1, shop_2],
    )

    db.session.add(admin)
    db.session.commit()
    return admin


@pytest.fixture
def user_employee(shop_1):
    employee = UsersTable(
        username="Employee",
        email="employee@employee",
        password=get_password_hash("employee"),
        active=True,
        roles=[RolesTable(name="employee", description="Employee Role")],
        shops=[shop_1],
    )

    db.session.add(employee)
    db.session.commit()
    return employee


@pytest.fixture
def user_employee_2(shop_2):
    employee = UsersTable(
        username="Employee2",
        email="employee@employee2",
        password=get_password_hash("employee2"),
        active=True,
        roles=[RolesTable(name="employee", description="Employee Role")],
        shops=[shop_2],
    )

    db.session.add(employee)
    db.session.commit()
    return employee


@pytest.fixture
def superuser_token_headers(test_client, user_admin) -> Dict[str, str]:
    login_data = {
        "username": "Admin",
        "password": "admin",
    }
    r = test_client.post("/api/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


@pytest.fixture
def employee_token_headers(test_client, user_employee) -> Dict[str, str]:
    login_data = {
        "username": "Employee",
        "password": "employee",
    }
    r = test_client.post("/api/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


@pytest.fixture
def employee_token_headers_2(test_client, user_employee_2) -> Dict[str, str]:
    login_data = {
        "username": "Employee2",
        "password": "employee2",
    }
    r = test_client.post("/api/login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


@pytest.fixture
def customer_logged_in(customer):
    user = UsersTable.query.filter(UsersTable.email == CUSTOMER_EMAIL).first()
    # Todo: actually login/handle cookie
    db.session.commit()
    return user


@pytest.fixture
def price_1():
    fixture = Price(id=str(uuid.uuid4()), internal_product_id="01", half=5.50, one=10.0, five=45.0, joint=4.50)
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def price_2():
    fixture = Price(id=str(uuid.uuid4()), internal_product_id="02", one=7.50, five=35.0, joint=4.00)
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def price_3():
    fixture = Price(id=str(uuid.uuid4()), internal_product_id="03", piece=2.50)
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def shop_1():
    fixture = Shop(id=str(uuid.uuid4()), name="Mississippi", description="Shop description")
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def shop_with_testclient_ip():
    fixture = Shop(id=str(uuid.uuid4()), name="IpShop", description="IpShop description", allowed_ips=["testclient"])
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def shop_with_custom_ip():
    fixture = Shop(
        id=str(uuid.uuid4()), name="CustomIpShop", description="CustomIpShop description", allowed_ips=["123.45.67.89"]
    )
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def shop_2():
    fixture = Shop(id=str(uuid.uuid4()), name="Head Shop", description="Shop description 2")
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def main_category_1(shop_1):
    fixture = MainCategory(
        name="Main Category 1",
        name_en="Main Category 1",
        description="Category 1 description",
        shop_id=shop_1.id,
        order_number=0,
        icon="main_1",
    )
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def main_category_2(shop_1):
    fixture = MainCategory(
        name="Main Category 2",
        name_en="Main Category 2",
        description="Category 2 description",
        shop_id=shop_1.id,
        order_number=1,
        icon="main_2",
    )
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def category_1(shop_1, main_category_1):
    fixture = Category(
        id=str(uuid.uuid4()),
        name="Category 1",
        description="Category description",
        shop_id=shop_1.id,
        main_category_id=main_category_1.id,
    )
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def category_2(shop_1, main_category_1):
    fixture = Category(
        id=str(uuid.uuid4()),
        name="Category 2",
        description="Category description 2",
        shop_id=shop_1.id,
        main_category_id=main_category_1.id,
    )
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def category_3(shop_1):
    fixture = Category(
        id=str(uuid.uuid4()),
        name="Test Category",
        description="Test Category description",
        shop_id=shop_1.id,
        color="#376E1A",
        image_1="test-category-1-1.png",
        image_2="test-category-2-1.png",
    )
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def tag_1():
    fixture = Tag(id=str(uuid.uuid4()), name="GigglyTest")
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def tag_2():
    fixture = Tag(id=str(uuid.uuid4()), name="FocusedTest")
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def flavor_1():
    fixture = Flavor(name="Moon", icon="moon", color="00fff0")
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def flavor_2():
    fixture = Flavor(name="Earth", icon="earth", color="00ff00")
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def strain_1():
    fixture = Strain(id=str(uuid.uuid4()), name="Haze")
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def strain_2():
    fixture = Strain(id=str(uuid.uuid4()), name="Kush")
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def license_1(fake_order):
    fixture = License(
        id=str(uuid.uuid4()),
        name="john",
        order_id=fake_order.id,
        is_recurring=True,
        seats=20,
        improviser_user=str(uuid.uuid4()),
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow(),
        created_at=datetime.utcnow(),
        modified_at=datetime.utcnow(),
    )
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def license_2(fake_order):
    fixture = License(
        id=str(uuid.uuid4()),
        name="doe",
        order_id=fake_order.id,
        is_recurring=False,
        seats=10,
        improviser_user=str(uuid.uuid4()),
        start_date=datetime.utcnow(),
        end_date=datetime.utcnow(),
        created_at=datetime.utcnow(),
        modified_at=datetime.utcnow(),
    )
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def kind_1(tag_1, flavor_1, strain_1):
    fixture_id = str(uuid.uuid4())
    fixture = Kind(
        id=fixture_id,
        name="Indica",
        c=False,
        h=False,
        i=True,
        s=False,
        short_description_nl="Cinderela 99 x Jack Herrer",
        description_nl="Amnesia is typisch een sativa-dominant cannabis strain, met wat variaites tussen de kwekers. "
        "Cinderela 99 x Jack Herrer in de volksmond ook wel bekend als Haze knalt.",
        short_description_en="Amnesia is typically a sativa-dominant cannabis strain",
        description_en="Amnesia is typically a sativa-dominant cannabis strain with some variation between breeders. "
        "Skunk, Cinderella 99, and Jack Herer are some of Amnesia’s genetic forerunners, passing on "
        "uplifting, creative, and euphoric effects. This strain normally has a high THC and low CBD "
        "profile and produces intense psychotropic effects that new consumers should be wary of.",
    )
    db.session.add(fixture)
    record = KindToTag(id=str(uuid.uuid4()), kind_id=fixture_id, tag=tag_1, amount=90)
    db.session.add(record)
    record = KindToFlavor(id=str(uuid.uuid4()), kind_id=fixture_id, flavor_id=flavor_1.id)
    db.session.add(record)
    record = KindToStrain(id=str(uuid.uuid4()), kind_id=fixture_id, strain_id=strain_1.id)
    db.session.add(record)
    db.session.commit()
    return fixture


@pytest.fixture
def kind_2():
    fixture_id = str(uuid.uuid4())
    fixture = Kind(
        id=fixture_id,
        name="Sativa",
        c=False,
        h=False,
        i=False,
        s=True,
        short_description_nl="Vet goeie indica",
        description_nl="Deze knalt er echt in. Alleen voor ervaren gebruikers.",
        short_description_en="Really good indica",
        description_en="This one will blow your mind. Only for experienced users.",
    )
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def kind_3():
    fixture_id = str(uuid.uuid4())
    fixture = Kind(
        id=fixture_id,
        name="Test Kind",
        c=False,
        h=False,
        i=False,
        s=True,
        short_description_nl="Test Kind description",
        description_nl="Test Kind description",
        short_description_en="Test Kind description",
        description_en="Test Kind description",
        image_1="test-kind-1-1.png",
        image_2="test-kind-2-1.png",
        image_3="test-kind-3-1.png",
    )
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def product_1():
    fixture_id = str(uuid.uuid4())
    fixture = ProductsTable(
        id=fixture_id,
        name="Cola",
        short_description_nl="Cola Light",
        description_nl="Deze knalt er echt in. Alleen voor echte caffeine addicts.",
        short_description_en="Cola Light",
        description_en="This one will blow your mind. Only for Real caffeine addicts.",
    )
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def product_2():
    fixture_id = str(uuid.uuid4())
    fixture = ProductsTable(
        id=fixture_id,
        name="Pepsi",
        short_description_nl="Pepsi Light",
        description_nl="niet zo goed als coca cola",
        short_description_en="Pepsi Light",
        description_en="Not as good as coca cola",
    )
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def product_3():
    fixture_id = str(uuid.uuid4())
    fixture = ProductsTable(
        id=fixture_id,
        name="Test Product",
        short_description_nl="Test Product description",
        description_nl="Test Product description",
        short_description_en="Test Product description",
        description_en="Test Product description",
        image_1="test-product-1-1.png",
        image_2="test-product-2-1.png",
        image_3="test-product-3-1.png",
    )
    db.session.add(fixture)
    db.session.commit()
    return fixture


@pytest.fixture
def shop_with_products(shop_1, kind_1, kind_2, price_1, price_2, price_3, product_1, category_1):
    shop_to_price1 = ShopToPrice(
        price_id=price_1.id, shop_id=shop_1.id, category_id=category_1.id, kind_id=kind_1.id, order_number=0
    )
    shop_to_price2 = ShopToPrice(
        price_id=price_2.id, shop_id=shop_1.id, category_id=category_1.id, kind_id=kind_2.id, order_number=1
    )
    shop_to_price3 = ShopToPrice(
        price_id=price_3.id, shop_id=shop_1.id, category_id=category_1.id, product_id=product_1.id, order_number=2
    )
    db.session.add(shop_to_price1)
    db.session.add(shop_to_price2)
    db.session.add(shop_to_price3)
    db.session.commit()
    return shop_1


@pytest.fixture
def shop_with_testclient_ip_with_products(shop_with_testclient_ip, kind_1, price_1, category_1):
    shop_to_price1 = ShopToPrice(
        price_id=price_1.id, shop_id=shop_with_testclient_ip.id, category_id=category_1.id, kind_id=kind_1.id
    )
    db.session.add(shop_to_price1)
    db.session.commit()
    return shop_with_testclient_ip


@pytest.fixture
def shop_with_custom_ip_with_products(shop_with_custom_ip, kind_1, price_1, category_1):
    shop_to_price1 = ShopToPrice(
        price_id=price_1.id, shop_id=shop_with_custom_ip.id, category_id=category_1.id, kind_id=kind_1.id
    )
    db.session.add(shop_to_price1)
    db.session.commit()
    return shop_with_custom_ip


@pytest.fixture
def shop_to_price_1(shop_1, kind_1, price_1, category_1):
    shop_to_price = ShopToPrice(
        id=uuid.uuid4(), price_id=price_1.id, shop_id=shop_1.id, category_id=category_1.id, kind_id=kind_1.id
    )
    db.session.add(shop_to_price)
    db.session.commit()
    return shop_to_price


@pytest.fixture
def shop_to_price_2(shop_1, product_1, price_1, category_1):
    shop_to_price = ShopToPrice(
        id=uuid.uuid4(), price_id=price_1.id, shop_id=shop_1.id, category_id=category_1.id, product_id=product_1.id
    )
    db.session.add(shop_to_price)
    db.session.commit()
    return shop_to_price


@pytest.fixture
def shop_with_orders(shop_with_products, kind_1, kind_2, price_1, price_2):
    items = [
        {
            "description": "1 gram",
            "price": price_1.one,
            "kind_id": str(kind_1.id),
            "kind_name": kind_1.name,
            "internal_product_id": "01",
            "quantity": 2,
        },
        {
            "description": "1 joint",
            "price": price_2.joint,
            "kind_id": str(kind_2.id),
            "kind_name": kind_2.name,
            "internal_product_id": "02",
            "quantity": 1,
        },
    ]
    order = Order(
        id=str(uuid.uuid4()),
        shop_id=str(shop_with_products.id),
        order_info=items,
        total=24.0,
        customer_order_id=1,
    )
    db.session.add(order)
    order = Order(
        id=str(uuid.uuid4()),
        shop_id=str(shop_with_products.id),
        order_info=items,
        total=24.0,
        customer_order_id=2,
        completed_at=datetime.utcnow(),
        status="complete",
    )
    db.session.add(order)
    db.session.commit()
    return shop_1


@pytest.fixture
def shop_with_different_statuses_orders(shop_with_products, kind_1, kind_2, price_1, price_2):
    items = [
        {
            "description": "1 gram",
            "price": price_1.one,
            "kind_id": str(kind_1.id),
            "kind_name": kind_1.name,
            "internal_product_id": "01",
            "quantity": 2,
        },
        {
            "description": "1 joint",
            "price": price_2.joint,
            "kind_id": str(kind_2.id),
            "kind_name": kind_2.name,
            "internal_product_id": "02",
            "quantity": 1,
        },
    ]
    order = Order(
        id=str(uuid.uuid4()),
        shop_id=str(shop_with_products.id),
        order_info=items,
        total=24.0,
        customer_order_id=1,
        status="pending",
    )
    db.session.add(order)
    order = Order(
        id=str(uuid.uuid4()),
        shop_id=str(shop_with_products.id),
        order_info=items,
        total=24.0,
        customer_order_id=2,
        completed_at=datetime.utcnow(),
        status="complete",
    )
    db.session.add(order)
    order = Order(
        id=str(uuid.uuid4()),
        shop_id=str(shop_with_products.id),
        order_info=items,
        total=24.0,
        customer_order_id=3,
        completed_at=datetime.utcnow(),
        status="cancelled",
    )
    db.session.add(order)
    db.session.commit()
    return shop_1


@pytest.fixture
def shop_with_mixed_orders(shop_with_products, kind_1, kind_2, price_1, price_2, price_3, product_1):
    items = [
        {
            "description": "1 gram",
            "price": price_1.one,
            "kind_id": str(kind_1.id),
            "kind_name": kind_1.name,
            "internal_product_id": "01",
            "quantity": 2,
        },
        {
            "description": "1 joint",
            "price": price_2.joint,
            "kind_id": str(kind_2.id),
            "kind_name": kind_2.name,
            "internal_product_id": "02",
            "quantity": 1,
        },
        {
            "description": "1 cola",
            "price": price_3.piece,
            "product_id": str(product_1.id),
            "product_name": product_1.name,
            "internal_product_id": "03",
            "quantity": 1,
        },
    ]
    order = Order(
        id=str(uuid.uuid4()),
        shop_id=str(shop_with_products.id),
        order_info=items,
        total=26.50,
        customer_order_id=1,
    )
    db.session.add(order)
    order = Order(
        id=str(uuid.uuid4()),
        shop_id=str(shop_with_products.id),
        order_info=items,
        total=26.50,
        customer_order_id=2,
        completed_at=datetime.utcnow(),
        status="complete",
    )
    db.session.add(order)
    db.session.commit()
    return shop_1


@pytest.fixture
def fake_order(shop_with_products, kind_1, kind_2, price_1, price_2):
    items = [
        {
            "description": "1 gram",
            "price": price_1.one,
            "kind_id": str(kind_1.id),
            "kind_name": kind_1.name,
            "internal_product_id": "01",
            "quantity": 2,
        },
        {
            "description": "1 joint",
            "price": price_2.joint,
            "kind_id": str(kind_2.id),
            "kind_name": kind_2.name,
            "internal_product_id": "02",
            "quantity": 1,
        },
    ]
    order = Order(
        id=str(uuid.uuid4()),
        shop_id=str(shop_with_products.id),
        order_info=items,
        total=24.0,
        customer_order_id=1,
    )
    db.session.add(order)
    db.session.commit()
    return order
