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
