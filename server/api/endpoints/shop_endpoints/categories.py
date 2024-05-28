from http import HTTPStatus
from typing import Any, List
from uuid import UUID

import structlog
from fastapi import HTTPException, APIRouter
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.api.helpers import invalidateShopCache
from server.crud.crud_category import category_crud
from server.schemas.category import (
    CategoryCreate,
    CategoryIsDeletable,
    CategorySchema,
    CategoryUpdate,
    CategoryWithNames,
)

logger = structlog.get_logger(__name__)

router = APIRouter()


def get_shop(shop_id: UUID):
    shop = crud_shop.get_by_id(id=shop_id)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")
    return shop


@router.get("/", response_model=List[CategoryWithNames])
def get_multi(shop_id: UUID, response: Response, common: dict = Depends(common_parameters)) -> List[CategorySchema]:
    # shop = get_shop(shop_id)
    categories, header_range = category_crud.shop_get_multi(
        shop_id=shop_id,
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    for category in categories:
        category.shop_name = category.shop.name
        # category.category_and_shop = f"{category.name} in {category.shop.name}"

    response.headers["Content-Range"] = header_range
    return categories


@router.get("/{category_id}", response_model=CategorySchema)
def get_by_id(shop_id: UUID, category_id: UUID) -> CategorySchema:
    category = category_crud.shop_get(shop_id, category_id)
    if not category:
        raise_status(HTTPStatus.NOT_FOUND, f"Category with id {category_id} not found")
    return category


# @router.get("/is-deletable/{id}", response_model=CategoryIsDeletable)
# def get_by_id(id: UUID) -> CategoryIsDeletable:
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
def create(data: CategoryCreate = Body(...)) -> None:
    logger.info("Saving category", data=data)
    return category_crud.create(obj_in=data)


@router.put("/{category_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(*, category_id: UUID, shop_id: UUID, item_in: CategoryUpdate) -> Any:
    category = category_crud.shop_get(shop_id, category_id)
    logger.info("Updating category", data=category)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category = category_crud.update(
        db_obj=category,
        obj_in=item_in,
    )

    if category.shop_id is not None:
        invalidateShopCache(category.shop_id)

    return category


@router.delete("/{category_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(category_id: UUID, shop_id: UUID) -> None:
    return category_crud.shop_delete(shop_id=shop_id, id=category_id)
