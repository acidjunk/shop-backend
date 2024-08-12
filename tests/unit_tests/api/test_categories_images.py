# from http import HTTPStatus
# from uuid import uuid4
#
# import pytest
# import structlog
#
# from server.utils.json import json_dumps
#
# logger = structlog.getLogger(__name__)
#
#
# def test_category_image_update(category_3, test_client, superuser_token_headers):
#     body = {
#         "name": "Test Category",
#         "description": "Test Category description",
#         "shop_id": str(category_3.shop_id),
#         "color": "#376E1A",
#         "image_1": "test-category-1-1.png",
#         "image_2": {"src": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA", "title": "new-image.png"},
#     }
#     response = test_client.put(
#         f"/api/categories-images/{category_3.id}", data=json_dumps(body), headers=superuser_token_headers
#     )
#     assert HTTPStatus.CREATED == response.status_code
#
#     response_updated = test_client.get(f"/api/categories/{category_3.id}", headers=superuser_token_headers)
#     category = response_updated.json()
#     assert category["image_2"] == "test-category-2-2.png"
#
#
# def test_category_image_delete(category_3, test_client, superuser_token_headers):
#     body = {"image": "image_2"}
#
#     response = test_client.put(
#         f"/api/categories-images/delete/{category_3.id}", data=json_dumps(body), headers=superuser_token_headers
#     )
#     assert HTTPStatus.CREATED == response.status_code
#
#     response_updated = test_client.get(f"/api/categories/{category_3.id}", headers=superuser_token_headers)
#     category = response_updated.json()
#     assert category["image_2"] is None
