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
from typing import List, Literal, Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel, Money
from server.schemas.shipping import ShippingCalculation


class CartCalculateItem(BoilerplateBaseModel):
    product_id: UUID
    quantity: int
    plan: Literal["onetime", "monthly", "yearly"] = "onetime"


class CartCalculateRequest(BoilerplateBaseModel):
    shop_id: UUID
    items: List[CartCalculateItem]


class CartLine(BoilerplateBaseModel):
    product_id: UUID
    product_name: str
    quantity: int
    unit_price_inc_vat: Money
    vat_rate: Money
    line_total_inc_vat: Money


class CartCalculation(BoilerplateBaseModel):
    lines: List[CartLine]
    subtotal_inc_vat: Money
    shipping: Optional[ShippingCalculation] = None
    grand_total: Money
