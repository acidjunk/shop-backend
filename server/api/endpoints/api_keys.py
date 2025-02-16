from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response

from server.api.deps import common_parameters
from server.crud.crud_api_key import api_key_crud
from server.db.models import UserTable
from server.schemas.api_key import APIKeyCreate, APIKeyInDBCreate, APIKeyInDBGet
from server.security import CustomCognitoToken, cognito_auth_required, generate_api_key

router = APIRouter()


@router.get("/")
def get_multi(
    response: Response,
    common: dict = Depends(common_parameters),
    token: CustomCognitoToken = Depends(cognito_auth_required),
) -> List[APIKeyInDBGet]:
    """
    Retrieve all API keys for a user.
    """
    api_keys, header_range = api_key_crud.get_multi(
        user_id=token.cognito_id,
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = header_range
    return api_keys


@router.post("/", status_code=HTTPStatus.CREATED)
def create_api_key(
    token: CustomCognitoToken = Depends(cognito_auth_required),
) -> APIKeyInDBCreate:
    """
    Create a new API key for a user.
    """
    raw_key, key_fingerprint, encrypted_key = generate_api_key()
    api_key_in = APIKeyCreate(user_id=token.cognito_id, fingerprint=key_fingerprint, encrypted_key=encrypted_key)
    db_obj = api_key_crud.create(obj_in=api_key_in)
    return APIKeyInDBCreate(
        id=db_obj.id,
        user_id=db_obj.user_id,
        created_at=db_obj.created_at,
        revoked_at=db_obj.revoked_at,
        api_key=raw_key,
    )


@router.delete("/{api_key_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def revoke_api_key(
    api_key_id: UUID,
    token: CustomCognitoToken = Depends(cognito_auth_required),
) -> None:
    """
    Revoke an API key for a shop.
    """
    try:
        api_key_crud.delete(UUID(token.cognito_id), api_key_id)
    except Exception as e:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail=f"{e.__cause__}")
