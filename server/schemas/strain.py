from typing import Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class StrainBase(BoilerplateBaseModel):
    name: str


# Properties to receive via API on creation
class StrainCreate(StrainBase):
    pass


# Properties to receive via API on update
class StrainUpdate(StrainBase):
    pass


class StrainInDBBase(StrainBase):
    id: UUID

    class Config:
        orm_mode = True


# Additional properties to return via API
class StrainSchema(StrainInDBBase):
    pass
