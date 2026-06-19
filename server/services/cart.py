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
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, List

from server.schemas.base import quantize_money
from server.schemas.cart import CartCalculateItem, CartCalculation, CartLine
from server.services.shipping import compute_shipping_for_cart, resolve_vat_rate


def _effective_price(product: Any, plan: str) -> Decimal | None:
    """Return the effective inc-VAT-base (ex-VAT) unit price for a plan, applying any active discount."""
    if plan == "monthly":
        price = product.recurring_price_monthly
    elif plan == "yearly":
        price = product.recurring_price_yearly
    else:
        price = product.price

    if price is None:
        return None

    # Apply discount only on one-time prices and only when the window is active.
    if (
        plan == "onetime"
        and product.discounted_price is not None
        and product.discounted_from is not None
        and product.discounted_to is not None
    ):
        now = datetime.now(timezone.utc)
        disc_from = product.discounted_from
        disc_to = product.discounted_to
        # Make aware if naive (DB stores without tz in some configs)
        if disc_from.tzinfo is None:
            disc_from = disc_from.replace(tzinfo=timezone.utc)
        if disc_to.tzinfo is None:
            disc_to = disc_to.replace(tzinfo=timezone.utc)
        if disc_from <= now <= disc_to:
            price = product.discounted_price

    return Decimal(str(price))


def compute_cart_total(items: List[CartCalculateItem], shop: Any) -> CartCalculation:
    """Calculate line totals, subtotal, shipping, and grand total for a cart.

    Prices on products are ex-VAT; this function adds VAT per line using the
    shop's configured rates and rounds each line to 2 decimal places before
    summing — matching the frontend rounding convention.
    """
    from server.crud.crud_product import product_crud

    lines: list[CartLine] = []
    order_info: list[dict] = []

    for item in items:
        product = product_crud.get_id_by_shop_id(shop.id, item.product_id)
        if product is None:
            continue

        price_ex_vat = _effective_price(product, item.plan)
        if price_ex_vat is None:
            continue

        vat_rate = resolve_vat_rate(product, shop)
        unit_price_inc_vat = quantize_money(price_ex_vat * (1 + vat_rate / Decimal("100")))
        line_total_inc_vat = quantize_money(unit_price_inc_vat * item.quantity)

        product_name = product.translation.main_name if product.translation else str(product.id)

        lines.append(
            CartLine(
                product_id=product.id,
                product_name=product_name,
                quantity=item.quantity,
                unit_price_inc_vat=unit_price_inc_vat,
                vat_rate=vat_rate,
                line_total_inc_vat=line_total_inc_vat,
            )
        )

        order_info.append(
            {
                "product_id": str(product.id),
                "product_name": product_name,
                "price": line_total_inc_vat,
                "quantity": item.quantity,
                "shippable": product.shippable,
            }
        )

    subtotal_inc_vat = quantize_money(sum((line.line_total_inc_vat for line in lines), Decimal("0")))

    shipping = compute_shipping_for_cart(order_info, shop)
    shipping_fee = shipping.fee_inc_btw if shipping is not None and shipping.enabled else Decimal("0")
    grand_total = quantize_money(subtotal_inc_vat + shipping_fee)

    return CartCalculation(
        lines=lines,
        subtotal_inc_vat=subtotal_inc_vat,
        shipping=shipping,
        grand_total=grand_total,
    )
