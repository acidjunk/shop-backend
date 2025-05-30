"""info_request_table.

Revision ID: 25b1dce0198a
Revises: b7c94f40743f
Create Date: 2025-04-12 15:22:02.863898

"""

import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op

# revision identifiers, used by Alembic.
revision = "25b1dce0198a"
down_revision = "b7c94f40743f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "info_requests",
        sa.Column(
            "id", sqlalchemy_utils.types.uuid.UUIDType(), server_default=sa.text("uuid_generate_v4()"), nullable=False
        ),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("shop_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.Column("product_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.ForeignKeyConstraint(
            ["shop_id"],
            ["shops.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_info_requests_id"), "info_requests", ["id"], unique=False)
    op.create_index(op.f("ix_info_requests_product_id"), "info_requests", ["product_id"], unique=False)
    op.create_index(op.f("ix_info_requests_shop_id"), "info_requests", ["shop_id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_info_requests_shop_id"), table_name="info_requests")
    op.drop_index(op.f("ix_info_requests_product_id"), table_name="info_requests")
    op.drop_index(op.f("ix_info_requests_id"), table_name="info_requests")
    op.drop_table("info_requests")
    # ### end Alembic commands ###
