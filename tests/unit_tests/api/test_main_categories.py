from http import HTTPStatus
from uuid import uuid4

import structlog

from server.utils.json import json_dumps

logger = structlog.getLogger(__name__)


def test_main_categories_get_multi(test_client, main_category_1, main_category_2, superuser_token_headers):
    response = test_client.get("/api/main-categories", headers=superuser_token_headers)
    assert HTTPStatus.OK == response.status_code
    main_categories = response.json()
    assert 2 == len(main_categories)


def test_main_category_get_by_id(main_category_2, test_client, superuser_token_headers):
    response = test_client.get(f"/api/main-categories/{main_category_2.id}", headers=superuser_token_headers)
    print(response.__dict__)
    assert HTTPStatus.OK == response.status_code
    main_category = response.json()
    assert main_category["name"] == "Main Category 2"


def test_main_category_get_by_id_404(main_category_1, test_client, superuser_token_headers):
    response = test_client.get(f"/api/main-categories/{str(uuid4())}", headers=superuser_token_headers)
    assert HTTPStatus.NOT_FOUND == response.status_code


def test_main_category_save(test_client, superuser_token_headers, shop_1, main_category_1, main_category_2):
    body = {"name": "New main_category", "icon": "New Icon", "color": "#ffffff", "shop_id": shop_1.id}
    response = test_client.post("/api/main-categories/", data=json_dumps(body), headers=superuser_token_headers)
    assert HTTPStatus.CREATED == response.status_code
    main_categories = test_client.get("/api/main-categories", headers=superuser_token_headers).json()
    assert 3 == len(main_categories)


def test_main_category_update(main_category_1, test_client, superuser_token_headers):
    body = {"name": "Updated main_category", "icon": "moon", "color": "00fff0", "shop_id": main_category_1.shop_id}
    response = test_client.put(
        f"/api/main-categories/{main_category_1.id}", data=json_dumps(body), headers=superuser_token_headers
    )
    assert HTTPStatus.CREATED == response.status_code

    response_updated = test_client.get(f"/api/main-categories/{main_category_1.id}", headers=superuser_token_headers)
    main_category = response_updated.json()
    assert main_category["name"] == "Updated main_category"


def test_main_category_delete(main_category_1, main_category_2, test_client, superuser_token_headers):
    response = test_client.delete(f"/api/main-categories/{main_category_1.id}", headers=superuser_token_headers)
    assert HTTPStatus.NO_CONTENT == response.status_code
    main_categories = test_client.get("/api/main_categories", headers=superuser_token_headers).json()
    assert 1 == len(main_categories)
