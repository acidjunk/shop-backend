"""empty message

Revision ID: d88fa9a45c17
Revises: 1d2c4f058c53
Create Date: 2019-09-17 14:42:36.379593

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d88fa9a45c17"
down_revision = "1d2c4f058c53"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "prices_to_shops",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("shop_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("price_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("half", sa.Boolean(), nullable=True),
        sa.Column("one", sa.Boolean(), nullable=True),
        sa.Column("two_five", sa.Boolean(), nullable=True),
        sa.Column("five", sa.Boolean(), nullable=True),
        sa.Column("joint", sa.Boolean(), nullable=True),
        sa.Column("piece", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"]),
        sa.ForeignKeyConstraint(["price_id"], ["prices.id"]),
        sa.ForeignKeyConstraint(["shop_id"], ["shops.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_prices_to_shops_category_id"), "prices_to_shops", ["category_id"], unique=False)
    op.create_index(op.f("ix_prices_to_shops_id"), "prices_to_shops", ["id"], unique=False)
    op.create_index(op.f("ix_prices_to_shops_price_id"), "prices_to_shops", ["price_id"], unique=False)
    op.create_index(op.f("ix_prices_to_shops_shop_id"), "prices_to_shops", ["shop_id"], unique=False)
    op.create_unique_constraint(None, "prices", ["internal_product_id"])
    op.alter_column("user", "fs_uniquifier", existing_type=sa.VARCHAR(length=255), nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("user", "fs_uniquifier", existing_type=sa.VARCHAR(length=255), nullable=False)
    op.drop_constraint(None, "prices", type_="unique")
    op.drop_index(op.f("ix_prices_to_shops_shop_id"), table_name="prices_to_shops")
    op.drop_index(op.f("ix_prices_to_shops_price_id"), table_name="prices_to_shops")
    op.drop_index(op.f("ix_prices_to_shops_id"), table_name="prices_to_shops")
    op.drop_index(op.f("ix_prices_to_shops_category_id"), table_name="prices_to_shops")
    op.drop_table("prices_to_shops")
    # ### end Alembic commands ###
