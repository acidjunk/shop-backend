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
from hashlib import sha256
from typing import Any, Optional, Union

from fastapi import HTTPException, Request, Security
from fastapi.param_functions import Depends
from fastapi.security import APIKeyHeader
from fastapi_cognito import CognitoAuth, CognitoSettings, CognitoToken
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, HttpUrl
from structlog import get_logger

from server.crud.crud_api_key import api_key_crud
from server.db.models import APIKeyTable
from server.settings import app_settings, auth_settings

logger = get_logger(__name__)


class CustomCognitoToken(BaseModel):
    origin_jti: Optional[str] = None
    cognito_id: str = Field(alias="sub")
    event_id: Optional[str] = None
    token_use: str
    scope: str
    auth_time: int
    iss: HttpUrl
    exp: int
    iat: int
    jti: str
    client_id: str
    username: str | None = None


cognito_eu = CognitoAuth(settings=CognitoSettings.from_global_settings(auth_settings), custom_model=CustomCognitoToken)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def api_key_auth_required(api_key: Optional[str] = Security(api_key_header)) -> APIKeyTable:
    """
    Checks if a valid API key is present in the request headers.

    :param bool error: If True, raises an HTTPException if no valid API key is present, otherwise returns None.
    """
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    # Look up API key by fingerprint
    key_fingerprint = get_api_key_fingerprint(api_key)
    api_key_record = api_key_crud.get_by_fingerprint(key_fingerprint)

    # Check if API key not revoked
    if not api_key_record or api_key_record.revoked_at:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Verify API key
    if not pwd_context.verify(api_key, api_key_record.encrypted_key):
        raise HTTPException(status_code=401, detail="Invalid API key")

    # TODO: Right now we rely on AWS Cognito during API key creation time,
    # but we should check if the api key is valid (corresponding user still active) as well!

    return api_key_record


async def cognito_auth_required(request: Request) -> CustomCognitoToken:
    """
    Checks if a valid Cognito JWT token is provided in the request.
    """
    token = await cognito_eu.auth_required(request)

    # check if we are dealing with a plain user token or M2M token
    if token.client_id == app_settings.AWS_COGNITO_CLIENT_ID:
        # No need to check scopes for user tokens
        return token

    if token.scope.endswith("/api"):
        return token

    raise HTTPException(status_code=401, detail="Invalid OAuth2 scope")


async def auth_required(request: Request, api_key: Optional[str] = Security(api_key_header)):
    if api_key:
        # If API key is present, perform auth using the API key
        return api_key_auth_required(api_key)

    # Otherwise check auth via cognito
    return await cognito_auth_required(request)


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


def get_api_key_fingerprint(api_key: str) -> str:
    return sha256(api_key.encode()).hexdigest()


def generate_api_key():
    raw_key = secrets.token_urlsafe(32)
    key_fingerprint = get_api_key_fingerprint(raw_key)
    encrypted_key = pwd_context.hash(raw_key)
    return raw_key, key_fingerprint, encrypted_key
