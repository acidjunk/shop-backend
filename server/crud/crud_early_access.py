from server.crud.base import CRUDBase
from server.db.models import earlyAccessTable
from server.schemas.early_access import EarlyAccessCreate


class CRUDEarlyAccess(CRUDBase[earlyAccessTable, EarlyAccessCreate, None]):
    pass

early_access_crud = CRUDEarlyAccess(earlyAccessTable)