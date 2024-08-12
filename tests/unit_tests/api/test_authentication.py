import re
import uuid

import pytest

EXCLUDED_ENDPOINTS = [
    {"path": "/reset-password/", "name": "reset_password", "method": "POST"},
    {"path": "/health/", "name": "get_health", "method": "GET"},
    {"path": "/products/", "name": "get_multi", "method": "GET"},
    {"path": "/products/{id}/", "name": "get_id", "method": "GET"},
    {"path": "/shops/{shop_id}/prices/", "name": "get_products", "method": "GET"},
    {"path": "/shops/{shop_id}/prices/", "name": "get_cart_products", "method": "POST"},
    {"path": "/orders/", "name": "create", "method": "POST"},
]


def get_endpoints(fastapi_app):
    url_list = []
    for route in fastapi_app.routes:
        if hasattr(route, "methods"):
            if str(route.path).endswith("/"):
                url_list.append({"path": route.path, "name": route.name, "method": list(route.methods)[0]})
    return url_list


def test_endpoint_auth(test_client):
    responses = []
    for endpoint in get_endpoints(fastapi_app=test_client.app):
        if endpoint not in EXCLUDED_ENDPOINTS:
            if endpoint["method"] == "GET":
                if re.search("{.*}", endpoint["path"]):
                    url_with_uuid = re.sub("{.*}", str(uuid.uuid4()), endpoint["path"])
                    responses.append(test_client.get(f"{url_with_uuid}"))
                else:
                    responses.append(test_client.get(f"{endpoint['path']}"))
            elif endpoint["method"] == "POST":
                responses.append(test_client.post(f"{endpoint['path']}"))
            elif endpoint["method"] == "PUT":
                url_with_uuid = re.sub("{.*}", str(uuid.uuid4()), endpoint["path"])
                responses.append(test_client.put(f"{url_with_uuid}"))
            elif endpoint["method"] == "DELETE":
                url_with_uuid = re.sub("{.*}", str(uuid.uuid4()), endpoint["path"])
                responses.append(test_client.delete(f"{url_with_uuid}"))

    not_401_responses = []

    for response in responses:
        if response.status_code != 401:
            not_401_responses.append(response)

    assert (
        len(not_401_responses) == 0
    ), f"These response where not behind security: {[(i.request.method, i.url) for i in not_401_responses]}"
