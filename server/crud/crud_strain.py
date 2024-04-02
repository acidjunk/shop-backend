from typing import Optional

from server.crud.base import CRUDBase
from server.db.models import Strain
from server.schemas.strain import StrainCreate, StrainUpdate


class CRUDStrain(CRUDBase[Strain, StrainCreate, StrainUpdate]):
    def get_by_name(self, *, name: str) -> Optional[Strain]:
        return Strain.query.filter(Strain.name == name).first()


strain_crud = CRUDStrain(Strain)
