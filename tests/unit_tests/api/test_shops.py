from http import HTTPStatus

from server.utils.json import json_dumps


def test_shops_get_multi(test_client, shop_1, shop_2, superuser_token_headers):
    response = test_client.get(f"/api/shop_endpoints", headers=superuser_token_headers)
    assert response.status_code == 200
    shops = response.json()
    assert 2 == len(shops)


def test_shops_get_multi_with_slash(test_client, shop_1, shop_2, superuser_token_headers):
    response = test_client.get(f"/api/shop_endpoints/", headers=superuser_token_headers)
    assert response.status_code == 200
    shops = response.json()
    assert 2 == len(shops)


def test_shop_get_by_id(shop_1, test_client):
    response = test_client.get(f"/api/shop_endpoints/{shop_1.id}")
    assert HTTPStatus.OK == response.status_code
    shop = response.json()
    assert shop["name"] == "Mississippi"


def test_shop_save(test_client, superuser_token_headers):
    body = {"name": "New Test Shop", "description": "New Test Shop description"}

    response = test_client.post("/api/shop_endpoints/", data=json_dumps(body), headers=superuser_token_headers)
    assert HTTPStatus.CREATED == response.status_code
    shops = test_client.get("/api/shop_endpoints").json()
    assert 1 == len(shops)


def test_shop_update(shop_1, test_client, superuser_token_headers):
    body = {"name": "Updated Shop", "description": "Shop description"}
    response = test_client.put(
        f"/api/shop_endpoints/{shop_1.id}", data=json_dumps(body), headers=superuser_token_headers
    )
    assert HTTPStatus.CREATED == response.status_code

    response_updated = test_client.get(f"/api/shop_endpoints/{shop_1.id}", headers=superuser_token_headers)
    shop = response_updated.json()
    assert shop["name"] == "Updated Shop"


def test_shop_delete(shop_1, test_client, superuser_token_headers):
    response = test_client.delete(f"/api/shop_endpoints/{shop_1.id}", headers=superuser_token_headers)
    assert HTTPStatus.NO_CONTENT == response.status_code
    shops = test_client.get("/api/shop_endpoints", headers=superuser_token_headers).json()
    assert len(shops) == 1  # Changed to 1 because admin has 2 shop_endpoints now
