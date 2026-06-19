import uuid
from datetime import datetime, timedelta, timezone

import pytest

from tests.unit_tests.factories.categories import make_category
from tests.unit_tests.factories.product import make_product
from tests.unit_tests.factories.shop import make_shop, make_shop_with_shipping


@pytest.fixture()
def shop_no_shipping():
    shop_id = make_shop(with_config=False)
    category = make_category(shop_id=shop_id)
    p = make_product(shop_id=shop_id, category_id=category, price=10.0, main_name="Alfa")
    return {"shop_id": shop_id, "p": p}


@pytest.fixture()
def shop_with_shipping():
    shop_id = make_shop_with_shipping(fixed_fee=4.95)
    category = make_category(shop_id=shop_id)
    p = make_product(shop_id=shop_id, category_id=category, price=10.0, main_name="Beta")
    return {"shop_id": shop_id, "p": p}


@pytest.fixture()
def shop_with_discount():
    shop_id = make_shop(with_config=False)
    category = make_category(shop_id=shop_id)
    now = datetime.now(timezone.utc)
    p = make_product(
        shop_id=shop_id,
        category_id=category,
        price=20.0,
        main_name="Gamma",
        discounted_price=15.0,
        discounted_from=now - timedelta(days=1),
        discounted_to=now + timedelta(days=1),
    )
    return {"shop_id": shop_id, "p": p}


@pytest.fixture()
def shop_with_recurring():
    shop_id = make_shop(with_config=False)
    category = make_category(shop_id=shop_id)
    p = make_product(
        shop_id=shop_id,
        category_id=category,
        price=100.0,
        main_name="Delta",
        recurring_price_monthly=8.0,
        recurring_price_yearly=80.0,
    )
    return {"shop_id": shop_id, "p": p}


def _body(shop_id, items):
    return {"shop_id": str(shop_id), "items": items}


def test_unknown_shop_returns_404(test_client):
    body = _body(uuid.uuid4(), [])
    response = test_client.post("/cart/calculate", json=body)
    assert response.status_code == 404


def test_empty_cart(shop_no_shipping, test_client):
    response = test_client.post("/cart/calculate", json=_body(shop_no_shipping["shop_id"], []))
    assert response.status_code == 200
    j = response.json()
    assert j["subtotal_inc_vat"] == 0.0
    assert j["grand_total"] == 0.0
    assert j["lines"] == []


def test_single_product_no_shipping(shop_no_shipping, test_client):
    ids = shop_no_shipping
    items = [{"product_id": str(ids["p"]), "quantity": 2, "plan": "onetime"}]
    response = test_client.post("/cart/calculate", json=_body(ids["shop_id"], items))
    assert response.status_code == 200
    j = response.json()
    # price=10, vat_standard=21% → unit inc = 12.10; qty 2 → line = 24.20
    assert j["lines"][0]["unit_price_inc_vat"] == 12.10
    assert j["lines"][0]["line_total_inc_vat"] == 24.20
    assert j["lines"][0]["vat_rate"] == 21.0
    assert j["lines"][0]["product_name"] == "Alfa"
    assert j["subtotal_inc_vat"] == 24.20
    assert j["grand_total"] == 24.20
    assert j["shipping"] is None


def test_single_product_with_shipping(shop_with_shipping, test_client):
    ids = shop_with_shipping
    items = [{"product_id": str(ids["p"]), "quantity": 1, "plan": "onetime"}]
    response = test_client.post("/cart/calculate", json=_body(ids["shop_id"], items))
    assert response.status_code == 200
    j = response.json()
    # price=10, vat=21% → inc=12.10; shipping fixed_fee=4.95 ex-VAT → inc=5.99
    assert j["subtotal_inc_vat"] == 12.10
    assert j["shipping"]["fee_inc_btw"] == 5.99
    assert j["grand_total"] == round(12.10 + 5.99, 2)


def test_discount_applied_when_active(shop_with_discount, test_client):
    ids = shop_with_discount
    items = [{"product_id": str(ids["p"]), "quantity": 1, "plan": "onetime"}]
    response = test_client.post("/cart/calculate", json=_body(ids["shop_id"], items))
    assert response.status_code == 200
    j = response.json()
    # discounted_price=15 → 15 * 1.21 = 18.15
    assert j["lines"][0]["unit_price_inc_vat"] == 18.15
    assert j["subtotal_inc_vat"] == 18.15


def test_recurring_monthly_price(shop_with_recurring, test_client):
    ids = shop_with_recurring
    items = [{"product_id": str(ids["p"]), "quantity": 1, "plan": "monthly"}]
    response = test_client.post("/cart/calculate", json=_body(ids["shop_id"], items))
    assert response.status_code == 200
    j = response.json()
    # recurring_price_monthly=8.0 * 1.21 = 9.68
    assert j["lines"][0]["unit_price_inc_vat"] == 9.68


def test_recurring_yearly_price(shop_with_recurring, test_client):
    ids = shop_with_recurring
    items = [{"product_id": str(ids["p"]), "quantity": 1, "plan": "yearly"}]
    response = test_client.post("/cart/calculate", json=_body(ids["shop_id"], items))
    assert response.status_code == 200
    j = response.json()
    # recurring_price_yearly=80.0 * 1.21 = 96.80
    assert j["lines"][0]["unit_price_inc_vat"] == 96.80


def test_unknown_product_is_skipped(shop_no_shipping, test_client):
    ids = shop_no_shipping
    items = [
        {"product_id": str(ids["p"]), "quantity": 1, "plan": "onetime"},
        {"product_id": str(uuid.uuid4()), "quantity": 1, "plan": "onetime"},
    ]
    response = test_client.post("/cart/calculate", json=_body(ids["shop_id"], items))
    assert response.status_code == 200
    j = response.json()
    assert len(j["lines"]) == 1
    assert j["subtotal_inc_vat"] == 12.10
