from http import HTTPStatus
from uuid import uuid4

from server.db import db
from server.db.models import AttributeOptionTable


def test_list_all_attribute_options_for_shop(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]

    resp = test_client.get(f"/shops/{shop_id}/attribute-options/")
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    # At least opt1a, opt1b, opt2a should be there
    assert len(data) >= 3
    assert all("value_key" in item for item in data)


def test_get_attribute_option_v2(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    option_id = ids["opt1a_id"]

    resp = test_client.get(f"/shops/{shop_id}/attribute-options/{option_id}")
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["id"] == str(option_id)


def test_get_attribute_option_v2_not_found(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    fake_option_id = uuid4()

    resp = test_client.get(f"/shops/{shop_id}/attribute-options/{fake_option_id}")
    assert resp.status_code == HTTPStatus.NOT_FOUND


def test_create_attribute_option_v2(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    attr_id = ids["attr1_id"]

    new_option = {"attribute_id": str(attr_id), "value_key": "NewOptionV2"}
    resp = test_client.post(f"/shops/{shop_id}/attribute-options/", json=new_option)
    assert resp.status_code == HTTPStatus.CREATED
    data = resp.json()
    assert data["value_key"] == "NewOptionV2"
    assert data["attribute_id"] == str(attr_id)

    # Verify in DB
    option = db.session.query(AttributeOptionTable).filter_by(id=data["id"]).first()
    assert option is not None
    assert option.value_key == "NewOptionV2"


def test_update_attribute_option_v2(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    attr_id = ids["attr1_id"]
    option_id = ids["opt1a_id"]

    update_data = {"attribute_id": str(attr_id), "value_key": "UpdatedValueV2"}
    resp = test_client.put(f"/shops/{shop_id}/attribute-options/{option_id}", json=update_data)
    assert resp.status_code == HTTPStatus.OK
    data = resp.json()
    assert data["value_key"] == "UpdatedValueV2"

    # Verify in DB
    option = db.session.query(AttributeOptionTable).filter_by(id=option_id).first()
    assert option.value_key == "UpdatedValueV2"


def test_delete_attribute_option_v2(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    option_id = ids["opt1a_id"]

    resp = test_client.delete(f"/shops/{shop_id}/attribute-options/{option_id}")
    assert resp.status_code == HTTPStatus.NO_CONTENT

    # Verify in DB
    option = db.session.query(AttributeOptionTable).filter_by(id=option_id).first()
    assert option is None


def test_deprecated_list_options(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    attr_id = ids["attr1_id"]

    resp = test_client.get(f"/shops/{shop_id}/attributes/{attr_id}/options/")
    assert resp.status_code == HTTPStatus.OK
