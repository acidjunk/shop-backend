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

from fastapi import Depends

from server.api import deps
from server.api.api_v1.endpoints import (  # forms,
    categories,
    category_images,
    downloads,
    forms,
    health,
    images,
    licenses,
    login,
    orders,
    product_images,
    products,
    shops,
    # shops_users,
    accounts,
    tags,
    users, products_to_tags,
)
from server.api.api_v1.router_fix import APIRouter
from server.websockets import chat

api_router = APIRouter()

# TODO Georgi: Bring back authentication
api_router.include_router(login.router, tags=["login"])
api_router.include_router(health.router, prefix="/health", tags=["system"])
api_router.include_router(shops.router, prefix="/shops", tags=["shops"])
api_router.include_router(orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["categories"],
    dependencies=[Depends(deps.get_current_active_superuser)],
)
api_router.include_router(
    category_images.router,
    prefix="/categories-images",
    tags=["categories-images"],
    dependencies=[Depends(deps.get_current_active_superuser)],
)
# api_router.include_router(
#     kind_images.router,
#     prefix="/kinds-images",
#     tags=["kinds-images"],
#     dependencies=[Depends(deps.get_current_active_superuser)],
# )
# api_router.include_router(
#     product_images.router,
#     prefix="/products-images",
#     tags=["products-images"],
#     dependencies=[Depends(deps.get_current_active_superuser)],
# )
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(
    products_to_tags.router,
    prefix="/products-to-tags",
    tags=["kinds-relations"],
    dependencies=[Depends(deps.get_current_active_superuser)],
)
api_router.include_router(
    tags.router, prefix="/tags", tags=["tags"], dependencies=[Depends(deps.get_current_active_superuser)]
)
api_router.include_router(
    accounts.router, prefix="/accounts", tags=["accounts"], dependencies=[Depends(deps.get_current_active_superuser)]
)
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    forms.router,
    prefix="/forms",
    tags=["forms"],
    dependencies=[Depends(deps.get_current_active_user)],
)
api_router.include_router(images.router, prefix="/images", tags=["images"])
# api_router.include_router(
#     shops_users.router,
#     prefix="/shops-users",
#     tags=["shops-users"],
#     dependencies=[Depends(deps.get_current_active_superuser)],
# )

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
