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
from server.db.models import RoleTable
from server.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[RoleTable, RoleCreate, RoleUpdate]):
    def get_by_name(self, *, name: str) -> Optional[RoleTable]:
        return RoleTable.query.filter(RoleTable.name == name).first()


role_crud = CRUDRole(RoleTable)
