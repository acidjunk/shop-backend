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
from uuid import UUID

from server.crud.base import CRUDBase
from server.db.models import AttributeTable
from server.schemas.attribute import AttributeCreate, AttributeUpdate


class CRUDAttribute(CRUDBase[AttributeTable, AttributeCreate, AttributeUpdate]):
    def get_by_name(self, *, name: str, shop_id: UUID) -> Optional[AttributeTable]:
        return (
            AttributeTable.query.filter(AttributeTable.shop_id == shop_id).filter(AttributeTable.name == name).first()
        )


attribute_crud = CRUDAttribute(AttributeTable)
