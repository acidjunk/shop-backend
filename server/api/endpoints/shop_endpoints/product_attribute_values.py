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
    ProductAttributeItem,
)
from server.schemas.product import ProductWithDefaultPrice

logger = structlog.get_logger(__name__)

router = APIRouter()

#TODO fix me
#@router.get("/", response_model=List[ProductAttributeValueSchema])
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


@router.put("/{id}", response_model=ProductAttributeValueSchema)
def update_product_attribute_value(shop_id: UUID, id: UUID, data: ProductAttributeValueUpdate = Body(...)) -> ProductAttributeValueSchema:
    pav = product_attribute_value_crud.get(id)
    if not pav:
        raise_status(HTTPStatus.NOT_FOUND, f"ProductAttributeValue with id {id} not found")
    if not pav.product or pav.product.shop_id != shop_id:
        raise_status(HTTPStatus.NOT_FOUND, f"ProductAttributeValue with id {id} not found for this shop")

    # Validate referenced entities if they are being updated
    # Product
    if data.product_id and data.product_id != pav.product_id:
        product = product_crud.get_id_by_shop_id(shop_id=shop_id, id=data.product_id)
        if not product:
            raise_status(HTTPStatus.NOT_FOUND, f"Product {data.product_id} not found for this shop")
    # Attribute
    if data.attribute_id and data.attribute_id != pav.attribute_id:
        attribute = attribute_crud.get_id_by_shop_id(shop_id=shop_id, id=data.attribute_id)
        if not attribute:
            raise_status(HTTPStatus.NOT_FOUND, f"Attribute {data.attribute_id} not found for this shop")
    # Option
    if data.option_id is not None:
        option = attribute_option_crud.get(id=data.option_id)
        # If option provided, it must match the (possibly updated) attribute_id
        target_attribute_id = data.attribute_id if data.attribute_id else pav.attribute_id
        if not option or option.attribute_id != target_attribute_id:
            raise_status(HTTPStatus.BAD_REQUEST, "Provided option_id does not belong to the given attribute")

    updated = product_attribute_value_crud.update(db_obj=pav, obj_in=data)
    return updated


@router.delete("/{id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete_product_attribute_value(shop_id: UUID, id: UUID) -> None:
    pav = product_attribute_value_crud.get(id)
    if not pav:
        raise_status(HTTPStatus.NOT_FOUND, f"ProductAttributeValue with id {id} not found")
    if not pav.product or pav.product.shop_id != shop_id:
        raise_status(HTTPStatus.NOT_FOUND, f"ProductAttributeValue with id {id} not found for this shop")
    product_attribute_value_crud.delete(id=str(id))
    #TODO returns 204 is this oke?
    return None


#TODO fix me
@router.get("/", response_model=List[ProductWithAttributes])
def get_products_with_attributes(shop_id: UUID, response: Response, common: dict = Depends(common_parameters)) -> List[ProductWithAttributes]:
    """Return products in the shop with all attached attributes and values (options/value_text)."""
    # Get base list of products in shop (paginated) using existing product_crud
    products, header_range = product_crud.get_multi_by_shop_id(
        shop_id=shop_id,
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = header_range

    if not products:
        return []

    product_ids = [p.id for p in products]

    # Fetch all attribute values for these products in one query, and join attribute + translation + option
    rows = (
        db.session.query(
            ProductAttributeValueTable.product_id,
            ProductAttributeValueTable.attribute_id,
            AttributeTranslationTable.main_name.label("attribute_name"),
            ProductAttributeValueTable.option_id,
            AttributeOptionTable.value_key.label("option_value_key"),
            ProductAttributeValueTable.value_text,
        )
        .join(ProductTable, ProductTable.id == ProductAttributeValueTable.product_id)
        .join(AttributeTable, AttributeTable.id == ProductAttributeValueTable.attribute_id)
        .join(AttributeTranslationTable, AttributeTranslationTable.attribute_id == AttributeTable.id)
        .outerjoin(AttributeOptionTable, AttributeOptionTable.id == ProductAttributeValueTable.option_id)
        .filter(ProductTable.shop_id == shop_id)
        .filter(ProductAttributeValueTable.product_id.in_(product_ids))
        .all()
    )

    grouped: dict[UUID, List[ProductAttributeItem]] = {}
    for r in rows:
        grouped.setdefault(r.product_id, []).append(
            ProductAttributeItem(
                attribute_id=r.attribute_id,
                attribute_name=r.attribute_name,
                option_id=r.option_id,
                option_value_key=r.option_value_key,
                value_text=r.value_text,
            )
        )

    # Build response list in the same order as products
    out: List[ProductWithAttributes] = []
    for p in products:
        # cast product to ProductWithDefaultPrice schema by reusing it directly (from_attributes enabled)
        prod_schema = ProductWithDefaultPrice.model_validate(p)
        out.append(
            ProductWithAttributes(
                product=prod_schema,
                attributes=grouped.get(p.id, []),
            )
        )

    return out
