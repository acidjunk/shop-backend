from http import HTTPStatus
from typing import Any, List
from uuid import UUID

import structlog
from fastapi import APIRouter, HTTPException
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.api.helpers import invalidateShopCache
from server.crud import crud_shop
from server.crud.crud_category import category_crud
from server.db.models import CategoryTable
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
