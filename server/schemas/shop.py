from datetime import datetime
from typing import List, Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class ShopEmptyBase(BoilerplateBaseModel):
    pass

    class Config:
        orm_mode = True


class ShopBase(BoilerplateBaseModel):
    name: str
    description: str


# Properties to receive via API on creation
class ShopCreate(ShopBase):
    pass


# Properties to receive via API on update
class ShopUpdate(ShopBase):
    modified_at: Optional[datetime]
    last_pending_order: Optional[str]
    last_completed_order: Optional[str]
    allowed_ips: Optional[List[str]] = None


class ShopInDBBase(ShopBase):
    id: UUID

    class Config:
        orm_mode = True


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
