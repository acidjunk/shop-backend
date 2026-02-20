from server.db import db
from server.db.models import (
    AttributeOptionTable,
    AttributeTable,
    AttributeTranslationTable,
    ProductAttributeValueTable,
)
from tests.unit_tests.factories.attribute import make_attribute, make_option, make_pav


def test_delete_attribute_blocked_by_products(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    attr_id = ids["attr1_id"]
    opt_a_id = ids["opt1a_id"]
    product_id = ids["product_id"]

    # Seed some PAVs
    make_pav(product_id, attr_id, opt_a_id)

    # Perform delete - should fail with 409
    resp = test_client.delete(f"/shops/{shop_id}/attributes/{attr_id}")
    assert resp.status_code == 409
    data = resp.json()
    assert data["detail"]["message"] == "Attribute is in use and cannot be deleted"


def test_delete_attribute_success_no_products(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    attr_id = ids["attr1_id"]

    # In this new implementation, we expect options and translations to stay
    # IF they don't have cascade delete.
    # Actually AttributeTable has cascade="save-update, merge, delete" for options and translation.
    # So they should be deleted automatically by SQLAlchemy when the attribute is deleted.

    # Pre-verification
    assert db.session.query(AttributeTable).filter_by(id=attr_id).first() is not None

    # Perform delete
    resp = test_client.delete(f"/shops/{shop_id}/attributes/{attr_id}")
    assert resp.status_code == 204

    # Post-verification: Attribute should be gone
    assert db.session.query(AttributeTable).filter_by(id=attr_id).first() is None
    # Options and translations should also be gone due to SQLAlchemy cascade
    assert db.session.query(AttributeOptionTable).filter_by(attribute_id=attr_id).count() == 0
    assert db.session.query(AttributeTranslationTable).filter_by(attribute_id=attr_id).count() == 0


def test_delete_attribute_scoping(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    attr_id = ids["attr1_id"]
    other_shop_id = ids["other_shop_id"]

    # Try to delete attribute from wrong shop
    resp = test_client.delete(f"/shops/{other_shop_id}/attributes/{attr_id}")
    assert resp.status_code == 404

    # Ensure it's still there
    assert db.session.query(AttributeTable).filter_by(id=attr_id).first() is not None
