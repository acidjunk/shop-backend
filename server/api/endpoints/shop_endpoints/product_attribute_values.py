from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

import structlog
from fastapi import APIRouter
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud.crud_attribute import attribute_crud
from server.crud.crud_attribute_option import attribute_option_crud
from server.crud.crud_product import product_crud
from server.crud.crud_product_attribute_value import product_attribute_value_crud
from server.db import db
from server.db.models import ProductAttributeValueTable, ProductTable, AttributeTable, AttributeTranslationTable, AttributeOptionTable
from server.schemas.product_attribute_value import (
    ProductAttributeValueCreate,
    ProductAttributeValueSchema,
    ProductAttributeValueUpdate,
    ProductWithAttributes,
)
from server.schemas.product_attribute import ProductAttributeItem
from server.schemas.product import ProductWithDefaultPrice

logger = structlog.get_logger(__name__)

router = APIRouter()

@router.get("/", response_model=List[ProductAttributeValueSchema])
def list_product_attribute_values(
    shop_id: UUID, response: Response, common: dict = Depends(common_parameters)
) -> List[ProductAttributeValueSchema]:
    """List product attribute values for a shop (scoped by product.shop_id)."""
    # Build a base query scoped to the shop via product table
    query = (
        db.session.query(ProductAttributeValueTable)
        .join(ProductTable, ProductTable.id == ProductAttributeValueTable.product_id)
        .filter(ProductTable.shop_id == shop_id)
    )

    results, content_range = product_attribute_value_crud.get_multi(
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
        query_parameter=query,
    )
    response.headers["Content-Range"] = content_range
    return results


@router.get("/{id}", response_model=ProductAttributeValueSchema)
def get_product_attribute_value(shop_id: UUID, id: UUID) -> ProductAttributeValueSchema:
    pav = product_attribute_value_crud.get(id)
    if not pav:
        raise_status(HTTPStatus.NOT_FOUND, f"ProductAttributeValue with id {id} not found")
    # Ensure it belongs to the shop via product
    if not pav.product or pav.product.shop_id != shop_id:
        raise_status(HTTPStatus.NOT_FOUND, f"ProductAttributeValue with id {id} not found for this shop")
    return pav

#TODO this should probably also work without needing to send both the attribute and option id,
# ig option should be enough to figure out the attribute id
@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create_product_attribute_value(shop_id: UUID, data: ProductAttributeValueCreate = Body(...)) -> None:
    """
    Create a new product attribute value for a product within a shop.
    Validations:
    - Product exists and belongs to the shop
    - Attribute exists and belongs to the shop
    - If option_id is provided, it belongs to the given attribute
    """
    # Validate product belongs to shop
    product = product_crud.get_id_by_shop_id(shop_id=shop_id, id=data.product_id)
    if not product:
        raise_status(HTTPStatus.NOT_FOUND, f"Product {data.product_id} not found for this shop")

    # Validate attribute belongs to shop
    attribute = attribute_crud.get_id_by_shop_id(shop_id=shop_id, id=data.attribute_id)
    if not attribute:
        raise_status(HTTPStatus.NOT_FOUND, f"Attribute {data.attribute_id} not found for this shop")

    # Validate option (if provided) belongs to attribute
    if data.option_id is not None:
        option = attribute_option_crud.get(id=data.option_id)
        if not option or option.attribute_id != data.attribute_id:
            raise_status(HTTPStatus.BAD_REQUEST, "Provided option_id does not belong to the given attribute")

    logger.info(
        "Saving product attribute value",
        product_id=str(data.product_id),
        attribute_id=str(data.attribute_id),
        option_id=str(data.option_id) if data.option_id else None,
    )

    #TODO add unique constrain so product cant have same option attribute and product id
    # Create
    pav = product_attribute_value_crud.create(obj_in=data)
    return pav


@router.delete("/{id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete_product_attribute_value(shop_id: UUID, id: UUID) -> None:
    pav = product_attribute_value_crud.get(id)
    if not pav:
        raise_status(HTTPStatus.NOT_FOUND, f"ProductAttributeValue with id {id} not found")
    if not pav.product or pav.product.shop_id != shop_id:
        raise_status(HTTPStatus.NOT_FOUND, f"ProductAttributeValue with id {id} not found for this shop")
    product_attribute_value_crud.delete(id=str(id))
    return None


