from server.crud.base import CRUDBase
from server.db.models import Table
from server.schemas.table import TableCreate, TableUpdate


class CRUDTable(CRUDBase[Table, TableCreate, TableUpdate]):
    pass


table_crud = CRUDTable(Table)
