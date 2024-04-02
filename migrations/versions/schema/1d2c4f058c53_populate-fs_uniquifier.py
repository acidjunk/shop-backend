"""empty message

Revision ID: 1d2c4f058c53
Revises: c7628b49ba8b
Create Date: 2019-09-14 20:21:36.710558

"""
import uuid

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "1d2c4f058c53"
down_revision = "c7628b49ba8b"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    conn.execute(sa.text("""UPDATE "user" SET fs_uniquifier=:uuid"""), uuid=str(uuid.uuid4().hex))
    op.alter_column("user", "fs_uniquifier", nullable=False)


def downgrade():
    pass
