from urllib.request import urlopen

import requests
from deepdiff import DeepDiff  # For Deep Difference of 2 objects
from deepdiff import DeepHash  # For hashing objects based on their contents
from deepdiff import DeepSearch, grep  # For finding if item exists in an object

from server.utils.json import json_dumps
from tests.acceptance_tests.acceptance_settings import acceptance_settings
from tests.acceptance_tests.helpers import get_difference_in_json_list, info_message

PRD_BACKEND_URI = acceptance_settings.PRD_BACKEND_URI
ACC_BACKEND_URI = acceptance_settings.ACC_BACKEND_URI
ACC_SUPERUSER_TOKEN_HEADERS = acceptance_settings.ACC_SUPERUSER_TOKEN_HEADERS


test_kind_id = "0097d977-7e43-4acc-adc6-186f54b4c495"


def test_kinds_get_by_id():
    response_prd = requests.get(PRD_BACKEND_URI + f"kinds/{test_kind_id}").json()
    response_acc = requests.get(ACC_BACKEND_URI + f"kinds/{test_kind_id}").json()
    ddiff = DeepDiff(response_acc, response_prd, ignore_order=True)
    assert ddiff == {}, print(info_message)


def test_kinds_get_multi():
    response_prd = requests.get(PRD_BACKEND_URI + "kinds/?range=%5B0%2C250%5D&sort=%5B%22name%22%2C%22ASC%22%5D").json()
    response_acc = requests.get(
        ACC_BACKEND_URI + "kinds?skip=0&limit=250&sort=name%3AASC", headers=ACC_SUPERUSER_TOKEN_HEADERS
    ).json()

    assert len(response_acc) == len(response_prd)

    kinds_differences = get_difference_in_json_list(response_acc, response_prd)
    assert kinds_differences == [], print(info_message)


def test_kinds_without_shop():
    response_multi_prd = requests.get(PRD_BACKEND_URI + "kinds/?range=%5B0%2C249%5D").json()
    kinds_ids = []
    for kind in response_multi_prd:
        kinds_ids.append(kind["id"])

    for kind_id in kinds_ids:
        response_prd = requests.get(PRD_BACKEND_URI + f"kinds/{kind_id}").json()
        response_acc = requests.get(ACC_BACKEND_URI + f"kinds/{kind_id}").json()
        acc_tags = response_acc["tags"]
        prd_tags = response_prd["tags"]
        acc_flavors = response_acc["flavors"]
        prd_flavors = response_prd["flavors"]
        acc_strains = response_acc["strains"]
        prd_strains = response_prd["strains"]
        acc_prices = response_acc["prices"]
        prd_prices = response_prd["prices"]

        assert len(acc_tags) == len(prd_tags)
        assert len(acc_flavors) == len(prd_flavors)
        assert len(acc_strains) == len(prd_strains)
        assert len(acc_prices) == len(prd_prices)

        tags_differences = get_difference_in_json_list(acc_list=acc_tags, prd_list=prd_tags)
        flavors_differences = get_difference_in_json_list(acc_list=acc_flavors, prd_list=prd_flavors)
        strains_differences = get_difference_in_json_list(acc_list=acc_strains, prd_list=prd_strains)
        prices_differences = get_difference_in_json_list(acc_list=acc_prices, prd_list=prd_prices)

        assert tags_differences == [], print(info_message)
        assert flavors_differences == [], print(info_message)
        assert strains_differences == [], print(info_message)
        assert prices_differences == [], print(info_message)


def test_kinds_with_shop():
    response_multi_prd = requests.get(PRD_BACKEND_URI + "shop_endpoints-to-prices").json()
    shops_with_kinds_ids = []

    for shop_to_price in response_multi_prd:
        if shop_to_price["kind_id"] is not None:
            shops_with_kinds_ids.append(dict(shop_id=shop_to_price["shop_id"], kind_id=shop_to_price["kind_id"]))

    for item in shops_with_kinds_ids:
        response_prd = requests.get(PRD_BACKEND_URI + f"kinds/{item['kind_id']}?shop={item['shop_id']}").json()
        response_acc = requests.get(ACC_BACKEND_URI + f"kinds/{item['kind_id']}?shop={item['shop_id']}").json()

        acc_tags = response_acc["tags"]
        prd_tags = response_prd["tags"]
        acc_flavors = response_acc["flavors"]
        prd_flavors = response_prd["flavors"]
        acc_strains = response_acc["strains"]
        prd_strains = response_prd["strains"]
        acc_prices = response_acc["prices"]
        prd_prices = response_prd["prices"]

        assert len(acc_tags) == len(prd_tags)
        assert len(acc_flavors) == len(prd_flavors)
        assert len(acc_strains) == len(prd_strains)
        assert len(acc_prices) == len(prd_prices)

        tags_differences = get_difference_in_json_list(acc_list=acc_tags, prd_list=prd_tags)
        flavors_differences = get_difference_in_json_list(acc_list=acc_flavors, prd_list=prd_flavors)
        strains_differences = get_difference_in_json_list(acc_list=acc_strains, prd_list=prd_strains)
        prices_differences = get_difference_in_json_list(acc_list=acc_prices, prd_list=prd_prices)

        assert tags_differences == [], print(info_message)
        assert flavors_differences == [], print(info_message)
        assert strains_differences == [], print(info_message)
        assert prices_differences == [], print(info_message)
