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
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import contains_eager, defer

from server.api.models import transform_json
from server.crud.base import CRUDBase
from server.db import db
from server.db.models import ShopToPrice
from server.schemas.shop_to_price import ShopToPriceCreate, ShopToPriceUpdate
from server.utils.json import json_dumps


class CRUDShopToPrice(CRUDBase[ShopToPrice, ShopToPriceCreate, ShopToPriceUpdate]):
    def create(self, *, obj_in: ShopToPriceCreate) -> ShopToPrice:
        obj_in_data = transform_json(obj_in.dict())

        # calculate new order number
        if obj_in.kind_id:
            order_number = -1
        else:
            product = (
                ShopToPrice.query.filter_by(category_id=obj_in.category_id)
                .filter(ShopToPrice.product_id.isnot(None))
                .order_by(ShopToPrice.order_number.desc())
                .first()
            )
            order_number = (product.order_number + 1) if product is not None else 0

        obj_in_data["order_number"] = order_number

        db_obj = self.model(**obj_in_data)
        db.session.add(db_obj)
        db.session.commit()
        db.session.refresh(db_obj)
        return db_obj

    def check_relation_by_kind(self, *, shop_id: UUID, price_id: UUID, kind_id: UUID) -> Optional[ShopToPrice]:
        check_query = (
            ShopToPrice.query.filter_by(shop_id=shop_id).filter_by(price_id=price_id).filter_by(kind_id=kind_id).all()
        )
        return check_query

    def check_relation_by_product(self, *, shop_id: UUID, price_id: UUID, product_id: UUID) -> Optional[ShopToPrice]:
        check_query = (
            ShopToPrice.query.filter_by(shop_id=shop_id)
            .filter_by(price_id=price_id)
            .filter_by(product_id=product_id)
            .all()
        )
        return check_query

    def get_products_with_prices_by_shop_id(self, *, shop_id: UUID):
        products = (
            ShopToPrice.query.join(ShopToPrice.price)
            .options(contains_eager(ShopToPrice.price), defer("price_id"))
            .filter(ShopToPrice.shop_id == shop_id)
            .all()
        )
        return products

    def get_shops_to_prices_by_kind(self, *, kind_id: UUID) -> List[Optional[ShopToPrice]]:
        query = ShopToPrice.query.filter_by(kind_id=kind_id).all()
        return query

    def get_shops_to_prices_by_category(self, *, category_id: UUID) -> List[Optional[ShopToPrice]]:
        query = ShopToPrice.query.filter_by(category_id=category_id).count()
        return query


shop_to_price_crud = CRUDShopToPrice(ShopToPrice)
