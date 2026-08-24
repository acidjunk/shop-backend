#!/usr/bin/env python3
"""Seed deterministic JVJ-eval shop data for the LibreChat orchestrator evals.

This reproduces the *shop half* of the flagship "JVJ referral" cross-domain scenario
(see ``docs/librechat-as-agent-orchestrator.md`` in the librechat repo and the eval plan).
The WFO half (JVJ Customer subscriptions) is seeded separately by
``wfo-backend-formatics/scripts/seed_jvj_eval.py``.

Pinned ground truth produced here:
  * 3 shops so ``list_my_shops`` is non-trivial: "JVJ Selection" + 2 decoys.
  * In "JVJ Selection": completed orders for ``youth1.terminated@example.com`` and
    ``youth2.terminated@example.com`` (the 2 of 6 terminated referrals who ordered),
    plus 2 decoy completed orders and 2 pending orders from non-referral buyers, so
    ``list_complete_orders`` / ``list_pending_orders`` are not trivially all-referral.
  * ``youth3..6.terminated@example.com`` deliberately have NO account/order here — they are
    terminated referrals who never ordered.

Identity model (load-bearing): the shop has **no email column on orders**. Customer identity is
``order.account_id -> Account.name``, and ``Account.name`` IS the email. The referral token is
never stored on the order — email is the only cross-domain join key. So the account emails below
must match the WFO referral emails exactly.

Idempotent: re-running purges the three seed shops (by exact name) and their dependent rows, then
recreates everything. It only touches shops whose name is in ``SEED_SHOP_NAMES`` — no global
truncate — so it is safe to run against a shared dev DB, though the eval stack points
``DATABASE_URI`` at a dedicated eval DB.

Usage:
    cd shop-virge-backend
    DATABASE_URI=postgresql://shop:shop@localhost/shop_eval PYTHONPATH=. python scripts/seed_jvj_eval.py
"""

from __future__ import annotations

from datetime import datetime
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

from server.db import db, init_database
from server.db.models import (
    Account,
    CategoryTable,
    CategoryTranslationTable,
    OrderTable,
    ProductTable,
    ProductTranslationTable,
    ShopTable,
)
from server.settings import app_settings

# --- Referral emails: MUST match wfo-backend-formatics/scripts/seed_jvj_eval.py exactly. -------
YOUTH1_EMAIL = "youth1.terminated@example.com"
YOUTH2_EMAIL = "youth2.terminated@example.com"

# --- Non-referral decoy buyers (unambiguously fake, no PII). -----------------------------------
BUYER_A_EMAIL = "buyerA@example.com"
BUYER_B_EMAIL = "buyerB@example.com"
BUYER_C_EMAIL = "buyerC@example.com"
BUYER_D_EMAIL = "buyerD@example.com"

JVJ_SHOP_NAME = "JVJ Selection"
DECOY_SHOP_NAMES = ["Gadget Corner", "Bookish"]
SEED_SHOP_NAMES = [JVJ_SHOP_NAME, *DECOY_SHOP_NAMES]

# Deterministic completion timestamps (no wall-clock reads -> reproducible seed).
_COMPLETED_AT = datetime(2026, 6, 15, 10, 0, 0)


def _purge_seed_shops() -> None:
    """Delete the seed shops and every row that depends on them, in FK-safe order.

    FKs to ``shops.id`` (accounts, products, categories, orders) are mostly declared without
    ``ON DELETE CASCADE``, so children must be removed before the shop row.
    """
    shops = db.session.query(ShopTable).filter(ShopTable.name.in_(SEED_SHOP_NAMES)).all()
    if not shops:
        return
    shop_ids = [s.id for s in shops]

    product_ids = [
        pid for (pid,) in db.session.query(ProductTable.id).filter(ProductTable.shop_id.in_(shop_ids)).all()
    ]
    category_ids = [
        cid for (cid,) in db.session.query(CategoryTable.id).filter(CategoryTable.shop_id.in_(shop_ids)).all()
    ]

    # orders -> accounts -> product translations -> products -> category translations -> categories -> shops
    db.session.query(OrderTable).filter(OrderTable.shop_id.in_(shop_ids)).delete(synchronize_session=False)
    db.session.query(Account).filter(Account.shop_id.in_(shop_ids)).delete(synchronize_session=False)
    if product_ids:
        db.session.query(ProductTranslationTable).filter(
            ProductTranslationTable.product_id.in_(product_ids)
        ).delete(synchronize_session=False)
    db.session.query(ProductTable).filter(ProductTable.shop_id.in_(shop_ids)).delete(synchronize_session=False)
    if category_ids:
        db.session.query(CategoryTranslationTable).filter(
            CategoryTranslationTable.category_id.in_(category_ids)
        ).delete(synchronize_session=False)
    db.session.query(CategoryTable).filter(CategoryTable.shop_id.in_(shop_ids)).delete(synchronize_session=False)
    db.session.query(ShopTable).filter(ShopTable.id.in_(shop_ids)).delete(synchronize_session=False)
    db.session.commit()


def _seed_shop_id(name: str) -> UUID:
    """Deterministic shop id so eval golden sets can pin shop_id arguments."""
    return uuid5(NAMESPACE_URL, f"https://virge.io/eval-seed/shop/{name}")


