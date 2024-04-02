from datetime import datetime
from typing import Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class TagBase(BoilerplateBaseModel):
    name: str


# Properties to receive via API on creation
class TagCreate(TagBase):
    pass


# Properties to receive via API on update
class TagUpdate(TagBase):
    pass


class TagInDBBase(TagBase):
    id: UUID

    class Config:
        orm_mode = True


# Additional properties to return via API
class TagSchema(TagInDBBase):
    pass
