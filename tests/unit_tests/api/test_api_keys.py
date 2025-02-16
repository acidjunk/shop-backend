from http import HTTPStatus

from server.db.models import APIKeyTable


def test_api_keys_get_multi(shop, api_key, test_client):
    response = test_client.get(f"/shops/{shop}/api-keys/")
    assert response.status_code == HTTPStatus.OK
    keys = response.json()
    assert 1 == len(keys)


def test_api_keys_create(shop, test_client):
    response = test_client.post(f"/shops/{shop}/api-keys/")
    assert response.status_code == HTTPStatus.CREATED
    api_key = response.json()
    api_key_record = APIKeyTable.query.filter_by(id=api_key["id"]).first()
    assert api_key_record.shop_id == shop
    assert api_key_record.revoked_at is None

    api_key_value = api_key["api_key"]
    assert isinstance(api_key_value, str)
    assert len(api_key_value) > 0


def test_products_delete(shop, api_key, test_client):
    response = test_client.delete(f"/shops/{shop}/api-keys/{api_key}")
    assert response.status_code == 204
