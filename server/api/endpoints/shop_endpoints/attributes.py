from http import HTTPStatus
from typing import Any, List
from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud.crud_attribute import attribute_crud
from server.crud.crud_product import product_crud
from server.db import db
from server.db.models import AttributeOptionTable, AttributeTable, ProductAttributeValueTable, ProductTable
from server.schemas.attribute import (
    AttributeBase,
    AttributeCreate,
    AttributeSchema,
    AttributeTranslationBase,
    AttributeUpdate,
    AttributeWithOptionsSchema,
)
from server.schemas.product import ProductWithDefaultPrice

logger = structlog.get_logger(__name__)

router = APIRouter()

# TODO add /attributes/{id}/with-options


@router.get("/with-options", response_model=List[AttributeWithOptionsSchema])
def get_with_options(
    shop_id: UUID, response: Response, common: dict = Depends(common_parameters)
) -> List[AttributeWithOptionsSchema]:
    """List attributes for a shop including their options."""
    # Base: all attributes for this shop (paginated)
    items, header_range = attribute_crud.get_multi_by_shop_id(
        shop_id=shop_id,
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = header_range

    if not items:
        return []

    attr_ids = [a.id for a in items]
    # Fetch all options for these attributes in one query
    options = db.session.query(AttributeOptionTable).filter(AttributeOptionTable.attribute_id.in_(attr_ids)).all()
    options_by_attr: dict[UUID, list[AttributeOptionTable]] = {}
    for opt in options:
        options_by_attr.setdefault(opt.attribute_id, []).append(opt)

    # Attach options
    result: List[AttributeWithOptionsSchema] = []
    for attr in items:
        attr.options = options_by_attr.get(attr.id, [])
        result.append(attr)
    return result


@router.get("/", response_model=List[AttributeSchema])
def get_multi(shop_id: UUID, response: Response, common: dict = Depends(common_parameters)) -> List[AttributeSchema]:
    """List attributes for a shop."""
    items, header_range = attribute_crud.get_multi_by_shop_id(
        shop_id=shop_id,
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = header_range
    return items


@router.get("/id/{attribute_id}", response_model=AttributeSchema)
def get_by_id(attribute_id: UUID, shop_id: UUID) -> AttributeSchema:
    attribute = attribute_crud.get_id_by_shop_id(shop_id, attribute_id)
    if not attribute:
        raise_status(HTTPStatus.NOT_FOUND, f"Attribute with id {attribute_id} not found")
    return attribute


@router.get("/name/{name}", response_model=AttributeSchema)
def get_by_name(name: str, shop_id: UUID) -> AttributeSchema:
    attribute = attribute_crud.get_by_name(name=name, shop_id=shop_id)
    if not attribute:
        raise_status(HTTPStatus.NOT_FOUND, f"Attribute with name {name} not found")
    return attribute


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(shop_id: UUID, data: AttributeCreate = Body(...)) -> None:
    """
    Create a new attribute for the given shop.
    This will also create the translation row and currently only requires main_name in translation.
    """
    logger.info("Saving attribute", data=data)

    new_attribute: AttributeBase = AttributeBase(
        translation=AttributeTranslationBase(main_name=data.name),
        name=data.name,
        shop_id=shop_id,
        unit=data.unit,
    )

    attr = attribute_crud.create_by_shop_id(shop_id=shop_id, obj_in=new_attribute)
    # TODO throws error 500 on duplicate entry
    return attr


@router.delete("/{attribute_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(attribute_id: UUID, shop_id: UUID) -> None:
    return attribute_crud.delete_deep_by_shop_id(shop_id=shop_id, id=attribute_id)
