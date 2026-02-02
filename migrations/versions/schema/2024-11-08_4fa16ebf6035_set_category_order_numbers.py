"""set category order numbers.

Revision ID: 4fa16ebf6035
Revises: 5476ce1082c1
Create Date: 2024-11-08 14:29:23.759800

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4fa16ebf6035"
down_revision = "5476ce1082c1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()

    # Fetch all unique shop_ids from the categories table
    shop_ids = conn.execute(sa.text("SELECT DISTINCT shop_id FROM categories")).fetchall()

    # Iterate over each shop_id
    for shop_id_tuple in shop_ids:
        shop_id = shop_id_tuple[0]

        # Select categories for this shop_id and sort them by id or another field
        categories = conn.execute(
            sa.text("""
                SELECT id FROM categories
                WHERE shop_id = :shop_id
                ORDER BY id ASC
            """),
            {"shop_id": shop_id},
        ).fetchall()

        # Update each category with an incremented order_number
        for index, category in enumerate(categories):
            category_id = category[0]
            conn.execute(
                sa.text("UPDATE categories SET order_number = :order_number WHERE id = :id"),
                {"order_number": index + 1, "id": category_id},
            )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE categories SET order_number = 0"))
