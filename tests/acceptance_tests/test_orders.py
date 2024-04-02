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
PRD_SUPERUSER_TOKEN_HEADERS = acceptance_settings.PRD_SUPERUSER_TOKEN_HEADERS


def test_orders_get_multi():
    response_prd = requests.get(
        PRD_BACKEND_URI + "orders/?range=%5B0%2C249%5D", headers=PRD_SUPERUSER_TOKEN_HEADERS
    ).json()
    response_acc = requests.get(ACC_BACKEND_URI + "orders?limit=250", headers=ACC_SUPERUSER_TOKEN_HEADERS).json()

    assert len(response_acc) == len(response_prd)

    orders_differences = get_difference_in_json_list(response_acc, response_prd)
    assert orders_differences == [], print(info_message)
