from datetime import datetime
from http import HTTPStatus
from operator import or_
from typing import Any, List, Optional
from uuid import UUID

import structlog
from fastapi import HTTPException, Request
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api import deps
from fastapi import APIRouter
from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.api.helpers import _query_with_filters, invalidateCompletedOrdersCache, invalidatePendingOrdersCache
from server.api.utils import is_ip_allowed, validate_uuid4
from server.crud.crud_account import account_crud
from server.crud.crud_order import order_crud
from server.crud.crud_shop import shop_crud
from server.db.models import OrderTable, UserTable
from server.schemas.order import OrderBase, OrderCreate, OrderCreated, OrderSchema, OrderUpdate, OrderUpdated
from server.schemas.account import AccountCreate

logger = structlog.get_logger(__name__)

router = APIRouter()


def get_price_rules_total(order_items):
    """Calculate the total number of grams."""
    JOINT = 0.4

    # Todo: add correct order line for 0.5 and 2.5
    prices = {"0,5 gram": 0.5, "1 gram": 1, "2,5 gram": 2.5, "5 gram": 5, "joint": JOINT}
    total = 0
    for item in order_items:
        if item.description in prices:
            total = total + (prices[item.description] * item.quantity)

    return total


# Commented because 'active' field no longer exists on products, nor does shops_to_prices
# def get_first_unavailable_product_name(order_items, shop_id):
#     """Search for the first unavailable product and return it's name."""
#     # products = shop_to_price_crud.get_products_with_prices_by_shop_id(shop_id=shop_id)
#     #
#     # for item in order_items:
#     #     found_product = False  # Start False
#     #     for product in products:
#     #         if item.kind_id == str(product.kind_id):
#     #             if product.active:
#     #                 if item.description == "0,5 gram" and (not product.use_half or not product.price.half):
#     #                     logger.warning("Product is currently not available in 0.5 gram", kind_name=item.kind_name)
#     #                 elif item.description == "1 gram" and (not product.use_one or not product.price.one):
#     #                     logger.warning("Product is currently not available in 1 gram", kind_name=item.kind_name)
#     #                 elif item.description == "2,5 gram" and (not product.use_two_five or not product.price.two_five):
#     #                     logger.warning("Product is currently not available in 2.5 gram", kind_name=item.kind_name)
#     #                 elif item.description == "5 gram" and (not product.use_five or not product.price.five):
#     #                     logger.warning("Product is currently not available in 5 gram", kind_name=item.kind_name)
#     #                 elif item.description == "1 joint" and (not product.use_joint or not product.price.joint):
#     #                     logger.warning("Product is currently not available as joint", kind_name=item.kind_name)
#     #                 else:
#     #                     logger.info(
#     #                         "Found product in order item and in available products",
#     #                         kind_id=item.kind_id,
#     #                         kind_name=item.kind_name,
#     #                     )
#     #                     found_product = True
#     #             else:
#     #                 logger.warning("Product is currently not available", kind_name=item.kind_name)
#     #         if item.product_id == str(product.product_id):
#     #             if product.active:
#     #                 if not product.use_piece or not product.price.piece:
#     #                     logger.warning("Product is currently not available as piece", product_name=item.product_name)
#     #                 else:
#     #                     logger.info(
#     #                         "Found horeca product in order item and in available products",
#     #                         product_id=item.product_id,
#     #                         product_name=item.product_name,
#     #                     )
#     #                     found_product = True
#     #             else:
#     #                 logger.warning("Horeca product is currently not available", product_name=item.product_name)
#     #     if not found_product:
#     #         return item.kind_name if item.kind_name else item.product_name
#     return None


@router.get("/", response_model=List[OrderSchema])
def get_multi(
    response: Response,
    common: dict = Depends(common_parameters),
    current_user: UserTable = Depends(deps.get_current_active_superuser),
) -> List[OrderSchema]:
    orders, header_range = order_crud.get_multi(
        skip=common["skip"], limit=common["limit"], filter_parameters=common["filter"], sort_parameters=common["sort"]
    )
    for order in orders:
        if (order.status == "complete" or order.status == "cancelled") and order.completed_by:
            order.completed_by_name = order.user.first_name
        if order.account_id:
            order.account_name = order.account.name
        if order.shop_id:
            order.shop_name = order.shop.name
    response.headers["Content-Range"] = header_range
    return orders


