from http import HTTPStatus

from server.db.models import ProductTable
from server.utils.json import json_dumps


def test_products_get_multi(shop_with_products, test_client):
    response = test_client.get(f"/shops/{shop_with_products}/products/")
    assert response.status_code == 200
    products = response.json()
    assert 2 == len(products)


def test_products_get_by_id(shop_with_config, product, test_client):
    response = test_client.get(f"/shops/{shop_with_config}/products/{product}")
    assert response.status_code == 200
    product = response.json()
    assert product["translation"]["main_name"] == "Product for Testing"


def test_products_create(shop, category, test_client):
    body = {
        "shop_id": shop,
        "category_id": category,
        "price": 1.0,
        "tax_category": "vat_zero",
        "max_one": False,
        "shippable": True,
        "featured": False,
        "new_product": False,
        "translation": {
            "main_name": "Create Product Test",
            "main_description": "Update Product Test Description",
            "main_description_short": "Update Product Test Description Short",
            "alt1_name": "",
        },
        "image_1": "",
        "image_2": "",
        "image_3": "",
        "image_4": "",
        "image_5": "",
        "image_6": "",
    }

    response = test_client.post(f"/shops/{shop}/products/", data=json_dumps(body))
    assert HTTPStatus.CREATED == response.status_code, f"No 201 status code: full response {response.json()}"
    product = ProductTable.query.filter_by(id=response.json()["id"]).first()
    assert product.translation.main_name == "Create Product Test"
    assert product.translation.alt1_name == None


def test_products_update(shop_with_config, product, category, test_client):
    body = {
        "shop_id": shop_with_config,
        "category_id": category,
        "price": 1.0,
        "tax_category": "vat_zero",
        "max_one": False,
        "shippable": True,
        "featured": False,
        "new_product": False,
        "translation": {
            "main_name": "Update Product Test",
            "main_description": "Update Product Test Description",
            "main_description_short": "Update Product Test Description Short",
        },
        "image_1": "",
        "image_2": "",
        "image_3": "",
        "image_4": "",
        "image_5": "",
        "image_6": "",
    }

    response = test_client.put(f"/shops/{shop_with_config}/products/{product}", data=json_dumps(body))
    assert response.status_code == 201
    product = ProductTable.query.filter_by(id=product).first()
    assert product.translation.main_name == "Update Product Test"
    assert product.translation.alt1_name == None


def test_products_delete(shop_with_config, product, test_client):
    response = test_client.delete(f"/shops/{shop_with_config}/products/{product}")
    assert response.status_code == 204


def test_products_get_multi_with_attributes(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]

    response = test_client.get(f"/shops/{shop_id}/products/with_attributes")
    assert response.status_code == 200
    products = response.json()
    assert len(products) > 0
    assert "product" in products[0]
    assert "attributes" in products[0]
    
    # Verify that the response contains the expected product ID
    product_ids = {p["product"]["id"] for p in products}
    assert str(ids["product_id"]) in product_ids


def test_products_get_by_id_with_attributes(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    product_id = ids["product_id"]

    response = test_client.get(f"/shops/{shop_id}/products/{product_id}/with_attributes")
    assert response.status_code == 200
    product = response.json()
    assert "product" in product
    assert "attributes" in product
    assert product["product"]["id"] == str(product_id)


def test_products_get_multi_with_attributes_filtered_by_option(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    product_id = ids["product_id"]
    opt1a_id = ids["opt1a_id"]
    attr1_id = ids["attr1_id"]

    # First, we need to create a ProductAttributeValue (PAV) to associate the option with the product
    from tests.unit_tests.factories.attribute import make_pav

    make_pav(product_id, attr1_id, opt1a_id)

    # Filter by option_id
    response = test_client.get(f"/shops/{shop_id}/products/with_attributes?option_id={opt1a_id}")
    assert response.status_code == 200
    products = response.json()
    assert len(products) == 1
    assert products[0]["product"]["id"] == str(product_id)

    # Filter by non-existent option_id should return empty list
    from uuid import uuid4

    response = test_client.get(f"/shops/{shop_id}/products/with_attributes?option_id={uuid4()}")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_products_get_multi_with_attributes_mutually_exclusive_filters(test_client, shop_with_products_and_attributes):
    ids = shop_with_products_and_attributes
    shop_id = ids["shop_id"]
    opt1a_id = ids["opt1a_id"]
    attr1_id = ids["attr1_id"]

    # Providing both option_id and attribute_id should fail
    response = test_client.get(f"/shops/{shop_id}/products/with_attributes?option_id={opt1a_id}&attribute_id={attr1_id}")
    assert response.status_code == 400
    assert "Only one filter may be used at a time" in response.json()["detail"]["message"]