from server.crud.base import CRUDBase
from server.db.models import Shop
from server.schemas.shop import ShopCreate, ShopUpdate


class CRUDShop(CRUDBase[Shop, ShopCreate, ShopUpdate]):
    pass


shop_crud = CRUDShop(Shop)
