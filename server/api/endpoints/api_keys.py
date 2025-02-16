from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from starlette.responses import Response

from server.api import deps
from server.api.deps import common_parameters
from server.crud.crud_api_key import api_key_crud
from server.db.models import UserTable
from server.schemas.api_key import APIKeyCreate, APIKeyInDBCreate, APIKeyInDBGet
from server.security import generate_api_key

router = APIRouter()


@router.get("/")
def get_multi(
    response: Response,
    shop_id: UUID,
    common: dict = Depends(common_parameters),
    current_user: UserTable = Depends(deps.get_current_active_superuser),
) -> List[APIKeyInDBGet]:
    """
    Retrieve all API keys for a shop.
    """
    api_keys, header_range = api_key_crud.get_multi_by_shop_id(
        shop_id=shop_id,
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = header_range
    return api_keys


@router.post("/")
def create_api_key(
    shop_id: UUID,
    current_user: UserTable = Depends(deps.get_current_active_superuser),
) -> APIKeyInDBCreate:
    """
    Create a new API key for a shop.
    """
    raw_key, hashed_key = generate_api_key()
    api_key_in = APIKeyCreate(shop_id=shop_id, hashed_key=hashed_key)
    db_obj = api_key_crud.create(obj_in=api_key_in)
    return APIKeyInDBCreate(**db_obj, api_key=raw_key)


@router.delete("/{api_key_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def revoke_api_key(
    api_key_id: UUID,
    current_user: UserTable = Depends(deps.get_current_active_superuser),
) -> None:
    """
    Revoke an API key for a shop.
    """
    try:
        api_key_crud.delete(api_key_id)
    except Exception as e:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail=f"{e.__cause__}")
