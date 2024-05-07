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
from typing import List, Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class ShopEmptyBase(BoilerplateBaseModel):
    pass

    class Config:
        from_attributes = True


class ShopBase(BoilerplateBaseModel):
    name: str
    description: str


# Properties to receive via API on creation
class ShopCreate(ShopBase):
    pass


# Properties to receive via API on update
class ShopUpdate(ShopBase):
    modified_at: Optional[datetime]
    # Todo: deal with the commented params below
    # last_pending_order: Optional[str]
    # last_completed_order: Optional[str]
    allowed_ips: Optional[List[str]] = None


class ShopInDBBase(ShopBase):
    id: UUID

    class Config:
        from_attributes = True


# Additional properties to return via API
class ShopSchema(ShopInDBBase):
    pass


class ShopWithPrices(ShopInDBBase):
    prices: List[dict]


class ShopCacheStatus(ShopEmptyBase):
    modified_at: Optional[datetime]


class ShopLastCompletedOrder(ShopEmptyBase):
    last_completed_order: Optional[str]


class ShopLastPendingOrder(ShopEmptyBase):
    last_pending_order: Optional[str]


class ShopIp(BoilerplateBaseModel):
    ip: str
