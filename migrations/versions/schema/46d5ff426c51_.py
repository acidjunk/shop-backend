"""empty message

Revision ID: 46d5ff426c51
Revises: 1cf62bad0d77
Create Date: 2020-08-18 20:17:50.912174

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "46d5ff426c51"
down_revision = "1cf62bad0d77"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("shops", sa.Column("modified_at", sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("shops", "modified_at")
    # ### end Alembic commands ###
