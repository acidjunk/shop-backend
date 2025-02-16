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
from datetime import datetime, timedelta
from typing import Any, Optional, Union

from fastapi import HTTPException, Request, Security
from fastapi.param_functions import Depends
from fastapi.security import APIKeyHeader
from fastapi_cognito import CognitoAuth, CognitoSettings, CognitoToken
from jose import jwt
from passlib.context import CryptContext
from structlog import get_logger

from server.crud.crud_api_key import api_key_crud
from server.db.models import APIKeyTable
from server.settings import app_settings, auth_settings

logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
cognito_eu = CognitoAuth(settings=CognitoSettings.from_global_settings(auth_settings))
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def api_key_auth_required(error: bool = True):
    """
    Checks if a valid API key is present in the request headers.

    :param bool error: If True, raises an HTTPException if no valid API key is present, otherwise returns None.
    """

    def check_api_key(api_key: Optional[str] = Security(api_key_header)):
        try:
            if not api_key:
                raise HTTPException(status_code=401, detail="API key required")

            api_key_record = api_key_crud.get_by_hashed_key(api_key)
            if (
                not api_key_record
                or api_key_record.revoked_at
                or not pwd_context.verify(api_key, api_key_record.hashed_key)
            ):
                raise HTTPException(status_code=401, detail="Invalid API key")

            return api_key_record
        except HTTPException as e:
            if error:
                raise e
            else:
                return None

    return check_api_key


def cognito_auth_required(error: bool = True):
    """
    Checks if a valid Cognito JWT token is provided in the request.

    :param bool error: If True, raises an HTTPException if no valid JWT token is present, otherwise returns None.
    """

    async def check_cognito_token(req: Request):
        try:
            token = await cognito_eu.auth_required(req)

            # check if we are dealing with a plain user token or M2M token
            if token.client_id == app_settings.AWS_COGNITO_CLIENT_ID:
                # No need to check scopes for user tokens
                return token

            if token.scope != "api":
                # M2M tokens: check required scope
                raise HTTPException(status_code=401, detail="Insufficient permissions")

            return token
        except HTTPException as e:
            if error:
                raise e
            else:
                return None

    return check_cognito_token


# We make use of error=False to postpone the dependencies from throwing.
# This way we can check if either of the dependencies succeeded.
def auth_required(
    token: CognitoToken | None = Depends(cognito_auth_required(error=False)),
    api_key: APIKeyTable | None = Depends(api_key_auth_required(error=False)),
):
    if not token and not api_key:
        raise HTTPException(status_code=401, detail="Insufficient permissions")

    return token or api_key


def create_access_token(subject: Union[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=app_settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, app_settings.SESSION_SECRET, algorithm=app_settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_api_key():
    raw_key = secrets.token_urlsafe(32)
    hashed_key = pwd_context.hash(raw_key)
    return raw_key, hashed_key
