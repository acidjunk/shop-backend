"""empty message

Revision ID: 3cb638cdf175
Revises: 86507b5c36ff
Create Date: 2022-10-04 15:08:56.636153

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3cb638cdf175"
down_revision = "86507b5c36ff"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(sa.text("""UPDATE shops_to_price SET joint_grams=0.0, piece_grams=0.0, order_number=0"""))
    op.alter_column("shops_to_price", "joint_grams", nullable=False)
    op.alter_column("shops_to_price", "piece_grams", nullable=False)
    op.alter_column("shops_to_price", "order_number", nullable=False)


def downgrade():
    pass
