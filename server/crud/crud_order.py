# Copyright 2024 René Dohmen <acidjunk@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from uuid import UUID

from server.crud.base import CRUDBase
from server.db.models import OrderTable
from server.schemas.order import OrderCreate, OrderUpdate
from server.utils.json import json_dumps


class CRUDOrder(CRUDBase[OrderTable, OrderCreate, OrderUpdate]):
    def get_newest_order_id(self, *, shop_id: UUID) -> int:
        order_id = OrderTable.query.filter_by(shop_id=str(shop_id)).count() + 1
        return order_id

    def get_all_orders_filtered_by(self, **kwargs):
        order = OrderTable.query.filter_by(**kwargs).all()
        return order

    def get_first_order_filtered_by(self, **kwargs):
        order = OrderTable.query.filter_by(**kwargs).first()
        return order


order_crud = CRUDOrder(OrderTable)
