# Copyright 2026 René Dohmen <acidjunk@gmail.com>
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
from typing import Optional, List
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel
from server.schemas.product import ProductWithDefaultPrice
from server.schemas.product_attribute import ProductAttributeItem


class ProductAttributeValueBase(BoilerplateBaseModel):
    product_id: UUID
    attribute_id: UUID
    option_id: Optional[UUID] = None #TODO make this not optional


class ProductAttributeValueCreate(ProductAttributeValueBase):
    pass


class ProductAttributeValueUpdate(ProductAttributeValueBase):
    pass


class ProductAttributeValueInDBBase(ProductAttributeValueBase):
    id: UUID

    class Config:
        from_attributes = True


class ProductAttributeValueSchema(ProductAttributeValueInDBBase):
    pass


class ProductWithAttributes(BoilerplateBaseModel):
    product: ProductWithDefaultPrice
    attributes: List[ProductAttributeItem] = []
