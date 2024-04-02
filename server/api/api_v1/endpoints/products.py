from http import HTTPStatus
from typing import Any, List, Optional
from uuid import UUID

import structlog
from fastapi import HTTPException
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api import deps
from server.api.api_v1.router_fix import APIRouter
from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud.crud_product import product_crud
from server.db.models import UsersTable
from server.schemas.product import (
    ProductCreate,
    ProductSchema,
    ProductUpdate,
    ProductWithDefaultPrice,
    ProductWithDetailsAndPrices,
)

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[ProductWithDefaultPrice])
def get_multi(
    response: Response,
    common: dict = Depends(common_parameters),
    current_user: UsersTable = Depends(deps.get_current_active_superuser),
) -> List[ProductWithDefaultPrice]:
    products, header_range = product_crud.get_multi(
        skip=common["skip"], limit=common["limit"], filter_parameters=common["filter"], sort_parameters=common["sort"]
    )
    response.headers["Content-Range"] = header_range

    for product in products:
        product.images_amount = 0
        for i in [1, 2, 3, 4, 5, 6]:
            if getattr(product, f"image_{i}"):
                product.images_amount += 1

    return products


@router.get("/{id}", response_model=ProductWithDetailsAndPrices)
def get_by_id(id: UUID, shop: Optional[UUID] = None) -> ProductWithDetailsAndPrices:
    product = product_crud.get(id)
    if not product:
        raise_status(HTTPStatus.NOT_FOUND, f"Product with id {id} not found")

    product.prices = []
    if shop:
        for price_relation in product.shop_to_price:
            if price_relation.shop_id == shop:
                product.prices.append(
                    {
                        "id": price_relation.price.id,
                        "internal_product_id": price_relation.price.internal_product_id,
                        "active": price_relation.active,
                        "new": price_relation.new,
                        # In flask's serializer there is no half
                        # "half": price_relation.price.half if price_relation.use_half else None,
                        "one": price_relation.price.one if price_relation.use_one else None,
                        "two_five": price_relation.price.two_five if price_relation.use_two_five else None,
                        "five": price_relation.price.five if price_relation.use_five else None,
                        "joint": price_relation.price.joint if price_relation.use_joint else None,
                        "piece": price_relation.price.piece if price_relation.use_piece else None,
                        "created_at": price_relation.created_at,
                        "modified_at": price_relation.modified_at,
                    }
                )
    else:
        product.prices = []

    product.images_amount = 0
    for i in [1, 2, 3, 4, 5, 6]:
        if getattr(product, f"image_{i}"):
            product.images_amount += 1

    return product


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(
    data: ProductCreate = Body(...), current_user: UsersTable = Depends(deps.get_current_active_employee)
) -> None:
    logger.info("Saving product", data=data)
    product = product_crud.create(obj_in=data)
    return product


@router.put("/{product_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(
    *, product_id: UUID, item_in: ProductUpdate, current_user: UsersTable = Depends(deps.get_current_active_employee)
) -> Any:
    product = product_crud.get(id=product_id)
    logger.info("Updating product", data=product)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product = product_crud.update(
        db_obj=product,
        obj_in=item_in,
    )
    return product


@router.delete("/{product_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(product_id: UUID, current_user: UsersTable = Depends(deps.get_current_active_superuser)) -> None:
    return product_crud.delete(id=product_id)
