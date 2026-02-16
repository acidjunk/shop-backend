from http import HTTPStatus
from typing import List, Union
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
from server.db.models import (
    AttributeOptionTable,
    ProductAttributeValueTable,
    ProductTable,
)
from server.schemas.product_attribute_value import (
    ProductAttributeValueCreate,
    ProductAttributeValueReplace,
    ProductAttributeValueSchema,
)

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


# TODO this should probably also work without needing to send both the attribute and option id,
# ig option should be enough to figure out the attribute id
@router.post("/", response_model=None, status_code=HTTPStatus.CREATED, deprecated=True)
def create_product_attribute_values(
    shop_id: UUID, data: Union[ProductAttributeValueCreate, list[ProductAttributeValueCreate]] = Body(...)
) -> None:
    """
    DEPRECATED: Create a new product attribute value for a product within a shop.
    Notes:
    - This endpoint is deprecated; prefer using the selected options endpoint when possible.
    - attribute_id may be omitted; if omitted, it will be inferred from option_id.

    Validations:
    - Product exists and belongs to the shop
    - Resolved Attribute exists and belongs to the shop
    - If option_id is provided, it must belong to the resolved attribute
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

    # TODO add unique constrain so product cant have same option attribute and product id
    # Create
    pav = product_attribute_value_crud.create(obj_in=data)
    return pav


@router.post("/{product_id}", response_model=None, status_code=HTTPStatus.CREATED)
def create_product_attribute_values_for_product(
    shop_id: UUID,
    product_id: UUID,
    data: ProductAttributeValueReplace = Body(...),
) -> None:
    """
    Create new product attribute value(s) for a specific product using product_id in the URL.
    This deprecates the old POST / endpoint that required product_id in the body.

    Notes:
    - attribute_id may be omitted; if omitted, it will be inferred from option_id.

    Validations per item:
    - Product (from path) exists and belongs to the shop
    - Resolved Attribute exists and belongs to the shop
    - If option_id is provided, it must belong to the resolved attribute
    """
    for option_id in data.option_ids:
        _create_single_pav_for_product(shop_id=shop_id, product_id=product_id, option_id=option_id)

    return None


def _create_single_pav_for_product(shop_id: UUID, product_id: UUID, option_id: UUID):
    # Validate product belongs to shop via path param
    product = product_crud.get_id_by_shop_id(shop_id=shop_id, id=product_id)
    if not product:
        raise_status(HTTPStatus.NOT_FOUND, f"Product {product_id} not found for this shop")

    if option_id is None:
        raise_status(
            HTTPStatus.BAD_REQUEST,
            "attribute_id is missing and cannot be inferred without option_id",
        )

    option = attribute_option_crud.get(id=option_id)
    if not option:
        raise_status(HTTPStatus.BAD_REQUEST, f"Option {option_id} does not exist")
    resolved_attribute_id = option.attribute_id

    # Validate attribute belongs to shop
    attribute = attribute_crud.get_id_by_shop_id(shop_id=shop_id, id=resolved_attribute_id)
    if not attribute:
        raise_status(HTTPStatus.NOT_FOUND, f"Attribute {resolved_attribute_id} not found for this shop")

    # Validate option (if provided) belongs to resolved attribute
    if option_id is not None:
        option = option or attribute_option_crud.get(id=option_id)
        if not option or option.attribute_id != resolved_attribute_id:
            raise_status(HTTPStatus.BAD_REQUEST, "Provided option_id does not belong to the resolved attribute")

    logger.info(
        "Saving product attribute value (by product in path)",
        product_id=str(product_id),
        attribute_id=str(resolved_attribute_id),
        option_id=str(option_id) if option_id else None,
    )

    pav_in = ProductAttributeValueCreate(
        product_id=product_id,
        attribute_id=resolved_attribute_id,
        option_id=option_id,
    )
    pav = product_attribute_value_crud.create(obj_in=pav_in)
    return pav


@router.put("/{product_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def put_selected_product_attribute_values_by_product(
    shop_id: UUID,
    product_id: UUID,
    data: ProductAttributeValueReplace = Body(...),
) -> None:
    """
    New version of selected options endpoint addressed by product_id in the path.
    This endpoint now accepts option_ids that may belong to different attributes.
    Requirements/validations:
      - product_id (path) must belong to the shop
      - option_ids must be a non-empty list
      - all option_ids must exist
      - every inferred attribute (from the options) must belong to the shop
      - for each inferred attribute, set selected options for (product_id, attribute) to exactly
        the provided option_ids that belong to that attribute
    """
    # Validate product belongs to shop using path param
    product = product_crud.get_id_by_shop_id(shop_id=shop_id, id=product_id)
    if not product:
        raise_status(HTTPStatus.NOT_FOUND, f"Product {product_id} not found for this shop")

    # Validate and load provided options
    selected_set = set(data.option_ids or [])
    if not selected_set:
        raise_status(HTTPStatus.BAD_REQUEST, "option_ids must be a non-empty list")

    options = db.session.query(AttributeOptionTable).filter(AttributeOptionTable.id.in_(list(selected_set))).all()
    if len(options) != len(selected_set):
        raise_status(HTTPStatus.BAD_REQUEST, "One or more option IDs do not exist")

    # Group selected options by their attribute_id
    attr_to_option_ids: dict[UUID, set[UUID]] = {}
    for opt in options:
        attr_to_option_ids.setdefault(opt.attribute_id, set()).add(opt.id)

    # Process each attribute group independently
    for inferred_attribute_id, option_ids_for_attr in attr_to_option_ids.items():
        # Validate attribute belongs to shop
        attribute = attribute_crud.get_id_by_shop_id(shop_id=shop_id, id=inferred_attribute_id)
        if not attribute:
            raise_status(HTTPStatus.NOT_FOUND, f"Attribute {inferred_attribute_id} not found for this shop")

        # Fetch existing PAVs for this product+attribute
        existing = (
            db.session.query(ProductAttributeValueTable)
            .filter(
                ProductAttributeValueTable.product_id == product_id,
                ProductAttributeValueTable.attribute_id == inferred_attribute_id,
            )
            .all()
        )

        existing_option_ids = set(row.option_id for row in existing if row.option_id is not None)

        to_add = option_ids_for_attr - existing_option_ids
        to_remove_ids = [row.id for row in existing if row.option_id not in option_ids_for_attr]

        # Create missing
        for option_id in to_add:
            pav_in = ProductAttributeValueCreate(
                product_id=product_id,
                attribute_id=inferred_attribute_id,
                option_id=option_id,
            )
            logger.info(
                "Saving product attribute value",
                product_id=str(product_id),
                attribute_id=str(inferred_attribute_id),
                option_id=str(option_id),
            )
            product_attribute_value_crud.create(obj_in=pav_in)

        # Delete absent
        for pav_id in to_remove_ids:
            product_attribute_value_crud.delete(id=str(pav_id))

        logger.info(
            "Updated selected product attribute values (by product in path)",
            product_id=str(product_id),
            attribute_id=str(inferred_attribute_id),
            added=len(to_add),
            removed=len(to_remove_ids),
        )

    return None


@router.delete("/{id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete_product_attribute_value(shop_id: UUID, id: UUID) -> None:
    pav = product_attribute_value_crud.get(id)
    if not pav:
        raise_status(HTTPStatus.NOT_FOUND, f"ProductAttributeValue with id {id} not found")
    if not pav.product or pav.product.shop_id != shop_id:
        raise_status(HTTPStatus.NOT_FOUND, f"ProductAttributeValue with id {id} not found for this shop")
    product_attribute_value_crud.delete(id=str(id))
    return None
