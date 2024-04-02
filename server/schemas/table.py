from datetime import datetime
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class TableBase(BoilerplateBaseModel):
    shop_id: UUID
    name: str


# Properties to receive via API on creation
class TableCreate(TableBase):
    pass


# Properties to receive via API on update
class TableUpdate(TableBase):
    pass


class TableInDBBase(TableBase):
    id: UUID

    class Config:
        orm_mode = True


# Additional properties to return via API
class TableSchema(TableInDBBase):
    pass
