"""Add ON DELETE CASCADE to orders.account_id FK.

Revision ID: 7890fc217968
Revises: bff2303828ce
Create Date: 2026-04-02 17:00:01.182729

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "7890fc217968"
down_revision = "bff2303828ce"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("orders_account_id_fkey", "orders", type_="foreignkey")
    op.create_foreign_key("orders_account_id_fkey", "orders", "accounts", ["account_id"], ["id"], ondelete="CASCADE")


def downgrade() -> None:
    op.drop_constraint("orders_account_id_fkey", "orders", type_="foreignkey")
    op.create_foreign_key("orders_account_id_fkey", "orders", "accounts", ["account_id"], ["id"])
