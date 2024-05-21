from urllib.request import urlopen

import requests
from deepdiff import DeepDiff  # For finding if item exists in an object; For Deep Difference of 2 objects
from deepdiff import DeepHash  # For hashing objects based on their contents
from deepdiff import DeepSearch, grep

from server.utils.json import json_dumps
from tests.acceptance_tests.acceptance_settings import acceptance_settings
from tests.acceptance_tests.helpers import get_difference_in_json_list, info_message

PRD_BACKEND_URI = acceptance_settings.PRD_BACKEND_URI
ACC_BACKEND_URI = acceptance_settings.ACC_BACKEND_URI
ACC_SUPERUSER_TOKEN_HEADERS = acceptance_settings.ACC_SUPERUSER_TOKEN_HEADERS

test_product_id = "087a7a49-3298-49b3-b24f-10a6d8e11c7d"


def test_products_get_multi():
    response_prd = requests.get(PRD_BACKEND_URI + "products/?range=%5B0%2C249%5D").json()
    response_acc = requests.get(ACC_BACKEND_URI + "products?limit=250", headers=ACC_SUPERUSER_TOKEN_HEADERS).json()

    assert len(response_acc) == len(response_prd)

    kinds_differences = get_difference_in_json_list(response_acc, response_prd)
    assert kinds_differences == [], print(info_message)


def test_products_get_by_id():
    response_prd = requests.get(PRD_BACKEND_URI + f"products/{test_product_id}").json()
    response_acc = requests.get(ACC_BACKEND_URI + f"products/{test_product_id}").json()
    ddiff = DeepDiff(response_acc, response_prd, ignore_order=True)
    assert ddiff == {}, print(info_message)


def test_products_without_shop():
    response_multi_prd = requests.get(PRD_BACKEND_URI + "products/?range=%5B0%2C249%5D").json()
    response_multi_acc = requests.get(
        ACC_BACKEND_URI + "products?limit=250", headers=ACC_SUPERUSER_TOKEN_HEADERS
    ).json()
    products_ids = []
    ddiff = DeepDiff(response_multi_acc, response_multi_prd, ignore_order=True)
    assert ddiff == {}
    for product in response_multi_prd:
        products_ids.append(product["id"])

    for product_id in products_ids:
        response_prd = requests.get(PRD_BACKEND_URI + f"products/{product_id}").json()
        response_acc = requests.get(ACC_BACKEND_URI + f"products/{product_id}").json()
        acc_prices = response_acc["prices"]
        prd_prices = response_prd["prices"]

        assert len(acc_prices) == len(prd_prices)

        prices_differences = get_difference_in_json_list(acc_list=acc_prices, prd_list=prd_prices)

        assert prices_differences == [], print(info_message)


def test_products_with_shop():
    response_multi_prd = requests.get(PRD_BACKEND_URI + "shop_endpoints-to-prices").json()
    shops_with_products_ids = []

    for shop_to_price in response_multi_prd:
        if shop_to_price["product_id"] is not None:
            shops_with_products_ids.append(
                dict(shop_id=shop_to_price["shop_id"], product_id=shop_to_price["product_id"])
            )

    for item in shops_with_products_ids:
        response_prd = requests.get(PRD_BACKEND_URI + f"products/{item['product_id']}/?shop={item['shop_id']}").json()
        response_acc = requests.get(ACC_BACKEND_URI + f"products/{item['product_id']}/?shop={item['shop_id']}").json()

        acc_prices = response_acc["prices"]
        prd_prices = response_prd["prices"]

        assert len(acc_prices) == len(prd_prices)

        prices_differences = get_difference_in_json_list(acc_list=acc_prices, prd_list=prd_prices)

        assert prices_differences == [], print(info_message)
