import sys
import warnings

import structlog
import typer
from sqlalchemy import exc as sa_exc

from server.db import db, init_database, transactional
from server.db.models import OrderTable as Order
from server.db.models import ShopTable
from server.schemas.shop import ConfigurationV1
from server.settings import app_settings

logger = structlog.get_logger(__name__)


def get_new_config(config: ConfigurationV1):
    print(config)


def rewrite_all_shop_config(dry_run: bool):
    shops = db.session.query(ShopTable).all()
    if not shops:
        sys.exit("No shops found")
    if dry_run:
        logger.info("Dry run enabled, not rewriting all shop config")
    with transactional(db, logger):
        for shop in shops:
            old_config = shop.config
            new_config = get_new_config(old_config)


app = typer.Typer()


@app.command()
def main(
    dry_run: bool = typer.Option(
        True, help="Disable to actually mutate stuff in the DB, otherwise print only what will be done."
    )
):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=sa_exc.SAWarning)
        rewrite_all_shop_config(dry_run=dry_run)


if __name__ == "__main__":
    init_database(app_settings)
    app()
