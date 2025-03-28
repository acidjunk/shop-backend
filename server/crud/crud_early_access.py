from server.crud.base import CRUDBase
from server.db.models import EarlyAccessTable
from server.schemas.early_access import EarlyAccessCreate


class CRUDEarlyAccess(CRUDBase[EarlyAccessTable, EarlyAccessCreate, None]):
    pass


early_access_crud = CRUDEarlyAccess(EarlyAccessTable)
