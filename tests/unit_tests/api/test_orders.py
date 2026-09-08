import pytest

from tests.unit_tests.factories.categories import make_category
from tests.unit_tests.factories.product import make_product
from tests.unit_tests.factories.shop import make_shop_with_shipping

# --- Filtering orders by the product they contain -----------------------------------
#
# Order lines live in the `order_info` JSONB array, so a product is not reachable
# through the generic `filter` parameter (that matches columns of OrderTable only).
# `product_id` does a JSONB containment match instead.


def test_orders_filter_by_product_returns_only_matching(shop, pending_order, test_client):
    """The fixture order contains two products; a third product matches nothing."""
    contained = str(pending_order.order_info[0]["product_id"])
    category = make_category(shop_id=shop)
    absent = make_product(shop_id=shop, category_id=category, main_name="Never ordered")

    hit = test_client.get(f"/orders/?product_id={contained}")
    assert hit.status_code == 200
    assert [o["id"] for o in hit.json()] == [str(pending_order.id)]

    miss = test_client.get(f"/orders/?product_id={absent}")
    assert miss.status_code == 200
    assert miss.json() == []


def test_orders_filter_by_product_counts_a_multiline_order_once(shop, pending_order, test_client):
    """Either line of a two-product order resolves to the same single order."""
    first, second = (str(line["product_id"]) for line in pending_order.order_info[:2])
    assert first != second
    for product_id in (first, second):
        resp = test_client.get(f"/orders/?product_id={product_id}")
        assert resp.status_code == 200
        assert [o["id"] for o in resp.json()] == [str(pending_order.id)]


def test_orders_without_product_id_is_unchanged(shop, pending_order, test_client):
    """Omitting the parameter must not narrow anything."""
    unfiltered = test_client.get("/orders/")
    assert unfiltered.status_code == 200
    assert len(unfiltered.json()) == 1


def test_pending_orders_filter_by_product(shop, pending_order, test_client):
    contained = str(pending_order.order_info[0]["product_id"])
    resp = test_client.get(f"/orders/shop/{shop}/pending?product_id={contained}")
    assert resp.status_code == 200
    assert [o["id"] for o in resp.json()] == [str(pending_order.id)]

    other_shop = make_shop_with_shipping()
    scoped_out = test_client.get(f"/orders/shop/{other_shop}/pending?product_id={contained}")
    assert scoped_out.status_code == 200
    assert scoped_out.json() == [], "product filter must not escape the shop scope"


def test_complete_orders_filter_by_product(shop, pending_order, test_client):
    from server.db import db

    contained = str(pending_order.order_info[0]["product_id"])

    # The order is still pending, so the complete/cancelled feed must not return it
    # however the product filter is applied.
    assert test_client.get(f"/orders/shop/{shop}/complete?product_id={contained}").json() == []

    pending_order.status = "complete"
    db.session.commit()

    resp = test_client.get(f"/orders/shop/{shop}/complete?product_id={contained}")
    assert resp.status_code == 200
    assert [o["id"] for o in resp.json()] == [str(pending_order.id)]

    assert test_client.get(f"/orders/shop/{shop}/pending?product_id={contained}").json() == []


def test_orders_filter_by_product_composes_with_status_filter(shop, pending_order, test_client):
    contained = str(pending_order.order_info[0]["product_id"])
    match = test_client.get(f"/orders/?product_id={contained}&filter=status:pending")
    assert match.status_code == 200
    assert len(match.json()) == 1

    miss = test_client.get(f"/orders/?product_id={contained}&filter=status:complete")
    assert miss.status_code == 200
    assert miss.json() == []


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


def _order_body(shop_id, items, total=0.0):
    body = {
        "shop_id": str(shop_id),
        "order_info": items,
        "account_name": f"buyer-{shop_id}@example.com",
        "notes": "test",
        "status": "pending",
        "customer_order_id": 1,
        "total": total,
    }
    return body


