from enum import Enum
from http import HTTPStatus
from uuid import UUID

import stripe
import structlog
from fastapi import APIRouter

from server.crud.crud_shop import shop_crud
from server.db.models import Account

router = APIRouter()
logger = structlog.get_logger(__name__)


def get_stripe_customer(account_id: UUID):
    account = (Account.query.filter(Account.id == account_id)).first()
    return account.details["stripe_customer_id"]


def get_stripe_prices(product_ids: list[UUID], yearly: bool):
    lookup_keys = []
    for id in product_ids:
        if yearly:
            lookup_keys.append(f"yearly-{id}")
        else:
            lookup_keys.append(f"monthly-{id}")

    prices = stripe.Price.list(lookup_keys=lookup_keys)

    items = []
    for price in prices.data:
        items.append({"price": price.id})

    return items


@router.post("/", status_code=HTTPStatus.CREATED)
def create_payment_intent(shop_id: UUID, price: int, account_id: UUID):
    try:
        shop = shop_crud.get(shop_id)
        stripe.api_key = shop.stripe_secret_key
        customer_id = get_stripe_customer(account_id)

        intent = stripe.PaymentIntent.create(
            amount=price,
            currency="eur",
            payment_method_types=["card", "ideal"],
            setup_future_usage="off_session",
            customer=customer_id,
        )
        return {"clientSecret": intent["client_secret"]}
    except Exception as e:
        return e


@router.post("/subscription", status_code=HTTPStatus.CREATED)
def create_subscription_intent(shop_id: UUID, product_ids: list[UUID], account_id: UUID, yearly: bool = False):
    try:
        shop = shop_crud.get(shop_id)
        stripe.api_key = shop.stripe_secret_key
        customer_id = get_stripe_customer(account_id)
        prices = get_stripe_prices(product_ids, yearly)

        subscription = stripe.Subscription.create(
            items=prices,
            payment_behavior="default_incomplete",
            payment_settings={
                "payment_method_types": ["card", "paypal"],
                "save_default_payment_method": "on_subscription",
            },
            customer=customer_id,
            expand=["latest_invoice.payment_intent"],
        )
        return {
            "clientSecret": subscription.latest_invoice.payment_intent.client_secret,
            "subscriptionId": subscription.id,
        }
    except Exception as e:
        return e


@router.delete("/subscription/{subscription_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def cancel_subscription(shop_id: UUID, subscription_id: str):
    try:
        shop = shop_crud.get(shop_id)
        stripe.api_key = shop.stripe_secret_key
        stripe.Subscription.cancel(subscription_id)

        return 204
    except Exception as e:
        return e
