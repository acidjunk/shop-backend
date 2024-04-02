from datetime import datetime
from typing import Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class KindToStrainBase(BoilerplateBaseModel):
    kind_id: UUID
    strain_id: UUID


# Properties to receive via API on creation
class KindToStrainCreate(KindToStrainBase):
    pass


# Properties to receive via API on update
class KindToStrainUpdate(KindToStrainBase):
    pass


class KindToStrainInDBBase(KindToStrainBase):
    id: UUID

    class Config:
        orm_mode = True


# Additional properties to return via API
class KindToStrainSchema(KindToStrainInDBBase):
    pass
