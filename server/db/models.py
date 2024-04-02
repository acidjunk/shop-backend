from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy
import structlog
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, TypeDecorator, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import Dialect
from sqlalchemy.exc import DontWrapMixin
from sqlalchemy.orm import backref, relationship
from sqlalchemy_utils import UUIDType

from server.db.database import BaseModel, Database
from server.settings import app_settings
from server.utils.date_utils import nowtz

# from server.db import db


logger = structlog.get_logger(__name__)

TAG_LENGTH = 20
STATUS_LENGTH = 255

db = Database(app_settings.DATABASE_URI)


class UtcTimestampException(Exception, DontWrapMixin):
    pass


class UtcTimestamp(TypeDecorator):
    """Timestamps in UTC.

    This column type always returns timestamps with the UTC timezone, regardless of the database/connection time zone
    configuration. It also guards against accidentally trying to store Python naive timestamps (those without a time
    zone).
    """

    impl = sqlalchemy.types.TIMESTAMP(timezone=True)

    def process_bind_param(self, value: Optional[datetime], dialect: Dialect) -> Optional[datetime]:
        if value is not None:
            if value.tzinfo is None:
                raise UtcTimestampException(f"Expected timestamp with tzinfo. Got naive timestamp {value!r} instead")
        return value

    def process_result_value(self, value: Optional[datetime], dialect: Dialect) -> Optional[datetime]:
        if value is not None:
            return value.astimezone(timezone.utc)
        return value


class ShopsUsersTable(BaseModel):
    __tablename__ = "shops_users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column("user_id", UUID(as_uuid=True), ForeignKey("user.id"))
    shop_id = Column("shop_id", UUID(as_uuid=True), ForeignKey("shops.id"))


class RolesUsersTable(BaseModel):
    __tablename__ = "roles_users"
    id = Column(Integer(), primary_key=True)
    user_id = Column("user_id", UUID(as_uuid=True), ForeignKey("users.id"))
    role_id = Column("role_id", UUID(as_uuid=True), ForeignKey("roles.id"))


class RolesTable(BaseModel):
    __tablename__ = "roles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

    # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


class UsersTable(BaseModel):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True)
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean())
    fs_uniquifier = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime())
    roles = relationship("RolesTable", secondary="roles_users", backref=backref("users", lazy="dynamic"))
    shops = relationship("Shop", secondary="shops_users", backref=backref("users", lazy="dynamic"))

    mail_offers = Column(Boolean, default=False)

    # Human-readable values for the User when editing user related stuff.
    def __str__(self):
        return f"{self.username} : {self.email}"

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.email)

    @property
    def is_active(self):
        """Returns `True` if the user is active."""
        return self.active

    @property
    def is_superuser(self):
        """Returns `True` if the user is a member of the admin role."""
        print(self.roles)
        for role in self.roles:
            if role.name == "admin":
                return True
        return False


class Tag(BaseModel):
    __tablename__ = "tags"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(60), unique=True, index=True)

    kinds_to_tags = relationship("ProductToTag", cascade="save-update, merge, delete")

    def __repr__(self):
        return self.name


class Shop(BaseModel):
    __tablename__ = "shops"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(String(255), unique=True)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow())
    allowed_ips = Column(JSON)
    shop_to_category = relationship("Category", cascade="save-update, merge, delete")

    def __repr__(self):
        return self.name


class Table(BaseModel):
    __tablename__ = "shop_tables"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255))
    shop_id = Column("shop_id", UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    shop = relationship("Shop", lazy=True)

    def __repr__(self):
        return f"{self.shop.name}: {self.name}"


class MainCategory(BaseModel):
    __tablename__ = "main_categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255))
    name_en = Column(String(255), nullable=True)
    icon = Column(String(60), nullable=True)
    description = Column(String(255), unique=True, index=True)
    shop_id = Column("shop_id", UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    shop = relationship("Shop", lazy=True)
    order_number = Column(Integer, default=0)

    def __repr__(self):
        return f"{self.shop.name}: {self.name}"


class Category(BaseModel):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    main_category_id = Column(
        "main_category_id", UUID(as_uuid=True), ForeignKey("main_categories.id"), nullable=True, index=True
    )
    main_category = relationship("MainCategory", lazy=True)
    color = Column(String(20), default="#376E1A")
    name = Column(String(255))
    name_en = Column(String(255), nullable=True)
    icon = Column(String(60), nullable=True)
    description = Column(String(255), unique=True, index=True)
    shop_id = Column("shop_id", UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    shop = relationship("Shop", lazy=True)
    order_number = Column(Integer, default=0)
    image_1 = Column(String(255), unique=True, index=True)
    image_2 = Column(String(255), unique=True, index=True)
    pricelist_column = Column(String, nullable=True)
    pricelist_row = Column(Integer, default=0)

    shops_to_price = relationship("ShopToPrice", cascade="save-update, merge, delete")

    def __repr__(self):
        main_category = self.main_category.name if self.main_category_id else "NO_MAIN"
        return f"{self.shop.name}: {main_category}: {self.name}"

class Order(BaseModel):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    customer_order_id = Column(Integer)
    notes = Column(String, nullable=True)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    table_id = Column(UUID(as_uuid=True), ForeignKey("shop_tables.id"), nullable=True)
    order_info = Column(JSON)
    total = Column(Float())
    status = Column(String(), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_by = Column("completed_by", UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    completed_at = Column(DateTime, nullable=True)

    shop = relationship("Shop", lazy=True)
    user = relationship("UsersTable", backref=backref("orders", uselist=False))
    table = relationship("Table", backref=backref("shop_tables", uselist=False))

    def __repr__(self):
        return "<Order for shop: %s with total: %s>" % (self.shop.name, self.total)


class ProductToTag(BaseModel):
    __tablename__ = "products_to_tags"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    shop_id = Column("shop_id", UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    product_id = Column("product_id", UUID(as_uuid=True), ForeignKey("products.id"), index=True)
    tag_id = Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id"), index=True)
    product = relationship("Product", lazy=True)
    tag = relationship("Tag", lazy=True)


class ProductsTable(BaseModel):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), index=True)
    short_description_nl = Column(String())
    description_nl = Column(String())
    short_description_en = Column(String())
    description_en = Column(String())
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    complete = Column("complete", Boolean(), default=False)
    approved_at = Column(DateTime)
    approved = Column("approved", Boolean(), default=False)
    approved_by = Column("approved_by", UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    disapproved_reason = Column(String())
    image_1 = Column(String(255), unique=True, index=True)
    image_2 = Column(String(255), unique=True, index=True)
    image_3 = Column(String(255), unique=True, index=True)
    image_4 = Column(String(255), unique=True, index=True)
    image_5 = Column(String(255), unique=True, index=True)
    image_6 = Column(String(255), unique=True, index=True)


# Todo: Not sure about this ons
class License(BaseModel):
    __tablename__ = "licenses"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False)
    is_recurring = Column(Boolean, nullable=False)
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime)
    improviser_user = Column(UUID(as_uuid=True), nullable=False)
    seats = Column(Integer, nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    order = relationship("Order", lazy=True)
