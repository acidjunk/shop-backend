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

import structlog
from fastapi.encoders import jsonable_encoder

from server.crud.base import CRUDBase
from server.db import db
from server.db.models import UsersTable
from server.schemas.user import UserCreate, UserUpdate
from server.security import get_password_hash, verify_password

logger = structlog.get_logger(__name__)


class CRUDUser(CRUDBase[UsersTable, UserCreate, UserUpdate]):
    def get_by_email(self, *, email: str) -> Optional[UsersTable]:
        return UsersTable.query.filter(UsersTable.email == email).first()

    def get_by_username(self, *, username: str) -> Optional[UsersTable]:
        return UsersTable.query.filter(UsersTable.username == username).first()

    def get(self, id: Optional[str] = None) -> Optional[UsersTable]:
        user = UsersTable.query.get(id)
        return user

    def create(self, *, obj_in: UserCreate) -> UsersTable:
        db_obj = UsersTable(
            email=obj_in.email,
            password=get_password_hash(obj_in.password),
            username=obj_in.username,
            active=obj_in.is_active,
        )
        db.session.add(db_obj)
        db.session.commit()
        return db_obj

    def update(self, *, db_obj: UsersTable, obj_in: UserUpdate) -> UsersTable:
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["password"] = hashed_password
        for field in obj_data:
            if field != "id" and field in update_data:
                setattr(db_obj, field, update_data[field])
        db.session.add(db_obj)
        db.session.commit()
        db.session.refresh(db_obj)
        return db_obj

    def authenticate(self, *, username: str, password: str) -> Optional[UsersTable]:
        # logger.log("AUth requested", username=username)
        user = self.get_by_username(username=username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    def is_active(self, user: UsersTable) -> bool:
        return user.active

    def is_superuser(self, user: UsersTable) -> bool:
        return user.is_superuser


user_crud = CRUDUser(UsersTable)
