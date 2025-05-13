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

"""Module that implements process related API endpoints."""

from fastapi import APIRouter, Depends

from server.api import deps
from server.api.endpoints import downloads, early_access, forms, health, images, licenses, login, shops, users
from server.api.endpoints.shop_endpoints import (
    accounts,
    categories,
    category_images,
    info_request,
    orders,
    prices,
    products,
    products_to_tags,
    stripe,
    tags,
)
from server.api.endpoints.shop_endpoints.images import router as shop_image_router
from server.security import auth_required

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(health.router, prefix="/health", tags=["system"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    forms.router,
    prefix="/forms",
    tags=["forms"],
    dependencies=[Depends(auth_required)],
)
api_router.include_router(images.router, prefix="/images", tags=["images"])

# Todo: determine if these are also shop specific
api_router.include_router(
    licenses.router,
    prefix="/licenses",
    tags=["licenses"],
)

api_router.include_router(
    downloads.router,
    prefix="/downloads",
    tags=["downloads"],
)

# SHOP specific endpoints
api_router.include_router(shops.router, prefix="/shops", tags=["shops"])
api_router.include_router(prices.router, prefix="/shops/{shop_id}/prices", tags=["shops"])
api_router.include_router(
    orders.router,
    prefix="/orders",
    tags=["orders"],
    dependencies=[Depends(auth_required)],
)
api_router.include_router(
    categories.router,
    prefix="/shops/{shop_id}/categories",
    tags=["categories"],
    dependencies=[Depends(auth_required)],
)
api_router.include_router(
    category_images.router,
    prefix="/shops/{shop_id}/categories-images",
    tags=["shops", "categories"],
    dependencies=[Depends(auth_required)],
)
api_router.include_router(
    shop_image_router,
    prefix="/shops/{shop_id}/images",
    tags=["shops", "images"],
    dependencies=[Depends(auth_required)],
)

# api_router.include_router(
#     product_images.router,
#     prefix="/shops/{shop_id}/products-images",
#     tags=["products-images"],
#     dependencies=[Depends(deps.get_current_active_superuser)],
# )
api_router.include_router(
    products.router,
    prefix="/shops/{shop_id}/products",
    tags=["shops", "products"],
    dependencies=[Depends(auth_required)],
)
api_router.include_router(
    products_to_tags.router,
    prefix="/shops/{shop_id}/products-to-tags",
    tags=["shops", "products"],
    dependencies=[Depends(auth_required)],
)
api_router.include_router(
    tags.router,
    prefix="/shops/{shop_id}/tags",
    tags=["shops", "products"],
    dependencies=[Depends(auth_required)],
)
api_router.include_router(
    accounts.router,
    prefix="/shops/{shop_id}/accounts",
    tags=["shops", "accounts"],
    dependencies=[Depends(auth_required)],
)
api_router.include_router(
    stripe.router,
    prefix="/shops/{shop_id}/stripe",
    tags=["stripe"],
    # dependencies=[Depends(deps.get_current_active_superuser)],
)

api_router.include_router(
    early_access.router, prefix="/early-access", tags=["early-access"], dependencies=[Depends(auth_required)]
)

api_router.include_router(
    info_request.router, prefix="/info-request", tags=["info-request"], dependencies=[Depends(auth_required)]
)

# api_router.include_router(
#     shops_users.router,
#     prefix="/shops/{shop_id}/shops-users",
#     tags=["shops-users"],
#     dependencies=[Depends(deps.get_current_active_superuser)],
# )
