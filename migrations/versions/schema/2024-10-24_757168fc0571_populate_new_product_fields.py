"""populate new_product fields.

Revision ID: 757168fc0571
Revises: 35a9b4add7a2
Create Date: 2024-10-24 13:02:50.233499

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '757168fc0571'
down_revision = '35a9b4add7a2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("""UPDATE products SET new_product=false"""))


def downgrade() -> None:
    pass
