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
from typing import List, Optional, Union
from uuid import UUID

from pydantic import ConfigDict

from server.schemas.base import BoilerplateBaseModel
from server.schemas.price import DefaultPrice
from server.schemas.product_attribute import ProductAttributeItem


class ProductEmptyBase(BoilerplateBaseModel):
    pass


class ProductTranslationBase(BoilerplateBaseModel):
    model_config = ConfigDict(from_attributes=True)

    main_name: str
    main_description: str
    main_description_short: str
    alt1_name: Optional[str] = None
    alt1_description: Optional[str] = None
    alt1_description_short: Optional[str] = None
    alt2_name: Optional[str] = None
    alt2_description: Optional[str] = None
    alt2_description_short: Optional[str] = None


class ProductBase(BoilerplateBaseModel):
    model_config = ConfigDict(from_attributes=True)

    shop_id: UUID
    category_id: UUID
    price: Optional[float] = None
    recurring_price_monthly: Optional[float] = None
    recurring_price_yearly: Optional[float] = None
    max_one: bool
    shippable: bool
    digital: Optional[str] = None
    featured: bool
    new_product: bool
    # Todo: make enum with: vat_standard, vat_lower_1, vat_lower_2, vat_lower_3, vat_special, vat_zero
    tax_category: str
    discounted_price: Optional[float] = None
    discounted_from: Optional[datetime] = None
    discounted_to: Optional[datetime] = None
    order_number: Optional[int] = None
    stock: Optional[int] = 1
    image_1: Union[Optional[dict], Optional[str]]
    image_2: Union[Optional[dict], Optional[str]]
    image_3: Union[Optional[dict], Optional[str]]
    image_4: Union[Optional[dict], Optional[str]]
    image_5: Union[Optional[dict], Optional[str]]
    image_6: Union[Optional[dict], Optional[str]]
    translation: ProductTranslationBase


# Properties to receive via API on creation
class ProductCreate(ProductBase):
    pass


# Properties to receive via API on update
class ProductUpdate(ProductBase):
    modified_at: Optional[datetime] = None


class ProductInDBBase(ProductBase):
    id: UUID
    # created_at: datetime
    modified_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Additional properties to return via API
class ProductSchema(ProductInDBBase):
    approved: bool = False
    approved_by: Optional[str] = None
    disapproved_reason: Optional[str] = None


class ProductWithDetails(ProductInDBBase):
    images_amount: int = 0


class ProductWithDefaultPrice(ProductWithDetails):
    # to be the same with the Flask backend
    prices: Optional[DefaultPrice] = DefaultPrice()


class ProductWithDetailsAndPrices(ProductWithDetails):
    prices: List[dict] = []


class ProductImageDelete(ProductEmptyBase):
    image: str


class ProductOrder(BoilerplateBaseModel):
    order_number: int
