"""Remove old attributes.

Revision ID: bff2303828ce
Revises: a1b2c3d4e5f6
Create Date: 2026-01-29 20:00:53.141593

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "bff2303828ce"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass  # For now the old stuff can stay, removing this field will add some extra work and i dont want that for the MVP version of the new attributes

def downgrade() -> None:
    pass  # For now the old stuff can stay, removing this field will add some extra work and i dont want that for the MVP version of the new attributes
