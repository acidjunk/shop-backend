# Copyright 2024 René Dohmen <acidjunk@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Optional

from server.crud.base import CRUDBase
from server.db.models import License
from server.schemas.license import LicenseCreate, LicenseUpdate


class CRUDLicense(CRUDBase[License, LicenseUpdate, LicenseCreate]):
    def get_by_improviser_user_id(self, *, improviser_user_id: str) -> Optional[License]:
        return License.query.filter(License.improviser_user == improviser_user_id).first()


license_crud = CRUDLicense(License)
