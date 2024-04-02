from typing import Optional

from server.crud.base import CRUDBase
from server.db.models import KindToTag
from server.schemas.kind_to_tag import KindToTagCreate, KindToTagUpdate


class CRUDKindToTag(CRUDBase[KindToTag, KindToTagCreate, KindToTagUpdate]):
    def get_relation(self, *, kind, tag) -> Optional[KindToTag]:
        return KindToTag.query.filter_by(kind_id=kind.id).filter_by(tag_id=tag.id).all()

    def get_relation_by_kind_tag(self, *, kind_id, tag_id) -> Optional[KindToTag]:
        return KindToTag.query.filter_by(kind_id=kind_id).filter_by(tag_id=tag_id).first()

    def get_relations_by_kind(self, *, kind_id) -> [Optional[KindToTag]]:
        return KindToTag.query.filter_by(kind_id=kind_id).all()


kind_to_tag_crud = CRUDKindToTag(KindToTag)
