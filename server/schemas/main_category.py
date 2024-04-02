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
