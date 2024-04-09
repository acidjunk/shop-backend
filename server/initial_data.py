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

from server.crud import user_crud
from server.db import db
from server.schemas import UserCreate
from server.settings import app_settings

logger = structlog.get_logger(__name__)


def main() -> None:
    logger.info("Creating initial data")
    user = user_crud.get_by_email(email=app_settings.FIRST_SUPERUSER)
    if not user:
        user_in = UserCreate(
            email=app_settings.FIRST_SUPERUSER,
            username=app_settings.FIRST_SUPERUSER,
            password=app_settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
        )
        user = user_crud.create(obj_in=user_in)  # noqa: F841
        logger.info("Initial data created")
    logger.info("Skipping creation: user already exists")


if __name__ == "__main__":
    main()
