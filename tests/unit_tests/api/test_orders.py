from datetime import datetime, timedelta

import pytest

from server.db import db
from server.db.models import OrderTable, ShopTable
from tests.unit_tests.factories.categories import make_category
from tests.unit_tests.factories.product import make_product
from tests.unit_tests.factories.shop import make_shop_with_shipping


def test_orders_get_multi(shop, pending_order, test_client):
    response = test_client.get(f"/orders/")
    assert response.status_code == 200
    orders = response.json()
    assert 1 == len(orders)
    assert 2 == len(orders[0]["order_info"])
    info_total = 0
    for order in orders:
        for info in order["order_info"]:
            info_total += info["price"] * info["quantity"]
        info_total += order.get("shipping_fee_inc_btw") or 0
        # Total matches info total
        assert order["total"] == info_total


@pytest.fixture()
def shop_no_shipping_with_products():
    shop_id = make_shop_with_shipping(enabled=False)
    category = make_category(shop_id=shop_id)
    p1 = make_product(shop_id=shop_id, category_id=category, main_name="Item 1", price=10.0)
    p2 = make_product(shop_id=shop_id, category_id=category, main_name="Item 2", price=20.0)
    return {"shop_id": shop_id, "p1": p1, "p2": p2}


@pytest.fixture()
def shop_shipping_fixed_with_products():
    shop_id = make_shop_with_shipping(fixed_fee=4.95)
    category = make_category(shop_id=shop_id)
    p1 = make_product(shop_id=shop_id, category_id=category, main_name="Item 1", price=10.0)
    p2 = make_product(shop_id=shop_id, category_id=category, main_name="Item 2", price=20.0)
    return {"shop_id": shop_id, "p1": p1, "p2": p2}


@pytest.fixture()
def shop_shipping_mixed_vat():
    shop_id = make_shop_with_shipping(fixed_fee=10.0)
    category = make_category(shop_id=shop_id)
    p_high = make_product(
        shop_id=shop_id, category_id=category, main_name="Std VAT", price=100.0, tax_category="vat_standard"
    )
    p_low = make_product(
        shop_id=shop_id, category_id=category, main_name="Low VAT", price=100.0, tax_category="vat_lower_1"
    )
    return {"shop_id": shop_id, "p_high": p_high, "p_low": p_low}


@pytest.fixture()
def shop_shipping_free_above():
    shop_id = make_shop_with_shipping(
        fixed_fee=4.95,
        free_shipping_above_enabled=True,
        free_shipping_above_amount=50.0,
    )
    category = make_category(shop_id=shop_id)
    p1 = make_product(shop_id=shop_id, category_id=category, main_name="Item 1", price=10.0)
    return {"shop_id": shop_id, "p1": p1}


def _order_body(shop_id, items):
    body = {
        "shop_id": str(shop_id),
        "order_info": items,
        "account_name": f"buyer-{shop_id}@example.com",
        "notes": "test",
    }
    return body


