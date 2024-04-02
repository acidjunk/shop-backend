from typing import List, Optional
from uuid import UUID

from server.crud.base import CRUDBase
from server.db.models import ShopsUsersTable
from server.schemas.shop_user import ShopUserCreate, ShopUserEmptyBase, ShopUserSchema, ShopUserUpdate


class CRUDShopUser(CRUDBase[ShopsUsersTable, ShopUserCreate, ShopUserUpdate]):
    pass


shop_user_crud = CRUDShopUser(ShopsUsersTable)
