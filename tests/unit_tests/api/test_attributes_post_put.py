from http import HTTPStatus

from server.db import db
from server.db.models import AttributeTable


def test_create_attribute_fixed(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]

    new_attr = {"name": "Test Attribute", "unit": "kg"}
    resp = test_client.post(f"/shops/{shop_id}/attributes/", json=new_attr)
    assert resp.status_code == HTTPStatus.CREATED
    data = resp.json()
    assert data["name"] == "Test Attribute"
    assert data["unit"] == "kg"

    # Verify in DB
    attr = db.session.query(AttributeTable).filter_by(shop_id=shop_id, name="Test Attribute").first()
    assert attr is not None
    assert attr.unit == "kg"


def test_update_attribute_empty_body(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    attr_id = ids["attr1_id"]

    # Original data
    attr_before = db.session.query(AttributeTable).get(attr_id)
    name_before = attr_before.name
    unit_before = attr_before.unit

    # Empty body update
    resp = test_client.put(f"/shops/{shop_id}/attributes/{attr_id}", json={})
    assert resp.status_code == HTTPStatus.OK

    # Should remain unchanged
    attr_after = db.session.query(AttributeTable).get(attr_id)
    assert attr_after.name == name_before
    assert attr_after.unit == unit_before


def test_update_attribute_valid_data(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    attr_id = ids["attr1_id"]

    update_data = {"name": "New Name", "unit": "new unit"}
    resp = test_client.put(f"/shops/{shop_id}/attributes/{attr_id}", json=update_data)
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["name"] == "New Name"
    assert data["unit"] == "new unit"

    # Verify in DB
    attr = db.session.query(AttributeTable).get(attr_id)
    assert attr.name == "New Name"
    assert attr.unit == "new unit"
