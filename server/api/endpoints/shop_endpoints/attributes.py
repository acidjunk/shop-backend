from http import HTTPStatus
from typing import Any, List
from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.db import db
from server.db.models import AttributeOptionTable, AttributeTable, ProductAttributeValueTable, ProductTable
from server.crud.crud_attribute import attribute_crud
from server.crud.crud_product import product_crud
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


@router.get("/with-options", response_model=List[AttributeWithOptionsSchema])
def get_with_options(shop_id: UUID, response: Response, common: dict = Depends(common_parameters)) -> List[AttributeWithOptionsSchema]:
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
    options = (
        db.session.query(AttributeOptionTable)
        .filter(AttributeOptionTable.attribute_id.in_(attr_ids))
        .all()
    )
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


@router.get("/{attribute_id}", response_model=AttributeSchema)
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


@router.get("/{attribute_id}/products", response_model=List[ProductWithDefaultPrice])
def get_products_by_attribute(shop_id: UUID, attribute_id: UUID, response: Response, common: dict = Depends(common_parameters)) -> List[ProductWithDefaultPrice]:
    """Return all products in the shop that have any value for the given attribute."""
    # Ensure attribute belongs to shop
    attribute = attribute_crud.get_id_by_shop_id(shop_id, attribute_id)
    if not attribute:
        raise_status(HTTPStatus.NOT_FOUND, f"Attribute with id {attribute_id} not found for this shop")

    base_query = (
        db.session.query(ProductTable)
        .join(ProductAttributeValueTable, ProductAttributeValueTable.product_id == ProductTable.id)
        .filter(ProductTable.shop_id == shop_id)
        .filter(ProductAttributeValueTable.attribute_id == attribute_id)
        .distinct()
    )

    items, header_range = product_crud.get_multi(
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
        query_parameter=base_query,
    )
    response.headers["Content-Range"] = header_range
    return items


@router.get("/{attribute_id}/options/{option_id}/products", response_model=List[ProductWithDefaultPrice])
def get_products_by_attribute_option(shop_id: UUID, attribute_id: UUID, option_id: UUID, response: Response, common: dict = Depends(common_parameters)) -> List[ProductWithDefaultPrice]:
    """Return all products in the shop that have the given attribute option assigned."""
    # Ensure attribute belongs to shop
    attribute = attribute_crud.get_id_by_shop_id(shop_id, attribute_id)
    if not attribute:
        raise_status(HTTPStatus.NOT_FOUND, f"Attribute with id {attribute_id} not found for this shop")

    # Ensure option belongs to attribute
    option = db.session.get(AttributeOptionTable, option_id)
    if not option or option.attribute_id != attribute_id:
        raise_status(HTTPStatus.NOT_FOUND, f"Option with id {option_id} not found for this attribute")

    base_query = (
        db.session.query(ProductTable)
        .join(ProductAttributeValueTable, ProductAttributeValueTable.product_id == ProductTable.id)
        .filter(ProductTable.shop_id == shop_id)
        .filter(ProductAttributeValueTable.attribute_id == attribute_id)
        .filter(ProductAttributeValueTable.option_id == option_id)
        .distinct()
    )

    items, header_range = attribute_crud.get_multi(
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
        query_parameter=base_query,
    )
    response.headers["Content-Range"] = header_range
    return items


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(shop_id: UUID, data: AttributeCreate = Body(...)) -> None:
    """
    Create a new attribute for the given shop.
    This will also create the translation row and currently only requires main_name in translation.
    """
    logger.info("Saving attribute", data=data)

    new_attribute: AttributeBase = AttributeBase(
        translation=AttributeTranslationBase(main_name=data.name),
        value_kind=data.value_kind,
        name=data.name,
        shop_id=shop_id,
        unit=data.unit,
    )

    attr = attribute_crud.create_by_shop_id(shop_id=shop_id, obj_in=new_attribute)
    return attr


@router.put("/{attribute_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(*, attribute_id: UUID, shop_id: UUID, item_in: AttributeUpdate) -> Any:
    attribute = attribute_crud.get_id_by_shop_id(shop_id, attribute_id)
    logger.info("Updating attribute", data=attribute)
    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")

    attribute = attribute_crud.update(
        db_obj=attribute,
        obj_in=item_in,
    )
    return attribute


@router.delete("/{attribute_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(attribute_id: UUID, shop_id: UUID) -> None:
    try:
        attribute_crud.delete_by_shop_id(shop_id=shop_id, id=attribute_id)
    except Exception as e:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail=f"{e.__cause__}")
    return
