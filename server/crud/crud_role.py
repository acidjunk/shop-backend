from typing import Optional

from server.crud.base import CRUDBase
from server.db.models import RolesTable
from server.schemas.role import RoleCreate, RoleUpdate


class CRUDRole(CRUDBase[RolesTable, RoleCreate, RoleUpdate]):
    def get_by_name(self, *, name: str) -> Optional[RolesTable]:
        return RolesTable.query.filter(RolesTable.name == name).first()


role_crud = CRUDRole(RolesTable)
