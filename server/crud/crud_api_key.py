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
from datetime import datetime, timezone
from typing import Any, List, Optional
from uuid import UUID

from server.crud.base import CRUDBase
from server.db import db
from server.db.models import APIKeyTable
from server.schemas.api_key import APIKeyCreate


class CRUDAPIKey(CRUDBase[APIKeyTable, APIKeyCreate, None]):
    def get_multi(
        self,
        *,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        filter_parameters: Optional[List[str]] = None,
        sort_parameters: Optional[List[str]] = None,
    ):
        query = db.session.query(self.model).filter(self.model.user_id == user_id)
        return super().get_multi(
            skip=skip,
            limit=limit,
            filter_parameters=filter_parameters,
            sort_parameters=sort_parameters,
            query_parameter=query,
        )

    def get_by_fingerprint(self, fingerprint: str) -> APIKeyTable | None:
        return db.session.query(self.model).filter(self.model.fingerprint == fingerprint).first()

    # this behaves more like a soft-delete
    def delete(self, user_id: UUID, id: UUID) -> None:
        db_obj = self.get(id)
        if not db_obj:
            raise ValueError("No matching API key found")

        # only allow the original user to revoke their own API keys
        if db_obj.user_id != user_id:
            # NOTE: we put the same generic error here, otherwise we might leak
            # info that there is an API key with this id
            raise ValueError("No matching API key found")

        if db_obj.revoked_at:
            return

        db_obj.revoked_at = datetime.now(timezone.utc)
        db.session.add(db_obj)
        db.session.commit()


api_key_crud = CRUDAPIKey(APIKeyTable)
