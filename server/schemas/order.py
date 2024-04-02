import uuid
from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, root_validator

from server.schemas.base import BoilerplateBaseModel
from server.types import JSON


# Made them optional for now because there are some empty order_info fields in DB
class OrderItem(BaseModel):
    description: Optional[str]
    price: Optional[float]
    kind_id: Optional[str]
    kind_name: Optional[str]
    product_id: Optional[str]
    product_name: Optional[str]
    internal_product_id: Optional[str]
    quantity: Optional[int]

    @root_validator
    def check_order_item_if_has_both(cls, values):
        if (values.get("kind_id") is None) and (values.get("product_id") is None):
            raise ValueError("Order item should have at least one kind_id or one product_id!")
        if (values.get("kind_name") is None) and (values.get("product_name") is None):
            raise ValueError("Order item should have at least one kind_name or one product_name!")
        if bool(values.get("kind_id")) == bool(values.get("product_id")):
            raise ValueError("Order item can have either kind_id or product_id but not both!")
        if bool(values.get("kind_name")) == bool(values.get("product_name")):
            raise ValueError("Order item can have either kind_name or product_name but not both!")
        return values


class OrderBase(BoilerplateBaseModel):
    table_id: Optional[UUID]  # Optional or required ?
    total: Optional[float]
    customer_order_id: Optional[int]  # Optional or required ?
    status: Optional[str]


# Properties to receive via API on creation
class OrderCreate(OrderBase):
    shop_id: UUID
    order_info: List[OrderItem]
    completed_at: Optional[datetime] = None


# Properties to receive via API after creation
class OrderCreated(OrderBase):
    id: UUID
    created_at: datetime
    completed_at: Optional[datetime] = None
    table_name: Optional[str]


# Properties to receive via API on update
class OrderUpdate(OrderBase):
    shop_id: UUID
    order_info: List[OrderItem]


class OrderUpdated(OrderUpdate):
    id: UUID


class OrderInDBBase(OrderBase):
    id: UUID
    shop_id: UUID
    order_info: List[OrderItem]
    created_at: datetime
    completed_at: Optional[datetime] = None
    completed_by: Optional[UUID]

    class Config:
        orm_mode = True


# Additional properties to return via API
class OrderSchema(OrderInDBBase):
    table_name: Optional[str]
    shop_name: Optional[str] = None
    completed_by_name: Optional[str]
