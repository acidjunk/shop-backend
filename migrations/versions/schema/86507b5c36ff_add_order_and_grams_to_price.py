"""empty message

Revision ID: 86507b5c36ff
Revises: b401271d2d81
Create Date: 2022-10-04 15:08:40.244823

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "86507b5c36ff"
down_revision = "b401271d2d81"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("shops_to_price", sa.Column("order_number", sa.Integer(), nullable=True))
    op.add_column("shops_to_price", sa.Column("joint_grams", sa.Float(), nullable=True))
    op.add_column("shops_to_price", sa.Column("piece_grams", sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("shops_to_price", "piece_grams")
    op.drop_column("shops_to_price", "joint_grams")
    op.drop_column("shops_to_price", "order_number")
    # ### end Alembic commands ###
