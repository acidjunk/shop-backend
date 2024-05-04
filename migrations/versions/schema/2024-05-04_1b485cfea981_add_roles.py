"""Add roles.

Revision ID: 1b485cfea981
Revises: c57ec832538d
Create Date: 2024-05-04 02:40:34.382262

"""

from uuid import uuid4

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1b485cfea981"
down_revision = "c57ec832538d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    admin_role_id = uuid4()
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            INSERT INTO role (id, name, description) VALUES (:id, 'admin', 'Admin role')
            """
        ),
        {"id": admin_role_id},
    )


def downgrade() -> None:
    pass
