from typing import Optional

from server.crud.base import CRUDBase
from server.db.models import Flavor
from server.schemas.flavor import FlavorCreate, FlavorUpdate


class CRUDFlavor(CRUDBase[Flavor, FlavorCreate, FlavorUpdate]):
    def get_flavor_by_name(self, *, name) -> Optional[Flavor]:
        return Flavor.query.filter_by(name=name).first()


flavor_crud = CRUDFlavor(Flavor)
