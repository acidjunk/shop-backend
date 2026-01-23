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
from server.db.models import AttributeOptionTable
from server.schemas.attribute_option import AttributeOptionCreate, AttributeOptionUpdate


class CRUDAttributeOption(CRUDBase[AttributeOptionTable, AttributeOptionCreate, AttributeOptionUpdate]):
    def get_by_value_key(self, *, attribute_id, value_key: str) -> Optional[AttributeOptionTable]:
        return (
            AttributeOptionTable.query.filter(AttributeOptionTable.attribute_id == attribute_id)
            .filter(AttributeOptionTable.value_key == value_key)
            .first()
        )


attribute_option_crud = CRUDAttributeOption(AttributeOptionTable)
