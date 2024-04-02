from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel
from server.schemas.price import DefaultPrice


class KindEmptyBase(BoilerplateBaseModel):
    pass


class KindBase(BoilerplateBaseModel):
    name: str
    short_description_nl: Optional[str] = None
    description_nl: Optional[str] = None
    short_description_en: Optional[str] = None
    description_en: Optional[str] = None
    c: bool = False
    h: bool = False
    i: bool = False
    s: bool = False
    complete: bool = False
    image_1: Union[Optional[dict], Optional[str]]
    image_2: Union[Optional[dict], Optional[str]]
    image_3: Union[Optional[dict], Optional[str]]
    image_4: Union[Optional[dict], Optional[str]]
    image_5: Union[Optional[dict], Optional[str]]
    image_6: Union[Optional[dict], Optional[str]]


# Properties to receive via API on creation
class KindCreate(KindBase):
    pass


# Properties to receive via API on update
class KindUpdate(KindBase):
    modified_at: Optional[datetime] = None


class KindInDBBase(KindBase):
    id: UUID
    created_at: datetime
    modified_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class KindSchema(KindInDBBase):
    approved: bool = False
    approved_by: Optional[str] = None
    disapproved_reason: Optional[str] = None


class KindWithDetails(KindInDBBase):
    # Todo: Georgi investigate if it's ok to use the "ModelSchema" here. It has DB write access which isn't needed
    # We could be more strict and generic by re-using the schema of tag, flavors etc. instead of `List[dict]`
    tags: List[dict]
    tags_amount: int = 0
    flavors: List[dict]
    flavors_amount: int = 0
    strains: List[dict]
    strains_amount: int = 0
    images_amount: int = 0


class KindWithDefaultPrice(KindWithDetails):
    # to be the same with the Flask backend
    prices: Optional[DefaultPrice] = DefaultPrice()


class KindWithDetailsAndPrices(KindWithDetails):
    prices: List[dict] = []


class KindImageDelete(KindEmptyBase):
    image: str
