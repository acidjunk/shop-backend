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
