from server.crud.base import CRUDBase
from server.db.models import FaqTable
from server.schemas.faq import FaqCreate, FaqUpdate


class CRUDFaq(CRUDBase[FaqTable, FaqCreate, FaqUpdate]):
    pass


faq_crud = CRUDFaq(FaqTable)
