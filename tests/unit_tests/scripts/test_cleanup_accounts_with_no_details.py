from typer.testing import CliRunner

from server.db.models import Account
from server.db.models import OrderTable as Order
from server.scripts.cleanup_accounts_with_no_details import app

runner = CliRunner()


def test_cleanup_of_accounts_and_orders(pending_order):
    assert Account.query.count() == 1
    assert Order.query.count() == 1

    result = runner.invoke(app, ["--apply"])
    assert result.exit_code == 0

    assert "Cleanup of accounts finished" in result.stdout
    assert "accounts_deleted=1" in result.stdout
    assert "orders_deleted=1" in result.stdout

    assert Account.query.count() == 0
    assert Order.query.count() == 0
