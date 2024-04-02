from http import HTTPStatus
from uuid import uuid4

import pytest
import structlog

from server.utils.json import json_dumps

logger = structlog.getLogger(__name__)


def test_kinds_get_multi(kind_1, kind_2, test_client, superuser_token_headers):
    response = test_client.get("/api/kinds", headers=superuser_token_headers)

    assert HTTPStatus.OK == response.status_code
    kinds = response.json()

    assert 2 == len(kinds)


def test_kind_get_by_id(kind_1, test_client, superuser_token_headers):
    response = test_client.get(f"/api/kinds/{kind_1.id}", headers=superuser_token_headers)
    assert HTTPStatus.OK == response.status_code
    kind = response.json()
    assert kind["name"] == "Indica"
    assert len(kind["tags"]) == 1
    assert kind["tags_amount"] == 1
    assert len(kind["flavors"]) == 1
    assert kind["flavors_amount"] == 1
    assert len(kind["strains"]) == 1


def test_kind_get_by_id_404(kind_1, test_client, superuser_token_headers):
    response = test_client.get(f"/api/kinds/{str(uuid4())}", headers=superuser_token_headers)
    assert HTTPStatus.NOT_FOUND == response.status_code


def test_kind_save(test_client, superuser_token_headers):
    body = {"name": "New Kind", "icon": "New Icon", "color": "#ffffff"}

    response = test_client.post("/api/kinds/", data=json_dumps(body), headers=superuser_token_headers)
    assert HTTPStatus.CREATED == response.status_code
    kinds = test_client.get("/api/kinds", headers=superuser_token_headers).json()
    assert 1 == len(kinds)


def test_kind_update(kind_1, test_client, superuser_token_headers):
    body = {"name": "Updated Kind", "icon": "moon", "color": "00fff0"}
    response = test_client.put(f"/api/kinds/{kind_1.id}", data=json_dumps(body), headers=superuser_token_headers)
    assert HTTPStatus.CREATED == response.status_code

    response_updated = test_client.get(f"/api/kinds/{kind_1.id}", headers=superuser_token_headers)
    kind = response_updated.json()
    assert kind["name"] == "Updated Kind"


# TODO: Unit test for kind with 2 shops


def test_kind_delete(kind_1, test_client, superuser_token_headers):
    response = test_client.delete(f"/api/kinds/{kind_1.id}", headers=superuser_token_headers)
    assert HTTPStatus.NO_CONTENT == response.status_code
    kinds = test_client.get("/api/kinds", headers=superuser_token_headers).json()
    assert 0 == len(kinds)
