from typing import Optional
from uuid import UUID

import structlog

from server.db import db
from server.db.models import Account

logger = structlog.getLogger(__name__)


def make_account(shop_id: UUID, name: str = "Test Account", details: Optional[dict] = None):
    # Pass ``details`` through only when the caller supplied one. SQLAlchemy's
    # JSON column with the default ``none_as_null=False`` encodes Python None
    # as JSON ``null`` (not SQL NULL), which would break callers that filter
    # on ``Account.details IS NULL`` (e.g. cleanup_accounts_with_no_details).
    kwargs: dict = {"shop_id": shop_id, "name": name}
    if details is not None:
        kwargs["details"] = details
    account = Account(**kwargs)
    db.session.add(account)
    db.session.commit()
    return account.id


def make_account_with_stripe(
    shop_id: UUID,
    name: str = "Test Account",
    customer_id: str = "cus_test_123",
):
    """Convenience wrapper: account whose ``details`` already carries a Stripe id."""
    return make_account(shop_id=shop_id, name=name, details={"stripe_customer_id": customer_id})
