from http import HTTPStatus
from uuid import uuid4

import structlog

from server.utils.json import json_dumps


def test_license_get_multi(license_1, license_2, test_client, superuser_token_headers):
    response = test_client.get("/api/licenses", headers=superuser_token_headers)

    assert HTTPStatus.OK == response.status_code
    licenses = response.json()

    assert 2 == len(licenses)


def test_license_get_by_id(license_1, test_client, superuser_token_headers):
    response = test_client.get(f"/api/licenses/{license_1.id}", headers=superuser_token_headers)
    assert HTTPStatus.OK == response.status_code
    license = response.json()
    assert license["name"] == "john"


def test_license_get_by_id_404(license_1, test_client, superuser_token_headers):
    response = test_client.get(f"/api/licenses/{str(uuid4())}", headers=superuser_token_headers)
    assert HTTPStatus.NOT_FOUND == response.status_code


def test_license_save(test_client, superuser_token_headers, fake_order):
    body = {
        "name": "New License",
        "improviser_user": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "is_recurring": True,
        "seats": 15,
        "order_id": fake_order.id,
    }

    response = test_client.post("/api/licenses", data=json_dumps(body), headers=superuser_token_headers)
    assert HTTPStatus.CREATED == response.status_code
    licenses = test_client.get("/api/licenses", headers=superuser_token_headers).json()
    assert 1 == len(licenses)


def test_license_save_recurring_end_date(test_client, superuser_token_headers, fake_order):
    body = {
        "name": "New License",
        "improviser_user": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "is_recurring": True,
        "seats": 15,
        "order_id": fake_order.id,
        "end_date": "2023-10-17T14:34:28.893Z",
    }

    response = test_client.post("/api/licenses", data=json_dumps(body), headers=superuser_token_headers)
    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code


def test_license_update(license_2, test_client, superuser_token_headers):
    body = {"seats": 40, "end_date": "2023-10-17T14:34:28.893Z"}
    response = test_client.put(f"/api/licenses/{license_2.id}", data=json_dumps(body), headers=superuser_token_headers)
    assert HTTPStatus.OK == response.status_code

    response_updated = test_client.get(f"/api/licenses/{license_2.id}", headers=superuser_token_headers)
    license = response_updated.json()
    assert license["seats"] == 40


def test_license_update_recurring_end_date(license_1, test_client, superuser_token_headers):
    body = {"seats": 40, "end_date": "2023-10-17T14:34:28.893Z"}
    response = test_client.put(f"/api/licenses/{license_1.id}", data=json_dumps(body), headers=superuser_token_headers)
    assert HTTPStatus.UNPROCESSABLE_ENTITY == response.status_code


def test_license_delete(license_1, test_client, superuser_token_headers):
    response = test_client.delete(f"/api/licenses/{license_1.id}", headers=superuser_token_headers)
    assert HTTPStatus.NO_CONTENT == response.status_code
    licenses = test_client.get("/api/licenses", headers=superuser_token_headers).json()
    assert 0 == len(licenses)
