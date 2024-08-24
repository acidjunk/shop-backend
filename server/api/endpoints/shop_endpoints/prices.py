from datetime import datetime
from enum import Enum
from uuid import UUID

import structlog
from fastapi import APIRouter
from pydantic import BaseModel

from server.crud.crud_shop import shop_crud
from server.db import ProductTable
from server.db.models import CategoryTable, CategoryTranslationTable, ProductTranslationTable

router = APIRouter()
logger = structlog.get_logger(__name__)


class Lang(str, Enum):
    """Language options."""

    MAIN = "main"
    ALT1 = "alt1"
    ALT2 = "alt2"


class ProductResponse(BaseModel):
    id: str
    category: str
    tags: list[str] = []
    name: str
    description_short: str
    description: str
    tax_category: str
    tax_percentage: float
    price: float | None = None
    recurring_price_monthly: float | None = None
    recurring_price_yearly: float | None = None
    max_one: bool
    shippable: bool
    digital: str | None = None
    featured: bool
    discounted_price: float | None = None
    discounted_from: datetime | None = None
    discounted_to: datetime | None = None
    image_1: str | None = None
    image_2: str | None = None
    image_3: str | None = None
    image_4: str | None = None
    image_5: str | None = None
    image_6: str | None = None


class Cart(BaseModel):
    products: list[UUID]


# Note: the "product" will have some Joined attributes that are not avail on the type itself
def to_response_model(product: ProductTable, lang: Lang, shop) -> ProductResponse:
    tax = getattr(shop, product.tax_category)

    if lang == Lang.MAIN:
        product_response = ProductResponse(
            id=str(product.id),
            category=product.category.translation.main_name,
            tags=[tag.translation.main_name for tag in product.tags],
            name=product.translation.main_name,
            description_short=product.translation.main_description_short,
            description=product.translation.main_description,
            tax_category=product.tax_category,
            tax_percentage=tax,
            price=product.price,
            recurring_price_monthly=product.recurring_price_monthly,
            recurring_price_yearly=product.recurring_price_yearly,
            max_one=product.max_one,
            shippable=product.shippable,
            digital=product.digital,
            featured=product.featured,
        )
    elif lang == Lang.ALT1:
        product_response = ProductResponse(
            id=str(product.id),
            category=product.category.translation.alt1_name,
            tags=[tag.translation.alt1_name for tag in product.tags],
            name=product.translation.alt1_name,
            description_short=product.translation.alt1_description_short,
            description=product.translation.alt1_description,
            tax_category=product.tax_category,
            tax_percentage=tax,
            price=product.price,
            recurring_price_monthly=product.recurring_price_monthly,
            recurring_price_yearly=product.recurring_price_yearly,
            max_one=product.max_one,
            shippable=product.shippable,
            digital=product.digital,
            featured=product.featured,
        )
    elif lang == Lang.ALT2:
        product_response = ProductResponse(
            id=str(product.id),
            category=product.category.translation.alt2_name,
            tags=[tag.translation.alt2_name for tag in product.tags],
            name=product.translation.alt2_name,
            description_short=product.translation.alt2_description_short,
            description=product.translation.alt2_description,
            tax_category=product.tax_category,
            tax_percentage=tax,
            price=product.price,
            recurring_price_monthly=product.recurring_price_monthly,
            recurring_price_yearly=product.recurring_price_yearly,
            max_one=product.max_one,
            shippable=product.shippable,
            digital=product.digital,
            featured=product.featured,
        )
    else:
        raise ValueError(f"Unsupported language: {lang}")

    product_response.discounted_price = product.discounted_price
    product_response.discounted_from = product.discounted_from
    product_response.discounted_to = product.discounted_to
    product_response.image_1 = product.image_1
    product_response.image_2 = product.image_2
    product_response.image_3 = product.image_3
    product_response.image_4 = product.image_4
    product_response.image_5 = product.image_5
    product_response.image_6 = product.image_6

    return product_response


@router.get("/", response_model=list[ProductResponse])
def get_products(
    shop_id: UUID,
    lang: Lang,
    # response: Response,
) -> list[dict]:
    products = (
        ProductTable.query.join(ProductTranslationTable)
        .join(CategoryTable)
        .join(CategoryTranslationTable)
        .filter(ProductTable.shop_id == shop_id)
    )

    if lang == Lang.ALT1:
        # filter out products and categories with missing translations
        products = (
            products.filter(ProductTranslationTable.alt1_name.is_not(None))
            .filter(ProductTranslationTable.alt1_description.is_not(None))
            .filter(ProductTranslationTable.alt1_description_short.is_not(None))
            .filter(CategoryTranslationTable.alt1_name.is_not(None))
        )
    if lang == Lang.ALT2:
        # filter out products and categories with missing translations
        products = (
            products.filter(ProductTranslationTable.alt2_name.is_not(None))
            .filter(ProductTranslationTable.alt2_description.is_not(None))
            .filter(ProductTranslationTable.alt2_description_short.is_not(None))
            .filter(CategoryTranslationTable.alt2_name.is_not(None))
        )

    shop = shop_crud.get(shop_id)

    return [to_response_model(product, lang, shop) for product in products]


@router.post("/", response_model=list[ProductResponse])
def get_cart_products(
    shop_id: UUID,
    lang: Lang,
    cart: Cart,
    # response: Response,
) -> list[dict]:
    products = (
        ProductTable.query.join(ProductTranslationTable)
        .join(CategoryTable)
        .join(CategoryTranslationTable)
        .filter(ProductTable.shop_id == shop_id)
        .filter(ProductTable.id.in_(cart.products))
    )

    response_products = []

    shop = shop_crud.get(shop_id)

    for product in products:
        if lang == Lang.ALT1:
            if (
                product.translation.alt1_name is None
                or product.translation.alt1_description is None
                or product.translation.alt1_description_short is None
                or product.category.translation.alt1_name is None
            ):
                response_product = to_response_model(product, Lang.MAIN, shop)
                response_products.append(response_product)
            else:
                response_product = to_response_model(product, lang, shop)
                response_products.append(response_product)
        elif lang == Lang.ALT2:
            if (
                product.translation.alt2_name is None
                or product.translation.alt2_description is None
                or product.translation.alt2_description_short is None
                or product.category.translation.alt2_name is None
            ):
                response_product = to_response_model(product, Lang.MAIN, shop)
                response_products.append(response_product)
            else:
                response_product = to_response_model(product, lang, shop)
                response_products.append(response_product)
        else:
            response_product = to_response_model(product, lang, shop)
            response_products.append(response_product)

    return response_products
