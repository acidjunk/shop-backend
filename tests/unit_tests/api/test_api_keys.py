from http import HTTPStatus
from uuid import uuid4

from fastapi.testclient import TestClient

from server.db.models import APIKeyTable
from tests.unit_tests.conftest import COGNITO_USER_ID


def test_api_keys_get_multi(test_client, api_key):
    response = test_client.get("/api-keys/")
    assert response.status_code == HTTPStatus.OK
    keys = response.json()
    assert len(keys) == 1
    assert keys[0]["id"] == str(api_key)
    assert keys[0]["user_id"] == COGNITO_USER_ID


def test_api_keys_create(test_client):
    response = test_client.post("/api-keys/")
    assert response.status_code == HTTPStatus.CREATED
    api_key = response.json()
    api_key_record = APIKeyTable.query.filter_by(id=api_key["id"]).first()
    assert str(api_key_record.user_id) == COGNITO_USER_ID
    assert api_key_record.revoked_at is None

    api_key_value = api_key["api_key"]
    assert isinstance(api_key_value, str)
    assert len(api_key_value) > 0


def test_api_keys_delete(api_key, test_client):
    response = test_client.delete(f"/api-keys/{api_key}")
    assert response.status_code == 204


def test_api_keys_delete_not_found(test_client):
    response = test_client.delete(f"/api-keys/{uuid4()}")
    assert response.status_code == 400


def test_api_keys_delete_revoked(api_key, test_client):
    response1 = test_client.delete(f"/api-keys/{api_key}")
    assert response1.status_code == 204
    api_key_record1 = APIKeyTable.query.first()
    assert api_key_record1.revoked_at is not None

    response2 = test_client.delete(f"/api-keys/{api_key}")
    assert response2.status_code == 204
    api_key_record2 = APIKeyTable.query.first()
    assert api_key_record1.revoked_at == api_key_record2.revoked_at


# We only test 1 endpoint since they all use the same middleware
def test_auth_using_api_key(fastapi_app_not_authenticated, shop_with_products, api_key_with_key):
    _, key = api_key_with_key
    test_client = TestClient(fastapi_app_not_authenticated, headers={"X-API-Key": str(key)})

    response = test_client.get(f"/shops/{shop_with_products}/products/")
    assert response.status_code == 200
    products = response.json()
    assert 2 == len(products)
