"""Set Tag translations to nullable.

Revision ID: f113c8f56714
Revises: 94e01caa3bf9
Create Date: 2024-08-13 17:39:42.122486

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "f113c8f56714"
down_revision = "94e01caa3bf9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("tag_translations", "alt1_name", existing_type=sa.VARCHAR(length=100), nullable=True)
    op.alter_column("tag_translations", "alt2_name", existing_type=sa.VARCHAR(length=100), nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("tag_translations", "alt2_name", existing_type=sa.VARCHAR(length=100), nullable=False)
    op.alter_column("tag_translations", "alt1_name", existing_type=sa.VARCHAR(length=100), nullable=False)
    # ### end Alembic commands ###
