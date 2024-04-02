from typing import Dict, List, Union

from fastapi import Depends, HTTPException, status
from fastapi.param_functions import Query
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import ValidationError

from server.crud.crud_role import role_crud
from server.crud.crud_user import user_crud
from server.db.models import UsersTable
from server.settings import app_settings

reusable_oauth = OAuth2PasswordBearer(tokenUrl=f"/v1/login/access-token")


async def common_parameters(
    skip: int = 0,
    limit: int = 100,
    filter: List[str] = Query(
        None,
        description="This filter can accept search query's like `key:value` and will split on the `:`. If it "
        "detects more than one `:`, or does not find a `:` it will search for the string in all columns.",
    ),
    sort: List[str] = Query(
        None,
        description="The sort will accept parameters like `col:ASC` or `col:DESC` and will split on the `:`. "
        "If it does not find a `:` it will sort ascending on that column.",
    ),
) -> Dict[str, Union[List[str], int]]:
    return {"skip": skip, "limit": limit, "filter": filter, "sort": sort}


def get_current_user(token: str = Depends(reusable_oauth)) -> UsersTable:
    try:
        payload = jwt.decode(token, app_settings.SESSION_SECRET, algorithms=[app_settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
    except (jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = user_crud.get(id=user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def get_current_active_user(
    current_user: UsersTable = Depends(get_current_user),
) -> UsersTable:
    if not user_crud.is_active(current_user):
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user


def get_current_active_superuser(
    current_user: UsersTable = Depends(get_current_user),
) -> UsersTable:
    if not user_crud.is_superuser(current_user):
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user


def get_current_active_employee(
    current_user: UsersTable = Depends(get_current_user),
) -> UsersTable:
    if not user_crud.is_superuser(current_user) and not role_crud.get_by_name(name="employee") in current_user.roles:
        raise HTTPException(status_code=403, detail="The user does need at least employee permissions")
    return current_user
