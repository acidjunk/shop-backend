from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from server.schemas.base import BoilerplateBaseModel


class LicenseBase(BoilerplateBaseModel):
    name: str
    improviser_user: UUID
    is_recurring: bool
    seats: float
    order_id: UUID
    end_date: Optional[datetime]


class LicenseCreate(LicenseBase):
    pass


class LicenseUpdate(BoilerplateBaseModel):
    seats: Optional[float]
    end_date: Optional[datetime]


class LicenseInDB(LicenseBase):
    id: UUID
    modified_at: datetime
    created_at: datetime
    start_date: datetime

    class Config:
        orm_mode = True


class LicenseSchema(LicenseInDB):
    pass
