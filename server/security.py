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
from datetime import datetime, timedelta
from typing import Any, Optional, Union

from fastapi import HTTPException, Security
from fastapi.param_functions import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi_cognito import CognitoAuth, CognitoSettings, CognitoToken
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, HttpUrl
from structlog import get_logger

from server.settings import app_settings, auth_settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
security = HTTPBearer()


def auth_required(
    token: CognitoToken = Depends(cognito_eu.auth_required),
    # Next line is needed to show all endpoints with auth properly under /docs
    _: HTTPAuthorizationCredentials = Security(security),
):
    if token.client_id == app_settings.AWS_COGNITO_CLIENT_ID:
        # No need to check scopes for user tokens
        return token

    # M2M tokens: check required scope
    if token.scope.endswith("/api"):
        return token

    raise HTTPException(status_code=401, detail="Invalid OAuth2 scope")


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
