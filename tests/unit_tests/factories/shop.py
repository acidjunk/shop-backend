import structlog

from server.db import ShopTable, db

logger = structlog.getLogger(__name__)


def make_shop(
    with_config=False,
):
    if with_config:
        config = {"config": {}}
        shop = ShopTable(name="Test Shop", description="Test Shop Description", config=config)
    else:
        shop = ShopTable(name="Test Shop", description="Test Shop Description")
    db.session.add(shop)
    db.session.commit()
    return shop.id
