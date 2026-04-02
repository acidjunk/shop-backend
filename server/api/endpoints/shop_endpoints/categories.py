from collections import defaultdict
from http import HTTPStatus
from typing import Any, List
from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Body, Depends
from sqlalchemy import func
from starlette.responses import Response

from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.api.helpers import invalidateShopCache
from server.crud import crud_shop
from server.crud.crud_category import category_crud
from server.db import db
from server.db.models import (
    AttributeOptionTable,
    AttributeTable,
    AttributeTranslationTable,
    CategoryTable,
    ProductAttributeValueTable,
    ProductTable,
)
from server.schemas.attribute import (
    AttributeTranslationBase,
    AvailableAttributeSchema,
    AvailableOptionSchema,
)
from server.schemas.category import (
    CategoryCreate,
    CategoryIsDeletable,
    CategoryOrder,
    CategorySchema,
    CategoryUpdate,
    CategoryWithNames,
)

logger = structlog.get_logger(__name__)

router = APIRouter()
public_router = APIRouter()


def get_shop(shop_id: UUID):
    shop = crud_shop.get_id(id=shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return shop


@router.get("/", response_model=List[CategorySchema])
def get_multi(shop_id: UUID, response: Response, common: dict = Depends(common_parameters)) -> List[CategorySchema]:
    # shop = get_shop(shop_id)
    categories, header_range = category_crud.get_multi_by_shop_id(
        shop_id=shop_id,
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = header_range
    return categories


@router.get("/{category_id}", response_model=CategorySchema)
def get_by_id(shop_id: UUID, category_id: UUID) -> CategorySchema:
    category = category_crud.get_id_by_shop_id(shop_id, category_id)
    if not category:
        raise_status(HTTPStatus.NOT_FOUND, f"Category with id {category_id} not found")
    return category


# @router.get("/is-deletable/{id}", response_model=CategoryIsDeletable)
# def get_id(id: UUID) -> CategoryIsDeletable:
#     shop_to_price = shop_to_price_crud.get_shops_to_prices_by_category(category_id=id)
#     if shop_to_price:
#         return CategoryIsDeletable(is_deletable=False)
#     else:
#         return CategoryIsDeletable(is_deletable=True)


@router.get("/name/{name}", response_model=CategorySchema)
def get_by_name(name: str, shop_id: UUID) -> CategorySchema:
    category = category_crud.get_by_name(name=name, shop_id=shop_id)

    if not category:
        raise_status(HTTPStatus.NOT_FOUND, f"Category with name {name} not found")
    return category


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(shop_id: UUID, data: CategoryCreate = Body(...)) -> None:
    category = CategoryTable.query.filter_by(shop_id=shop_id).order_by(CategoryTable.order_number.desc()).first()
    data.order_number = (category.order_number + 1) if category is not None else 0

    logger.info("Saving category", data=data)
    return category_crud.create_by_shop_id(obj_in=data, shop_id=shop_id)


@router.put("/{category_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(*, category_id: UUID, shop_id: UUID, item_in: CategoryUpdate) -> Any:
    category = category_crud.get_id_by_shop_id(shop_id, category_id)
    logger.info("Updating category", data=category)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category = category_crud.update(
        db_obj=category,
        obj_in=item_in,
    )

    # if category.shop_id is not None:
    #     invalidateShopCache(category.shop_id)

    return category


@router.put("/{category_id}/swap", response_model=None, status_code=HTTPStatus.CREATED)
def swap(shop_id: UUID, category_id: UUID, move_up: bool):
    category = category_crud.get_id_by_shop_id(shop_id, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    last_category = CategoryTable.query.filter_by(shop_id=shop_id).order_by(CategoryTable.order_number.desc()).first()

    first_category = CategoryTable.query.filter_by(shop_id=shop_id).order_by(CategoryTable.order_number.asc()).first()

    old_order_number = category.order_number
    new_order_number = None

    if move_up:
        if old_order_number == first_category.order_number:
            raise HTTPException(status_code=400, detail="Cannot move up further - Minimum order number achieved.")
        new_order_number = old_order_number - 1
    else:
        if old_order_number == last_category.order_number:
            raise HTTPException(status_code=400, detail="Cannot move down further - Maximum order number achieved.")
        new_order_number = old_order_number + 1

    category_to_swap = CategoryTable.query.filter_by(shop_id=shop_id).filter_by(order_number=new_order_number).first()

    if category_to_swap is not None:
        category_crud.update(db_obj=category_to_swap, obj_in=CategoryOrder(order_number=old_order_number), commit=False)

    category_crud.update(db_obj=category, obj_in=CategoryOrder(order_number=new_order_number))

    return HTTPStatus.CREATED


@router.delete("/{category_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(category_id: UUID, shop_id: UUID) -> None:
    return category_crud.delete_by_shop_id(shop_id=shop_id, id=category_id)


@public_router.get(
    "/{category_id}/available-attributes",
    response_model=list[AvailableAttributeSchema],
    summary="Get available filter attributes for a category",
    description="Returns attributes actually used by products in this category, with option counts.",
)
def get_available_attributes(shop_id: UUID, category_id: UUID) -> list[AvailableAttributeSchema]:
    category = category_crud.get_id_by_shop_id(shop_id, category_id)
    if not category:
        raise_status(HTTPStatus.NOT_FOUND, f"Category with id {category_id} not found")

    # Single aggregation query: get attribute+option+count for all used options in this category
    results = (
        db.session.query(
            AttributeTable.id.label("attribute_id"),
            AttributeTable.name.label("attribute_name"),
            AttributeTable.unit.label("attribute_unit"),
            AttributeOptionTable.id.label("option_id"),
            AttributeOptionTable.value_key.label("option_value_key"),
            func.count(ProductAttributeValueTable.id).label("product_count"),
        )
        .join(ProductAttributeValueTable, ProductAttributeValueTable.attribute_id == AttributeTable.id)
        .join(ProductTable, ProductTable.id == ProductAttributeValueTable.product_id)
        .join(AttributeOptionTable, AttributeOptionTable.id == ProductAttributeValueTable.option_id)
        .filter(ProductTable.shop_id == shop_id)
        .filter(ProductTable.category_id == category_id)
        .group_by(
            AttributeTable.id,
            AttributeTable.name,
            AttributeTable.unit,
            AttributeOptionTable.id,
            AttributeOptionTable.value_key,
        )
        .all()
    )

    if not results:
        return []

    # Batch-load translations for the distinct attribute IDs
    attr_ids = list({r.attribute_id for r in results})
    translations = (
        db.session.query(AttributeTranslationTable).filter(AttributeTranslationTable.attribute_id.in_(attr_ids)).all()
    )
    trans_by_attr = {t.attribute_id: t for t in translations}

    # Assemble nested response grouped by attribute
    attrs_dict: dict[UUID, AvailableAttributeSchema] = {}
    for row in results:
        if row.attribute_id not in attrs_dict:
            trans = trans_by_attr.get(row.attribute_id)
            translation = (
                AttributeTranslationBase(
                    main_name=trans.main_name,
                    alt1_name=trans.alt1_name,
                    alt2_name=trans.alt2_name,
                )
                if trans
                else None
            )
            attrs_dict[row.attribute_id] = AvailableAttributeSchema(
                id=row.attribute_id,
                name=row.attribute_name,
                unit=row.attribute_unit,
                translation=translation,
                options=[],
            )
        attrs_dict[row.attribute_id].options.append(
            AvailableOptionSchema(
                id=row.option_id,
                value_key=row.option_value_key,
                product_count=row.product_count,
            )
        )

    return list(attrs_dict.values())
