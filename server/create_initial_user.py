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
import structlog

from server.crud.crud_role import role_crud
from server.crud.crud_role_user import role_user_crud
from server.crud.crud_user import user_crud
from server.schemas import RoleCreate, UserCreate
from server.schemas.role_user import RoleUserCreate
from server.settings import app_settings

logger = structlog.get_logger(__name__)


def main() -> None:
    logger.info("Creating initial user")
    superuser = user_crud.get_by_email(email=app_settings.FIRST_SUPERUSER)
    role_admin = role_crud.get_by_name(name=app_settings.FIRST_SUPERUSER_ROLE)
    if not role_admin:
        role_in = RoleCreate(
            name=app_settings.FIRST_SUPERUSER_ROLE, description=app_settings.FIRST_SUPERUSER_ROLE_DESCRIPTION
        )
        role_admin = role_crud.create(obj_in=role_in)
        logger.info("Initial role created")
    else:
        logger.info("Skipping role creation: role already exists")

    if not superuser:
        user_in = UserCreate(
            email=app_settings.FIRST_SUPERUSER,
            username=app_settings.FIRST_SUPERUSER,
            password=app_settings.FIRST_SUPERUSER_PASSWORD,
        )
        superuser = user_crud.create(obj_in=user_in)  # noqa: F841
        role_user_in = RoleUserCreate(user_id=superuser.id, role_id=role_admin.id)
        role_user_crud.create(obj_in=role_user_in)
        logger.info("Initial superuser created")
    else:
        logger.info("Skipping creation: superuser already exists")


if __name__ == "__main__":
    main()
