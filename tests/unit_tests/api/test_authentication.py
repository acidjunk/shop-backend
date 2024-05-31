import re
import uuid

import pytest

EXCLUDED_ENDPOINTS = [
    {"path": "/api/reset-password/", "name": "reset_password", "method": "POST"},
    {"path": "/api/health/", "name": "get_health", "method": "GET"},
    {"path": "/api/health/ping/", "name": "pong", "method": "GET"},
    {"path": "/api/kinds/", "name": "get_multi", "method": "GET"},
    {"path": "/api/kinds/{id}/", "name": "get_id", "method": "GET"},
    {"path": "/api/products/", "name": "get_multi", "method": "GET"},
    {"path": "/api/products/{id}/", "name": "get_id", "method": "GET"},
    {"path": "/api/shop_endpoints/{id}/", "name": "get_id", "method": "GET"},
    {"path": "/api/shop_endpoints/cache-status/{id}/", "name": "get_cache_status", "method": "GET"},
    {"path": "/api/shop_endpoints/last-completed-order/{id}/", "name": "get_last_completed_order", "method": "GET"},
    {"path": "/api/shop_endpoints/last-pending-order/{id}/", "name": "get_last_pending_order", "method": "GET"},
    {"path": "/api/shop_endpoints-to-prices/", "name": "get_multi", "method": "GET"},
    {"path": "/api/shop_endpoints-to-prices/{id}/", "name": "get_id", "method": "GET"},
    {"path": "/api/orders/check/{ids}/", "name": "check", "method": "GET"},
    {"path": "/api/orders/", "name": "create", "method": "POST"},
    {"path": "/api/chat/", "name": "get", "method": "GET"},
    {"path": "/api/images/signed-url/{image_name}/", "name": "get_signed_url", "method": "GET"},
    {"path": "/api/images/move/", "name": "move_images", "method": "POST"},
    {"path": "/api/images/delete-temp/", "name": "delete_temporary_images", "method": "POST"},
    {"path": "/api/downloads/{file_name}/", "name": "get_signed_download_link", "method": "GET"},
    {"path": "/api/downloads/send/", "name": "send_download_link_via_email", "method": "POST"},
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