@router.get("/shop/{shop_id}/pending", response_model=List[OrderSchema])
def show_all_pending_orders_per_shop(
    shop_id: UUID,
    response: Response,
    common: dict = Depends(common_parameters),
    current_user: UserTable = Depends(deps.get_current_active_superuser),
) -> List[OrderSchema]:
    query = (OrderTable.query.filter(OrderTable.shop_id == shop_id)
             .filter(OrderTable.status == "pending")
             )
    orders, header_range = order_crud.get_multi(
        query_parameter=query,
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )

    for order in orders:
        if order.account_id:
            order.account_name = order.account.name
        if order.shop_id:
            order.shop_name = order.shop.name

    response.headers["Content-Range"] = header_range
    return orders


@router.get("/shop/{shop_id}/complete", response_model=List[OrderSchema])
def show_all_complete_orders_per_shop(
    shop_id: UUID,
    response: Response,
    common: dict = Depends(common_parameters),
    current_user: UserTable = Depends(deps.get_current_active_superuser),
) -> List[OrderSchema]:
    query = (OrderTable.query.filter(OrderTable.shop_id == shop_id)
             .filter(or_(OrderTable.status == "complete", OrderTable.status == "cancelled"))
             )
    orders, header_range = order_crud.get_multi(
        query_parameter=query,
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )

    for order in orders:
        if (order.status == "complete" or order.status == "cancelled") and order.completed_by:
            order.completed_by_name = order.user.first_name
        if order.account_id:
            order.account_name = order.account.name
        if order.shop_id:
            order.shop_name = order.shop.name

    response.headers["Content-Range"] = header_range
    return orders


@router.get("/{id}")
def get_by_id(id: UUID, current_user: UserTable = Depends(deps.get_current_active_superuser)) -> OrderSchema:
    order = order_crud.get(id)
    if not order:
        raise_status(HTTPStatus.NOT_FOUND, f"Order with id {id} not found")

    if (order.status == "complete" or order.status == "cancelled") and order.completed_by:
        order.completed_by_name = order.user.first_name
    if order.account_id:
        order.account_name = order.account.name
    if order.shop_id:
        order.shop_name = order.shop.name

    return order


@router.get("/check/{ids}", response_model=List[OrderCreated])
def check(
    ids: str,
) -> List[OrderCreated]:
    id_list = ids.split(",")

    # Validate input
    for index, id in enumerate(id_list):
        if not validate_uuid4(id):
            raise_status(HTTPStatus.BAD_REQUEST, f"ID {index + 1} is not valid")

    if len(id_list) > 10:
        raise_status(HTTPStatus.BAD_REQUEST, "Max 10 orders")

    # Build response
    items = []
    items_with_schema = []
    for id in id_list:
        # item = load(Order, id, allow_404=True) #the old
        item = order_crud.get(id)
        if item:
            item.account_name = item.account.name
            items.append(item)

    for item in items:
        if item.shop_id != items[0].shop_id:
            raise_status(HTTPStatus.BAD_REQUEST, "All ID's should belong to one shop")
        else:
            checked_order = OrderCreated(
                account_id=item.account_id,
                total=item.total,
                customer_order_id=item.customer_order_id,
                status=item.status,
                id=item.id,
                created_at=item.created_at,
                completed_at=item.completed_at,
                account_name=item.account.name,
            )
            items_with_schema.append(checked_order)

    return items_with_schema


