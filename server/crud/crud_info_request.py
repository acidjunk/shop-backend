from server.crud.base import CRUDBase
from server.db.models import InfoRequestTable
from server.schemas.info_request import InfoRequestCreate


class CRUDInfoRequest(CRUDBase[InfoRequestTable, InfoRequestCreate, None]):
    pass


info_request_crud = CRUDInfoRequest(InfoRequestTable)
