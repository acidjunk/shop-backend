"""empty message

Revision ID: 5f89f26268da
Revises: 62e315123504
Create Date: 2019-12-06 22:47:06.604183

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5f89f26268da"
down_revision = "62e315123504"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(sa.text("""UPDATE "kinds" SET complete=false, approved=false"""))


def downgrade():
    pass
