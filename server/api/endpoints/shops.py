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
from server.api.helpers import load
from server.crud.crud_shop import shop_crud
from server.db.models import ShopTable, UserTable
from server.schemas.shop import (
    ShopCacheStatus,
    ShopConfig,
    ShopCreate,
    ShopIp,
    ShopLastCompletedOrder,
    ShopLastPendingOrder,
    ShopSchema,
    ShopUpdate,
    ShopWithPrices,
)

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/", response_model=List[ShopSchema])
def get_multi(
    response: Response,
    common: dict = Depends(common_parameters),
    current_user: UserTable = Depends(deps.get_current_active_superuser),
) -> List[ShopSchema]:
    shops, header_range = shop_crud.get_multi(
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = header_range
    return shops


@router.post("/", response_model=ShopSchema, status_code=HTTPStatus.CREATED)
def create(
    data: ShopCreate = Body(...), current_user: UserTable = Depends(deps.get_current_active_superuser)
) -> ShopSchema:
    logger.info("Saving shop", data=data)
    shop = shop_crud.create(obj_in=data)
    return shop


@router.get("/cache-status/{id}", response_model=ShopCacheStatus)
def get_cache_status(id: UUID) -> ShopCacheStatus:
    """Show date of last change in data that could be visible in this shop"""
    shop = shop_crud.get(id)
    if not shop:
        raise_status(HTTPStatus.NOT_FOUND, f"Shop with id {id} not found")
    return shop


@router.get("/last-completed-order/{id}", response_model=ShopLastCompletedOrder)
def get_last_completed_order(id: UUID) -> ShopLastCompletedOrder:
    """Show date of last change in data that could be visible in this shop"""
    shop = shop_crud.get(id)
    if not shop:
        raise_status(HTTPStatus.NOT_FOUND, f"Shop with id {id} not found")
    return shop


@router.get("/last-pending-order/{id}", response_model=ShopLastPendingOrder)
def get_last_pending_order(id: UUID) -> ShopLastPendingOrder:
    """Show date of last change in data that could be visible in this shop"""
    shop = shop_crud.get(id)
    if not shop:
        raise_status(HTTPStatus.NOT_FOUND, f"Shop with id {id} not found")
    return shop


@router.get("/{id}", response_model=ShopWithPrices)
def get_by_id(id: UUID, is_horeca: Optional[bool] = None):
    """List Shop"""
    item = load(ShopTable, id)
    # price_relations = None
    #
    # if is_horeca:
    #     price_relations = (
    #         ShopToPrice.query.filter_by(shop_id=item.id)
    #         .filter_by(kind_id=None)
    #         .join(ShopToPrice.price)
    #         .join(ShopToPrice.category)
    #         .order_by(Category.name, ShopToPrice.order_number, Price.piece)
    #         .all()
    #     )
    # elif is_horeca is not None:
    #     price_relations = (
    #         ShopToPrice.query.filter_by(shop_id=item.id)
    #         .filter_by(product_id=None)
    #         .join(ShopToPrice.price)
    #         .join(ShopToPrice.category)
    #         .order_by(Category.name, Price.piece, Price.joint, Price.one, Price.five, Price.half, Price.two_five)
    #         .all()
    #     )
    # else:
    #     price_relations = (
    #         ShopToPrice.query.filter_by(shop_id=item.id)
    #         .join(ShopToPrice.price)
    #         .join(ShopToPrice.category)
    #         .order_by(
    #             Category.pricelist_column,
    #             Category.pricelist_row,
    #             ShopToPrice.order_number,
    #             Price.piece,
    #             Price.joint,
    #             Price.one,
    #             Price.five,
    #             Price.half,
    #             Price.two_five,
    #         )
    #         .all()
    #     )

    # item.prices = [
    #     {
    #         "id": pr.id,
    #         "internal_product_id": pr.price.internal_product_id,
    #         "active": pr.active,
    #         "new": pr.new,
    #         "category_id": pr.category_id,
    #         "category_name": pr.category.name,
    #         "category_name_en": pr.category.name_en,
    #         "category_icon": pr.category.icon,
    #         "category_color": pr.category.color,
    #         "category_order_number": pr.category.order_number,
    #         "category_image_1": pr.category.image_1,
    #         "category_image_2": pr.category.image_2,
    #         "category_pricelist_column": pr.category.pricelist_column,
    #         "category_pricelist_row": pr.category.pricelist_row,
    #         "main_category_id": pr.category.main_category.id if pr.category.main_category else "Unknown",
    #         "main_category_name": pr.category.main_category.name if pr.category.main_category else "Unknown",
    #         "main_category_name_en": pr.category.main_category.name_en if pr.category.main_category else "Unknown",
    #         "main_category_icon": pr.category.main_category.icon if pr.category.main_category else "Unknown",
    #         "main_category_order_number": pr.category.main_category.order_number if pr.category.main_category else 0,
    #         "kind_id": pr.kind_id,
    #         "kind_image": pr.kind.image_1 if pr.kind_id else None,
    #         "kind_name": pr.kind.name if pr.kind_id else None,
    #         "strains": [dict({"name": strain.strain.name}) for strain in pr.kind.kind_to_strains] if pr.kind_id else [],
    #         "kind_short_description_nl": pr.kind.short_description_nl if pr.kind_id else None,
    #         "kind_short_description_en": pr.kind.short_description_en if pr.kind_id else None,
    #         "kind_c": pr.kind.c if pr.kind_id else None,
    #         "kind_h": pr.kind.h if pr.kind_id else None,
    #         "kind_i": pr.kind.i if pr.kind_id else None,
    #         "kind_s": pr.kind.s if pr.kind_id else None,
    #         "product_id": pr.product_id,
    #         "product_image": pr.product.image_1 if pr.product_id else None,
    #         "product_name": pr.product.name if pr.product_id else None,
    #         "product_short_description_nl": pr.product.short_description_nl if pr.product_id else None,
    #         "product_short_description_en": pr.product.short_description_en if pr.product_id else None,
    #         "half": pr.price.half if pr.use_half else None,
    #         "one": pr.price.one if pr.use_one else None,
    #         "two_five": pr.price.two_five if pr.use_two_five else None,
    #         "five": pr.price.five if pr.use_five else None,
    #         "joint": pr.price.joint if pr.use_joint else None,
    #         "piece": pr.price.piece if pr.use_piece else None,
    #         "created_at": pr.created_at,
    #         "modified_at": pr.modified_at,
    #         "order_number": pr.order_number,
    #     }
    #     for pr in price_relations
    # ]

    # item.prices = []
    return item


@router.put("/{shop_id}", response_model=ShopSchema, status_code=HTTPStatus.CREATED)
def update(
    *, shop_id: UUID, item_in: ShopUpdate, current_user: UserTable = Depends(deps.get_current_active_superuser)
) -> None:
    shop = shop_crud.get(id=shop_id)
    logger.info("Updating shop", data=shop)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    shop = shop_crud.update(
        db_obj=shop,
        obj_in=item_in,
    )
    return shop


@router.delete("/{shop_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(shop_id: UUID, current_user: UserTable = Depends(deps.get_current_active_superuser)) -> None:
    return shop_crud.delete(id=shop_id)


@router.get("/config/{id}", response_model=ShopConfig)
def get_config(
    id: UUID,
) -> ShopConfig:
    shop = shop_crud.get(id)
    if not shop:
        raise_status(HTTPStatus.NOT_FOUND, f"Shop with id {id} not found")

    return shop


@router.put("/config/{id}", response_model=ShopConfig, status_code=HTTPStatus.CREATED)
def update_config(
    id: UUID, item_in: ShopConfig, current_user: UserTable = Depends(deps.get_current_active_superuser)
) -> ShopConfig:
    shop = shop_crud.get(id=id)
    logger.info("Updating shop", data=shop)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    shop = shop_crud.update(
        db_obj=shop,
        obj_in=item_in,
    )
    return shop


@router.get("/allowed-ips/{id}", response_model=List[str])
def get_allowed_ips(
    id: UUID,
    current_user: UserTable = Depends(deps.get_current_active_superuser),
) -> List[str]:
    shop = shop_crud.get(id)
    if not shop:
        raise_status(HTTPStatus.NOT_FOUND, f"Shop with id {id} not found")

    if shop.allowed_ips:
        return shop.allowed_ips
    else:
        return []


@router.post("/allowed-ips/{id}", response_model=List[str])
def add_new_ip(id: UUID, new_ip: ShopIp, current_user: UserTable = Depends(deps.get_current_active_superuser)):
    shop = shop_crud.get(id)
    if not shop:
        raise_status(HTTPStatus.NOT_FOUND, f"Shop with id {id} not found")

    updated_shop = ShopUpdate(name=shop.name, description=shop.description, allowed_ips=shop.allowed_ips)

    if shop.allowed_ips and new_ip.ip not in shop.allowed_ips:
        updated_shop.allowed_ips.append(new_ip.ip)
    elif shop.allowed_ips and new_ip.ip in shop.allowed_ips:
        raise_status(HTTPStatus.BAD_REQUEST, f"IP {new_ip.ip} already exists")
    else:
        updated_shop.allowed_ips = [new_ip.ip]

    shop_crud.update(db_obj=shop, obj_in=updated_shop)

    return updated_shop.allowed_ips


@router.post("/allowed-ips/{id}/remove", response_model=List[str])
def remove_ip(id: UUID, old_ip: ShopIp, current_user: UserTable = Depends(deps.get_current_active_superuser)):
    shop = shop_crud.get(id)
    if not shop:
        raise_status(HTTPStatus.NOT_FOUND, f"Shop with id {id} not found")

    updated_shop = ShopUpdate(name=shop.name, description=shop.description, allowed_ips=shop.allowed_ips)

    if shop.allowed_ips and old_ip.ip in shop.allowed_ips:
        updated_shop.allowed_ips.remove(old_ip.ip)
    else:
        raise_status(HTTPStatus.BAD_REQUEST, f"IP {old_ip.ip} not on list")

    shop_crud.update(db_obj=shop, obj_in=updated_shop)

    return updated_shop.allowed_ips
