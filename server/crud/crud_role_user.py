from server.crud.base import CRUDBase
from server.db.models import RolesUsersTable
from server.schemas.role_user import RoleUserCreate, RoleUserUpdate


class CRUDRoleUser(CRUDBase[RolesUsersTable, RoleUserCreate, RoleUserUpdate]):
    pass


role_user_crud = CRUDRoleUser(RolesUsersTable)
