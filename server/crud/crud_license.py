from typing import Optional

from server.crud.base import CRUDBase
from server.db.models import License
from server.schemas.license import LicenseCreate, LicenseUpdate


class CRUDLicense(CRUDBase[License, LicenseUpdate, LicenseCreate]):
    def get_by_improviser_user_id(self, *, improviser_user_id: str) -> Optional[License]:
        return License.query.filter(License.improviser_user == improviser_user_id).first()


license_crud = CRUDLicense(License)
