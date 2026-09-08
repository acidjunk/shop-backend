# Copyright 2024 René Dohmen <acidjunk@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Pin the auth posture of every /shops route.

``server.api.endpoints.shops`` used to be one router mixing public reads with
authenticated writes, so the guard had to be repeated on each route and a new
route shipped unauthenticated if the author forgot it. It is now two routers —
``router`` carries ``Depends(auth_required)`` at router level, ``public_router``
carries nothing — and these tests are what stops a route from silently moving
between them.

``test_endpoint_auth`` in test_authentication.py only sweeps paths ending in
``/``, so none of the routes below are covered there.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

SHOP_ID = str(uuid.uuid4())

PROTECTED = [
    ("GET", "/shops/"),
    ("GET", "/shops/my-shops"),
    ("POST", "/shops/"),
    ("PUT", f"/shops/{SHOP_ID}"),
    ("DELETE", f"/shops/{SHOP_ID}"),
    ("PUT", f"/shops/config/{SHOP_ID}"),
    ("GET", f"/shops/allowed-ips/{SHOP_ID}"),
    ("POST", f"/shops/allowed-ips/{SHOP_ID}"),
    ("POST", f"/shops/allowed-ips/{SHOP_ID}/remove"),
]

PUBLIC = [
    ("GET", f"/shops/cache-status/{SHOP_ID}"),
    ("GET", f"/shops/last-completed-order/{SHOP_ID}"),
    ("GET", f"/shops/last-pending-order/{SHOP_ID}"),
    ("GET", f"/shops/{SHOP_ID}"),
    ("GET", f"/shops/config/{SHOP_ID}"),
]


@pytest.mark.parametrize("method, path", PROTECTED)
def test_protected_shop_routes_require_a_token(fastapi_app_not_authenticated, method, path):
    client = TestClient(fastapi_app_not_authenticated)
    response = client.request(method, path)
    assert response.status_code == 401, f"{method} {path} responded {response.status_code}, not 401"


@pytest.mark.parametrize("method, path", PUBLIC)
def test_public_shop_routes_stay_reachable_without_a_token(fastapi_app_not_authenticated, method, path):
    """These back storefront cache-invalidation polling, before any sign-in."""
    client = TestClient(fastapi_app_not_authenticated)
    response = client.request(method, path)
    assert response.status_code != 401, f"{method} {path} responded 401 but is meant to be public"
