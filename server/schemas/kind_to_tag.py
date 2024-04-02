from datetime import datetime
from typing import Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class KindToTagBase(BoilerplateBaseModel):
    kind_id: UUID
    tag_id: UUID
    amount: int


# Properties to receive via API on creation
class KindToTagCreate(KindToTagBase):
    pass


# Properties to receive via API on update
class KindToTagUpdate(KindToTagBase):
    pass


class KindToTagInDBBase(KindToTagBase):
    id: UUID

    class Config:
        orm_mode = True


# Additional properties to return via API
class KindToTagSchema(KindToTagInDBBase):
    pass
