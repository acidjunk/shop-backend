from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel
from server.schemas.price import DefaultPrice


class ProductEmptyBase(BoilerplateBaseModel):
    pass


class ProductBase(BoilerplateBaseModel):
    name: str
    short_description_nl: Optional[str] = None
    description_nl: Optional[str] = None
    short_description_en: Optional[str] = None
    description_en: Optional[str] = None
    complete: bool = False
    image_1: Union[Optional[dict], Optional[str]]
    image_2: Union[Optional[dict], Optional[str]]
    image_3: Union[Optional[dict], Optional[str]]
    image_4: Union[Optional[dict], Optional[str]]
    image_5: Union[Optional[dict], Optional[str]]
    image_6: Union[Optional[dict], Optional[str]]


# Properties to receive via API on creation
class ProductCreate(ProductBase):
    pass


# Properties to receive via API on update
class ProductUpdate(ProductBase):
    modified_at: Optional[datetime] = None


class ProductInDBBase(ProductBase):
    id: UUID
    created_at: datetime
    modified_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None

    class Config:
        orm_mode = True


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
