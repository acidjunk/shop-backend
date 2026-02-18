from server.utils.json import json_dumps


def test_post_create_product_attribute_values_for_product_duplicate_conflict(
    test_client, shop_with_products_and_attributes
):
    ids = shop_with_products_and_attributes

    body = {"option_ids": [str(ids["opt1a_id"])]}

    # First creation should succeed
    resp1 = test_client.post(
        f"/shops/{ids['shop_id']}/product-attribute-values/{ids['product_id']}",
        data=json_dumps(body),
    )
    assert resp1.status_code == 201

    # Second, identical creation should be rejected with 409 Conflict
    resp2 = test_client.post(
        f"/shops/{ids['shop_id']}/product-attribute-values/{ids['product_id']}",
        data=json_dumps(body),
    )
    assert resp2.status_code == 409


def test_post_deprecated_create_product_attribute_value_duplicate_conflict(
    test_client, shop_with_products_and_attributes
):
    ids = shop_with_products_and_attributes

    # First create via deprecated endpoint
    body = {
        "product_id": str(ids["product_id"]),
        "attribute_id": str(ids["attr1_id"]),
        "option_id": str(ids["opt1a_id"]),
    }
    resp1 = test_client.post(
        f"/shops/{ids['shop_id']}/product-attribute-values/",
        data=json_dumps(body),
    )
    assert resp1.status_code == 201

    # Duplicate via the same endpoint should return 409
    resp2 = test_client.post(
        f"/shops/{ids['shop_id']}/product-attribute-values/",
        data=json_dumps(body),
    )
    assert resp2.status_code == 409
