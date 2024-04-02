from typing import Optional

from server.crud.base import CRUDBase
from server.db.models import KindToFlavor
from server.schemas.kind_to_flavor import KindToFlavorCreate, KindToFlavorUpdate


class CRUDKindToFlavor(CRUDBase[KindToFlavor, KindToFlavorCreate, KindToFlavorUpdate]):
    def get_relation(self, *, kind, tag) -> Optional[KindToFlavor]:
        return KindToFlavor.query.filter_by(kind_id=kind.id).filter_by(tag_id=tag.id).all()

    def get_relation_by_kind_flavor(self, *, kind_id, flavor_id) -> Optional[KindToFlavor]:
        return KindToFlavor.query.filter_by(kind_id=kind_id).filter_by(flavor_id=flavor_id).first()

    def get_relations_by_kind(self, *, kind_id) -> [Optional[KindToFlavor]]:
        return KindToFlavor.query.filter_by(kind_id=kind_id).all()


kind_to_flavor_crud = CRUDKindToFlavor(KindToFlavor)
