from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class RoleUserBase(BoilerplateBaseModel):
    user_id: UUID
    role_id: UUID


# Properties to receive via API on creation
class RoleUserCreate(RoleUserBase):
    pass


# Properties to receive via API on update
class RoleUserUpdate(RoleUserBase):
    pass


class RoleUserInDBBase(RoleUserBase):
    id: UUID

    class Config:
        orm_mode = True


# Additional properties to return via API
class RoleUserSchema(RoleUserInDBBase):
    pass
