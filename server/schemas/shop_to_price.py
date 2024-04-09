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
from datetime import datetime
from typing import Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class ShopToPriceBase(BoilerplateBaseModel):
    active: bool
    new: bool
    price_id: UUID
    shop_id: UUID
    category_id: UUID
    kind_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    use_half: bool = False
    half: Optional[float] = None
    use_one: bool = False
    one: Optional[float] = None
    two_five: float = None
    use_two_five: bool = None
    use_five: bool = False
    five: Optional[float] = None
    use_joint: bool = False
    joint: Optional[float] = None
    use_piece: bool = False
    piece: Optional[float] = None


class ShopToPriceAvailability(BoilerplateBaseModel):
    active: bool


class ShopToPriceSwap(BoilerplateBaseModel):
    order_number: int


# Properties to receive via API on creation
class ShopToPriceCreate(ShopToPriceBase):
    pass


# Properties to receive via API on update
class ShopToPriceUpdate(ShopToPriceBase):
    pass


class ShopToPriceInDBBase(ShopToPriceBase):
    id: UUID
    created_at: datetime
    modified_at: datetime
    order_number: int

    class Config:
        orm_mode = True


# Additional properties to return via API
class ShopToPriceSchema(ShopToPriceInDBBase):
    pass
