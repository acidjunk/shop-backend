# Copyright 2024 René Dohmen <acidjunk@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

import sqlalchemy
import structlog
from sqlalchemy import JSON, Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, TypeDecorator, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine import Dialect
from sqlalchemy.exc import DontWrapMixin
from sqlalchemy.orm import backref, relationship
from sqlalchemy_utils import UUIDType

from server.db.database import BaseModel, Database
from server.schemas.shop import ShopType
from server.settings import app_settings

logger = structlog.get_logger(__name__)

TAG_LENGTH = 100
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
    cache_ok = False
    python_type = datetime

    def process_bind_param(self, value: Optional[datetime], dialect: Dialect) -> datetime | None:
        if value is not None:
            if value.tzinfo is None:
                raise UtcTimestampException(f"Expected timestamp with tzinfo. Got naive timestamp {value!r} instead")
        return value

    def process_result_value(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        return value.astimezone(timezone.utc) if value else value


class ShopUserTable(BaseModel):
    __tablename__ = "shops_users"
    id = Column(UUIDType, server_default=text("uuid_generate_v4()"), primary_key=True, index=True)
    user_id = Column("user_id", UUIDType, ForeignKey("users.id"))
    shop_id = Column("shop_id", UUIDType, ForeignKey("shops.id"))


class RoleUserTable(BaseModel):
    __tablename__ = "roles_users"
    id = Column(UUIDType, server_default=text("uuid_generate_v4()"), primary_key=True, index=True)
    user_id = Column("user_id", UUIDType, ForeignKey("users.id"))
    role_id = Column("role_id", UUIDType, ForeignKey("roles.id"))


class RoleTable(BaseModel):
    __tablename__ = "roles"
    id = Column(UUIDType, server_default=text("uuid_generate_v4()"), primary_key=True, index=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

    # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


class UserTable(BaseModel):
    __tablename__ = "users"
    id = Column(UUIDType, server_default=text("uuid_generate_v4()"), primary_key=True, index=True)
    email = Column(String(255), unique=True)
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean(), server_default=text("true"))
    created_at = Column(UtcTimestamp, server_default=text("CURRENT_TIMESTAMP"))
    confirmed_at = Column(UtcTimestamp)
    roles = relationship("RoleTable", secondary="roles_users", backref=backref("users", lazy="dynamic"))
    shops = relationship("ShopTable", secondary="shops_users", backref=backref("users", lazy="dynamic"))

    mail_offers = Column(Boolean, default=False)

    def __repr__(self):
        return f"{self.username} : {self.email}"

    @property
    def is_active(self):
        """Returns `True` if the user is active."""
        return self.active

    @property
    def is_superuser(self):
        """Returns `True` if the user is a member of the admin role."""
        for role in self.roles:
            if role.name == "admin":
                return True
        return False


class ShopTable(BaseModel):
    __tablename__ = "shops"
    id = Column(UUIDType, server_default=text("uuid_generate_v4()"), primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    shop_type = Column(Enum(ShopType), nullable=False, server_default="Basic Webshop")
    description = Column(String(255), unique=True)
    allowed_ips = Column(postgresql.JSONB())
    config = Column(postgresql.JSONB())
    config_version = Column(Integer, nullable=False, server_default="1")
    stripe_secret_key = Column(String(255), nullable=True)
    stripe_public_key = Column(String(255), nullable=True)
    vat_standard = Column(Float, default=21.0)
    vat_lower_1 = Column(Float, default=10.0)
    vat_lower_2 = Column(Float, default=5.0)
    vat_lower_3 = Column(Float, default=2.0)
    vat_special = Column(Float, default=12.0)
    vat_zero = Column(Float, default=0.0)
    created_at = Column(UtcTimestamp, server_default=text("CURRENT_TIMESTAMP"))
    modified_at = Column(
        UtcTimestamp, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP")
    )
    shop_to_category = relationship("CategoryTable", cascade="save-update, merge, delete")

    def __repr__(self):
        return self.name


class TagTable(BaseModel):
    __tablename__ = "tags"
    id = Column(UUIDType, server_default=text("uuid_generate_v4()"), primary_key=True, index=True)
    shop_id = Column("shop_id", UUIDType, ForeignKey("shops.id"), index=True)
    name = Column(String(60), index=True)

    shop = relationship("ShopTable", lazy=True)
    products_to_tags = relationship("ProductToTagTable", cascade="save-update, merge, delete")
    translation = relationship("TagTranslationTable", back_populates="tag", uselist=False)

    def __repr__(self):
        return f"{self.shop.name}: {self.translation.main_name}"


class TagTranslationTable(BaseModel):
    __tablename__ = "tag_translations"
    id = Column(UUIDType, server_default=text("uuid_generate_v4()"), primary_key=True, index=True)
    tag_id = Column("tag_id", UUIDType, ForeignKey("tags.id"))
    main_name = Column(String(TAG_LENGTH), index=True, nullable=False)
    alt1_name = Column(String(TAG_LENGTH), index=True, nullable=True)
    alt2_name = Column(String(TAG_LENGTH), index=True, nullable=True)
    tag = relationship("TagTable", back_populates="translation")


class Account(BaseModel):
    __tablename__ = "accounts"
    id = Column(UUIDType, server_default=text("uuid_generate_v4()"), primary_key=True, index=True)
    shop_id = Column("shop_id", UUIDType, ForeignKey("shops.id"), index=True)
    name = Column(String(255))
    # a hash for the name, so sensible info can be used as an identifier
    hash_name = Column(String(255), nullable=True, index=True)
    # details for address and customer name
    details = Column("details", JSON, nullable=True)
    shop = relationship("ShopTable", lazy=True)

    def __repr__(self):
        return f"{self.shop.name}: {self.name}"


class CategoryTable(BaseModel):
    __tablename__ = "categories"
    id = Column(UUIDType, server_default=text("uuid_generate_v4()"), primary_key=True, index=True)
    color = Column(String(20), default="#376E1A")
    # Todo: deal with translation in a correct way
    icon = Column(String(TAG_LENGTH), nullable=True)
    shop_id = Column("shop_id", UUIDType, ForeignKey("shops.id"), index=True)
    shop = relationship("ShopTable", lazy=True)
    order_number = Column(Integer, default=0)
    main_image = Column(String(255), index=True)
    alt1_image = Column(String(255), index=True)
    alt2_image = Column(String(255), index=True)
    translation = relationship("CategoryTranslationTable", back_populates="category", uselist=False)

    def __repr__(self):
        return f"{self.shop.name}: {self.translation.main_name}"


class CategoryTranslationTable(BaseModel):
    __tablename__ = "category_translations"
    id = Column(UUIDType, server_default=text("uuid_generate_v4()"), primary_key=True, index=True)
    category_id = Column("category_id", UUIDType, ForeignKey("categories.id"))
    main_name = Column(String(255), index=True, nullable=False)
    main_description = Column(String(), index=True, nullable=False)
    alt1_name = Column(String(255), index=True, nullable=True)
    alt1_description = Column(String(), index=True, nullable=True)
    alt2_name = Column(String(255), index=True, nullable=True)
    alt2_description = Column(String(), index=True, nullable=True)
    category = relationship("CategoryTable", back_populates="translation")


class OrderTable(BaseModel):
    __tablename__ = "orders"
    id = Column(UUIDType, server_default=text("uuid_generate_v4()"), primary_key=True, index=True)
    customer_order_id = Column(Integer)
    notes = Column(String, nullable=True)
    shop_id = Column(UUIDType, ForeignKey("shops.id"), index=True)
    account_id = Column(UUIDType, ForeignKey("accounts.id"), nullable=True)
    order_info = Column(postgresql.JSONB())
    total = Column(Float())
    status = Column(String(), default="pending")
    created_at = Column(UtcTimestamp, server_default=text("CURRENT_TIMESTAMP"))
    completed_by = Column("completed_by", UUIDType, ForeignKey("users.id"), nullable=True)
    completed_at = Column(DateTime, nullable=True)

    shop = relationship("ShopTable", lazy=True)
    user = relationship("UserTable", backref=backref("orders", uselist=False))
    account = relationship("Account", backref=backref("accounts", uselist=False))

    def __repr__(self):
        return "<Order for shop: %s with total: %s>" % (self.shop.name, self.total)


class ProductTable(BaseModel):
    __tablename__ = "products"
    id = Column(UUIDType, server_default=text("uuid_generate_v4()"), primary_key=True, index=True)
    shop_id = Column("shop_id", UUIDType, ForeignKey("shops.id"), index=True)
    category_id = Column("category_id", UUIDType, ForeignKey("categories.id"), index=True)
    price = Column(Float(), nullable=True)
    tax_category = Column(String(20), default="vat_standard")
    discounted_price = Column(Float(), nullable=True)
    discounted_from = Column(DateTime, nullable=True)
    discounted_to = Column(DateTime, nullable=True)
    recurring_price_monthly = Column(Float(), nullable=True)
    recurring_price_yearly = Column(Float(), nullable=True)
    max_one = Column(Boolean(), default=False)
    digital = Column(String(255), nullable=True)  # if provided: links to original asset
    shippable = Column(Boolean(), default=True)
    featured = Column(Boolean(), default=False)
    new_product = Column(Boolean(), default=False)
    order_number = Column(Integer, default=0)
    image_1 = Column(String(255), index=True)
    image_2 = Column(String(255), index=True)
    image_3 = Column(String(255), index=True)
    image_4 = Column(String(255), index=True)
    image_5 = Column(String(255), index=True)
    image_6 = Column(String(255), index=True)
    created_at = Column(UtcTimestamp, server_default=text("CURRENT_TIMESTAMP"))
    modified_at = Column(
        UtcTimestamp, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP")
    )

    translation = relationship("ProductTranslationTable", back_populates="product", uselist=False)
    shop = relationship("ShopTable", lazy=True)
    category = relationship("CategoryTable", lazy=True)
    tags = relationship("TagTable", secondary="products_to_tags", backref=backref("products", lazy="dynamic"))

    def __repr__(self):
        return f"{self.shop.name}: {self.translation.main_name}"


class ProductTranslationTable(BaseModel):
    __tablename__ = "product_translations"
    id = Column(UUIDType, server_default=text("uuid_generate_v4()"), primary_key=True, index=True)
    product_id = Column("product_id", UUIDType, ForeignKey("products.id"))
    main_name = Column(String(255), index=True, nullable=False)
    main_description = Column(String(), index=True, nullable=False)
    main_description_short = Column(String(), index=True, nullable=False)
    alt1_name = Column(String(255), index=True, nullable=True)
    alt1_description = Column(String(), index=True, nullable=True)
    alt1_description_short = Column(String(), index=True, nullable=True)
    alt2_name = Column(String(255), index=True, nullable=True)
    alt2_description = Column(String(), index=True, nullable=True)
    alt2_description_short = Column(String(), index=True, nullable=True)

    product = relationship("ProductTable", back_populates="translation")


class ProductToTagTable(BaseModel):
    __tablename__ = "products_to_tags"
    id = Column(UUIDType, server_default=text("uuid_generate_v4()"), primary_key=True, index=True)
    shop_id = Column("shop_id", UUIDType, ForeignKey("shops.id"), index=True)
    product_id = Column("product_id", UUIDType, ForeignKey("products.id"), index=True)
    tag_id = Column("tag_id", UUIDType, ForeignKey("tags.id"), index=True)
    product = relationship("ProductTable", lazy=True)
    tag = relationship("TagTable", lazy=True)


class License(BaseModel):
    __tablename__ = "licenses"
    # Todo: determine if we can get rid of the improviser_user and if we need a shop_id
    id = Column(UUIDType, server_default=text("uuid_generate_v4()"), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    is_recurring = Column(Boolean, nullable=False)
    start_date = Column(UtcTimestamp, server_default=text("CURRENT_TIMESTAMP"))
    end_date = Column(UtcTimestamp)
    improviser_user = Column(UUIDType, nullable=False)
    seats = Column(Integer, nullable=False)
    order_id = Column(UUIDType, ForeignKey("orders.id"), index=True)
    created_at = Column(UtcTimestamp, server_default=text("CURRENT_TIMESTAMP"))
    modified_at = Column(
        UtcTimestamp, server_default=text("CURRENT_TIMESTAMP"), server_onupdate=text("CURRENT_TIMESTAMP")
    )
    order = relationship("OrderTable", lazy=True)
