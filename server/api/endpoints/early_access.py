from http import HTTPStatus
from typing import Any, List, Optional
from uuid import UUID
from fastapi.param_functions import Body
import structlog
from fastapi import APIRouter

from pydantic import EmailStr

from server.crud.crud_early_access import early_access_crud
from server.schemas.early_access import EarlyAccessCreate

logger = structlog.get_logger(__name__)

router = APIRouter()

@router.post("/", response_model=None,status_code=HTTPStatus.CREATED)
def create(data: EarlyAccessCreate = Body(...)) -> None:
    logger.info("Saving early access", data=data)
    logger.info("asdasd")
    early_access = early_access_crud.create(data)
    return early_access



