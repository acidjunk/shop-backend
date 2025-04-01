"""set product order numbers.

Revision ID: 165126b5951e
Revises: fc7487025229
Create Date: 2024-11-12 12:20:11.582069

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "165126b5951e"
down_revision = "fc7487025229"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # Fetch all unique (shop_id, category_id) pairs from the products table
    shop_category_pairs = conn.execute(sa.text("SELECT DISTINCT shop_id, category_id FROM products")).fetchall()

    # Iterate over each (shop_id, category_id) pair
    for shop_id, category_id in shop_category_pairs:
        # Select products for this shop_id and category_id, sorted by id or another relevant field
        products = conn.execute(
            sa.text(
                """
            SELECT id FROM products
            WHERE shop_id = :shop_id AND category_id = :category_id
            ORDER BY id ASC
        """
            ),
            {"shop_id": shop_id, "category_id": category_id},
        ).fetchall()

        # Update each product with an incremented order_number
        for index, product in enumerate(products):
            product_id = product[0]
            conn.execute(
                sa.text("UPDATE products SET order_number = :order_number WHERE id = :id"),
                {"order_number": index + 1, "id": product_id},
            )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("UPDATE products SET order_number = 0"))
