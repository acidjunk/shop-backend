from http import HTTPStatus
from uuid import uuid4

import structlog

from server.utils.json import json_dumps

logger = structlog.getLogger(__name__)


def test_flavors_get_multi(flavor_1, test_client, superuser_token_headers):
    response = test_client.get("/api/flavors", headers=superuser_token_headers)

    assert HTTPStatus.OK == response.status_code
    flavors = response.json()

    assert 48 == len(flavors)


def test_flavor_get_by_id(flavor_2, test_client, superuser_token_headers):
    response = test_client.get(f"/api/flavors/{flavor_2.id}", headers=superuser_token_headers)
    print(response.__dict__)
    assert HTTPStatus.OK == response.status_code
    flavor = response.json()
    assert flavor["name"] == "Earth"


def test_flavor_get_by_id_404(flavor_1, test_client, superuser_token_headers):
    response = test_client.get(f"/api/flavors/{str(uuid4())}", headers=superuser_token_headers)
    assert HTTPStatus.NOT_FOUND == response.status_code


def test_flavor_save(test_client, superuser_token_headers):
    body = {"name": "New Flavor", "icon": "New Icon", "color": "#ffffff"}

    response = test_client.post("/api/flavors/", data=json_dumps(body), headers=superuser_token_headers)
    assert HTTPStatus.CREATED == response.status_code
    flavors = test_client.get("/api/flavors", headers=superuser_token_headers).json()
    assert 48 == len(flavors)


def test_flavor_update(flavor_1, test_client, superuser_token_headers):
    body = {"name": "Updated Flavor", "icon": "moon", "color": "00fff0"}
    response = test_client.put(f"/api/flavors/{flavor_1.id}", data=json_dumps(body), headers=superuser_token_headers)
    assert HTTPStatus.CREATED == response.status_code

    response_updated = test_client.get(f"/api/flavors/{flavor_1.id}", headers=superuser_token_headers)
    flavor = response_updated.json()
    assert flavor["name"] == "Updated Flavor"


def test_flavor_delete(flavor_1, test_client, superuser_token_headers):
    response = test_client.delete(f"/api/flavors/{flavor_1.id}", headers=superuser_token_headers)
    assert HTTPStatus.NO_CONTENT == response.status_code
    shops = test_client.get("/api/flavors", headers=superuser_token_headers).json()
    assert 47 == len(shops)
