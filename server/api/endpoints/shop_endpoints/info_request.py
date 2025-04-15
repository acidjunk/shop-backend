from http import HTTPStatus
from typing import Any

import structlog
from fastapi import APIRouter, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.param_functions import Body
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from server.api.helpers import load
from server.crud.crud_info_request import info_request_crud
from server.crud.crud_product import product_crud
from server.db.models import ShopTable
from server.mail import generate_confirmation_mail, send_mail
from server.schemas.info_request import InfoRequestCreate
from server.settings import mail_settings
from server.utils.types import MailAddress, MailType

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create_info_request(data: InfoRequestCreate = Body(...)) -> Any:
    try:
        logger.info("Saving early access", data=data)
        info_request_crud.create(obj_in=data)

        product = product_crud.get_id_by_shop_id(data.shop_id, data.product_id)
        shop = load(ShopTable, data.shop_id)

        if product is None or shop is None:
            raise HTTPException(
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                detail="The product or shop does not exist.",
            )

        contact_persons = [MailAddress(email=data.email, name="")]

        confirmation_mail = generate_confirmation_mail(product, MailType.INFO, shop.name, contact_persons, None, None)
        if mail_settings.SHOP_MAIL_ENABLED:
            logger.info("Sending info mail", email=data.email)
            send_mail(confirmation_mail)
        else:
            logger.info("Sending the email is disabled for this specific step, not actually sending it.")
        return {"confirmation_mail": confirmation_mail}

    except ValidationError as ve:
        # Log the validation error
        logger.error("Validation error occurred", error=str(ve), data=data)
        # Raise 422 for incorrect input format
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="Incorrect input format or missing fields in the request.",
        )

    except IntegrityError as ie:
        # Log the duplicate entry error
        logger.error("Duplicate entry error", error=str(ie), data=data)
        # Raise 409 for duplicate entry (e.g., unique constraint violation)
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Duplicate entry. The record already exists.",
        )

    except RequestValidationError as rve:
        # Log the 400 Bad Request error
        logger.error("Bad request error", error=str(rve), data=data)
        # Raise 400 for bad requests (malformed or incomplete data)
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Malformed request or invalid data.",
        )

    except Exception as e:
        # Log the unexpected error
        logger.error("Unexpected error occurred", error=str(e), data=data)
        # Raise 500 for unexpected errors
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )
