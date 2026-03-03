from http import HTTPStatus

from server.db.models import ProductTable, ShopTable
from server.utils.json import json_dumps


def test_update_shop_defaults(test_client, shop):
    # Update defaults
    defaults_body = {"tax_category": "vat_lower_1", "shippable": False}
    response = test_client.put(f"/shops/{shop}/defaults", data=json_dumps(defaults_body))
    assert response.status_code == HTTPStatus.CREATED

    # Verify shop config updated
    updated_shop = ShopTable.query.get(shop)
    assert updated_shop.config["defaults"]["tax_category"] == "vat_lower_1"
    assert updated_shop.config["defaults"]["shippable"] == False


def test_product_creation_uses_fallback_defaults_no_default_set(test_client, shop, category):
    # 1. Create product without specifying tax_category and shippable
    product_body = {
        "shop_id": str(shop),
        "category_id": str(category),
        "price": 10.0,
        "max_one": False,
        "featured": False,
        "new_product": True,
        "translation": {
            "main_name": "Defaulted Product",
            "main_description": "Description",
            "main_description_short": "Short",
        },
        "image_1": "",
        "image_2": "",
        "image_3": "",
        "image_4": "",
        "image_5": "",
        "image_6": "",
    }

    response = test_client.post(f"/shops/{shop}/products/", data=json_dumps(product_body))
    assert response.status_code == HTTPStatus.CREATED

    product_id = response.json()["id"]
    product = ProductTable.query.get(product_id)

    # 3. Verify defaults were applied
    assert product.tax_category == "vat_standard"
    assert product.shippable == True


def test_product_creation_uses_defaults(test_client, shop, category):
        # 1. Set defaults for the shop
        defaults_body = {"tax_category": "vat_special", "shippable": False}
        test_client.put(f"/shops/{shop}/defaults", data=json_dumps(defaults_body))

        # 2. Create product without specifying tax_category and shippable
        product_body = {
            "shop_id": str(shop),
            "category_id": str(category),
            "price": 10.0,
            "max_one": False,
            "featured": False,
            "new_product": True,
            "translation": {
                "main_name": "Defaulted Product",
                "main_description": "Description",
                "main_description_short": "Short",
            },
            "image_1": "",
            "image_2": "",
            "image_3": "",
            "image_4": "",
            "image_5": "",
            "image_6": "",
        }

        response = test_client.post(f"/shops/{shop}/products/", data=json_dumps(product_body))
        assert response.status_code == HTTPStatus.CREATED

        product_id = response.json()["id"]
        product = ProductTable.query.get(product_id)

        # 3. Verify defaults were applied
        assert product.tax_category == "vat_special"
        assert product.shippable == False


def test_product_creation_overrides_defaults(test_client, shop, category):
    # 1. Set defaults for the shop
    defaults_body = {"tax_category": "vat_special", "shippable": False}
    test_client.put(f"/shops/{shop}/defaults", data=json_dumps(defaults_body))

    # 2. Create product specifying tax_category and shippable
    product_body = {
        "shop_id": str(shop),
        "category_id": str(category),
        "price": 10.0,
        "max_one": False,
        "shippable": True,
        "featured": False,
        "new_product": True,
        "tax_category": "vat_zero",
        "translation": {
            "main_name": "Overridden Product",
            "main_description": "Description",
            "main_description_short": "Short",
        },
        "image_1": "",
        "image_2": "",
        "image_3": "",
        "image_4": "",
        "image_5": "",
        "image_6": "",
    }

    response = test_client.post(f"/shops/{shop}/products/", data=json_dumps(product_body))
    assert response.status_code == HTTPStatus.CREATED

    product_id = response.json()["id"]
    product = ProductTable.query.get(product_id)

    # 3. Verify provided values were used instead of defaults
    assert product.tax_category == "vat_zero"
    assert product.shippable == True
