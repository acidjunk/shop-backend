from datetime import datetime, timezone
from http import HTTPStatus
from typing import Any, List, Optional
from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api import deps
from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud import crud_shop
from server.crud.crud_product import product_crud
from server.db.models import ProductTable, UserTable
from server.schemas.product import (
    ProductCreate,
    ProductOrder,
    ProductSchema,
    ProductUpdate,
    ProductWithDefaultPrice,
    ProductWithDetailsAndPrices,
)
from server.schemas.product_attribute_value import ProductWithAttributes

logger = structlog.get_logger(__name__)

router = APIRouter()


def get_shop(shop_id: UUID):
    shop = crud_shop.get_by_id(id=shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return shop


@router.get("/", response_model=List[ProductWithAttributes])
def get_multi(
    shop_id: UUID, response: Response, common: dict = Depends(common_parameters), include: Optional[str] = None
) -> List[ProductWithAttributes]:
    # Base: fetch paginated products for this shop
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

    # Calculate images_amount as before
    for product in products:
        product.images_amount = 0
        for i in [1, 2, 3, 4, 5, 6]:
            if getattr(product, f"image_{i}"):
                product.images_amount += 1

    # Optionally include attributes when requested via include=attributes
    include_attrs = False
    if include:
        include_parts = {part.strip().lower() for part in include.split(",") if part.strip()}
        include_attrs = "attributes" in include_parts

    # Build response preserving original order
    from server.schemas.product_attribute_value import ProductWithAttributes
    out: List[ProductWithAttributes] = []
    from server.schemas.product import ProductWithDefaultPrice

    if not include_attrs:
        # Fast path: no attributes requested, avoid extra joins
        for p in products:
            prod_schema = ProductWithDefaultPrice.model_validate(p)
            out.append(
                ProductWithAttributes(
                    product=prod_schema,
                    attributes=[],
                )
            )
        return out

    # Collect product IDs and fetch all related attribute values in one go
    from server.db import db
    from server.db.models import (
        ProductAttributeValueTable,
        ProductTable as _ProductTable,
        AttributeTable as _AttributeTable,
        AttributeTranslationTable as _AttributeTranslationTable,
        AttributeOptionTable as _AttributeOptionTable,
    )
    from server.schemas.product_attribute import ProductAttributeItem
    from server.schemas.product_attribute_value import ProductWithAttributes

    product_ids = [p.id for p in products]

    rows = (
        db.session.query(
            ProductAttributeValueTable.product_id,
            ProductAttributeValueTable.attribute_id,
            _AttributeTranslationTable.main_name.label("attribute_name"),
            ProductAttributeValueTable.option_id,
            _AttributeOptionTable.value_key.label("option_value_key"),
            ProductAttributeValueTable.value_text,
        )
        .join(_ProductTable, _ProductTable.id == ProductAttributeValueTable.product_id)
        .join(_AttributeTable, _AttributeTable.id == ProductAttributeValueTable.attribute_id)
        .join(_AttributeTranslationTable, _AttributeTranslationTable.attribute_id == _AttributeTable.id)
        .outerjoin(_AttributeOptionTable, _AttributeOptionTable.id == ProductAttributeValueTable.option_id)
        .filter(_ProductTable.shop_id == shop_id)
        .filter(ProductAttributeValueTable.product_id.in_(product_ids))
        .all()
    )

    grouped: dict[UUID, list[ProductAttributeItem]] = {}
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

    for p in products:
        prod_schema = ProductWithDefaultPrice.model_validate(p)
        out.append(
            ProductWithAttributes(
                product=prod_schema,
                attributes=grouped.get(p.id, []),
            )
        )

    return out


@router.get("/{product_id}", response_model=ProductWithDetailsAndPrices)
def get_by_id(product_id: UUID, shop_id: UUID) -> ProductWithDetailsAndPrices:
    product = product_crud.get_id_by_shop_id(shop_id, product_id)
    if not product:
        raise_status(HTTPStatus.NOT_FOUND, f"Product with id {product_id} not found")

    # product.prices = []
    # for price_relation in product.shop_to_price:
    #     if price_relation.shop_id == shop_id:
    #         product.prices.append(
    #             {
    #                 "id": price_relation.price.id,
    #                 "internal_product_id": price_relation.price.internal_product_id,
    #                 "active": price_relation.active,
    #                 "new": price_relation.new,
    #                 # In flask's serializer there is no half
    #                 # "half": price_relation.price.half if price_relation.use_half else None,
    #                 "one": price_relation.price.one if price_relation.use_one else None,
    #                 "two_five": price_relation.price.two_five if price_relation.use_two_five else None,
    #                 "five": price_relation.price.five if price_relation.use_five else None,
    #                 "joint": price_relation.price.joint if price_relation.use_joint else None,
    #                 "piece": price_relation.price.piece if price_relation.use_piece else None,
    #                 "created_at": price_relation.created_at,
    #                 "modified_at": price_relation.modified_at,
    #             }
    #         )

    product.images_amount = 0
    for i in [1, 2, 3, 4, 5, 6]:
        if getattr(product, f"image_{i}"):
            product.images_amount += 1

    return product


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(shop_id: UUID, data: ProductCreate = Body(...)) -> None:
    product = (
        ProductTable.query.filter_by(shop_id=shop_id)
        .filter_by(category_id=data.category_id)
        .order_by(ProductTable.order_number.desc())
        .first()
    )
    data.order_number = (product.order_number + 1) if product is not None else 0

    logger.info("Saving product", data=data)
    product = product_crud.create_by_shop_id(obj_in=data, shop_id=shop_id)
    return product


@router.put("/{product_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(*, product_id: UUID, shop_id: UUID, item_in: ProductUpdate) -> Any:
    product = product_crud.get_id_by_shop_id(shop_id, product_id)
    logger.info("Updating product", data=product)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    item_in.modified_at = datetime.now(timezone.utc)

    product = product_crud.update(
        db_obj=product,
        obj_in=item_in,
    )
    return product


@router.put("/{product_id}/swap", response_model=None, status_code=HTTPStatus.CREATED)
def swap(shop_id: UUID, product_id: UUID, move_up: bool):
    product = product_crud.get_id_by_shop_id(shop_id, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    last_product = (
        ProductTable.query.filter_by(shop_id=shop_id)
        .filter_by(category_id=product.category_id)
        .order_by(ProductTable.order_number.desc())
        .first()
    )

    first_product = (
        ProductTable.query.filter_by(shop_id=shop_id)
        .filter_by(category_id=product.category_id)
        .order_by(ProductTable.order_number.asc())
        .first()
    )

    old_order_number = product.order_number
    new_order_number = None

    if move_up:
        if old_order_number == first_product.order_number:
            raise HTTPException(status_code=400, detail="Cannot move up further - Minimum order number achieved.")
        new_order_number = old_order_number - 1
    else:
        if old_order_number == last_product.order_number:
            raise HTTPException(status_code=400, detail="Cannot move down further - Maximum order number achieved.")
        new_order_number = old_order_number + 1

    product_to_swap = (
        ProductTable.query.filter_by(shop_id=shop_id)
        .filter_by(category_id=product.category_id)
        .filter_by(order_number=new_order_number)
        .first()
    )

    if product_to_swap is not None:
        product_crud.update(db_obj=product_to_swap, obj_in=ProductOrder(order_number=old_order_number), commit=False)

    product_crud.update(db_obj=product, obj_in=ProductOrder(order_number=new_order_number))

    return HTTPStatus.CREATED


@router.delete("/{product_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(product_id: UUID, shop_id: UUID) -> None:
    return product_crud.delete_by_shop_id(shop_id=shop_id, id=product_id)