def test_create_order_no_shipping(shop_no_shipping_with_products, test_client):
    ids = shop_no_shipping_with_products
    items = [
        {"description": "x", "product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 2},
        {"description": "x", "product_id": str(ids["p2"]), "product_name": "Item 2", "quantity": 1},
    ]
    body = _order_body(ids["shop_id"], items)
    response = test_client.post("/orders/", json=body)
    assert response.status_code == 201, response.json()
    j = response.json()
    assert j["shipping_fee_inc_btw"] is None
    # Product prices are ex-VAT: (10 * 1.21 * 2) + (20 * 1.21) = 48.40.
    assert j["total"] == 48.4


def test_quote_order_calculates_gross_price_from_net_product_price(shop_no_shipping_with_products, test_client):
    ids = shop_no_shipping_with_products
    category = make_category(shop_id=ids["shop_id"])
    product_id = make_product(
        shop_id=ids["shop_id"],
        category_id=category,
        main_name="VAT example",
        price=100.0,
    )

    response = test_client.post(
        "/orders/quote",
        json={
            "shop_id": str(ids["shop_id"]),
            "order_info": [{"product_id": str(product_id), "product_name": "VAT example", "quantity": 1}],
        },
    )

    assert response.status_code == 200, response.json()
    assert response.json()["order_info"][0]["price"] == 121.0
    assert response.json()["subtotal"] == 121.0
    assert response.json()["total"] == 121.0

    order_response = test_client.post(
        "/orders/",
        json={
            "shop_id": str(ids["shop_id"]),
            "account_name": "vat-example@example.com",
            "order_info": [{"product_id": str(product_id), "product_name": "VAT example", "quantity": 1}],
        },
    )
    assert order_response.status_code == 201, order_response.json()
    assert order_response.json()["total"] == 121.0


def test_quote_and_create_order_check_stock_when_enabled(shop_no_shipping_with_products, test_client):
    ids = shop_no_shipping_with_products
    shop = db.session.get(ShopTable, ids["shop_id"])
    shop.config = {"toggles": {"enable_stock_on_products": True}}
    db.session.commit()

    body = _order_body(
        ids["shop_id"],
        [{"product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 2}],
    )
    assert (
        test_client.post(
            "/orders/quote", json={"shop_id": body["shop_id"], "order_info": body["order_info"]}
        ).status_code
        == 400
    )
    assert test_client.post("/orders/", json=body).status_code == 400


def test_order_rejects_mixed_payment_plans(shop_no_shipping_with_products, test_client):
    ids = shop_no_shipping_with_products
    response = test_client.post(
        "/orders/",
        json=_order_body(
            ids["shop_id"],
            [
                {"product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 1, "plan": "onetime"},
                {"product_id": str(ids["p2"]), "product_name": "Item 2", "quantity": 1, "plan": "monthly"},
            ],
        ),
    )
    assert response.status_code == 422, response.json()


def test_order_customer_ids_increment_per_shop(shop_no_shipping_with_products, test_client):
    ids = shop_no_shipping_with_products
    body = _order_body(
        ids["shop_id"],
        [{"product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 1}],
    )
    first = test_client.post("/orders/", json=body)
    second = test_client.post("/orders/", json=body)

    assert first.status_code == 201, first.json()
    assert second.status_code == 201, second.json()
    assert first.json()["customer_order_id"] == 1
    assert second.json()["customer_order_id"] == 2


def test_patch_order_sets_completed_at(shop_no_shipping_with_products, test_client):
    ids = shop_no_shipping_with_products
    response = test_client.post(
        "/orders/",
        json=_order_body(
            ids["shop_id"],
            [{"product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 1}],
        ),
    )
    assert response.status_code == 201, response.json()

    response = test_client.patch(f"/orders/{response.json()['id']}", json={"status": "cancelled"})
    assert response.status_code == 201, response.json()

    order = db.session.get(OrderTable, response.json()["id"])
    assert order.status == "cancelled"
    assert order.completed_at is not None


def test_create_order_with_shipping_single_rate(shop_shipping_fixed_with_products, test_client):
    ids = shop_shipping_fixed_with_products
    items = [
        {"description": "x", "product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 2},
    ]
    body = _order_body(ids["shop_id"], items)
    response = test_client.post("/orders/", json=body)
    assert response.status_code == 201, response.json()
    j = response.json()
    # fixed_fee=4.95 is ex-VAT; with 21% VAT → 5.99 inc
    assert j["shipping_fee_inc_btw"] == 5.99
    # items_total = 24.20 including VAT; total = 24.20 + 5.99
    assert j["total"] == 30.19


def test_create_order_with_shipping_mixed_vat(shop_shipping_mixed_vat, test_client):
    ids = shop_shipping_mixed_vat
    items = [
        {"description": "x", "product_id": str(ids["p_high"]), "product_name": "Std", "quantity": 1},
        {"description": "x", "product_id": str(ids["p_low"]), "product_name": "Low", "quantity": 1},
    ]
    body = _order_body(ids["shop_id"], items)
    response = test_client.post("/orders/", json=body)
    assert response.status_code == 201, response.json()
    j = response.json()
    # fixed_fee=10.0 ex-VAT is allocated 50/50 across the 100/100 net cart split.
    assert j["shipping_fee_inc_btw"] == 11.5
    assert j["total"] == 241.5


def test_create_order_free_shipping_threshold(shop_shipping_free_above, test_client):
    ids = shop_shipping_free_above
    # Cart total inc-VAT = 72.60, threshold = 50 -> shipping should be 0
    items = [
        {"description": "x", "product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 6},
    ]
    body = _order_body(ids["shop_id"], items)
    response = test_client.post("/orders/", json=body)
    assert response.status_code == 201, response.json()
    j = response.json()
    assert j["shipping_fee_inc_btw"] == 0.0
    assert j["total"] == 72.6


def test_create_order_below_free_shipping_threshold(shop_shipping_free_above, test_client):
    ids = shop_shipping_free_above
    # Cart total inc-VAT = 36.30, threshold = 50 -> shipping should apply
    items = [
        {"description": "x", "product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 3},
    ]
    body = _order_body(ids["shop_id"], items)
    response = test_client.post("/orders/", json=body)
    assert response.status_code == 201, response.json()
    j = response.json()
    # 4.95 ex-VAT @ 21% → 5.99 inc; products are 36.30 inc
    assert j["shipping_fee_inc_btw"] == 5.99
    assert j["total"] == 42.29


def test_create_order_rejects_client_supplied_price(shop_shipping_fixed_with_products, test_client):
    ids = shop_shipping_fixed_with_products
    items = [
        {"description": "x", "price": 0.01, "product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 1},
    ]
    body = _order_body(ids["shop_id"], items)
    response = test_client.post("/orders/", json=body)
    assert response.status_code == 422, response.json()


def test_order_updates_reject_client_prices(shop_no_shipping_with_products, test_client):
    ids = shop_no_shipping_with_products
    response = test_client.post(
        "/orders/",
        json=_order_body(
            ids["shop_id"],
            [{"product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 1}],
        ),
    )
    assert response.status_code == 201, response.json()

    update_response = test_client.patch(f"/orders/{response.json()['id']}", json={"total": 0.01})
    assert update_response.status_code == 422, update_response.json()


@pytest.fixture()
def shop_shipping_vat_bypass_with_products():
    shop_id = make_shop_with_shipping(fixed_fee=5.00, vat_calculation_enabled=False)
    category = make_category(shop_id=shop_id)
    p1 = make_product(shop_id=shop_id, category_id=category, main_name="Item 1", price=10.0)
    return {"shop_id": shop_id, "p1": p1}


def test_create_order_vat_bypass_adds_flat_fee(shop_shipping_vat_bypass_with_products, test_client):
    """With VAT bypass on, configured fee is added to total without VAT calc."""
    ids = shop_shipping_vat_bypass_with_products
    items = [
        {"description": "x", "product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 2},
    ]
    body = _order_body(ids["shop_id"], items)
    response = test_client.post("/orders/", json=body)
    assert response.status_code == 201, response.json()
    j = response.json()
    # Configured 5.00 added flat (no VAT split, no per-rate inflation)
    assert j["shipping_fee_inc_btw"] == 5.0
    assert j["total"] == 29.2


def test_create_order_uses_active_discount_and_persists_gross_price(shop_no_shipping_with_products, test_client):
    ids = shop_no_shipping_with_products
    category = make_category(shop_id=ids["shop_id"])
    product_id = make_product(
        shop_id=ids["shop_id"],
        category_id=category,
        main_name="Discounted",
        price=100.0,
        discounted_price=50.0,
        discounted_from=datetime.now() - timedelta(days=1),
        discounted_to=datetime.now() + timedelta(days=1),
    )
    response = test_client.post(
        "/orders/",
        json=_order_body(
            ids["shop_id"],
            [{"product_id": str(product_id), "product_name": "Discounted", "quantity": 1}],
        ),
    )
    assert response.status_code == 201, response.json()
    order = test_client.get(f"/orders/{response.json()['id']}").json()
    assert order["total"] == 60.5
    assert order["order_info"][0]["price"] == 60.5


def test_create_order_uses_selected_recurring_plan(shop_no_shipping_with_products, test_client):
    ids = shop_no_shipping_with_products
    category = make_category(shop_id=ids["shop_id"])
    product_id = make_product(
        shop_id=ids["shop_id"],
        category_id=category,
        main_name="Subscription",
        price=100.0,
        recurring_price_monthly=10.0,
    )
    response = test_client.post(
        "/orders/",
        json=_order_body(
            ids["shop_id"],
            [{"product_id": str(product_id), "product_name": "Subscription", "quantity": 1, "plan": "monthly"}],
        ),
    )
    assert response.status_code == 201, response.json()
    assert response.json()["total"] == 12.1
