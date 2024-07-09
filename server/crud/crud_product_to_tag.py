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
from typing import Optional

from server.crud.base import CRUDBase
from server.db.models import ProductToTagTable
from server.schemas.product_to_tag import ProductToTagCreate, ProductToTagUpdate


class CRUDProductToTag(CRUDBase[ProductToTagTable, ProductToTagCreate, ProductToTagUpdate]):
    def get_relation(self, *, product, tag) -> Optional[ProductToTagTable]:
        return ProductToTagTable.query.filter_by(product_id=product.id).filter_by(tag_id=tag.id).all()

    def get_relation_by_product_tag(self, *, product_id, tag_id) -> Optional[ProductToTagTable]:
        return ProductToTagTable.query.filter_by(product_id=product_id).filter_by(tag_id=tag_id).first()

    def get_relations_by_product(self, *, product_id) -> [Optional[ProductToTagTable]]:
        return ProductToTagTable.query.filter_by(product_id=product_id).all()


product_to_tag_crud = CRUDProductToTag(ProductToTagTable)
