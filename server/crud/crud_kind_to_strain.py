from typing import Optional

from server.crud.base import CRUDBase
from server.db.models import KindToStrain
from server.schemas.kind_to_strain import KindToStrainCreate, KindToStrainUpdate


class CRUDKindToStrain(CRUDBase[KindToStrain, KindToStrainCreate, KindToStrainUpdate]):
    def get_relation(self, *, kind, strain) -> Optional[KindToStrain]:
        return KindToStrain.query.filter_by(kind_id=kind.id).filter_by(strain_id=strain.id).all()

    def get_relation_by_kind_strain(self, *, kind_id, strain_id) -> Optional[KindToStrain]:
        return KindToStrain.query.filter_by(kind_id=kind_id).filter_by(strain_id=strain_id).first()

    def get_relations_by_kind(self, *, kind_id) -> [Optional[KindToStrain]]:
        return KindToStrain.query.filter_by(kind_id=kind_id).all()


kind_to_strain_crud = CRUDKindToStrain(KindToStrain)
