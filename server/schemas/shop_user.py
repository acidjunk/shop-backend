from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class ShopUserEmptyBase(BoilerplateBaseModel):
    pass

    class Config:
        orm_mode = True


class ShopId(ShopUserEmptyBase):
    id: UUID
    shop_id: UUID


class UserId(ShopUserEmptyBase):
    id: UUID
    user_id: UUID


class ShopUserBase(ShopUserEmptyBase):
    shop_id: UUID
    user_id: UUID


# Properties to receive via API on creation
class ShopUserCreate(ShopUserBase):
    pass


# Properties to receive via API on update
class ShopUserUpdate(ShopUserBase):
    pass


class ShopUserInDBBase(ShopUserBase):
    id: UUID

    class Config:
        orm_mode = True


# Additional properties to return via API
class ShopUserSchema(ShopUserInDBBase):
    pass
