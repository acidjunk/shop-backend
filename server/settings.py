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

import secrets
import string
from typing import Any, Dict, List, Optional

from pydantic import BaseSettings, validator
from pydantic.networks import EmailStr, PostgresDsn


class AppSettings(BaseSettings):
    """
    Deal with global app settings.

    The goal is to provide some sensible default for developers here. All constants can be
    overloaded via ENV vars. The validators are used to ensure that you get readable error
    messages when an ENV var isn't correctly formated; for example when you provide an incorrect
    formatted DATABASE_URI.

    ".env" loading is also supported. FastAPI will autoload and ".env" file if one can be found

    In production you need to provide a lot stuff via the ENV. At least DATABASE_URI, SESSION_SECRET,
    TESTING, LOGLEVEL and EMAILS_ENABLED + mail server settings if needed.
    """

    PROJECT_NAME: str = "Prijslijst backend"
    TESTING: bool = True
    EMAILS_ENABLED: bool = False
    # SESSION_SECRET: str = "".join(secrets.choice(string.ascii_letters) for i in range(16))  # noqa: S311
    SESSION_SECRET: str = "CHANGEME"
    # OAUTH settings
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    JWT_ALGORITHM = "HS256"
    # CORS settings
    CORS_ORIGINS: str = "*"
    CORS_ALLOW_METHODS: List[str] = [
        "GET",
        "PUT",
        "PATCH",
        "POST",
        "DELETE",
        "OPTIONS",
        "HEAD",
    ]
    # Todo: find correct header settings for upload of file with:
    #  No 'Access-Control-Allow-Origin' header is present on the requested resource.
    CORS_ALLOW_HEADERS: List[str] = [
        "If-None-Match",
        "Authorization",
        "If-Match",
        "Content-Type",
        "Access-Control-Allow-Origin",
    ]
    # CORS_ALLOW_HEADERS: List[str] = ["*"]

    CORS_EXPOSE_HEADERS: List[str] = [
        "Cache-Control",
        "Content-Language",
        "Content-Length",
        "Content-Type",
        "Expires",
        "Last-Modified",
        "Pragma",
        "Content-Range",
        "ETag",
    ]
    SWAGGER_PORT: int = 8080
    ENVIRONMENT: str = "local"
    SWAGGER_HOST: str = "localhost"
    GUI_URI: str = "http://localhost:3000"
    # DB (probably only postgres for now; we use UUID postgres dialect for the ID's)
    DATABASE_URI: str = "postgresql://pricelist:pricelist@localhost/pricelist"

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    MAX_WORKERS: int = 5
    CACHE_HOST: str = "127.0.0.1"
    CACHE_PORT: int = 6379
    POST_MORTEM_DEBUGGER: str = ""
    SERVICE_NAME: str = "Prijslijst backend"
    LOGGING_HOST: str = "localhost"
    LOG_LEVEL: str = "DEBUG"

    # Mail settings
    SMTP_TLS: bool = True
    SMTP_ENABLED: bool = False
    SMTP_PORT: Optional[int] = 587
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = "no-reply@prijslijst.info"
    EMAILS_FROM_NAME: Optional[str] = "Prijslijst Backend"
    EMAILS_CC: Optional[str] = "no-reply@prijslijst.info"

    FIRST_SUPERUSER = "NAME"
    FIRST_SUPERUSER_PASSWORD = "JePass"
    FIRST_SUPERUSER_ROLE = "admin"
    FIRST_SUPERUSER_ROLE_DESCRIPTION = "God Mode!"

    @validator("EMAILS_FROM_NAME")
    def get_project_name(cls, v: Optional[str], values: Dict[str, Any]) -> str:
        if not v:
            return values["PROJECT_NAME"]
        return v

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    # Todo: check path. The original had one extra folder "app"
    EMAIL_TEMPLATES_DIR: str = "server/email-templates/build"

    @validator("EMAILS_ENABLED", pre=True)
    def get_emails_enabled(cls, v: bool, values: Dict[str, Any]) -> bool:
        return bool(values.get("SMTP_HOST") and values.get("SMTP_PORT") and values.get("EMAILS_FROM_EMAIL"))

    EMAIL_TEST_USER: EmailStr = "test@example.com"  # type: ignore

    # AWS Lambda settings
    LAMBDA_ACCESS_KEY_ID = "CHANGEME"
    LAMBDA_SECRET_ACCESS_KEY = "CHANGEME"

    # TODO: think of better naming convention
    # Production S3 bucket
    S3_BUCKET_IMAGES_ACCESS_KEY_ID: str = "CHANGEME"
    S3_BUCKET_IMAGES_SECRET_ACCESS_KEY: str = "CHANGEME"
    S3_BUCKET_IMAGES_NAME = "CHANGE_THIS_FOR_UPLOAD"  # used to store images and to generate signed URI's

    S3_BUCKET_DOWNLOADS_NAME = "CHANGE_THIS_FOR_UPLOAD"
    S3_BUCKET_DOWNLOADS_ACCESS_KEY_ID: str = "CHANGEME"
    S3_BUCKET_DOWNLOADS_SECRET_ACCESS_KEY: str = "CHANGEME"

    # Temporary S3 where images go before they are moved to the production bucket
    S3_BUCKET_TEMPORARY_NAME: str = "CHANGEME"
    S3_TEMPORARY_ACCESS_KEY_ID: str = "CHANGEME"
    S3_TEMPORARY_ACCESS_KEY: str = "CHANGEME"

    class Config:
        env_file = ".env"


app_settings = AppSettings()
