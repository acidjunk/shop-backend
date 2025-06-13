from http import HTTPStatus
from typing import Any

import structlog
from fastapi import APIRouter, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.param_functions import Body
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from server.crud.crud_faq import faq_crud
from server.schemas.faq import FaqCreate, FaqCreated

# Set up structured logging with structlog
logger = structlog.get_logger(__name__)

# Create the API router
router = APIRouter()


@router.post("/", response_model=FaqCreated, status_code=HTTPStatus.CREATED)
def create(data: FaqCreate = Body(...)) -> Any:
    try:
        logger.info("Creating FAQ entry", data=data)
        faq = faq_crud.create(obj_in=data)
        return faq

    except ValidationError as ve:
        logger.error("Validation error occurred", error=str(ve), data=data)
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Incorrect input format or missing fields in the request.",
        )

    except IntegrityError as ie:
        logger.error("Integrity constraint violated", error=str(ie), data=data)
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Duplicate or constraint violation. The FAQ entry may already exist.",
        )

    except RequestValidationError as rve:
        logger.error("Bad request error", error=str(rve), data=data)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Malformed request or invalid data.",
        )

    except Exception as e:
        logger.error("Unexpected error occurred", error=str(e), data=data)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )
