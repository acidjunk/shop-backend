# Copyright 2025 Luc Tielen <luc.tielen@gmail.com>
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
from datetime import datetime
from uuid import UUID

from server.crud.base import CRUDBase
from server.db import db
from server.db.models import APIKeyTable
from server.schemas.api_key import APIKeyCreate, APIKeyUpdate


class CRUDAPIKey(CRUDBase[APIKeyTable, APIKeyCreate, None]):
    def get_multi_by_shop_id(self, shop_id: UUID):
        return db.session.query(APIKeyTable).filter(APIKeyTable.shop_id == shop_id).all()

    def get_by_hashed_key(self, hashed_key: str):
        return db.session.query(APIKeyTable).filter(APIKeyTable.hashed_key == hashed_key).first()

    # this behaves more like a soft-delete
    def delete(self, id: UUID):
        db_obj = self.get(id)
        db_obj.revoked_at = db_obj.revoked_at or datetime.utcnow()
        db.session.add(db_obj)
        db.session.commit()
        return db_obj


api_key_crud = CRUDAPIKey(APIKeyTable)
