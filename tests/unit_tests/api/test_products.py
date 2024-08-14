from http import HTTPStatus

from server.db.models import ProductTable
from server.utils.json import json_dumps


def test_products_get_multi(shop_with_products, test_client):
    response = test_client.get(f"/shops/{shop_with_products}/products/")
    assert response.status_code == 200
    products = response.json()
    assert 2 == len(products)


def test_products_get_by_id(shop, product, test_client):
    response = test_client.get(f"/shops/{shop}/products/{product}")
    assert response.status_code == 200
    product = response.json()
    assert product["translation"]["main_name"] == "Product for Testing"


def test_products_create(shop, category, test_client):
    body = {
        "shop_id": shop,
        "category_id": category,
        "price": 1.0,
        "tax_category": "vat_zero",
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


def test_products_update(shop, product, category, test_client):
    body = {
        "shop_id": shop,
        "category_id": category,
        "price": 1.0,
        "tax_category": "vat_zero",
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

    response = test_client.put(f"/shops/{shop}/products/{product}", data=json_dumps(body))
    assert response.status_code == 201
    product = ProductTable.query.filter_by(id=product).first()
    assert product.translation.main_name == "Update Product Test"
    assert product.translation.alt1_name == None


def test_products_delete(shop, product, test_client):
    response = test_client.delete(f"/shops/{shop}/products/{product}")
    assert response.status_code == 204
