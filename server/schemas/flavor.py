from datetime import datetime
from typing import Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class FlavorBase(BoilerplateBaseModel):
    name: str
    icon: str
    color: Optional[str]


# Properties to receive via API on creation
class FlavorCreate(FlavorBase):
    pass


# Properties to receive via API on update
class FlavorUpdate(FlavorBase):
    pass


class FlavorInDBBase(FlavorBase):
    id: UUID

    class Config:
        orm_mode = True


# Additional properties to return via API
class FlavorSchema(FlavorInDBBase):
    pass
