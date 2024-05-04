from http import HTTPStatus
from typing import Any, List
from uuid import UUID

import structlog
from fastapi import HTTPException
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api.api_v1.router_fix import APIRouter
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


# Todo: fix filtering on shop_id


@router.get("/", response_model=List[CategoryWithNames])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[CategorySchema]:
    categories, header_range = category_crud.get_multi(
        skip=common["skip"], limit=common["limit"], filter_parameters=common["filter"], sort_parameters=common["sort"]
    )
    for category in categories:
        category.shop_name = category.shop.name
        # category.category_and_shop = f"{category.name} in {category.shop.name}"

    response.headers["Content-Range"] = header_range
    return categories


@router.get("/{id}", response_model=CategorySchema)
def get_by_id(id: UUID) -> CategorySchema:
    category = category_crud.get(id)
    if not category:
        raise_status(HTTPStatus.NOT_FOUND, f"Category with id {id} not found")
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
def update(*, category_id: UUID, item_in: CategoryUpdate) -> Any:
    category = category_crud.get(id=category_id)
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
def delete(category_id: UUID) -> None:
    return category_crud.delete(id=category_id)
