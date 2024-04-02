from server.crud.base import CRUDBase
from server.db.models import Kind
from server.schemas.kind import KindCreate, KindUpdate


class CRUDKind(CRUDBase[Kind, KindCreate, KindUpdate]):
    pass


kind_crud = CRUDKind(Kind)
