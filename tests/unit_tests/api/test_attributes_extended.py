from http import HTTPStatus
from uuid import uuid4

from server.db import db
from server.db.models import AttributeOptionTable, AttributeTable


def test_get_attributes_with_options(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]

    resp = test_client.get(f"/shops/{shop_id}/attributes/with-options")
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert len(data) >= 2

    # Check if options are present
    attr1 = next(a for a in data if a["id"] == str(ids["attr1_id"]))
    assert len(attr1["options"]) >= 1
    assert "value_key" in attr1["options"][0]


def test_get_attribute_by_id(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    attr_id = ids["attr1_id"]

    resp = test_client.get(f"/shops/{shop_id}/attributes/id/{attr_id}")
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["id"] == str(attr_id)


def test_create_attribute(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]

    new_attr = {"name": "Material", "unit": "string"}
    resp = test_client.post(f"/shops/{shop_id}/attributes/", json=new_attr)
    assert resp.status_code == HTTPStatus.CREATED

    # Verify in DB
    attr = db.session.query(AttributeTable).filter_by(shop_id=shop_id, name="Material").first()
    assert attr is not None
    assert attr.unit == "string"


def test_create_attribute_duplicate(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    attr_name = "Color"  # Likely exists in shop_with_products_and_attributes

    # First ensure it exists
    existing = db.session.query(AttributeTable).filter_by(shop_id=shop_id, name=attr_name).first()
    if not existing:
        # If "Color" doesn't exist, use one that does
        existing = db.session.query(AttributeTable).filter_by(shop_id=shop_id).first()
        attr_name = existing.name

    new_attr = {"name": attr_name, "unit": "string"}
    resp = test_client.post(f"/shops/{shop_id}/attributes/", json=new_attr)
    assert resp.status_code == HTTPStatus.CONFLICT


def test_update_attribute(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    attr_id = ids["attr1_id"]

    update_data = {
        "name": "Updated Name",
        "unit": "cm",
        "shop_id": str(shop_id),
        "translation": {"main_name": "Updated Name"},
    }
    resp = test_client.put(f"/shops/{shop_id}/attributes/{attr_id}", json=update_data)
    assert resp.status_code == HTTPStatus.OK

    # Verify
    attr = db.session.query(AttributeTable).filter_by(id=attr_id).first()
    assert attr.name == "Updated Name"
    assert attr.unit == "cm"


def test_get_attribute_by_id_with_options(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    attr_id = ids["attr1_id"]

    # This endpoint doesn't exist yet
    resp = test_client.get(f"/shops/{shop_id}/attributes/id/{attr_id}/with-options")
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["id"] == str(attr_id)
    assert "options" in data
    assert len(data["options"]) > 0


def test_get_attribute_by_id_with_options_direct(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    attr_id = ids["attr1_id"]

    resp = test_client.get(f"/shops/{shop_id}/attributes/{attr_id}/with-options")
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["id"] == str(attr_id)
    assert "options" in data
    assert len(data["options"]) > 0
