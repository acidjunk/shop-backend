"""add recurring and json fields.

Revision ID: 94e01caa3bf9
Revises: 5fc9da366ad7
Create Date: 2024-08-13 15:23:49.833907

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "94e01caa3bf9"
down_revision = "5fc9da366ad7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("accounts", sa.Column("details", sa.JSON(), nullable=True))
    op.add_column("products", sa.Column("recurring_price_monthly", sa.Float(), nullable=True))
    op.add_column("products", sa.Column("recurring_price_yearly", sa.Float(), nullable=True))
    op.add_column("products", sa.Column("max_one", sa.Boolean(), nullable=True))
    op.add_column("products", sa.Column("digital", sa.String(length=255), nullable=True))
    op.add_column("products", sa.Column("shippable", sa.Boolean(), nullable=True))
    op.alter_column("products", "price", existing_type=sa.DOUBLE_PRECISION(precision=53), nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("products", "price", existing_type=sa.DOUBLE_PRECISION(precision=53), nullable=False)
    op.drop_column("products", "shippable")
    op.drop_column("products", "digital")
    op.drop_column("products", "max_one")
    op.drop_column("products", "recurring_price_yearly")
    op.drop_column("products", "recurring_price_monthly")
    op.drop_column("accounts", "details")
    # ### end Alembic commands ###
