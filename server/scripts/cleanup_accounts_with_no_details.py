import warnings
from typing import Optional
from uuid import UUID

import structlog
import typer
from sqlalchemy import exc as sa_exc

from server.db import db, init_database, transactional
from server.db.models import Account
from server.db.models import OrderTable as Order
from server.settings import app_settings

logger = structlog.get_logger(__name__)


def get_accounts_with_missing_details():
    return db.session.query(Account).filter(Account.details == None)


def get_orders_for_accounts(accounts: list[Account]):
    account_ids = (account.id for account in accounts)
    return db.session.query(Order).filter(Order.account_id.in_(account_ids))


def cleanup_accounts_and_orders(dry_run: bool = False):
    init_database(app_settings)
    logger.info("Cleaning up accounts with no details")

    with transactional(db, logger):
        accounts_with_no_details = get_accounts_with_missing_details().all()
        orders_query = get_orders_for_accounts(accounts_with_no_details)

        if dry_run:
            logger.info("Showing planned changes")
            logger.info(f"Accounts to be deleted: {accounts_with_no_details}")
            logger.info(f"Orders to be deleted: {orders_query.all()}")
            return

        logger.info("Deleting accounts with no details and corresponding orders")
        orders_query.delete()
        get_accounts_with_missing_details().delete()

    logger.info("Clean up of accounts finished")


def main(
    apply: bool = typer.Option(
        False, help="If set, will delete accounts and orders, otherwise only show what would be deleted."
    )
):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=sa_exc.SAWarning)
        cleanup_accounts_and_orders(dry_run=not apply)


if __name__ == "__main__":
    typer.run(main)
