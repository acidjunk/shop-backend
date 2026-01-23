from http import HTTPStatus
from typing import List
from uuid import UUID

import structlog
from fastapi import APIRouter
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud.crud_attribute import attribute_crud
from server.crud.crud_attribute_option import attribute_option_crud
from server.db import db
from server.db.models import AttributeOptionTable
from server.schemas.attribute_option import (
    AttributeOptionBase,
    AttributeOptionCreate,
    AttributeOptionSchema,
    AttributeOptionUpdate,
)

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[AttributeOptionSchema])
def list_options(
    shop_id: UUID, attribute_id: UUID, response: Response, common: dict = Depends(common_parameters)
) -> List[AttributeOptionSchema]:
    """List options for an attribute within a shop."""
    # Ensure attribute belongs to shop
    attribute = attribute_crud.get_id_by_shop_id(shop_id=shop_id, id=attribute_id)
    if not attribute:
        raise_status(HTTPStatus.NOT_FOUND, f"Attribute with id {attribute_id} not found for this shop")

    query = db.session.query(AttributeOptionTable).filter(AttributeOptionTable.attribute_id == attribute_id)
    results, content_range = attribute_option_crud.get_multi(
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
        query_parameter=query,
    )
    response.headers["Content-Range"] = content_range
    return results


@router.get("/{option_id}", response_model=AttributeOptionSchema)
def get_option(shop_id: UUID, attribute_id: UUID, option_id: UUID) -> AttributeOptionSchema:
    # Ensure attribute belongs to shop
    attribute = attribute_crud.get_id_by_shop_id(shop_id=shop_id, id=attribute_id)
    if not attribute:
        raise_status(HTTPStatus.NOT_FOUND, f"Attribute with id {attribute_id} not found for this shop")

    option = attribute_option_crud.get(id=option_id)
    if not option or option.attribute_id != attribute_id:
        raise_status(HTTPStatus.NOT_FOUND, f"Option with id {option_id} not found for this attribute")
    return option


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create_option(shop_id: UUID, attribute_id: UUID, data: AttributeOptionCreate = Body(...)) -> None:
    """
    Create a new option for an attribute within a shop.
    Validates that the attribute exists and belongs to the given shop.
    The body must contain value_key; attribute_id from the path will be used.
    """
    # Ensure the attribute exists under the shop
    attribute = attribute_crud.get_id_by_shop_id(shop_id=shop_id, id=attribute_id)
    if not attribute:
        raise_status(HTTPStatus.NOT_FOUND, f"Attribute with id {attribute_id} not found for this shop")

    # Override attribute_id from path to avoid spoofing
    payload = AttributeOptionBase(attribute_id=attribute_id, value_key=data.value_key)
    logger.info("Saving attribute option", attribute_id=str(attribute_id), value_key=payload.value_key)

    # TODO it now throws a 500 if it's not unique (DB unique constraint)
    option = attribute_option_crud.create(obj_in=payload)
    return option


@router.put("/{option_id}", response_model=AttributeOptionSchema)
def update_option(
    shop_id: UUID, attribute_id: UUID, option_id: UUID, data: AttributeOptionUpdate = Body(...)
) -> AttributeOptionSchema:
    # Ensure attribute belongs to shop
    attribute = attribute_crud.get_id_by_shop_id(shop_id=shop_id, id=attribute_id)
    if not attribute:
        raise_status(HTTPStatus.NOT_FOUND, f"Attribute with id {attribute_id} not found for this shop")

    option = attribute_option_crud.get(id=option_id)
    if not option or option.attribute_id != attribute_id:
        raise_status(HTTPStatus.NOT_FOUND, f"Option with id {option_id} not found for this attribute")

    # Force attribute_id from path to avoid reassignment through body
    payload = AttributeOptionBase(attribute_id=attribute_id, value_key=data.value_key)
    updated = attribute_option_crud.update(db_obj=option, obj_in=payload)
    return updated


@router.delete("/{option_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete_option(shop_id: UUID, attribute_id: UUID, option_id: UUID) -> None:
    # Ensure attribute belongs to shop
    attribute = attribute_crud.get_id_by_shop_id(shop_id=shop_id, id=attribute_id)
    if not attribute:
        raise_status(HTTPStatus.NOT_FOUND, f"Attribute with id {attribute_id} not found for this shop")

    option = attribute_option_crud.get(id=option_id)
    if not option or option.attribute_id != attribute_id:
        raise_status(HTTPStatus.NOT_FOUND, f"Option with id {option_id} not found for this attribute")

    attribute_option_crud.delete(id=str(option_id))
    return None
