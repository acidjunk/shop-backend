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
from uuid import UUID

from server.crud.base import CRUDBase
from server.db.models import TagTable
from server.schemas.tag import TagCreate, TagUpdate


class CRUDTag(CRUDBase[TagTable, TagCreate, TagUpdate]):
    def get_by_name(self, *, name: str, shop_id: UUID) -> Optional[TagTable]:
        return TagTable.query.filter(TagTable.shop_id == shop_id).filter(TagTable.name == name).first()


tag_crud = CRUDTag(TagTable)
