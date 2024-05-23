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
    user_id = Column("user_id", UUID(as_uuid=True), ForeignKey("user.id"))
    role_id = Column("role_id", UUID(as_uuid=True), ForeignKey("role.id"))


class RolesTable(BaseModel):
    __tablename__ = "role"
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
    __tablename__ = "user"
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
        for role in self.roles:
            if role.name == "admin":
                return True
        return False


class Shop(BaseModel):
    __tablename__ = "shops"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(String(255), unique=True)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow())
    allowed_ips = Column(JSON)
    vat_standard = Column(Float, default=21.0)
    vat_lower_1 = Column(Float, default=10.0)
    vat_lower_2 = Column(Float, default=5.0)
    vat_lower_3 = Column(Float, default=2.0)
    vat_special = Column(Float, default=12.0)
    vat_zero = Column(Float, default=0.0)
    shop_to_category = relationship("Category", cascade="save-update, merge, delete")

    def __repr__(self):
        return self.name


class Tag(BaseModel):
    __tablename__ = "tags"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    shop_id = Column("shop_id", UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    name = Column(String(60), unique=True, index=True)

    shop = relationship("Shop", lazy=True)
    products_to_tags = relationship("ProductToTag", cascade="save-update, merge, delete")
    translation = relationship("TagTranslation", back_populates="tag", uselist=False)

    def __repr__(self):
        return f"{self.shop.name}: {self.translation.main_name}"


class TagTranslation(BaseModel):
    __tablename__ = "tag_translations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    tag_id = Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id"))
    main_name = Column(String(TAG_LENGTH), unique=True, index=True)
    alt1_name = Column(String(TAG_LENGTH), unique=True, index=True, nullable=False)
    alt2_name = Column(String(TAG_LENGTH), unique=True, index=True, nullable=False)
    tag = relationship("Tag", back_populates="translation")


class Account(BaseModel):
    __tablename__ = "accounts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    shop_id = Column("shop_id", UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    name = Column(String(255))
    # Todo: add a md5 repr of the name, so e-mail can safely be used as an identifer?

    shop = relationship("Shop", lazy=True)

    def __repr__(self):
        return f"{self.shop.name}: {self.name}"


class Category(BaseModel):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    color = Column(String(20), default="#376E1A")
    # Todo: deal with translation in a correct way
    icon = Column(String(TAG_LENGTH), nullable=True)
    shop_id = Column("shop_id", UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    shop = relationship("Shop", lazy=True)
    order_number = Column(Integer, default=0)
    image_1 = Column(String(255), unique=True, index=True)
    image_2 = Column(String(255), unique=True, index=True)
    translation = relationship("CategoryTranslation", back_populates="category", uselist=False)

    def __repr__(self):
        return f"{self.shop.name}: {self.translation.main_name}"


class CategoryTranslation(BaseModel):
    __tablename__ = "category_translations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    category_id = Column("category_id", UUID(as_uuid=True), ForeignKey("categories.id"))
    main_name = Column(String(255), unique=True, index=True)
    main_description = Column(String(), unique=True, index=True, nullable=True)
    alt1_name = Column(String(255), unique=True, index=True, nullable=True)
    alt1_description = Column(String(), unique=True, index=True, nullable=True)
    alt2_name = Column(String(255), unique=True, index=True, nullable=True)
    alt2_description = Column(String(), unique=True, index=True, nullable=True)
    category = relationship("Category", back_populates="translation")


class Order(BaseModel):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    customer_order_id = Column(Integer)
    notes = Column(String, nullable=True)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True)
    order_info = Column(JSON)
    # total = Column(Float())
    # status = Column(String(), default="pending")
    # created_at = Column(DateTime, default=datetime.utcnow)
    # completed_by = Column("completed_by", UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    # completed_at = Column(DateTime, nullable=True)
    #
    # shop = relationship("Shop", lazy=True)
    # user = relationship("UsersTable", backref=backref("orders", uselist=False))
    # table = relationship("Table", backref=backref("shop_tables", uselist=False))
    #
    # def __repr__(self):
    #     return "<Order for shop: %s with total: %s>" % (self.shop.name, self.total)


class ProductTable(BaseModel):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    shop_id = Column("shop_id", UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    category_id = Column("category_id", UUID(as_uuid=True), ForeignKey("categories.id"), index=True)
    price = Column(Float(), nullable=False)
    tax_category = Column(String(20), default="vat_standard")
    discounted_price = Column(Float(), nullable=True)
    discounted_from = Column(DateTime, nullable=True)
    discounted_to = Column(DateTime, nullable=True)
    image_1 = Column(String(255), unique=True, index=True)
    image_2 = Column(String(255), unique=True, index=True)
    image_3 = Column(String(255), unique=True, index=True)
    image_4 = Column(String(255), unique=True, index=True)
    image_5 = Column(String(255), unique=True, index=True)
    image_6 = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    translation = relationship("ProductTranslation", back_populates="product", uselist=False)
    shop = relationship("Shop", lazy=True)
    category = relationship("Category", lazy=True)

    def __repr__(self):
        return f"{self.shop.name}: {self.translation.main_name}"


class ProductTranslation(BaseModel):
    __tablename__ = "product_translations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    product_id = Column("product_id", UUID(as_uuid=True), ForeignKey("products.id"))
    main_name = Column(String(255), unique=True, index=True)
    main_description = Column(String(), unique=True, index=True)
    main_description_short = Column(String(), unique=True, index=True, nullable=True)
    alt1_name = Column(String(255), unique=True, index=True, nullable=True)
    alt1_description = Column(String(), unique=True, index=True, nullable=True)
    alt1_description_short = Column(String(), unique=True, index=True, nullable=True)
    alt2_name = Column(String(255), unique=True, index=True, nullable=True)
    alt2_description = Column(String(), unique=True, index=True, nullable=True)
    alt2_description_short = Column(String(), unique=True, index=True, nullable=True)

    product = relationship("ProductTable", back_populates="translation")


class ProductToTag(BaseModel):
    __tablename__ = "products_to_tags"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    shop_id = Column("shop_id", UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    product_id = Column("product_id", UUID(as_uuid=True), ForeignKey("products.id"), index=True)
    tag_id = Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id"), index=True)
    product = relationship("ProductTable", lazy=True)
    tag = relationship("Tag", lazy=True)


class License(BaseModel):
    __tablename__ = "licenses"
    # Todo: determine if we can get rid of the improviser_user and if we need a shop_id
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
