from server.crud.base import CRUDBase
from server.db.models import Price
from server.schemas.price import PriceCreate, PriceUpdate


class CRUDPrice(CRUDBase[Price, PriceCreate, PriceUpdate]):
    pass


price_crud = CRUDPrice(Price)
