from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from server.db import db
from server.db.models import OrderTable, ShopTable
from server.mail import send_order_confirmation_emails
from tests.unit_tests.factories.account import make_account
from tests.unit_tests.factories.categories import make_category
from tests.unit_tests.factories.product import make_product


@pytest.fixture()
def mock_smtp(monkeypatch):
    """Replace server.mail.SMTP so send_order_confirmation_emails never opens a socket."""
    instance = MagicMock()
    smtp_cls = MagicMock(return_value=instance)
    monkeypatch.setattr("server.mail.SMTP", smtp_cls)
    return smtp_cls, instance


@pytest.fixture()
def completed_order(shop_with_config):
    shop_id = shop_with_config
    account_id = make_account(shop_id=shop_id, name="customer@example.com")
    category = make_category(shop_id=shop_id)
    product_1 = make_product(shop_id=shop_id, category_id=category, main_name="Widget A")
    product_2 = make_product(shop_id=shop_id, category_id=category, main_name="Widget B")
    order = OrderTable(
        shop_id=shop_id,
        account_id=account_id,
        customer_order_id=42,
        order_info=[
            {
                "description": "first line",
                "product_name": "Widget A",
                "price": 10.0,
                "quantity": 2,
                "product_id": str(product_1),
            },
            {
                "description": "second line",
                "product_name": "Widget B",
                "price": 5.0,
                "quantity": 1,
                "product_id": str(product_2),
            },
        ],
        total=25.0,
        status="complete",
        completed_at=datetime(2026, 4, 23, 12, 0, tzinfo=timezone.utc),
    )
    db.session.add(order)
    db.session.commit()
    return order.id


def test_send_order_confirmation_emails_renders_without_smtp(completed_order, shop_with_config, mock_smtp):
    smtp_cls, smtp_instance = mock_smtp
    order = db.session.get(OrderTable, completed_order)
    shop = db.session.get(ShopTable, shop_with_config)
    account = order.account

    send_order_confirmation_emails(order=order, shop=shop, account=account)

    # Customer + owner notification + owner copy of customer mail — three SMTP sessions.
    assert smtp_cls.call_count == 3
    assert smtp_instance.send_message.call_count == 3
    smtp_instance.quit.assert_called()

    subjects = [call.args[0]["Subject"] for call in smtp_instance.send_message.call_args_list]
    assert any(s.startswith("Orderbevestiging #42") for s in subjects), subjects
    assert any("Nieuwe bestelling #42" in s for s in subjects), subjects
    assert any(s.startswith("[KOPIE klantmail]") and "#42" in s for s in subjects), subjects

    recipients = [call.args[0]["To"] for call in smtp_instance.send_message.call_args_list]
    assert "customer@example.com" in recipients
    assert recipients.count("user@example.com") == 2  # owner notification + owner copy of customer mail


def test_send_order_confirmation_emails_skips_owner_without_contact_email(completed_order, shop_with_config, mock_smtp):
    """If the shop config has no contact.email, only the customer mail goes out."""
    smtp_cls, smtp_instance = mock_smtp
    shop = db.session.get(ShopTable, shop_with_config)
    config = dict(shop.config)
    contact = dict(config.get("contact", {}))
    contact["email"] = ""
    config["contact"] = contact
    shop.config = config
    db.session.commit()

    order = db.session.get(OrderTable, completed_order)
    send_order_confirmation_emails(order=order, shop=shop, account=order.account)

    assert smtp_cls.call_count == 1
    assert smtp_instance.send_message.call_count == 1
    assert smtp_instance.send_message.call_args.args[0]["To"] == "customer@example.com"


def test_send_order_confirmation_emails_swallows_render_errors(shop_with_config, mock_smtp):
    """send_order_confirmation_emails is wrapped in try/except — a broken order must not raise."""
    smtp_cls, _ = mock_smtp
    shop = db.session.get(ShopTable, shop_with_config)

    broken_order = MagicMock()
    broken_order.id = "bad"
    broken_order.order_info = None  # triggers TypeError in _compute_order_lines_for_email
    broken_order.customer_order_id = 1
    broken_order.completed_at = None

    account = MagicMock()
    account.name = "x@example.com"
    account.details = None

    send_order_confirmation_emails(order=broken_order, shop=shop, account=account)
    assert smtp_cls.call_count == 0
