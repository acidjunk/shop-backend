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
from typing import List, Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class ProductAttributeValueBase(BoilerplateBaseModel):
    """Base schema for product attribute values."""

    product_id: UUID
    attribute_id: UUID
    option_id: Optional[UUID] = None  # TODO make this not optional


class ProductAttributeValueCreate(ProductAttributeValueBase):
    """Schema for creating a product attribute value."""

    pass


class ProductAttributeOptionSelectionReplace(BoilerplateBaseModel):
    """Payload for creating or replacing selected attribute options for a product."""

    option_ids: List[UUID]


class ProductAttributeOptionSelectionAdd(BoilerplateBaseModel):
    """Payload for creating or replacing selected attribute options for a product."""

    option_ids: List[UUID]


class ProductAttributeValueInDBBase(ProductAttributeValueBase):
    """Base schema for product attribute values as stored in the database."""

    id: UUID

    class Config:
        from_attributes = True


class ProductAttributeValueSchema(ProductAttributeValueInDBBase):
    """Schema for representing a product attribute value."""

    pass
