from uuid import UUID

import structlog

from server.db import db
from server.db.models import Account

logger = structlog.getLogger(__name__)


def make_account(shop_id: UUID, name="Test Account"):
    account = Account(shop_id=shop_id, name=name)
    db.session.add(account)
    db.session.commit()
    return account.id