@router.post("/", response_model=OrderCreated, status_code=HTTPStatus.CREATED)
def create(request: Request, data: OrderCreate = Body(...)) -> OrderCreated:
    logger.info("Saving order", data=data)

    if data.customer_order_id:
        del data.customer_order_id
    shop_id = data.shop_id
    shop = shop_crud.get(str(shop_id))
    if not shop:
        raise_status(HTTPStatus.NOT_FOUND, f"Shop with id {shop_id} not found")

    if data.account_name and not data.account_id:
        account_data = AccountCreate(shop_id=data.shop_id, name=data.account_name)
        account = account_crud.create(obj_in=account_data)
        data.account_id = account.id
        del data.account_name

    if not is_ip_allowed(request, shop) and str(data.account_id) != "0999fbcd-a72b-4cc2-abbe-41ccd466cdaf":
        # allow test table to bypass IP check if any
        raise_status(HTTPStatus.BAD_REQUEST, "NOT_ON_SHOP_WIFI")

    # 5 gram check
    total_cannabis = get_price_rules_total(data.order_info)
    logger.info("Checked order weight", weight=total_cannabis)
    if total_cannabis > 5:
        raise_status(HTTPStatus.BAD_REQUEST, "MAX_5_GRAMS_ALLOWED")

    # Availability check
    # unavailable_product_name = get_first_unavailable_product_name(data.order_info, data.shop_id)
    # if unavailable_product_name:
    #     raise_status(HTTPStatus.BAD_REQUEST, f"{unavailable_product_name}, OUT_OF_STOCK")

    data.customer_order_id = order_crud.get_newest_order_id(shop_id=shop_id)

    if data.status in ["complete", "cancelled"] and not data.completed_at:
        data.completed_at = datetime.utcnow()

    if data.status not in ["pending", "complete", "cancelled"]:
        data.status = "pending"

    if str(data.account_id) == "0999fbcd-a72b-4cc2-abbe-41ccd466cdaf":
        # Test table -> flag it complete
        data.status = "complete"
        data.completed_at = datetime.utcnow()

    order = order_crud.create(obj_in=data)

    created_order = OrderCreated(
        account_id=order.account_id,
        total=order.total,
        customer_order_id=order.customer_order_id,
        notes=order.notes,
        status=order.status,
        id=order.id,
        order_info=order.order_info,
        created_at=order.created_at,
        completed_at=order.completed_at,
        account_name=order.account.name,
    )
    if str(data.account_id) == "0999fbcd-a72b-4cc2-abbe-41ccd466cdaf":
        # Test table -> invalidate completed orders
        invalidateCompletedOrdersCache(created_order.id)
    else:
        invalidatePendingOrdersCache(created_order.id)
    return created_order


@router.patch("/{order_id}", response_model=OrderUpdated, status_code=HTTPStatus.CREATED)
def patch(
    *, order_id: UUID, item_in: OrderBase, current_user: UserTable = Depends(deps.get_current_active_user)
) -> OrderUpdated:
    order = order_crud.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if (
        "complete" not in order.status
        and item_in.status
        and (item_in.status == "complete" or item_in.status == "cancelled")
        and not order.completed_at
    ):
        order.completed_at = datetime.utcnow()
        order.completed_by = current_user.id

    order = order_crud.update(
        db_obj=order,
        obj_in=item_in,
    )

    updated_order = OrderUpdated(
        account_id=order.account_id,
        notes=order.notes,
        total=order.total,
        customer_order_id=order.customer_order_id,
        status=order.status,
        shop_id=order.shop_id,
        order_info=order.order_info,
        id=order.id,
    )
    invalidateCompletedOrdersCache(updated_order.id)
    return updated_order


@router.put("/{order_id}", response_model=OrderUpdated, status_code=HTTPStatus.CREATED)
def update(
    *, order_id: UUID, item_in: OrderUpdate, current_user: UserTable = Depends(deps.get_current_active_superuser)
) -> OrderUpdated:
    order = order_crud.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if item_in.status and (item_in.status == "complete" or item_in.status == "cancelled") and not order.completed_at:
        order.completed_at = datetime.utcnow()
        order.completed_by = current_user.id

    order = order_crud.update(
        db_obj=order,
        obj_in=item_in,
    )

    updated_order = OrderUpdated(
        account_id=order.account_id,
        notes=order.notes,
        total=order.total,
        customer_order_id=order.customer_order_id,
        status=order.status,
        shop_id=order.shop_id,
        order_info=order.order_info,
        id=order.id,
    )

    return updated_order


@router.delete("/{order_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(order_id: UUID, current_user: UserTable = Depends(deps.get_current_active_superuser)) -> None:
    return order_crud.delete(id=order_id)
