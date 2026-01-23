# Copyright 2026 René Dohmen <acidjunk@gmail.com>
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
from server.db.models import ProductAttributeValueTable
from server.schemas.product_attribute_value import (
    ProductAttributeValueCreate,
    ProductAttributeValueUpdate,
)


class CRUDProductAttributeValue(
    CRUDBase[ProductAttributeValueTable, ProductAttributeValueCreate, ProductAttributeValueUpdate]
):
    def get_existing(
        self, *, product_id, attribute_id, option_id: Optional[str], value_text: Optional[str]
    ) -> Optional[ProductAttributeValueTable]:
        query = ProductAttributeValueTable.query.filter_by(product_id=product_id, attribute_id=attribute_id)
        if option_id is not None:
            query = query.filter_by(option_id=option_id)
        else:
            query = query.filter(ProductAttributeValueTable.option_id.is_(None))
        if value_text is not None:
            query = query.filter_by(value_text=value_text)
        else:
            query = query.filter(ProductAttributeValueTable.value_text.is_(None))
        return query.first()


product_attribute_value_crud = CRUDProductAttributeValue(ProductAttributeValueTable)
