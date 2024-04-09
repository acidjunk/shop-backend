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


class MainCategoryBase(BoilerplateBaseModel):
    name: str
    name_en: Optional[str]
    description: Optional[str] = None
    icon: Optional[str] = None
    order_number: Optional[int] = None
    shop_id: UUID


# Properties to receive via API on creation
class MainCategoryCreate(MainCategoryBase):
    shop_id: UUID


# Properties to receive via API on update
class MainCategoryUpdate(MainCategoryBase):
    pass


class MainCategoryInDBBase(MainCategoryBase):
    id: UUID

    class Config:
        orm_mode = True


# Additional properties to return via API
class MainCategorySchema(MainCategoryInDBBase):
    pass


class MainCategoryWithNames(MainCategoryInDBBase):
    shop_name: str
    main_category_and_shop: str