def _make_shop(name: str) -> UUID:
    """Create a minimal shop with an explicit name (``make_shop`` can't set the name)."""
    shop = ShopTable(
        id=_seed_shop_id(name),
        name=name,
        description=f"{name} (JVJ eval seed)",
        stripe_public_key="string",
        vat_standard=21,
        vat_lower_1=15,
        vat_lower_2=10,
        vat_lower_3=5,
        vat_special=2,
        vat_zero=0,
        config="{}",
        shop_type="{}",
    )
    db.session.add(shop)
    db.session.commit()
    return shop.id


def _make_category(shop_id: UUID, name: str) -> UUID:
    category = CategoryTable(shop_id=shop_id)
    db.session.add(category)
    db.session.commit()
    trans = CategoryTranslationTable(category_id=category.id, main_name=name, main_description=f"{name} category")
    db.session.add(trans)
    db.session.commit()
    return category.id


def _make_product(shop_id: UUID, category_id: UUID, name: str, price: float = 9.99) -> UUID:
    new_id = uuid4()
    product = ProductTable(
        id=new_id,
        short_id=str(new_id)[:12],
        shop_id=shop_id,
        category_id=category_id,
        price=price,
        stock=100,
        tax_category="vat_standard",
        shippable=True,
    )
    db.session.add(product)
    db.session.commit()
    trans = ProductTranslationTable(
        product_id=product.id,
        main_name=name,
        main_description=f"{name} description",
        main_description_short=f"{name} short",
    )
    db.session.add(trans)
    db.session.commit()
    return product.id


def _make_account(shop_id: UUID, email: str) -> UUID:
    """Account whose ``name`` IS the customer email (the cross-domain join key)."""
    account = Account(shop_id=shop_id, name=email)
    db.session.add(account)
    db.session.commit()
    return account.id


def _make_order(
    shop_id: UUID,
    account_id: UUID,
    product_id_1: UUID,
    product_id_2: UUID,
    customer_order_id: int,
    status: str,
    total: float = 19.98,
) -> UUID:
    order_info = [
        {"description": "JVJ eval item", "product_name": "Item A", "price": 9.99, "quantity": 1,
         "product_id": str(product_id_1)},
        {"description": "JVJ eval item", "product_name": "Item B", "price": 9.99, "quantity": 1,
         "product_id": str(product_id_2)},
    ]
    order = OrderTable(
        shop_id=shop_id,
        account_id=account_id,
        customer_order_id=customer_order_id,
        order_info=order_info,
        total=total,
        status=status,
    )
    if status in ("complete", "cancelled"):
        order.completed_at = _COMPLETED_AT
    db.session.add(order)
    db.session.commit()
    return order.id


def _seed_jvj_selection() -> None:
    shop_id = _make_shop(JVJ_SHOP_NAME)
    category_id = _make_category(shop_id, "JVJ Merch")
    p1 = _make_product(shop_id, category_id, "JVJ Starter Pack")
    p2 = _make_product(shop_id, category_id, "JVJ Booster")

    order_seq = 1

    # The two terminated referrals who DID order (ground truth: 2 of 6).
    for email in (YOUTH1_EMAIL, YOUTH2_EMAIL):
        acc = _make_account(shop_id, email)
        _make_order(shop_id, acc, p1, p2, order_seq, status="complete")
        order_seq += 1

    # Decoy completed orders from non-referral buyers (so complete-orders isn't all-referral).
    for email in (BUYER_A_EMAIL, BUYER_B_EMAIL):
        acc = _make_account(shop_id, email)
        _make_order(shop_id, acc, p1, p2, order_seq, status="complete")
        order_seq += 1

    # Pending orders from non-referral buyers.
    for email in (BUYER_C_EMAIL, BUYER_D_EMAIL):
        acc = _make_account(shop_id, email)
        _make_order(shop_id, acc, p1, p2, order_seq, status="pending")
        order_seq += 1


def _seed_decoy_shop(name: str, buyer_email: str) -> None:
    shop_id = _make_shop(name)
    category_id = _make_category(shop_id, f"{name} Goods")
    p1 = _make_product(shop_id, category_id, f"{name} Item 1")
    p2 = _make_product(shop_id, category_id, f"{name} Item 2")
    acc = _make_account(shop_id, buyer_email)
    _make_order(shop_id, acc, p1, p2, customer_order_id=1, status="complete")


def _report() -> None:
    for name in SEED_SHOP_NAMES:
        shop = db.session.query(ShopTable).filter(ShopTable.name == name).one()
        n_complete = (
            db.session.query(OrderTable)
            .filter(OrderTable.shop_id == shop.id, OrderTable.status == "complete")
            .count()
        )
        n_pending = (
            db.session.query(OrderTable)
            .filter(OrderTable.shop_id == shop.id, OrderTable.status == "pending")
            .count()
        )
        print(f"  {name!r}: {n_complete} complete, {n_pending} pending order(s)")


def main() -> None:
    init_database(app_settings)
    print(f"Seeding JVJ eval shop data into {app_settings.DATABASE_URI}")
    _purge_seed_shops()
    _seed_jvj_selection()
    for name, buyer in zip(DECOY_SHOP_NAMES, (BUYER_A_EMAIL, BUYER_B_EMAIL)):
        _seed_decoy_shop(name, buyer)
    print("Done. Shops seeded:")
    _report()


if __name__ == "__main__":
    main()
