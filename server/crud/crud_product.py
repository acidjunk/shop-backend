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
from server.crud.base import CRUDBase
from server.db.models import ProductTable
from server.schemas.product import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[ProductTable, ProductCreate, ProductUpdate]):
    def get_multi_by_shop_id(
        self,
        *,
        shop_id: Any,
        skip: int = 0,
        limit: int = 100,
        filter_parameters: Optional[List[str]],
        sort_parameters: Optional[List[str]],
        query_parameter: Optional[Any] = None,
    ) -> Tuple[List[ProductTable], str]:
        query = query_parameter
        if query is None:
            query = db.session.query(self.model).filter(self.model.shop_id == shop_id)

        if filter_parameters:
            for filter_parameter in filter_parameters:
                key, *value = filter_parameter.split(":", 1)
                if len(value) > 0:
                    val = value[0]
                    match key:
                        case "attribute_id":
                            query = query.join(ProductAttributeValueTable).filter(
                                ProductAttributeValueTable.attribute_id == val
                            )
                        case "option_id":
                            query = query.join(ProductAttributeValueTable).filter(
                                ProductAttributeValueTable.option_id == val
                            )
                        case "option_value_key":
                            query = (
                                query.join(ProductAttributeValueTable)
                                .join(
                                    AttributeOptionTable,
                                    ProductAttributeValueTable.option_id == AttributeOptionTable.id,
                                )
                                .filter(AttributeOptionTable.value_key.ilike(f"%{val}%"))
                            )
                        case "attribute_name":
                            query = (
                                query.join(ProductAttributeValueTable)
                                .join(AttributeTable, ProductAttributeValueTable.attribute_id == AttributeTable.id)
                                .join(
                                    AttributeTranslationTable,
                                    AttributeTable.id == AttributeTranslationTable.attribute_id,
                                )
                                .filter(
                                    or_(
                                        AttributeTranslationTable.main_name.ilike(f"%{val}%"),
                                        AttributeTranslationTable.alt1_name.ilike(f"%{val}%"),
                                        AttributeTranslationTable.alt2_name.ilike(f"%{val}%"),
                                    )
                                )
                            )
                        case _:
                            pass

        return self.get_multi(
            skip=skip,
            limit=limit,
            filter_parameters=filter_parameters,
            sort_parameters=sort_parameters,
            query_parameter=query,
        )


product_crud = CRUDProduct(ProductTable)
