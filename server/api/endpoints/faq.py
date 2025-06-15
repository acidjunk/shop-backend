from http import HTTPStatus
from typing import Any
from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Body
from sqlalchemy.exc import IntegrityError

from server.crud.crud_faq import faq_crud
from server.db.models import FaqTable
from server.schemas.faq import FaqCreate, FaqCreated, FaqUpdate, FaqUpdated

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=FaqCreated, status_code=HTTPStatus.CREATED)
def create(data: FaqCreate = Body(...)) -> Any:
    try:
        logger.info("Creating FAQ entry", data=data)

        existing_faq = FaqTable.query.filter_by(question=data.question).first()
        if existing_faq:
            logger.error("FAQ question already exists", question=data.question)
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="A FAQ entry with this question already exists.",
            )

        faq = faq_crud.create(obj_in=data)
        return faq

    except IntegrityError as ie:
        logger.error("Integrity constraint violated", error=str(ie), data=data)
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Duplicate or constraint violation. The FAQ entry may already exist.",
        )

    except Exception as e:
        logger.error("Unexpected error occurred", error=str(e), data=data)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}",
        )


@router.put("/{faq_id}", response_model=FaqUpdated, status_code=HTTPStatus.CREATED)
def update(*, faq_id: UUID, item_in: FaqUpdate) -> FaqUpdated:
    try:
        faq = faq_crud.get(faq_id)
        if not faq:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="FAQ entry not found")

        duplicate = FaqTable.query.filter(FaqTable.question == item_in.question, FaqTable.id != faq_id).first()
        if duplicate:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail="Another FAQ entry with the same question already exists.",
            )

        faq = faq_crud.update(db_obj=faq, obj_in=item_in)

        updated_faq = FaqUpdated(
            id=faq.id,
            question=faq.question,
            answer=faq.answer,
            category=faq.category,
        )

        return updated_faq

    except IntegrityError as ie:
        logger.error("Integrity constraint violated", error=str(ie), data=item_in)
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="Database constraint violated.",
        )

    except Exception as e:
        logger.error("Unexpected error during FAQ update", error=str(e), data=item_in)
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred while updating FAQ.",
        )
