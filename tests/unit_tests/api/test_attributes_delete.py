from server.db import db
from server.db.models import (
    AttributeOptionTable,
    AttributeTable,
    AttributeTranslationTable,
    ProductAttributeValueTable,
)
from tests.unit_tests.factories.attribute import make_pav, make_attribute, make_option

def test_delete_attribute_deep(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    attr_id = ids["attr1_id"]
    opt_a_id = ids["opt1a_id"]
    opt_b_id = ids["opt1b_id"]
    product_id = ids["product_id"]

    # Seed some PAVs
    make_pav(product_id, attr_id, opt_a_id)
    make_pav(product_id, attr_id, opt_b_id)

    # Ensure translation exists (make_attribute currently doesn't create it in factory, 
    # but the API `create` does. Let's manually add it for this test if needed, 
    # or check if it's there.)
    trans = AttributeTranslationTable(attribute_id=attr_id, main_name="Size")
    db.session.add(trans)
    db.session.commit()

    # Pre-verification
    assert db.session.query(AttributeTable).filter_by(id=attr_id).first() is not None
    assert db.session.query(AttributeOptionTable).filter_by(attribute_id=attr_id).count() == 2
    assert db.session.query(ProductAttributeValueTable).filter_by(attribute_id=attr_id).count() == 2
    assert db.session.query(AttributeTranslationTable).filter_by(attribute_id=attr_id).count() == 1

    # Perform delete
    resp = test_client.delete(f"/shops/{shop_id}/attributes/{attr_id}")
    assert resp.status_code == 204

    # Post-verification: All related records should be gone
    assert db.session.query(AttributeTable).filter_by(id=attr_id).first() is None
    assert db.session.query(AttributeOptionTable).filter_by(attribute_id=attr_id).count() == 0
    assert db.session.query(ProductAttributeValueTable).filter_by(attribute_id=attr_id).count() == 0
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
