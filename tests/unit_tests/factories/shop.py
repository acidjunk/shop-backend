import structlog

from server.db import ShopTable, db

logger = structlog.getLogger(__name__)


def make_shop(
    with_products=False,
):
    shop = ShopTable(name="Test Shop", description="Test Shop Description")
    db.session.add(shop)
    db.session.commit()
    return shop.id
