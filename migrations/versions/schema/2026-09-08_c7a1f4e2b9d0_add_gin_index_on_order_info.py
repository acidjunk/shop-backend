"""Add a GIN index on orders.order_info for product containment lookups.

Order lines live in the ``order_info`` JSONB array, so "which orders contain
product X" is a containment query (``order_info @> '[{"product_id": ...}]'``).
Without an index that is a sequential scan of every order in the table.

``jsonb_path_ops`` is the narrower of the two GIN operator classes: it indexes
only the value paths, which is all ``@>`` needs, and produces a smaller, faster
index than the default ``jsonb_ops``. It does not support key-existence
operators (``?``, ``?|``, ``?&``) — nothing here uses those.

Revision ID: c7a1f4e2b9d0
Revises: b4e6d8f0a2c3
Create Date: 2026-09-08

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "c7a1f4e2b9d0"
down_revision = "b4e6d8f0a2c3"
branch_labels = None
depends_on = None

INDEX_NAME = "ix_orders_order_info_gin"


def upgrade() -> None:
    op.execute(f"CREATE INDEX IF NOT EXISTS {INDEX_NAME} ON orders USING gin (order_info jsonb_path_ops)")


def downgrade() -> None:
    op.execute(f"DROP INDEX IF EXISTS {INDEX_NAME}")
