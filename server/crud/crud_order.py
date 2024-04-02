from uuid import UUID

from server.crud.base import CRUDBase
from server.db.models import Order
from server.schemas.order import OrderCreate, OrderUpdate
from server.utils.json import json_dumps


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def get_newest_order_id(self, *, shop_id: UUID) -> int:
        order_id = Order.query.filter_by(shop_id=str(shop_id)).count() + 1
        return order_id

    def get_all_orders_filtered_by(self, **kwargs):
        order = Order.query.filter_by(**kwargs).all()
        return order

    def get_first_order_filtered_by(self, **kwargs):
        order = Order.query.filter_by(**kwargs).first()
        return order


order_crud = CRUDOrder(Order)
