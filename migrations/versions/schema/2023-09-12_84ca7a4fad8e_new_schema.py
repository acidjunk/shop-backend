"""New schema.

Revision ID: 84ca7a4fad8e
Revises: 1bb26fb06db1
Create Date: 2023-09-12 16:55:47.371981

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "84ca7a4fad8e"
down_revision = "1bb26fb06db1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "licenses",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_licenses_id"), "licenses", ["id"], unique=False)
    op.create_index(op.f("ix_licenses_name"), "licenses", ["name"], unique=True)
    op.alter_column("shops", "name", existing_type=sa.VARCHAR(length=255), nullable=False)
    op.alter_column(
        "shops_to_price", "joint_grams", existing_type=postgresql.DOUBLE_PRECISION(precision=53), nullable=True
    )
    op.alter_column("shops_to_price", "order_number", existing_type=sa.INTEGER(), nullable=True)
    op.alter_column(
        "shops_to_price", "piece_grams", existing_type=postgresql.DOUBLE_PRECISION(precision=53), nullable=True
    )
    op.alter_column("strains", "name", existing_type=sa.VARCHAR(length=255), nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("strains", "name", existing_type=sa.VARCHAR(length=255), nullable=True)
    op.alter_column(
        "shops_to_price", "piece_grams", existing_type=postgresql.DOUBLE_PRECISION(precision=53), nullable=False
    )
    op.alter_column("shops_to_price", "order_number", existing_type=sa.INTEGER(), nullable=False)
    op.alter_column(
        "shops_to_price", "joint_grams", existing_type=postgresql.DOUBLE_PRECISION(precision=53), nullable=False
    )
    op.alter_column("shops", "name", existing_type=sa.VARCHAR(length=255), nullable=True)
    op.drop_index(op.f("ix_licenses_name"), table_name="licenses")
    op.drop_index(op.f("ix_licenses_id"), table_name="licenses")
    op.drop_table("licenses")
    # ### end Alembic commands ###
