from typing import Optional

from server.crud.base import CRUDBase
from server.db.models import Tag
from server.schemas.tag import TagCreate, TagUpdate


class CRUDTag(CRUDBase[Tag, TagCreate, TagUpdate]):
    def get_by_name(self, *, name: str) -> Optional[Tag]:
        return Tag.query.filter(Tag.name == name).first()


tag_crud = CRUDTag(Tag)
