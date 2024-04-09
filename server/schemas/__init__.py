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

from server.schemas.category import CategoryCreate, CategorySchema, CategoryUpdate
from server.schemas.flavor import FlavorCreate, FlavorSchema, FlavorUpdate
from server.schemas.kind import KindCreate, KindSchema, KindUpdate
from server.schemas.kind_to_flavor import KindToFlavorCreate, KindToFlavorSchema, KindToFlavorUpdate
from server.schemas.kind_to_strain import KindToStrainCreate, KindToStrainSchema, KindToStrainUpdate
from server.schemas.kind_to_tag import KindToTagCreate, KindToTagSchema, KindToTagUpdate
from server.schemas.main_category import MainCategoryCreate, MainCategorySchema, MainCategoryUpdate
from server.schemas.msg import Msg
from server.schemas.product import ProductCreate, ProductSchema, ProductUpdate
from server.schemas.role import RoleCreate, RoleSchema, RoleUpdate
from server.schemas.shop import ShopCreate, ShopSchema, ShopUpdate
from server.schemas.shop_to_price import ShopToPriceCreate, ShopToPriceSchema, ShopToPriceUpdate
from server.schemas.strain import StrainCreate, StrainSchema, StrainUpdate
from server.schemas.table import TableCreate, TableSchema, TableUpdate
from server.schemas.tag import TagCreate, TagSchema, TagUpdate
from server.schemas.token import Token, TokenPayload
from server.schemas.user import User, UserCreate, UserUpdate

__all__ = (
    "FlavorCreate",
    "FlavorUpdate",
    "FlavorSchema",
    "TagCreate",
    "TagUpdate",
    "TagSchema",
    "CategoryCreate",
    "CategoryUpdate",
    "CategorySchema",
    "MainCategoryCreate",
    "MainCategoryUpdate",
    "MainCategorySchema",
    "ShopCreate",
    "ShopUpdate",
    "ShopSchema",
    "ShopCreate",
    "ShopUpdate",
    "ShopSchema",
    "ShopToPriceCreate",
    "ShopToPriceUpdate",
    "ShopToPriceSchema",
    "ProductCreate",
    "ProductUpdate",
    "ProductSchema",
    "KindCreate",
    "KindUpdate",
    "KindSchema",
    "KindToFlavorCreate",
    "KindToFlavorUpdate",
    "KindToFlavorSchema",
    "KindToTagCreate",
    "KindToTagUpdate",
    "KindToTagSchema",
    "KindToStrainCreate",
    "KindToStrainUpdate",
    "KindToStrainSchema",
    "Token",
    "TokenPayload",
    "User",
    "UserCreate",
    "UserUpdate",
    "Msg",
    "RoleCreate",
    "RoleUpdate",
    "RoleSchema",
)
