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
from http import HTTPStatus

import structlog
from fastapi import APIRouter
from fastapi.param_functions import Body

from server.api.error_handling import raise_status
from server.crud.crud_shop import shop_crud
from server.schemas.cart import CartCalculateRequest, CartCalculation
from server.services.cart import compute_cart_total

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post(
    "/calculate",
    response_model=CartCalculation,
    summary="Calculate cart totals",
    description=(
        "Resolves prices (including active discounts), applies VAT per line, "
        "computes the subtotal, and—when shipping is configured on the shop—"
        "appends the shipping fee to produce a grand total."
    ),
)
def calculate(data: CartCalculateRequest = Body(...)) -> CartCalculation:
    shop = shop_crud.get(data.shop_id)
    if not shop:
        raise_status(HTTPStatus.NOT_FOUND, f"Shop with id {data.shop_id} not found")

    return compute_cart_total(data.items, shop)