def test_create_order_no_shipping(shop_no_shipping_with_products, test_client):
    ids = shop_no_shipping_with_products
    items = [
        {"description": "x", "price": 10.0, "product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 2},
        {"description": "x", "price": 20.0, "product_id": str(ids["p2"]), "product_name": "Item 2", "quantity": 1},
    ]
    body = _order_body(ids["shop_id"], items, total=999.0)
    response = test_client.post("/orders/", json=body)
    assert response.status_code == 201, response.json()
    j = response.json()
    assert j["shipping_fee_inc_btw"] is None
    # items_total = 10*2 + 20*1 = 40; client-sent total ignored
    assert j["total"] == 40.0


def test_create_order_with_shipping_single_rate(shop_shipping_fixed_with_products, test_client):
    ids = shop_shipping_fixed_with_products
    items = [
        {"description": "x", "price": 10.0, "product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 2},
    ]
    body = _order_body(ids["shop_id"], items)
    response = test_client.post("/orders/", json=body)
    assert response.status_code == 201, response.json()
    j = response.json()
    # fixed_fee=4.95 is ex-VAT; with 21% VAT → 5.99 inc
    assert j["shipping_fee_inc_btw"] == 5.99
    # items_total = 20; total = 20 + 5.99
    assert j["total"] == 25.99


def test_create_order_with_shipping_mixed_vat(shop_shipping_mixed_vat, test_client):
    ids = shop_shipping_mixed_vat
    items = [
        {"description": "x", "price": 100.0, "product_id": str(ids["p_high"]), "product_name": "Std", "quantity": 1},
        {"description": "x", "price": 100.0, "product_id": str(ids["p_low"]), "product_name": "Low", "quantity": 1},
    ]
    body = _order_body(ids["shop_id"], items)
    response = test_client.post("/orders/", json=body)
    assert response.status_code == 201, response.json()
    j = response.json()
    # fixed_fee=10.0 ex-VAT split 50/50 → 5*1.21 + 5*1.09 = 11.50 inc
    assert j["shipping_fee_inc_btw"] == 11.5
    # items_total = 200; total = 200 + 11.50
    assert j["total"] == 211.5


def test_create_order_free_shipping_threshold(shop_shipping_free_above, test_client):
    ids = shop_shipping_free_above
    # Cart total inc-VAT = 60, threshold = 50 -> shipping should be 0
    items = [
        {"description": "x", "price": 10.0, "product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 6},
    ]
    body = _order_body(ids["shop_id"], items)
    response = test_client.post("/orders/", json=body)
    assert response.status_code == 201, response.json()
    j = response.json()
    assert j["shipping_fee_inc_btw"] == 0.0
    assert j["total"] == 60.0


def test_create_order_below_free_shipping_threshold(shop_shipping_free_above, test_client):
    ids = shop_shipping_free_above
    # Cart total inc-VAT = 30, threshold = 50 -> shipping should apply
    items = [
        {"description": "x", "price": 10.0, "product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 3},
    ]
    body = _order_body(ids["shop_id"], items)
    response = test_client.post("/orders/", json=body)
    assert response.status_code == 201, response.json()
    j = response.json()
    # 4.95 ex-VAT @ 21% → 5.99 inc
    assert j["shipping_fee_inc_btw"] == 5.99
    assert j["total"] == 35.99


def test_create_order_client_total_overridden(shop_shipping_fixed_with_products, test_client):
    ids = shop_shipping_fixed_with_products
    items = [
        {"description": "x", "price": 10.0, "product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 1},
    ]
    body = _order_body(ids["shop_id"], items, total=1.0)
    response = test_client.post("/orders/", json=body)
    assert response.status_code == 201, response.json()
    j = response.json()
    # Client sent total=1.0 but server should override with items + shipping = 10 + 5.99
    assert j["total"] == 15.99
    assert j["shipping_fee_inc_btw"] == 5.99


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
        {"description": "x", "price": 10.0, "product_id": str(ids["p1"]), "product_name": "Item 1", "quantity": 2},
    ]
    body = _order_body(ids["shop_id"], items)
    response = test_client.post("/orders/", json=body)
    assert response.status_code == 201, response.json()
    j = response.json()
    # Configured 5.00 added flat (no VAT split, no per-rate inflation)
    assert j["shipping_fee_inc_btw"] == 5.0
    assert j["total"] == 25.0
