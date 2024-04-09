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
from typing import Optional, Union
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class CategoryEmptyBase(BoilerplateBaseModel):
    pass


class CategoryBase(BoilerplateBaseModel):
    shop_id: UUID
    main_category_id: Optional[UUID] = None
    name: str
    name_en: Optional[str] = None
    description: Optional[str] = None
    color: str
    icon: Optional[str] = None
    order_number: Optional[int] = None
    cannabis: bool = False
    image_1: Union[Optional[dict], Optional[str]]
    image_2: Union[Optional[dict], Optional[str]]
    pricelist_column: Optional[str]
    pricelist_row: Optional[int]


# Properties to receive via API on creation
class CategoryCreate(CategoryBase):
    pass


# Properties to receive via API on update
class CategoryUpdate(CategoryBase):
    pass


class CategoryInDBBase(CategoryBase):
    id: UUID

    class Config:
        orm_mode = True


# Additional properties to return via API
class CategorySchema(CategoryInDBBase):
    pass


class CategoryWithNames(CategoryInDBBase):
    main_category_name: str
    main_category_name_en: Optional[str] = None
    shop_name: str


class CategoryImageDelete(CategoryEmptyBase):
    image: str


class CategoryIsDeletable(CategoryEmptyBase):
    is_deletable: bool
