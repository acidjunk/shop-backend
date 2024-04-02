from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class RoleBase(BoilerplateBaseModel):
    name: str
    description: str


# Properties to receive via API on creation
class RoleCreate(RoleBase):
    pass


# Properties to receive via API on update
class RoleUpdate(RoleBase):
    pass


class RoleInDBBase(RoleBase):
    id: UUID

    class Config:
        orm_mode = True


# Additional properties to return via API
class RoleSchema(RoleInDBBase):
    pass
